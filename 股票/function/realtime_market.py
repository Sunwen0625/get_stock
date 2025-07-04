# realtime_market.py
from __future__ import annotations
import logging
from datetime import time as dtime
from typing import List,cast
from pathlib import Path

from .excel_utils import ExcelSession
from .get_stock import RealtimeStockData   # 你的檔名可自行調整
from . import classification

logger = logging.getLogger(__name__)

CLOSING_TIME: dtime = dtime(13, 40)
POLL_SEC = 3

class RealtimeMarket:
    """負責盤中輪詢、收盤後最後更新與分類。"""

    def __init__(
        self,
        codes: List[str],
        xls_path: str | Path,
        sheet_name: str,
        auto_close: bool =True,  
        *,
        closing: dtime = CLOSING_TIME,
        poll_sec: int = POLL_SEC,
    ) -> None:
        self.codes = codes
        self.xls_path = xls_path
        self.sheet_name = sheet_name
        self.auto_close = auto_close
        self.closing = closing
        self.poll_sec = poll_sec

    # -------- 核心流程 -------- #
    def run(self) -> None:
        # —— 型別斷言：把 Path 強制視為 str —— #
        xls_path_str: str = cast(str, self.xls_path)
        with ExcelSession(xls_path_str, self.sheet_name,auto_close=self.auto_close) as xls:
            #logger.info("♦ 盤中輪詢開始")
            #self._poll_until_close(xls)

            logger.info("♦ 收盤最後一次更新")
            RealtimeStockData.update_realtime_data(self.codes, xls)   # re-use 函式

            logger.info("♦ 分類開始")
            classification.classification(self.codes, xls)
            logger.info("♦ 分類結束")

    """ 
    # -------- 私有方法 -------- #
    def _poll_until_close(self, xls: ExcelSession) -> None:
        while datetime.now().time() < self.closing:
            failed = RealtimeStockData.update_realtime_data(self.codes, xls)
            if failed:
                logger.warning("本回合失敗股票：%s", ", ".join(failed))
            time.sleep(self.poll_sec)
    """
