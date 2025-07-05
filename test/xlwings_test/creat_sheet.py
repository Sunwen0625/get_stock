import xlwings as xw

# 连接到当前活动的Excel应用程序
app = xw.apps.active

# 获取活动工作簿
wb = app.books.active
sheet_names = ['ETF調整配息日', 'ETF管理費率', '績效排行', '美國公債殖利率', '全球經濟總覽', 'ETF比較', 'new title', '主頁', '敦陽科', '統一超', '台達電', '日月光', '台氣電', '範例', '2480敦陽科', '2912統一超', '0050台灣50', '0052富邦科技', '0056元大高股息', '006208富邦台灣50', '00690兆豐藍籌30', '00692富邦公司治理', '00701國泰精選30', '00713元大台灣高息', '00728第一金工業', '00730富邦 高息', '00731FH富時高息', '00850元大台灣永續', '00878國泰高息', '00881國泰5G', '00888永豐台灣', '債券類', 'ETF範例', '雜股', '查 詢網站', '備忘錄', 'CMoneySetting_DTSource', 'CMoneySetting_DTSourceDetail', 'CMoneySetting_APItem', 'CMoneySetting_Convert', 'CMoneySetting_CodeNames', 'CMoneySetting_AUTHOR']
for sheet_name in sheet_names:
    try:
        wb.sheets.add(name=sheet_name)
    except:
        continue

wb.save()