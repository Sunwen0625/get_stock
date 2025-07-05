import requests

url = "https://tw.stock.yahoo.com/quote/0050.TW"  # 替换为您要请求的URL

response = requests.get(url)

if response.status_code == 200:
    print("请求成功！")
else:
    print("请求失败！")
