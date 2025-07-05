import requests
from bs4 import BeautifulSoup

#(市淨率)股價淨值比
url = "https://histock.tw/stock/2912/%E7%9B%88%E9%A4%98%E5%86%8D%E6%8A%95%E8%B3%87%E6%AF%94%E7%8E%87"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

elements = soup.find_all("td")
#盈餘再投資比
print(f"盈餘再投資比:{elements[1].text}")
