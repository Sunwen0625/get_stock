import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import logging

from .crawler.fetch_html import fetch_html
from .crawler.stock_crawler import *
from .excel_utils import ExcelSession 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("crawler")

#=============================================================
class OtherStockData:
    def __init__(
            self, 
            code: str, 
            row: int, 
            is_etf_flag: bool |None
            ) -> None:
        self.code=code
        self.row=row
        self._is_etf_flag = is_etf_flag  # ★ 儲存外部傳入的布林值 (True/False/None)
        self.current_code=""
        # 初始化所有屬性
        self.昨收 = "-"
        self.市盈率 = "-"
        self.市淨率 = "-"
        self.ROE = "-"
        self.資產報酬率 = "-"
        self.毛利率 = "-"
        self.營益率 = "-"
        self.稅後淨利率 = "-"
        self.每股淨值 = "-"
        self.盈餘 = "-"
        self.流動比率 = "-"
        self.速動比率 = "-"
        self.負債比率 = "-"
        self.利息保障倍數 = "-"
        self.應收帳款收現天數 = "-"
        self.存貨週轉天數 = "-"
        self.現金股利 = "-"
        self.股票股利 = "-"
        self.殖利率 = "-"
        self.除息日 = "-"
        self.股息發放日 = "-"
        self.除權日 = "-"
        self.盈餘再投資比 = "-"
        self.現金流="-"
        self.管理費 = "-"
        # 收集訊息用
        self._buf: list[str] = []
        self._buf_lock = threading.Lock()
            
    #info 訊息功能
    def _log(self, msg: str) -> None:
        """把訊息暫存到本股票的 buffer；採用 f-string。"""
        with self._buf_lock:
            self._buf.append(msg)

    def _flush_log(self) -> None:
        """將本股票暫存訊息一次寫出並清空。"""
        with self._buf_lock:
            if self._buf:
                joined = "\n  ".join(self._buf)  # 每行縮排 2 空格更清晰
                logger.info(f"[{self.code}] \n  {joined}")
                self._buf.clear()

    #資料
    def yesterday_close(self,soup:BeautifulSoup) -> None:
        self.昨收 = fetch_yesterday_close(soup)
        self._log(f"{self.code} 昨收:{self.昨收}")

                
    #管理費
    def ManagementFee(self,soup:BeautifulSoup) -> None:
        self.管理費 = fetch_management_fee(soup)
        self._log(f"{self.code} 管理費:{self.管理費}")

    def 股息發放日_ETF(self,soup: BeautifulSoup) -> None:
        self.股息發放日 = fetch_etf_dividend_date(soup)
        self._log(f"{self.code} 股息發放日:{self.股息發放日}")
    
        
    #-------------------------------------------------------------------------------------------
    def 股息發放日_person(self,soup: BeautifulSoup) -> None:
        self.股息發放日 = fetch_person_dividend_date(soup)
        self._log(f"{self.code} 股息發放日:{self.股息發放日}")
        

    #市盈率(PE)
    def get_PE(self):
        self.市盈率 = fetch_pe(self.code, fetch_html)
        self._log(f"{self.code} 市盈率:{self.市盈率}")
        

    #市淨率
    def get_PB(self):
        self.市淨率 = fetch_pb(self.code, fetch_html)
        self._log(f"{self.code} 市淨率:{self.市淨率}")
        

    def 財務報表(self):
        data = fetch_financial(self.code, fetch_html)
        self.除權日 = data["除權日"]
        self.除息日 = data["除息日"]
        self.股票股利 = data["股票股利"]
        self.現金股利 = data["現金股利"]
        self.盈餘 = data["盈餘"]
        self.殖利率 = data["殖利率"]
        self._log(f"{self.code} 財務報表:{data}")
        

    def 杜邦分析(self):
        data = fetch_dupont(self.code, fetch_html)
        self.ROE = data["ROE"]
        self.資產報酬率 = data["資產報酬率"]
        self._log(f"{self.code} 杜邦分析:{data}")
        

    #每股淨值
    def NAVPS(self,soup:BeautifulSoup) -> None:
        self.每股淨值 = fetch_navps(soup)
        self._log(f"{self.code} 每股淨值:{self.每股淨值}")
        
        

    def 三率(self):
        data = fetch_profitability(self.code, fetch_html)
        self.毛利率 = data["毛利率"]
        self.營益率 = data["營益率"]
        self.稅後淨利率 = data["稅後淨利率"]
        self._log(f"{self.code} 三率:{data}")
        

    def 流速動比率(self):
        data = fetch_current_ratio(self.code, fetch_html)
        self.流動比率 = data["流動比率"]
        self.速動比率 = data["速動比率"]
        self._log(f"{self.code} 流速動比率:{data}")
        

    def 負債比(self):
        self.負債比率 = fetch_debt_ratio(self.code, fetch_html)
        self._log(f"{self.code} 負債比:{self.負債比率}")
        

    def get_利息保障倍數(self):
        self.利息保障倍數 = fetch_interest_protection(self.code, fetch_html)
        self._log(f"{self.code} 利息保障倍數:{self.利息保障倍數}")
        

    def 營運週轉天數(self):
        data = fetch_turnover_days(self.code, fetch_html)
        self.應收帳款收現天數 = data["應收帳款收現天數"]
        self.存貨週轉天數 = data["存貨週轉天數"]
        self._log(f"{self.code} 營運週轉天數:{data}")
        

    def get_盈餘再投資比(self):
        self.盈餘再投資比 = fetch_reinvestment(self.code, fetch_html)
        self._log(f"{self.code} 盈餘再投資比:{self.盈餘再投資比}")

    def get_現金流(self):
        self.現金流 = fetch_cashflow(self.code, fetch_html)
        self._log(f"{self.code} 現金流:{self.現金流}")

    def _is_etf(self,symbol: str) -> bool:
        """利用 Yahoo Finance Search API 判斷代碼是否為 ETF。

        API: https://query2.finance.yahoo.com/v1/finance/search?q=<symbol>
        若找不到 API 或 JSON 解析失敗，返回 False（視為個股），並打印警告。
        """
        HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; StockScraper/1.0)"}
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={symbol}.tw"
        try:
            resp = requests.get(url, headers=HEADERS,timeout=5)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}")
            data = resp.json()
            for quote in data.get("quotes", []):
                #logger.info(quote)
                # 台股符號通常返回形如 "0050.TW"，先取前段比對
                if quote.get("typeDisp", "").split(".")[0] == "ETF":
                    return quote.get("quoteType") == "ETF"
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[WARN] is_etf({symbol}) API error: {exc}")
        return False

    


    #判斷
    def judge(self):
        base_url = f"https://tw.stock.yahoo.com/quote/{self.code}"
        profile_url = f"{base_url}/profile"

        yahoo_soup   = fetch_html(base_url)
        profile_soup = fetch_html(profile_url)
        #获取股票代码
        self.current_code = yahoo_soup.find_all("title")
        #logger.info(f"\n {self.current_code}")


        #判斷是否為ETF
        if self._is_etf_flag is not None:          # 外部已指定 True/False
            is_etf_result = self._is_etf_flag
        else:                                      # 否則 fallback 用 API 判斷
            is_etf_result = self._is_etf(self.code)

        if is_etf_result:
            self._handle_etf(profile_soup, yahoo_soup)
        else:
            self._handle_stock(profile_soup, yahoo_soup)

    def _handle_etf(self, profile_soup: BeautifulSoup, yahoo_soup: BeautifulSoup):
        threads=[]
        threads.append(threading.Thread(target=self.ManagementFee, args=(profile_soup,)))
        threads.append(threading.Thread(target=self.股息發放日_ETF, args=(profile_soup,)))
        threads.append(threading.Thread(target=self.財務報表))
        threads.append(threading.Thread(target=self.yesterday_close, args=(yahoo_soup,)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self._flush_log()     


    def _handle_stock(self, profile_soup: BeautifulSoup, yahoo_soup: BeautifulSoup):
        threads=[]
        threads.append(threading.Thread(target=self.get_PE))
        threads.append(threading.Thread(target=self.get_PB))
        threads.append(threading.Thread(target=self.杜邦分析))
        threads.append(threading.Thread(target=self.NAVPS,args=(profile_soup,)))
        threads.append(threading.Thread(target=self.三率))
        threads.append(threading.Thread(target=self.流速動比率))
        threads.append(threading.Thread(target=self.負債比))
        threads.append(threading.Thread(target=self.營運週轉天數))
        threads.append(threading.Thread(target=self.get_利息保障倍數))
        threads.append(threading.Thread(target=self.get_盈餘再投資比))
        threads.append(threading.Thread(target=self.yesterday_close,args=(yahoo_soup,)))
        threads.append(threading.Thread(target=self.股息發放日_person,args=(profile_soup,)))
        threads.append(threading.Thread(target=self.get_現金流))
        threads.append(threading.Thread(target=self.財務報表))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self._flush_log() 

        #---------------------------------------
        
    def _build_row(self) -> list:
        """把所有欄位整理成 list；不做任何 I/O。"""
        return [
            self.昨收 ,
            self.市盈率 ,
            self.市淨率,
            self.ROE ,
            self.資產報酬率 ,
            self.毛利率 ,
            self.營益率 ,
            self.稅後淨利率 ,
            self.每股淨值 ,
            self.盈餘 ,
            self.流動比率 ,
            self.速動比率 ,
            self.負債比率 ,
            self.利息保障倍數 ,
            self.應收帳款收現天數 ,
            self.存貨週轉天數 ,
            self.現金股利 ,
            self.股票股利 ,
            self.殖利率 ,
            self.除息日 ,
            self.股息發放日 ,
            self.除權日 ,
            self.盈餘再投資比 ,
            self.現金流,
            self.管理費 ,
        ]


        
    
def fetch_one(code: str, row: int,isETF:bool|None=False) -> tuple[int, list]:
    stock = OtherStockData(code, row,isETF)
    stock.judge()            # ← 網路抓取 & 解析
    data = stock._build_row()
    return row, data

def update_data_parallel(session: ExcelSession,
                        codes: list[str] | dict[str, dict],
                        row_map: dict[str, int],
                        max_workers: int = 8):
    """
    根據 isETF 欄位做分流，多執行緒抓資料寫入 Excel。
    codes: dict[code, {isETF:bool, position:int}] 或 list[str]
    row_map: {code: row}
    """
    # 1. 取得 code 與 isETF 對應關係
    if isinstance(codes, dict):
        code_list = list(codes.keys())
        etf_map = {code: info.get("isETF", False) for code, info in codes.items()}
    else:
        code_list = codes
        # 若 codes 為 list，無法判斷 isETF，預設 False
        etf_map = {code: None for code in code_list}
    
    # 2) 建立 ThreadPoolExecutor，提交所有任務
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        # 對每支股票提交任務
        futures = {}
        for code in code_list:
            row = row_map[code]
            is_etf  = etf_map[code]
            
            futures[pool.submit(fetch_one, code, row, is_etf)] = (code, row, is_etf)
            

        # 3) 依完成順序寫入 Excel
        for future in as_completed(futures):
            row, data = future.result()          # fetch_one 回傳 (row, data)
            addr = f"P{row}:AN{row}"
            session.range(addr).value = data
            logger.info(f"{futures[future][0]} 寫入完成 (row {row})")

    session.autofit()
    

