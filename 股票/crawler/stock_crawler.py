from bs4 import BeautifulSoup
from bs4.element import Tag

#昨收(基本資料)
def fetch_yesterday_close(soup:BeautifulSoup) -> str:
    li_elements = soup.select("li.price-detail-item")
    for li in li_elements:
        if "昨收" in li.text:
            spans = li.find_all("span")
            if len(spans) >= 2:
                return spans[1].text.strip()
    return "-"

#管理費
def fetch_management_fee(soup: BeautifulSoup) -> str:
    elem = soup.find("div", class_="Py(8px) Pstart(12px) Bxz(bb) etf-management-fee")
    return elem.text if elem else "-"

#股息發放日_ETF
def fetch_etf_dividend_date(soup:BeautifulSoup) -> str:
    elements = soup.find_all("div", class_="table-grid Mb(20px) row-fit-half")
    second_element = elements[0]
    if not isinstance(second_element, Tag):
            return "-"
    
    desired_elements = second_element.find_all("div", class_="Py(8px) Pstart(12px) Bxz(bb)")
    return desired_elements[-1].text
    
    
#股息發放日_person
def fetch_person_dividend_date(soup: BeautifulSoup) -> str:
    elements = soup.find_all("div", class_="table-grid Mb(20px) row-fit-half", attrs={"style": True})
    second_element=elements[1]
    if not isinstance(second_element, Tag):
        return "-"
    
    desired_elements = second_element.find_all("div", class_="Py(8px) Pstart(12px) Bxz(bb)")
    return desired_elements[-1].text
    
#市盈率(PE)
def fetch_pe(code: str, fetch_html) -> str:
    url = f"https://histock.tw/stock/{code}/%E6%9C%AC%E7%9B%8A%E6%AF%94"
    soup = fetch_html(url)
    td = soup.find("td", attrs={"style": True})
    return td.text if td else "-"

#市淨率
def fetch_pb(code: str, fetch_html) -> str:
    url = f"https://histock.tw/stock/{code}/%E8%82%A1%E5%83%B9%E6%B7%A8%E5%80%BC%E6%AF%94"
    soup = fetch_html(url)
    td = soup.find("td", attrs={"style": True})
    return td.text if td else "-"


#財務報表
def fetch_financial(code: str, fetch_html) -> dict:
    url = f"https://histock.tw/stock/{code}/%E9%99%A4%E6%AC%8A%E9%99%A4%E6%81%AF"
    soup = fetch_html(url)
    elements = soup.find_all("td")
    data = {
        "除權日": elements[2].text if len(elements) > 2 else "-",
        "除息日": f'{elements[1].text}/{elements[3].text}' if len(elements) > 3 else "-",
        "股票股利": elements[5].text if len(elements) > 5 else "-",
        "現金股利": elements[6].text if len(elements) > 6 else "-",
        "盈餘": elements[7].text if len(elements) > 7 else "-",
        "殖利率": elements[9].text if len(elements) > 9 and elements[9].text != "" else "-",
    }
    return data

#杜邦分析
def fetch_dupont(code: str, fetch_html) -> dict:
    url = f"https://histock.tw/stock/{code}/%E5%A0%B1%E9%85%AC%E7%8E%87"
    soup = fetch_html(url)
    elements = soup.find_all("td")
    return {
        "ROE": elements[1].text if len(elements) > 1 else "-",
        "資產報酬率": elements[2].text if len(elements) > 2 else "-",
    }

#每股淨值
def fetch_navps(soup: BeautifulSoup) -> str:
    elements = soup.find("div", class_="table-grid Mb(20px) row-fit-half", attrs={"style": True})
    if elements and isinstance(elements, Tag):
        subelements = elements.find_all("div", class_="Py(8px) Pstart(12px) Bxz(bb)")
        if subelements:
            return subelements[-1].text
    return "-"

#三率
def fetch_profitability(code: str, fetch_html) -> dict:
    url = f"https://histock.tw/stock/{code}/%E5%88%A9%E6%BD%A4%E6%AF%94%E7%8E%87"
    soup = fetch_html(url)
    elements = soup.find_all("td")
    return {
        "毛利率": elements[1].text if len(elements) > 1 else "-",
        "營益率": elements[2].text if len(elements) > 2 else "-",
        "稅後淨利率": elements[4].text if len(elements) > 4 else "-",
    }

#流速動比率
def fetch_current_ratio(code: str, fetch_html) -> dict:
    url = f"https://histock.tw/stock/{code}/%E6%B5%81%E9%80%9F%E5%8B%95%E6%AF%94%E7%8E%87"
    soup = fetch_html(url)
    elements = soup.find_all("td")
    return {
        "流動比率": elements[1].text if len(elements) > 1 else "-",
        "速動比率": elements[2].text if len(elements) > 2 else "-",
    }

#負債比
def fetch_debt_ratio(code: str, fetch_html) -> str:
    url = f"https://histock.tw/stock/{code}/%E8%B2%A0%E5%82%B5%E4%BD%94%E8%B3%87%E7%94%A2%E6%AF%94"
    soup = fetch_html(url)
    elements = soup.find_all("td")
    return elements[1].text if len(elements) > 1 else "-"

#利息保障倍數
def fetch_interest_protection(code: str, fetch_html) -> str:
    url = f"https://histock.tw/stock/{code}/%E5%88%A9%E6%81%AF%E4%BF%9D%E9%9A%9C%E5%80%8D%E6%95%B8"
    soup = fetch_html(url)
    elements = soup.find_all("td")
    return elements[1].text if len(elements) > 1 else "-"

#營運週轉天數
def fetch_turnover_days(code: str, fetch_html) -> dict:
    url = f"https://histock.tw/stock/{code}/%E7%87%9F%E9%81%8B%E9%80%B1%E8%BD%89%E5%A4%A9%E6%95%B8"
    soup = fetch_html(url)
    elements = soup.find_all("td")
    return {
        "應收帳款收現天數": elements[1].text if len(elements) > 1 else "-",
        "存貨週轉天數": elements[2].text if len(elements) > 2 else "-",
    }

#盈餘再投資比
def fetch_reinvestment(code: str, fetch_html) -> str:
    url = f"https://histock.tw/stock/{code}/%E7%9B%88%E9%A4%98%E5%86%8D%E6%8A%95%E8%B3%87%E6%AF%94%E7%8E%87"
    soup = fetch_html(url)
    elements = soup.find_all("td")
    return elements[1].text if len(elements) > 1 else "-"

#現金流
def fetch_cashflow(code: str, fetch_html) -> str:
    url = f"https://tw.stock.yahoo.com/quote/{code}/cash-flow-statement"
    soup = fetch_html(url)
    li_list = soup.find_all("li", class_="List(n)")
    if len(li_list) >= 4 and isinstance(li_list[3], Tag):
        elements = li_list[3].find_all("span")
        if len(elements) > 1:
            return elements[1].text
    return "-"

                    