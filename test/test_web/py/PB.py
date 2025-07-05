import requests
from bs4 import BeautifulSoup

#(市淨率)股價淨值比
url = "https://histock.tw/stock/2912/%E8%82%A1%E5%83%B9%E6%B7%A8%E5%80%BC%E6%AF%94"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
span_elements = soup.find("td", attrs={"style": True})
print(f"市淨率:{span_elements.text}")