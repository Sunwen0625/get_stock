import requests
from bs4 import BeautifulSoup

#市盈率
url = "https://histock.tw/stock/2912/%E5%88%A9%E6%BD%A4%E6%AF%94%E7%8E%87"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

elements = soup.find_all("td")
#毛利率
print(f"毛利率:{elements[1].text}")
#營益率
print(f"營益率:{elements[2].text}")
#淨利率
print(f"淨利率:{elements[4].text}")