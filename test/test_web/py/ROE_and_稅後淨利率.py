import requests
from bs4 import BeautifulSoup

#市盈率
url = "https://histock.tw/stock/2912/%E6%9D%9C%E9%82%A6%E5%88%86%E6%9E%90"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

elements = soup.find_all("td")
#ROE
print(f"ROE:{elements[1].text}")
#稅後淨利率
print(f"稅後淨利率:{elements[2].text}")