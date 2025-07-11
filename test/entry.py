import sys
from pathlib import Path

    # 讓本模組可以從 CLI 執行
sys.path.append(str(Path(__file__).resolve().parents[1]))
# ──────────────────────────────
from 股票.Other_Stock_Data import update_data_parallel
from 股票.excel_utils import ExcelSession
from 股票.stock_add_sheet import ensure_code_sheets

long_symbols = [
        '0050', '0052', '0056', '006208', '00679B', '00687B', '00690',
        '00692', '00701', '00713', '00728', '00731', '00751B', '00773B',
        '00850', '00878', '00881', '00888', '1232', '2308', '2317',
        '2480', '2912', '3711', '8926'
    ]
short_codes = ["0050", "2912", "00773B", "1232", "2308", "2317", "2330", "2337"]

with ExcelSession("data.xlsx", "new title",auto_close=False) as xls:  
        # End 收盤資料
        #update_data_parallel(xls,["1232", "2105", "2308","2317"])

        #新增頁面
        #xls.add_sheet("0050",if_exists="rename")

        #重新命名
        #xls.rename_sheet("0050", "0050台灣50", if_exists="rename")
        
        #確保頁面存在
        #ensure_code_sheets(xls, short_codes)
        pass