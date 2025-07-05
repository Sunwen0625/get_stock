import requests
from bs4 import BeautifulSoup

url = "https://tw.stock.yahoo.com/quote/2912.TW/cash-flow-statement"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

li = soup.find_all("li",class_="List(n)")[3]
elements=li.find_all("span")
#現金流
print(f"現金流:{elements[1].text}")