import requests
from bs4 import BeautifulSoup


url = f"https://tw.stock.yahoo.com/quote/2105.TW"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# 找出所有包含昨收的 li 元素
li_elements = soup.select("li.price-detail-item")
for li in li_elements:
    print(li.text)
    # 如果 li 元素的文本包含 "昨收"
    if "昨收" in li.text:
        # 找出第二個 span（即數值）
        spans = li.find_all("span")
        if len(spans) >= 2:
            yesterday_close = spans[1].text.strip()
            print(f"昨收：{yesterday_close}")


    
