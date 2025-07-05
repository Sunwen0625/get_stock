import xlwings as xw

# 连接到当前活动的Excel应用程序
app = xw.apps.active

# 获取活动工作簿
wb = app.books.active

# 获取活动工作表
sheet = wb.sheets.active

# 将第4行的文字向下移动一格
sheet.range("4:4").api.Insert()

# 保存并关闭工作簿
wb.save()

