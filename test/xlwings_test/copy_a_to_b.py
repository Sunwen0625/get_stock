import xlwings as xw

# 连接到当前活动的Excel应用程序
app = xw.apps.active

# 获取活动工作簿
wb = app.books.active

# 获取A工作表和B工作表
sheet_a = wb.sheets['a']
sheet_b = wb.sheets['b']

# 复制B2到N2的范围到B工作表的第4行
sheet_a.range('B2:N2').api.Copy(sheet_b.range('B4').api)

# 保存并关闭工作簿
wb.save()
