import requests
from bs4 import BeautifulSoup

#市盈率
url = "https://histock.tw/stock/2912/%E5%88%A9%E6%81%AF%E4%BF%9D%E9%9A%9C%E5%80%8D%E6%95%B8"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

elements = soup.find_all("td")
#利息保障倍數
print(f"利息保障倍數:{elements[1].text}")