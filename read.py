"""
read.py
主流程：先更新歷史資料 → 收盤後拉價格並做分類
依賴：股票.function.* 相關模組
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd


from 股票 import stock_cache
from 股票.StockDataProcessor import StockDataProcessor,FatalError


# ──────────────────────────────
# 1. 設定與常數
# ──────────────────────────────
CONFIG_PATH = Path("setting.json")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# ──────────────────────────────
# 2. 公用工具
# ──────────────────────────────
def load_config(path: Path = CONFIG_PATH) -> Dict:
    with path.open(encoding="utf-8") as fp:
        return json.load(fp)


def read_symbols(file: str, sheet: str) -> List[str]:
    df = pd.read_excel(file, sheet,dtype="str")
    return df.iloc[:, 1].astype(str).tolist()


def symbols_match_config(symbols: List[str], codes_cfg: dict) -> bool:
    """
    確認 symbols 的順序與 codes_cfg 完全一致。
    
    此函數檢查輸入的股票代碼列表是否與配置字典中的鍵完全匹配，
    包括順序和內容都必須一致。
    
    Args:
        symbols (List[str]): 需要檢查的股票代碼列表
        codes_cfg (dict): 包含股票代碼配置的字典
    
    Returns:
        bool:如果 symbols 的標準化結果與 codes_cfg 的鍵完全匹配則返回 True，否則返回 False
    
    Note:
        - 會使用 stock_cache.normalize_symbol() 對輸入的股票代碼進行標準化處理
        - 比較時要求順序和內容都完全一致
    """

    # 將 symbols 轉換為標準格式
    normalized = [stock_cache.normalize_symbol(s) for s in symbols]
    # 取得 codes_cfg 的鍵
    cfg_keys = list(codes_cfg.keys())
    """ 
    #debug 用
    print(f"symbols = {normalized}")
    print(f"config  = {cfg_keys}")
    """
    # 必須完全一樣，且長度相同
    return normalized == cfg_keys 


def prompt_yes_no(msg: str) -> bool:
    return input(f"{msg} (y/n): ").strip().lower() == "y"







def run() -> None:
    cfg = load_config()

    read_excel = cfg["read_excel"]
    write_excel = cfg["write_excel"]
    wait = cfg["wait"]
    excel_config = cfg["excel_config"]

    #執行前先備份excel檔案
    if excel_config.get("save"):
        from 股票.backup_excel import backup_excel

        backup_excel(
            read_excel["file"],
            excel_config["backup_path"],
            excel_config["backup_filename_format"]
            )

    symbols = read_symbols(read_excel["file"], read_excel["sheet"])

    # 若 symbols 不在設定檔 code 區塊，嘗試更新後重新載入
    if not symbols_match_config(symbols, cfg["stock_code"]):
        logger.info("symbols 與設定檔不一致，執行 stock_cache.update_code_section()")
        stock_cache.update_code_section(symbols)
        cfg = load_config()  # 熱重載
        have_changed = True
    else:
        have_changed = False
        print("symbols 與設定檔一致，無需更新")
    

    try :
        # 2. 收盤後最後一次拉即時 & 分類
        StockDataProcessor(
            codes=cfg["stock_code"],
            xls_path=write_excel["file"],
            sheet_name=write_excel["sheet"],
            auto_close=excel_config["excel_auto_close"],
            auto_add_sheet=excel_config["auto_add_sheet"],
            have_changed=have_changed,
        ).process_market_data()
    except FatalError as exc:
        raise FatalError("股票出現錯誤") from exc


    if wait.get("ending_wait"):
        input("流程完畢，按任意鍵結束…")


# ──────────────────────────────
# 4. 進入點
# ──────────────────────────────
if __name__ == "__main__":
    try:
        run()
    except FatalError as exc:
        logger.error("致命錯誤：%s", exc, exc_info=True)
    except KeyboardInterrupt:
        logger.warning("使用者中斷程式")
