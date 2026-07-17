# StockDataProcessor.py
from __future__ import annotations
import logging
from datetime import time as dtime
from typing import List,cast
from pathlib import Path

from .excel_utils import ExcelSession
from .get_stock import RealtimeStockData   
from . import classification
from . import Other_Stock_Data
from .rename_code_only_sheets import rename_code_only_sheets
from .stock_add_sheet import ensure_code_sheets


logger = logging.getLogger(__name__)

CLOSING_TIME: dtime = dtime(13, 40)
POLL_SEC = 3
class FatalError(Exception):
    """可預期但致命的錯誤 — 直接結束程式。"""

class StockDataProcessor:
    """負責盤中輪詢、收盤後最後更新與分類。"""

    def __init__(
        self,
        codes: List[str] | dict[str, dict],
        xls_path: str | Path,
        sheet_name: str,
        auto_close: bool =True, 
        have_changed: bool = False, 
        auto_add_sheet: bool = False,
        *,
        closing: dtime = CLOSING_TIME,
        poll_sec: int = POLL_SEC,
    ) -> None:
        self.codes = codes
        self.xls_path = xls_path
        self.sheet_name = sheet_name
        self.auto_close = auto_close
        self.have_changed = have_changed
        self.auto_add_sheet = auto_add_sheet
        self.closing = closing
        self.poll_sec = poll_sec

    # -------- 核心流程 -------- #
    def process_market_data(self) -> None:
        """執行完整的數據處理流程"""
        # —— 型別斷言：把 Path 強制視為 str —— #
        xls_path_str: str = cast(str, self.xls_path)
        with ExcelSession(xls_path_str, self.sheet_name,auto_close=self.auto_close) as xls:
            #logger.info("♦ 盤中輪詢開始")
            #self._poll_until_close(xls)

            code_list = self._extract_code_list(self.codes)
            row_map = self._create_position_mapping(self.codes)
            #有改動增加工作表
            if self.have_changed and self.auto_add_sheet :
                ensure_code_sheets(xls,code_list )

            # 1. 額外資料
            try:
                logger.info("更新歷史資料 …")
                Other_Stock_Data.update_data_parallel(xls, self.codes,row_map=row_map)
                logger.info("更新歷史資料完成")
            except Exception : 
                raise FatalError("更新歷史資料失敗") 
            
            # 2. 實時資料
            try :
                logger.info("♦ 收盤最後一次更新")
                RealtimeStockData.update_realtime_data(code_list, xls, row_map)   
                logger.info("♦ 收盤最後一次更新完成")
            except Exception :
                raise FatalError("收盤最後一次更新失敗")
            
            #把有改動的工作表以(代碼+名稱)命名 EX: "0050" -> "0050台灣50"
            if self.have_changed:
                logger.info("♦ 更新工作頁名稱")
                rename_code_only_sheets(xls)

            logger.info("♦ 分類開始")
            classification.classification(code_list, xls)
            logger.info("♦ 分類結束")

            xls.save()  # 保存工作簿
    
    def _extract_code_list(
            self, 
            codes: dict[str, dict]|list[str]
            ) -> List[str]:
        """從輸入中提取股票代碼列表"""
        # 1. 取得代碼名單
        if isinstance(codes, dict):
            code_list = list(codes.keys())
        else:
            # list 直接使用
            code_list = codes
        
        return code_list
    def _create_position_mapping(
            self,
            codes: list[str] | dict[str, dict]
            ) -> dict[str, int]:
        """
        建立股票代碼到Excel行位置的映射
        
        此方法根據輸入的股票代碼格式，建立代碼與Excel工作表中對應行號的映射關係。
        支援兩種輸入格式：
        1. 列表格式：按順序從第2行開始排列
        2. 字典格式：使用position欄位指定行號位置
        
        Args:
            codes (list[str] | dict[str, dict]): 股票代碼資料
                - 當為list時：包含股票代碼字串的列表
                - 當為dict時：以股票代碼為key，包含position欄位的字典為value
                  格式如：{"2330": {"position": 1}, "2317": {"position": 2}}
        
        Returns:
            dict[str, int]: 股票代碼到Excel行號的映射字典
                - key: 股票代碼字串
                - value: 對應的Excel行號（從2開始，因為第1行通常是標題）
        
        Raises:
            ValueError: 當字典格式中存在以下問題時拋出異常：
                - 某個代碼缺少position欄位
                - position欄位值重複
                - position欄位值不連續或不從1開始遞增
        
        Examples:
            >>> # 列表格式輸入
            >>> codes_list = ["2330", "2317", "3008"]
            >>> mapping = self._create_position_mapping(codes_list)
            >>> print(mapping)  # {"2330": 2, "2317": 3, "3008": 4}
            
            >>> # 字典格式輸入
            >>> codes_dict = {
            ...     "2330": {"position": 2},
            ...     "2317": {"position": 3},
            ...     "3008": {"position": 4}
            ... }
            >>> mapping = self._create_position_mapping(codes_dict)
            >>> print(mapping)  # {"2330": 2, "2317": 3, "3008": 4}
        
        Note:
            - 列表格式：row = index + 2（第2行開始排列）
            - 字典格式：row = position + 1（position建議從1開始，對應Excel第2行）
            - Excel第1行通常保留給欄位標題
        """
        if isinstance(codes, dict):
            positions = []
            for k, v in codes.items():
                pos = v.get("position")
                if pos is None:
                    raise ValueError(f"代碼 {k} 缺少 position 欄位")
                positions.append(pos)
            if len(set(positions)) != len(positions):
                raise ValueError("position 欄位重複，請檢查設定")
            if sorted(positions) != list(range(1, len(positions)+1)):
                raise ValueError("position 欄位必須連續遞增，請檢查設定")
            
            # position 欄建議從 1 起算，+1 對應 Excel row=2
            return {k: v["position"]+1 for k, v in codes.items()}
        else:
            return {code: idx+2 for idx, code in enumerate(codes)}

    """ 
    # -------- 私有方法 -------- #
    def _poll_until_close(self, xls: ExcelSession) -> None:
        while datetime.now().time() < self.closing:
            failed = RealtimeStockData.update_realtime_data(self.codes, xls)
            if failed:
                logger.warning("本回合失敗股票：%s", ", ".join(failed))
            time.sleep(self.poll_sec)
    """
