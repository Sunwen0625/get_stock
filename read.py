import pandas as pd
from datetime import datetime,time
import time as t
import requests
import json

from 股票.function import get_stock
from 股票.function import stock_end
from 股票.function.excel_utils import ExcelSession
from 股票.function import classification
import 股票.error_case as error_case



#這裡還有問題
def opening_stock(data_list, write_file: str, write_sheet: str):
    # 取得現在的時間
    now = datetime.now().time()
    # 設定下午1點半的時間
    closing_time = time(13, 40)

    error_count = 0  # 错误计数器
    with ExcelSession(write_file, write_sheet) as xls:
        
        while now < closing_time:
            try:
                get_stock.update_realtime_data(data_list, xls)
                t.sleep(3)
                now = datetime.now().time()
            except requests.exceptions.ConnectionError as e:
                print("連接錯誤:", str(e))
                t.sleep(5)
            except Exception as e:
                error_count += 1
                if error_count >= 2:
                    error_case.error_case(e)
                    break      # 避免無窮迴圈


def reload_data():
    print("是否重新載入資料 y/n")
    input_str = input("輸入:")
    if input_str.lower()  == "y":
        #get_stock.update_realtime_data(data_list,sheet)
        reload_data()
#-------------------------------------------------
# 讀取 JSON 檔案
with open('setting.json', 'r',encoding='utf-8') as file:
    config = json.load(file)
#讀取
read_file = config['read_file']
read_sheet = config['read_sheet']

#寫入
write_file=config['write_file']
write_sheet=config['write_sheet']
#存檔
save=config['save']
#等待
check_wait=config['check_wait']
ending_wait=config['ending_wait']


#-------------------------------------------------------------------------
# 读取Excel文件
df = pd.read_excel(read_file,read_sheet)

# 获取第一列数据并转换为字符串列表
data_list = df.iloc[:, 1].astype(str).tolist()

# 打印列表
print(data_list)


# 另存为新文件
if save:
    import 股票.save_as as save_as
    save_as.save_as(read_file)


#資料
with ExcelSession(write_file, write_sheet) as xls:
    try:
        print("讀取資料")
        stock_end.update_data(data_list,xls)
        print("即時資料-開始:")
    except Exception as e:
        error_case.error_case(e)

#盤中
opening_stock(data_list,write_file=write_file, write_sheet=write_sheet)


#-------------------------------------------------------------------------
try:
    #最後補齊即時資料
    with ExcelSession(write_file, write_sheet) as xls2:
        get_stock.update_realtime_data(data_list, xls2)

        if check_wait:
                reload_data()

        print("即時資料-結束")
        print("資料分類-開始")
    
        classification.classification(data_list,xls2)
        print("資料分類-結束")
    if ending_wait:
        input("------請按任意鍵結束-------")
    
except Exception as e:
    print("發生錯誤，請檢查程式碼或資料")
    error_case.error_case(e)




