import json
import requests
import twstock

SETTING_FILE = "setting.json"

def is_etf(symbol: str) -> bool | None:
    """利用 Yahoo Finance Search API 判斷代碼是否為 ETF。"""
    HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StockScraper/1.0)"}
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={symbol}.tw"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=5)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}")
        data = resp.json()
        for quote in data.get("quotes", []):
            if quote.get("typeDisp", "").split(".")[0] == "ETF":
                return quote.get("quoteType") == "ETF"
    except Exception as exc:
        print(f"[WARN] is_etf({symbol}) API error: {exc}")
        return 
    return False

def load_setting():
    """讀取 setting.json"""
    with open(SETTING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_setting(setting: dict):
    """寫回 setting.json（只動 code 區塊，其餘設定原樣保留）"""
    with open(SETTING_FILE, "w", encoding="utf-8") as f:
        json.dump(setting, f, ensure_ascii=False, indent=2)

def update_code_section(symbols: list[str]):
    """只更新 setting.json 裡的 code 欄位"""
    # 先更新 twstock 的股票代碼清單
    twstock.__update_codes()
    setting = load_setting()
    # 若沒有 code 欄位則新增一個空 dict
    code_cache = setting.get("code", {})

    # 產生新 code 快取，只保留當前 symbols 清單
    new_code = {}
    for symbol in symbols:
        if symbol in code_cache:
            result = code_cache[symbol]
            print(f"{symbol} is ETF (cached): {result}")
        else:
            result = is_etf(symbol)
            print(f"{symbol} is ETF (fetched): {result}")
        new_code[symbol] = result

    # 移除快取裡多餘的股票
    setting["code"] = new_code

    # 其他欄位完全不變
    save_setting(setting)

if __name__ == "__main__":
    # 例：你要判斷的股票清單
    test_symbols = [
        '0050', '0052', '0056', '006208', '00679B', '00687B', '00690',
        '00692', '00701', '00713', '00728', '00731', '00751B', '00773B',
        '00850', '00878', '00881', '00888', '1232', '2308', '2317',
        '2480', '2912', '3711', '8926'
    ]
    update_code_section(test_symbols)
