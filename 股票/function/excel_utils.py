# excel_utils.py
import xlwings as xw


class ExcelSession:
    """
    封裝 xlwings 的工作簿 / 工作表，
    - 進入 with：開檔
    - auto_close=True  → 離開 with 時 save + close
    - auto_close=False → 只 save，不關閉，保留 Excel 供後續檢視
    """

    def __init__(self,
                file: str,
                sheet_name: str | None = None,
                visible: bool = True,
                auto_close: bool = True) -> None:
        
        if visible == False and auto_close == False: 
            self._auto_close = True  # 若不可見，則強制 auto_close=True
            print("[WARN] Excel 在背景開啟且未自動關閉，檔案將被鎖定")
        else:
            self._auto_close = auto_close

        self._app: xw.App | None = None

        try:
            self.wb = xw.Book(file)
        except Exception:
            self._app = xw.App(visible=visible, add_book=False)
            self.wb = self._app.books.open(file)

        self.sh = self.wb.sheets.active if not sheet_name else self.wb.sheets[sheet_name]

    # ---------- 快捷封裝 ----------
    def range(self, addr: str) -> xw.Range:
        """等同 self.sh.range(addr)。"""
        return self.sh.range(addr)

    def autofit(self):
        """column + row 一次自動寬高。"""
        self.sh.autofit()

    def save(self):
        self.wb.save()

    def close(self):
        self.wb.close()
        if self._app:
            self._app.quit()

    # ---------- with 支援 ----------
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb):
        self.save()
        if self._auto_close:           # ★ 只在需要時才 close
            self.close()
