import requests
from bs4 import BeautifulSoup
import time as t
import pandas as pd
import threading
# 读取Excel文件
df = pd.read_excel('88.xlsx')

# 获取第一列数据并转换为字符串列表
data_list = df.iloc[:, 1].astype(str).tolist()



#=============================================================

#判斷
def judge(code):
    url = f"https://tw.stock.yahoo.com/quote/{code}.TW"
    response = requests.get(url)
    yahoo = BeautifulSoup(response.text, "html.parser")
    span_elements = yahoo.find_all("title")

    
    #如果tw找不到就換TWO
    if span_elements == []:
        url = f"https://tw.stock.yahoo.com/quote/{code}.TWO"
        response = requests.get(url)
        yahoo = BeautifulSoup(response.text, "html.parser")
        span_elements = yahoo.find_all("title")
    

    #判斷是否為個股
    url += "/profile"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    #yahoo重要行事曆
    elements =soup.find_all("div",class_="table-grid row-fit-half", attrs={"style": True})
    #個股
    if len(elements)==4:
        thread1  = threading.Thread(target=PE,args=(code,))
        thread2 =threading.Thread(target=PB,args=(code,))
        thread3=threading.Thread(target=杜邦分析,args=(code,))
        thread4=threading.Thread(target=NAVPS,args=(soup,))
        thread5=threading.Thread(target=三率,args=(code,))
        thread6=threading.Thread(target=流速動比率,args=(code,))
        thread7=threading.Thread(target=負債比,args=(code,))
        thread8=threading.Thread(target=利息保障倍數,args=(code,))
        thread9=threading.Thread(target=盈餘再投資比,args=(code,))
        


        thread10=threading.Thread(target=現金股利發放日_person,args=(soup,))
        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        thread5.start()
        thread6.start()
        thread7.start()
        thread8.start()
        thread9.start()
        thread10.start()
        



    #ETF ->只有除息日 跟管理費
    else:
        ManagementFee(soup)
        現金股利發放日_ETF(soup)
        
    財務報表(code)
    HighsAndLows(yahoo)
    #---------------------------------------
    
    print(span_elements)
    print(url)
    print("\n")
    

#收盤
def HighsAndLows(soup):
    close=soup.find("span",class_="Fw(600) Fz(16px)--mobile Fz(14px) D(f) Ai(c)")
    print(f'收盤價:{close.text}')
    

#管理費
def ManagementFee(soup):
    elements =soup.find("div",class_="Py(8px) Pstart(12px) Bxz(bb) etf-management-fee")

    print(f'管理費:{elements.text}')
    

def 現金股利發放日_ETF(soup):
    elements =soup.find_all("div",class_="table-grid Mb(20px) row-fit-half")

    second_element=elements[0]
    desired_elements=second_element.find_all("div",class_="Py(8px) Pstart(12px) Bxz(bb)")
    print(f'現金股利發放日:{desired_elements[-1].text}')
    
#-------------------------------------------------------------------------------------------
def 現金股利發放日_person(soup):
    elements =soup.find_all("div",class_="table-grid Mb(20px) row-fit-half", attrs={"style": True})
    second_element=elements[1]
    find= second_element.find_all("div",class_="Py(8px) Pstart(12px) Bxz(bb)")
    print(f'現金股利發放日:{find[-1].text}')
    

#市盈率(PE)
def PE(code):
    url = f"https://histock.tw/stock/{code}/%E6%9C%AC%E7%9B%8A%E6%AF%94"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    span_elements = soup.find("td", attrs={"style": True})
    print(f"市盈率:{span_elements.text}")
    

#市淨率
def PB(code):
    url = f"https://histock.tw/stock/{code}/%E8%82%A1%E5%83%B9%E6%B7%A8%E5%80%BC%E6%AF%94"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    span_elements = soup.find("td", attrs={"style": True})
    print(f"市淨率:{span_elements.text}")
    

def 財務報表(code):
    url = f"https://histock.tw/stock/{code}/%E9%99%A4%E6%AC%8A%E9%99%A4%E6%81%AF"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.find_all("td")
    #除權日
    print(f'除權日:{elements[2].text}')
    #除息日
    print(f'除息日:{elements[1].text}/{elements[3].text}')
    #股票股利
    print(f'股票股利:{elements[5].text}')
    #現金股利
    print(f'現金股利:{elements[6].text}')
    #EPS(盈餘)
    print(f'EPS:{elements[7].text}')
    #現金殖利率(殖利率)
    print(f'現金殖利率:{elements[9].text}')
    

def 杜邦分析(code):
    url = f"https://histock.tw/stock/{code}/%E6%9D%9C%E9%82%A6%E5%88%86%E6%9E%90"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.find_all("td")
    #ROE
    print(f"ROE:{elements[1].text}")
    #稅後淨利率
    print(f"稅後淨利率:{elements[2].text}")
    

#每股淨值
def NAVPS(soup):
    elements =soup.find("div",class_="table-grid Mb(20px) row-fit-half", attrs={"style": True})
    second_element=elements.find_all("div",class_="Py(8px) Pstart(12px) Bxz(bb)")
    print(f"每股淨值:{second_element[-1].text}")


    

def 三率(code):
    url = f"https://histock.tw/stock/{code}/%E5%88%A9%E6%BD%A4%E6%AF%94%E7%8E%87"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.find_all("td")
    #毛利率
    print(f"毛利率:{elements[1].text}")
    #營益率
    print(f"營益率:{elements[2].text}")
    #淨利率
    print(f"淨利率:{elements[4].text}")
    

def 流速動比率(code):
    url = f"https://histock.tw/stock/{code}/%E6%B5%81%E9%80%9F%E5%8B%95%E6%AF%94%E7%8E%87"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.find_all("td")
    #流動比
    print(f"流動比:{elements[1].text}")
    #速動比
    print(f"速動比:{elements[2].text}")
    

def 負債比(code):
    url = f"https://histock.tw/stock/{code}/%E8%B2%A0%E5%82%B5%E4%BD%94%E8%B3%87%E7%94%A2%E6%AF%94"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.find_all("td")
    #負債比
    print(f"負債比:{elements[1].text}")
    

def 利息保障倍數(code):
    url = f"https://histock.tw/stock/{code}/%E5%88%A9%E6%81%AF%E4%BF%9D%E9%9A%9C%E5%80%8D%E6%95%B8"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.find_all("td")
    #利息保障倍數
    print(f"利息保障倍數:{elements[1].text}")
    

def 營運週轉天數(code):
    url = f"https://histock.tw/stock/{code}/%E7%87%9F%E9%81%8B%E9%80%B1%E8%BD%89%E5%A4%A9%E6%95%B8"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.find_all("td")
    #應收帳款收現天數
    print(f"應收帳款收現天數:{elements[1].text}")
    #存貨週轉天數
    print(f"存貨週轉天數:{elements[2].text}")
    

def 盈餘再投資比(code):
    url = f"https://histock.tw/stock/{code}/%E7%9B%88%E9%A4%98%E5%86%8D%E6%8A%95%E8%B3%87%E6%AF%94%E7%8E%87"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    elements = soup.find_all("td")
    #盈餘再投資比
    print(f"盈餘再投資比:{elements[1].text}")

#測試用資料
#data_list = ["0050","2912","1232","0056"]
# 打印列表
print(data_list)
#判斷列表股票代碼資料 
for i in data_list:
    judge(i)
    
    

   



    
    

   
