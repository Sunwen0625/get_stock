import requests
from bs4 import BeautifulSoup

#市盈率(PE)
url = "https://histock.tw/stock/2912/%E6%9C%AC%E7%9B%8A%E6%AF%94"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
span_elements = soup.find("td", attrs={"style": True})
print(f"市盈率:{span_elements.text}")
