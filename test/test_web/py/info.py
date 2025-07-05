import requests
from bs4 import BeautifulSoup

url = "https://tw.stock.yahoo.com/quote/0050.TW"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")


""" 
#全部資料
pos = soup.find("div", class_="Fx(n) W(316px) Bxz(bb) Pstart(16px) Pt(12px)")
for i in pos:
    print(i.text)

 """


#獲取成交,開盤  等等資料
ul=soup.find("ul",class_="D(f) Fld(c) Flw(w) H(192px) Mx(-16px)")
#變成字典
dictionary = {key.text: value.text for key, value in ul}
#print(dictionary)
#獲取字典裡的"漲跌幅"
print(f"漲跌幅:{dictionary['漲跌幅']}")

#獲取字典裡的"漲跌"
print(f"漲跌:{dictionary['漲跌']}")

