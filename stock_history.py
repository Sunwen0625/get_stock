from __future__ import annotations

import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from twstock import Stock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from read import load_config, read_symbols, symbols_match_config
from 股票 import stock_cache
from 股票.excel_utils import ExcelSession

from 股票.stock_add_sheet import ensure_code_sheets

"""
抓取股票歷史資料腳本
要自行定義時間範圍等之料，並且EXCEL來源是抓取settin.json的設定
"""
START_DATE = date(2026, 6, 1)
TODAY = date.today()
PLACEHOLDER = "-"
HEADERS = ["日期", "代碼","股票名稱" ]

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


def normalize_symbols(symbols: Iterable[str]) -> list[str]:
    return [
        stock_cache.normalize_symbol(str(symbol).strip())
        for symbol in symbols
        if str(symbol).strip() and str(symbol).strip().lower() != "nan"
    ]


def fetch_history_rows(code: str, start: date = START_DATE, end: date = TODAY) -> list[list]:
    """
    取得 twstock 歷史資料，並轉成目前 Excel 使用的 A:p 欄位位置。

    twstock.Stock 歷史資料沒有買進、賣出、單量、委買、委賣，
    這些欄位固定用 "-" 佔位，讓欄位位置和即時資料一致。
    """
    stock = Stock(code)
    stock.fetch_from(start.year, start.month)

    rows: list[list] = []
    previous_close = None

    for idx, trade_date in enumerate(stock.date):
        trade_date = as_date(trade_date)
        close_price = stock.close[idx]
        if trade_date < start or trade_date > end:
            previous_close = close_price
            continue

        yesterday_close = previous_close if previous_close is not None else PLACEHOLDER
        change = stock.change[idx] if stock.change[idx] is not None else PLACEHOLDER
        change_pct = calculate_change_pct(change, yesterday_close)

        rows.append([
            trade_date,
            code,
            PLACEHOLDER,              # 股票名稱
            PLACEHOLDER,              # 買進
            PLACEHOLDER,              # 賣出
            close_price,              # 成交
            change,                   # 漲跌
            change_pct,               # 漲幅%
            PLACEHOLDER,              # 單量
            PLACEHOLDER,              # 委買
            PLACEHOLDER,              # 委賣
            stock.capacity[idx],      # 總量
            stock.high[idx],          # 最高
            stock.low[idx],           # 最低
            stock.open[idx],          # 開盤
            yesterday_close,          # 昨收
        ])
        previous_close = close_price

    return rows


def as_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise TypeError(f"不支援的日期格式: {value!r}")


def calculate_change_pct(change, yesterday_close):
    try:
        if change in (None, "", PLACEHOLDER) or yesterday_close in (None, "", PLACEHOLDER, 0):
            return PLACEHOLDER
        return round(float(change) / float(yesterday_close) * 100, 2)
    except (TypeError, ValueError, ZeroDivisionError):
        return PLACEHOLDER


def find_code_sheet(session: ExcelSession, code: str):
    for sheet in session.wb.sheets:
        if code in sheet.name:
            return sheet
    return session.add_sheet(code, if_exists="return", activate=False)


def write_history_to_sheet(sheet, rows: list[list]) -> None:
    sheet.range("A:P").clear_contents()
    sheet.range("A1:P1").value = HEADERS
    if rows:
        sheet.range(f"A2:P{len(rows) + 1}").value = rows
    sheet.autofit()


def run() -> None:
    cfg = load_config()
    read_excel = cfg["read_excel"]
    write_excel = cfg["write_excel"]
    excel_config = cfg["excel_config"]

    symbols = normalize_symbols(read_symbols(read_excel["file"], read_excel["sheet"]))
    if not symbols_match_config(symbols, cfg["stock_code"]):
        logger.info("symbols 與 setting.json 不一致，更新 stock_code 區塊")
        stock_cache.update_code_section(symbols)
        cfg = load_config()

    codes = list(cfg["stock_code"].keys()) or symbols
    xls_path = Path(write_excel["file"])

    with ExcelSession(
        str(xls_path),
        write_excel["sheet"],
        auto_close=excel_config.get("excel_auto_close", True),
    ) as session:
        ensure_code_sheets(session, codes)

        for code in codes:
            logger.info("抓取 %s 歷史資料：%s ~ %s", code, START_DATE, TODAY)
            rows = fetch_history_rows(code)
            target_sheet = find_code_sheet(session, code)
            write_history_to_sheet(target_sheet, rows)
            logger.info("%s 寫入完成，共 %s 筆", code, len(rows))

        session.save()


if __name__ == "__main__":
    run()
