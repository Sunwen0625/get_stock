# excel_utils.py
import xlwings as xw


class ExcelSession:
    """
    封裝 xlwings 的工作簿 / 工作表，
    - 進入 with：開檔
    - 離開 with：自動 save + close
    """

    def __init__(self,
                file: str,
                sheet_name: str | None = None,
                visible: bool = True):
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
        self.close()
