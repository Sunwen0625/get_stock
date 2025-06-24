"""
stock_runner.py
主流程：先更新歷史資料 → 開盤期間持續拉即時價格 → 收盤後再次拉即時價格並做分類
依賴：股票.function.* 相關模組
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, time as dtime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests

from 股票.function import (
    classification,
    get_stock,
    stock_end,
    stock_cache,
)
from 股票.function.excel_utils import ExcelSession

# ──────────────────────────────
# 1. 設定與常數
# ──────────────────────────────
CONFIG_PATH = Path("setting.json")

CLOSING_TIME: dtime = dtime(13, 40)          # 收盤時間
REALTIME_POLL_SEC = 3                        # 盤中抓價頻率
CONN_RETRY_SEC = 5                           # 連線錯誤再試間隔
MAX_GENERIC_ERRORS = 2                       # 其他例外次數上限

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


# ──────────────────────────────
# 3. 業務邏輯
# ──────────────────────────────
def pull_realtime_until_close(symbols: List[str], xls: ExcelSession) -> None:
    errors = 0
    while datetime.now().time() < CLOSING_TIME:
        try:
            get_stock.update_realtime_data(symbols, xls)
            time.sleep(REALTIME_POLL_SEC)
        except requests.exceptions.ConnectionError as exc:
            logger.warning("連線錯誤：%s，%d 秒後重試", exc, CONN_RETRY_SEC)
            time.sleep(CONN_RETRY_SEC)
        except Exception as exc:  # pylint: disable=broad-except
            errors += 1
            logger.exception("未知錯誤（%d/%d）：%s", errors, MAX_GENERIC_ERRORS, exc)
            if errors >= MAX_GENERIC_ERRORS:
                raise FatalError("盤中拉價連續失敗次數過多") from exc


def run() -> None:
    cfg = load_config()
    symbols = read_symbols(cfg["read_file"], cfg["read_sheet"])

    # 若 symbols 不在設定檔 code 區塊，嘗試更新後重新載入
    if not symbols_match_config(symbols, cfg["code"]):
        logger.info("symbols 與設定檔不一致，執行 stock_cache.update_code_section()")
        stock_cache.update_code_section(symbols)
        cfg = load_config()  # 熱重載

    # 1. 歷史資料
    with ExcelSession(cfg["write_file"], cfg["write_sheet"]) as xls_hist:
        try:
            logger.info("更新歷史資料 …")
            stock_end.update_data(xls_hist, symbols)
        except Exception as exc:  # pylint: disable=broad-except
            raise FatalError("更新歷史資料失敗") from exc

    # 2. 盤中即時資料
    with ExcelSession(cfg["write_file"], cfg["write_sheet"]) as xls_live:
        logger.info("開始盤中即時抓價 …")
        pull_realtime_until_close(symbols, xls_live)

    # 3. 收盤後最後一次拉即時 & 分類
    with ExcelSession(cfg["write_file"], cfg["write_sheet"]) as xls_final:
        logger.info("收盤後最後一次更新即時資料 …")
        get_stock.update_realtime_data(symbols, xls_final)

        if cfg.get("check_wait") and prompt_yes_no("是否再次更新即時資料？"):
            get_stock.update_realtime_data(symbols, xls_final)

        logger.info("進行資料分類 …")
        classification.classification(symbols, xls_final)

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
