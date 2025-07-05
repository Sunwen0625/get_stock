#yahoo
import requests
from bs4 import BeautifulSoup

url = "https://tw.stock.yahoo.com/quote/2912.TW/profile"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

""" 
#重要行事曆
elements =soup.find_all("div",class_="table-grid row-fit-half", attrs={"style": True})

if len(elements) >= 2:
    elements =soup.find("div",class_="Py(8px) Pstart(12px) Bxz(bb) etf-management-fee")

    print(f'管理費:{elements.text}')


 """

#財務資訊
""" 
#每股淨值
elements =soup.find("div",class_="table-grid Mb(20px) row-fit-half", attrs={"style": True})
second_element=elements.find_all("div",class_="Py(8px) Pstart(12px) Bxz(bb)")
print(f"每股淨值:{second_element[-1].text}")

 """




""" 
#現金股利發放日    by 個股

elements =soup.find_all("div",class_="table-grid Mb(20px) row-fit-half", attrs={"style": True})
second_element=elements[1]
find= second_element.find_all("div",class_="Py(8px) Pstart(12px) Bxz(bb)")
print(f'現金股利發放日:{find[-1].text}')

 """




""" 

#現金股利發放日 by ETF
elements =soup.find_all("div",class_="table-grid Mb(20px) row-fit-half")

second_element=elements[0]
desired_elements=second_element.find_all("div",class_="Py(8px) Pstart(12px) Bxz(bb)")
print(f'現金股利發放日:{desired_elements[-1].text}')
 """