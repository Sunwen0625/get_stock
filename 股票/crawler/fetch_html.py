import requests
from bs4 import BeautifulSoup
import time
#連接url如果狀態!=200就重抓一次
def fetch_html(url: str) -> BeautifulSoup:
    """
    共用抓取＋重試邏輯，失敗時擲回例外。

    该函数用于从指定的URL抓取HTML内容，并使用BeautifulSoup解析。如果请求失败，会尝试重试3次。
    如果3次请求都失败，则抛出运行时异常。

    参数:
    url (str): 要抓取的网页的URL。

    返回:
    BeautifulSoup: 解析后的HTML内容。

    抛出:
    RuntimeError: 如果3次请求都失败，抛出运行时异常，包含HTTP状态码和URL信息。
    """
    for _ in range(3):  # 尝试3次
        resp = requests.get(url, timeout=5)  # 发送GET请求，设置超时时间为5秒
        if resp.status_code == 200:  # 如果状态码为200，表示请求成功
            return BeautifulSoup(resp.text, "html.parser")  # 返回BeautifulSoup对象
        time.sleep(1)  # 如果请求失败，等待1秒后重试
    raise RuntimeError(f"HTTP {resp.status_code}: {url}")  # 如果3次请求都失败，抛出异常