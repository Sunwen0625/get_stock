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


from 股票.function import (
    stock_end,
    stock_cache,
    
)
from 股票.function.realtime_market import RealtimeMarket
from 股票.function.excel_utils import ExcelSession
from 股票.function.stock_add_sheet import ensure_code_sheets

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
    df = pd.read_excel(file, sheet)
    return df.iloc[:, 1].astype(str).tolist()


def symbols_match_config(symbols: List[str], codes_cfg: Dict[str, bool]) -> bool:
    """確認 symbols 均存在於 codes_cfg 的 key 內"""
    return all(sym in codes_cfg for sym in symbols)


def prompt_yes_no(msg: str) -> bool:
    return input(f"{msg} (y/n): ").strip().lower() == "y"


class FatalError(Exception):
    """可預期但致命的錯誤 — 直接結束程式。"""




def run() -> None:
    cfg = load_config()
    symbols = read_symbols(cfg["read_file"], cfg["read_sheet"])

    # 若 symbols 不在設定檔 code 區塊，嘗試更新後重新載入
    if not symbols_match_config(symbols, cfg["code"]):
        logger.info("symbols 與設定檔不一致，執行 stock_cache.update_code_section()")
        stock_cache.update_code_section(symbols)
        cfg = load_config()  # 熱重載
        have_changed = True
    else:
        have_changed = False
        print("symbols 與設定檔一致，無需更新")
    
    # 1. 歷史資料
    with ExcelSession(cfg["write_file"], cfg["write_sheet"]) as xls_hist:
        if have_changed:
            ensure_code_sheets(xls_hist,symbols )

        try:
            logger.info("更新歷史資料 …")
            stock_end.update_data_parallel(xls_hist, cfg["code"])
        except Exception as exc:  # pylint: disable=broad-except
            raise FatalError("更新歷史資料失敗") from exc

    

    # 2. 收盤後最後一次拉即時 & 分類
    RealtimeMarket(
        codes=symbols,
        xls_path=cfg["write_file"],
        sheet_name=cfg["write_sheet"],
        auto_close=cfg["excel_auto_close"],
        have_changed=have_changed,
    ).run()
    

    if cfg.get("save"):
        import 股票.save_as as save_as  # 避免循環匯入
        save_as.save_as(cfg["read_file"])

    if cfg.get("ending_wait"):
        input("流程完畢，按任意鍵結束…")


# ──────────────────────────────
# 4. 進入點
# ──────────────────────────────
if __name__ == "__main__":
    try:
        run()
    except FatalError as exc:
        logger.error("致命錯誤：%s", exc)
    except KeyboardInterrupt:
        logger.warning("使用者中斷程式")
