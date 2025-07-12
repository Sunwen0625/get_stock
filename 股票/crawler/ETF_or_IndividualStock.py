import requests
import logging

logger = logging.getLogger(__name__)


def is_etf(symbol: str) -> bool:
    HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StockScraper/1.0)"}
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={symbol}.tw"

    resp = requests.get(url, headers=HEADERS, timeout=5)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}")
    data = resp.json()
    quotes = data.get("quotes", [])

    for quote in quotes:
        match quote.get("typeDisp", ""):
            case "ETF":
                return True
            case "Equity":
                return False

    # 如果完全找不到 symbol（quotes 是空的）
    raise RuntimeError(f"找不到此代碼: {symbol}")

if __name__ == "__main__":
    print(is_etf("0050"))    # True
    print(is_etf("2330"))    # False
    print(is_etf("INVALID")) # 會拋出 RuntimeError: 找不到此代碼: INVALID
    print(is_etf("114514"))    # 會拋出 RuntimeError: 找不到此代碼: 114514

    