import requests
from bs4 import BeautifulSoup

url = 'https://www.wantgoo.com/'

response = requests.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'})
print(response.status_code)
soup = BeautifulSoup(response.text, 'html.parser')

print(soup.find('title').text)
