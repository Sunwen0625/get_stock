import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import logging


from excel_utils import ExcelSession 
from settings_loader import load_codes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("crawler")

#=============================================================
class End:
    def __init__(
            self, 
            code: str, 
            row: int, 
            is_etf_flag: bool | None = None
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
        li_elements = soup.select("li.price-detail-item")
        for li in li_elements:
            # 如果 li 元素的文本包含 "昨收"
            if "昨收" in li.text:
                # 找出第二個 span（即數值）
                spans = li.find_all("span")
                if len(spans) >= 2:
                    yesterday_close = spans[1].text.strip()
                    self.昨收=yesterday_close
                    self._log(f"{self.code} 昨收:{yesterday_close}")

                
    #管理費
    def ManagementFee(self,soup:BeautifulSoup) -> None:
        elements =soup.find("div",class_="Py(8px) Pstart(12px) Bxz(bb) etf-management-fee")
        if elements:
            self.管理費=elements.text
            self._log(f"{self.code}管理費:{elements.text}")
        else:
            self._log(f"[警告] {self.code} 找不到管理費")

    def 股息發放日_ETF(self,soup: BeautifulSoup) -> None:
        elements =soup.find_all("div",class_="table-grid Mb(20px) row-fit-half")

        second_element=elements[0]
        if not isinstance(second_element, Tag):
            return
        desired_elements=second_element.find_all("div",class_="Py(8px) Pstart(12px) Bxz(bb)")
        self.股息發放日=desired_elements[-1].text
        self._log(f'{self.code} 股息發放日:{desired_elements[-1].text}')
    
        
    #-------------------------------------------------------------------------------------------
    def 股息發放日_person(self,soup: BeautifulSoup) -> None:
        elements =soup.find_all("div",class_="table-grid Mb(20px) row-fit-half", attrs={"style": True})
        second_element=elements[1]
        if not isinstance(second_element, Tag):
            return
        find= second_element.find_all("div",class_="Py(8px) Pstart(12px) Bxz(bb)")
        self.股息發放日=find[-1].text
        self._log(f"{self.code} 股息發放日:{find[-1].text}")
        

    #市盈率(PE)
    def get_PE(self):
        # 定义获取市盈率的函数
        url = f"https://histock.tw/stock/{self.code}/%E6%9C%AC%E7%9B%8A%E6%AF%94"

        # 获取网页内容
        soup = fetch_html(url)
        # 查找包含市盈率的span元素
        span_elements = soup.find("td", attrs={"style": True})
        # 如果没有找到span元素，则返回
        if span_elements is None:
            return
        # 将市盈率赋值给self.市盈率
        self.市盈率=span_elements.text
        # 打印市盈率
        self._log(f"{self.code} 市盈率:{span_elements.text}")
        

    #市淨率
    def get_PB(self):
        # 获取市净率
        url = f"https://histock.tw/stock/{self.code}/%E8%82%A1%E5%83%B9%E6%B7%A8%E5%80%BC%E6%AF%94"
        
        # 获取网页内容
        soup = fetch_html(url)
        # 查找包含市净率的span元素
        span_elements = soup.find("td", attrs={"style": True})
        # 如果没有找到span元素，则返回
        if span_elements is None:
            return 
        # 将市净率赋值给self.市淨率
        self.市淨率=span_elements.text
        # 打印市净率
        self._log(f"{self.code} 市淨率:{span_elements.text}")
        

    def 財務報表(self):
        #获取财务报表的url
        url = f"https://histock.tw/stock/{self.code}/%E9%99%A4%E6%AC%8A%E9%99%A4%E6%81%AF"
        #获取网页内容
        soup = fetch_html(url)

        #获取网页中的所有td元素
        elements = soup.find_all("td")
        #如果没有获取到td元素，则返回
        if elements is []:
            return 
        

        #除權日
        #如果除權日不为空，则赋值给self.除權日
        if elements[2].text!="":
            self.除權日=elements[2].text
        #打印除權日
        self._log(f'{self.code} 除權日:{elements[2].text}')

        #除息日
        #将除息日的年月日拼接起来，赋值给self.除息日
        self.除息日=f'{elements[1].text}/{elements[3].text}'
        #打印除息日
        self._log(f'{self.code} 除息日:{elements[1].text}/{elements[3].text}')

        #股票股利
        #将股票股利赋值给self.股票股利
        self.股票股利=elements[5].text
        #打印股票股利
        self._log(f'{self.code} 股票股利:{elements[5].text}')

        #現金股利
        #将現金股利赋值给self.現金股利
        self.現金股利=elements[6].text
        #打印現金股利
        self._log(f'{self.code} 現金股利:{elements[6].text}')

        #EPS(盈餘)
        #将EPS(盈餘)赋值给self.盈餘
        self.盈餘=elements[7].text
        #打印EPS(盈餘)
        self._log(f'{self.code} EPS:{elements[7].text}')

        #現金殖利率(殖利率)
        #如果現金殖利率不为空，则赋值给self.殖利率
        if elements[9].text!="":
            self.殖利率=elements[9].text
        #打印現金殖利率(殖利率)
        self._log(f'{self.code} 現金殖利率:{elements[9].text}')
        

    def 杜邦分析(self):
        # 获取杜邦分析页面URL
        url = f"https://histock.tw/stock/{self.code}/%E5%A0%B1%E9%85%AC%E7%8E%87"
        # 获取页面内容
        soup = fetch_html(url)

        # 获取页面中的所有td元素
        elements = soup.find_all("td")
        # 如果没有获取到td元素，则返回"-"
        if elements is []:
            return 
        #ROE
        self.ROE=elements[1].text
        self._log(f"{self.code} ROE:{elements[1].text}")
        #ROA
        self.資產報酬率=elements[2].text
        self._log(f"{self.code} 資產報酬率:{elements[2].text}")
        

    #每股淨值
    def NAVPS(self,soup:BeautifulSoup) -> None:
        elements =soup.find("div",class_="table-grid Mb(20px) row-fit-half", attrs={"style": True})
        if not isinstance(elements, Tag):
            return
        second_element=elements.find_all("div",class_="Py(8px) Pstart(12px) Bxz(bb)")
        if second_element is []:
            return

        self.每股淨值=second_element[-1].text
        self._log(f"{self.code} 每股淨值:{second_element[-1].text}")
        
        

    def 三率(self):
        #获取毛利率、營益率、稅後淨利率
        url = f"https://histock.tw/stock/{self.code}/%E5%88%A9%E6%BD%A4%E6%AF%94%E7%8E%87"
        soup = fetch_html(url)

        elements = soup.find_all("td")
        if elements is []:
            return

        #毛利率
        self.毛利率=elements[1].text
        self._log(f"{self.code} 毛利率:{elements[1].text}")
        #營益率
        self.營益率=elements[2].text
        self._log(f"{self.code} 營益率:{elements[2].text}")
        #稅後淨利率
        self.稅後淨利率=elements[4].text
        self._log(f"{self.code} 淨利率:{elements[4].text}")
        

    def 流速動比率(self):
        url = f"https://histock.tw/stock/{self.code}/%E6%B5%81%E9%80%9F%E5%8B%95%E6%AF%94%E7%8E%87"
        soup = fetch_html(url)

        elements = soup.find_all("td")
        if elements is []:
            return
        #流動比
        self.流動比率=elements[1].text
        self._log(f"{self.code} 流動比:{elements[1].text}")
        #速動比
        self.速動比率=elements[2].text
        self._log(f"{self.code} 速動比:{elements[2].text}")
        

    def 負債比(self):
        url = f"https://histock.tw/stock/{self.code}/%E8%B2%A0%E5%82%B5%E4%BD%94%E8%B3%87%E7%94%A2%E6%AF%94"
        soup = fetch_html(url)

        elements = soup.find_all("td")
        #負債比
        self.負債比率=elements[1].text
        self._log(f"{self.code} 負債比:{elements[1].text}")
        

    def get_利息保障倍數(self):
        url = f"https://histock.tw/stock/{self.code}/%E5%88%A9%E6%81%AF%E4%BF%9D%E9%9A%9C%E5%80%8D%E6%95%B8"
        soup = fetch_html(url)

        elements = soup.find_all("td")
        if elements is None:
            return "-"
        #利息保障倍數
        self.利息保障倍數=elements[1].text
        self._log(f"{self.code} 利息保障倍數:{elements[1].text}")
        

    def 營運週轉天數(self):
        url = f"https://histock.tw/stock/{self.code}/%E7%87%9F%E9%81%8B%E9%80%B1%E8%BD%89%E5%A4%A9%E6%95%B8"
        soup = fetch_html(url)

        elements = soup.find_all("td")
        if elements is []:
            return 
        #應收帳款收現天數
        self.應收帳款收現天數=elements[1].text
        self._log(f"{self.code} 應收帳款收現天數:{elements[1].text}")
        #存貨週轉天數
        self.存貨週轉天數=elements[2].text
        self._log(f"{self.code} 存貨週轉天數:{elements[2].text}")
        

    def get_盈餘再投資比(self):
        url = f"https://histock.tw/stock/{self.code}/%E7%9B%88%E9%A4%98%E5%86%8D%E6%8A%95%E8%B3%87%E6%AF%94%E7%8E%87"
        soup = fetch_html(url)

        elements = soup.find_all("td")
        if elements is None:
            return
        #盈餘再投資比
        self.盈餘再投資比=elements[1].text
        self._log(f"{self.code} 盈餘再投資比:{elements[1].text}")

    def get_現金流(self):
        url = f"https://tw.stock.yahoo.com/quote/{self.code}/cash-flow-statement"
        soup = fetch_html(url)

        li = soup.find_all("li",class_="List(n)")[3]
        if li is None:
            return 
        if not isinstance(li, Tag):
            return 
        elements=li.find_all("span")
        self.現金流=elements[1].text
        #現金流
        self._log(f"{self.code} 現金流:{elements[1].text}")

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

#連接url如果狀態!=200就重抓一次
def fetch_html(url: str) -> BeautifulSoup:
    """
    共用抓取＋重試邏輯，失敗時擲回例外。

    该函数用于从指定的URL抓取HTML内容，并使用BeautifulSoup解析。如果请求失败，会尝试重试3次。
    如果3次请求都失败，则抛出运行时异常。

    参数:
    url (str): 要抓取的网页的URL。

    返回:
    BeautifulSoup: 解析后的HTML内容。

    抛出:
    RuntimeError: 如果3次请求都失败，抛出运行时异常，包含HTTP状态码和URL信息。
    """
    for _ in range(3):  # 尝试3次
        resp = requests.get(url, timeout=5)  # 发送GET请求，设置超时时间为5秒
        if resp.status_code == 200:  # 如果状态码为200，表示请求成功
            return BeautifulSoup(resp.text, "html.parser")  # 返回BeautifulSoup对象
        time.sleep(1)  # 如果请求失败，等待1秒后重试
    raise RuntimeError(f"HTTP {resp.status_code}: {url}")  # 如果3次请求都失败，抛出异常
        
    
def fetch_one(code: str, row: int) -> tuple[int, list]:
    stock = End(code, row)
    stock.judge()            # ← 網路抓取 & 解析
    data = stock._build_row()
    return row, data

def update_data_parallel(session: ExcelSession,
                        codes: list[str] | dict[str, bool],
                        max_workers: int = 6):
    if isinstance(codes, dict):
        iterable = codes.items()
    else:
        iterable = ((c, None) for c in codes)
    
    # 2) 建立 ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        # 對每支股票提交任務
        futures = {
            pool.submit(fetch_one, code, idx + 2):  (code, idx + 2)
            for idx, (code, _) in enumerate(iterable)
        }

        # 3) 依完成順序寫入 Excel
        for future in as_completed(futures):
            row, data = future.result()          # 取 (row, list)
            addr = f"P{row}:AN{row}"
            session.range(addr).value = data
            logger.info(f"{futures[future][0]} 寫入完成 (row {row})")

    session.autofit()
    session.save()




if __name__ == '__main__':
    
    with ExcelSession("data.xlsx", "new title") as xls:  # ← 只要這一行
        update_data_parallel(xls,["1232", "2105", "2308","2317"])
