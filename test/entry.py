import sys
from pathlib import Path

    # 讓本模組可以從 CLI 執行
sys.path.append(str(Path(__file__).resolve().parents[1]))
# ──────────────────────────────
from 股票.function.stock_end import update_data_parallel
from 股票.function.excel_utils import ExcelSession

with ExcelSession("data.xlsx", "new title",auto_close=False) as xls:  
        # End 收盤資料
        #update_data_parallel(xls,["1232", "2105", "2308","2317"])

        #新增頁面
        #xls.add_sheet("0050",if_exists="rename")

        #重新命名
        #xls.rename_sheet("0050", "0050台灣50", if_exists="rename")

        xls.get_sheet(["0050", "2330", "2317"])