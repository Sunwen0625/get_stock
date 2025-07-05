import requests
from bs4 import BeautifulSoup


url = "https://histock.tw/stock/2912/%E8%B2%A0%E5%82%B5%E4%BD%94%E8%B3%87%E7%94%A2%E6%AF%94"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

elements = soup.find_all("td")
#負債比
print(f"負債比:{elements[1].text}")