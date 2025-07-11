from .excel_utils import ExcelSession

def classification(codes: list[str], session: ExcelSession) -> None: 
    """
    將來源工作表 (session.sh) 中第 2 列開始的資料，
    依據股票代號複製到目標工作表（名稱含該代號者）。

    - symbols: 目標股票代號清單
    - session : 以 ExcelSession 封裝的 workbook 與來源 sheet
    """
    wb          = session.wb      # xw.Book
    src_sheet   = session.sh      # 來源 Sheet
    all_sheets  = {s.name: s for s in wb.sheets}

    for row_idx, code in enumerate(codes, start=2):   # 對應 A2, A3 ...
        # 找出名稱包含 code 的工作表
        targets = [s for name, s in all_sheets.items() if code in name]
        for dst in targets:
            # 若 A{row_idx} 已經複製過，就不插入空白列
            if src_sheet.range(f"A{row_idx}").value != dst.range("A5").value:
                dst.range("4:4").api.Insert()
            # 複製來源 A{row}:P{row} 到目標 A5
            src_sheet.range(f"A{row_idx}:P{row_idx}").api.Copy(dst.range("A5").api)
            dst.autofit()    # 自動欄寬/高
        

    
    
    
    