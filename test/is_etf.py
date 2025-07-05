import requests

def is_etf(symbol: str) -> bool:
    """利用 Yahoo Finance Search API 判斷代碼是否為 ETF。

    API: https://query2.finance.yahoo.com/v1/finance/search?q=<symbol>
    若找不到 API 或 JSON 解析失敗，返回 False（視為個股），並打印警告。
    """
    HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StockScraper/1.0)"}
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={symbol}.tw"
    try:
        resp = requests.get(url, headers=HEADERS,timeout=5)
        #resp = requests.get(url,timeout=5)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}")
        data = resp.json()
        for quote in data.get("quotes", []):
            #print(quote)
            # 台股符號通常返回形如 "0050.TW"，先取前段比對
            if quote.get("typeDisp", "").split(".")[0] == "ETF":
                return quote.get("quoteType") == "ETF"
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] is_etf({symbol}) API error: {exc}")
    return False 


if __name__ == "__main__":
    # 測試用例
    test_symbols = ['0050', '0052', '0056', '006208', '00679B', '00687B', '00690', '00692', '00701', '00713', '00728', '00731', '00751B', '00773B', '00850', '00878', '00881', '00888', '1232', '2308', '2317', '2480', '2912', '3711', '8926']
    for symbol in test_symbols:
        print(f"{symbol} is ETF: {is_etf(symbol)}")