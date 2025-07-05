import requests
from bs4 import BeautifulSoup

#市盈率
url = "https://histock.tw/stock/2912/%E6%B5%81%E9%80%9F%E5%8B%95%E6%AF%94%E7%8E%87"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

elements = soup.find_all("td")
#流動比
print(f"流動比:{elements[1].text}")
#速動比
print(f"速動比:{elements[2].text}")