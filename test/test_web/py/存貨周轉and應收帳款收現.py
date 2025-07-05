import requests
from bs4 import BeautifulSoup


url = "https://histock.tw/stock/2912/%E7%87%9F%E9%81%8B%E9%80%B1%E8%BD%89%E5%A4%A9%E6%95%B8"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

elements = soup.find_all("td")
#應收帳款收現天數
print(f"應收帳款收現天數:{elements[1].text}")
#存貨週轉天數
print(f"存貨週轉天數:{elements[2].text}")