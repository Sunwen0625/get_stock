import requests
from bs4 import BeautifulSoup


url = "https://histock.tw/stock/2912/%E9%99%A4%E6%AC%8A%E9%99%A4%E6%81%AF"
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
