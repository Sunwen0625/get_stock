import json
import re
import requests
import twstock

SETTING_FILE = "setting.json"
_CODE_PREFIX_RE = re.compile(r"^(\d{1,5})([A-Za-z]*)$")  # 支援補齊成4~6碼股票代碼

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

def normalize_symbol(code: str) -> str:
    """補齊股票代碼前綴 0，例如 '50' → '0050'"""
    match = _CODE_PREFIX_RE.match(code)
    if match:
        num, suffix = match.groups()
        return num.zfill(4) + suffix.upper()
    return code

def load_setting():
    """讀取 setting.json"""
    with open(SETTING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_setting(setting: dict):
    """寫回 setting.json（只動 code 區塊，其餘設定原樣保留）"""
    with open(SETTING_FILE, "w", encoding="utf-8") as f:
        json.dump(setting, f, ensure_ascii=False, indent=4)

def update_code_section(symbols: list[str]):
    """只更新 setting.json 裡的 code 欄位"""
    # 先更新 twstock 的股票代碼清單
    twstock.__update_codes()
    setting = load_setting()
    # 若沒有 code 欄位則新增一個空 dict
    code_cache = setting.get("stock_code", {})

    # 產生新 code 快取，只保留當前 symbols 清單
    new_code = {}
    for idx, symbol in enumerate(symbols, start=1):   # 位置從 1 開始
        norm_symbol = normalize_symbol(symbol)
        # 取得 ETF 狀態（舊有快取 or 查詢）
        if isinstance(code_cache.get(norm_symbol), dict):
            result = code_cache[norm_symbol].get("isETF")
        else:
            result = code_cache.get(norm_symbol)
            
        if result is None:
            result = is_etf(norm_symbol)
            print(f"{norm_symbol} is ETF (fetched): {result}")
        else:
            print(f"{norm_symbol} is ETF (cached): {result}")
        new_code[norm_symbol] = {"isETF": bool(result), "position": idx}

    # 移除快取裡多餘的股票
    setting["stock_code"] = new_code

    # 其他欄位完全不變
    save_setting(setting)

