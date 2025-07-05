import xlwings as xw
import pandas as pd
#  √  move   ,copy     ,


# 连接到当前活动的Excel应用程序
app = xw.apps.active

# 获取活动工作簿
wb = app.books.active
my_list = [s.name for s in wb.sheets]

# 读取Excel文件
df = pd.read_excel("data.xlsx","a")

# 获取第一列数据并转换为字符串列表
data_list = df.iloc[:, 1].astype(str).tolist()
# 获取A工作表和B工作表
original_sheet = wb.sheets['a']

n=1
for target in data_list:
    n+=1
    for i ,element in enumerate(my_list):
        if target in element:
            print(f"Element '{element}' contains target '{target}' at position {i}")
            # 将第4行的文字向下移动一格
            wb.sheets[i].range("4:4").api.Insert()
            #複製
            original_sheet.range(f'A{n}:P{n}').api.Copy(wb.sheets[i].range('A5').api)
            wb.sheets[i].autofit()
# 保存并关闭工作簿
#wb.save() 


print(data_list)
#print(my_list)