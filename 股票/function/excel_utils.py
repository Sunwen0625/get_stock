# excel_utils.py
import xlwings as xw
from typing import Literal

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
    
    def get_sheet(self, codes: list[str]) -> None:
        for sheet in self.wb.sheets:
            print(sheet.name)
            
    
    def add_sheet(
        self,
        name: str | None = None,
        *,
        position: Literal["before", "after", "end"] = "end",
        reference: str | int | None = None,
        if_exists: Literal["rename", "return", "error"] = "rename",
        activate: bool = False
    ) -> xw.Sheet:
        """
        新增一張工作表並回傳。
        
        Parameters
        ----------
        name : str | None
            欲命名的新工作表。若為 None，xlwings 會自動命名 (e.g. Sheet1)。
        position : {"before", "after", "end"}
            - before/after：相對於 `reference` 工作表位置
            - end (預設)：直接插入至最後
        reference : str | int | None
            參考工作表名稱或索引；當 `position=end` 時忽略。
        if_exists : {"rename", "return", "error"}
            - rename (預設)：自動重命名避免衝突
            - return      ：若同名已存在，回傳該工作表不新增
            - error       ：拋出 ValueError
        activate : bool
            新增後是否設為使用中的工作表。

        使用範例：
            with ExcelSession("report.xlsx") as xls:
                # 1. 在最後新增 "Summary"
                summary = xls.add_sheet("Summary")

                # 2. 在 "RawData" 前面插一張 "Pivot"
                xls.add_sheet("Pivot", position="before", reference="RawData")

                # 3. 若 "Config" 已存在就直接回傳
                cfg = xls.add_sheet("Config", if_exists="return", activate=False)

                # 後續可直接用 xls.range(...) 對新 active 工作表寫資料
                summary.range("A1").value = "Hello, World!"

        關鍵註解摘要:
            - if_exists：集中處理同名衝突，預設自動改名方便快速試驗；需嚴格控制時可指定 "error"。

            - reference / position：比 xlwings 原生更直觀；預設把 reference 省略就以當前工作表為基準。

            - activate 邏輯：若做背景批次生成，可設 activate=False，確保游標不跳動。
        """

        # --- 1. 同名處理 ---
        if name and name in [s.name for s in self.wb.sheets]:
            match if_exists:
                case "return":
                    target_sh = self.wb.sheets[name]
                    return target_sh
                case "error":
                    raise ValueError(f"Worksheet '{name}' already exists.")
                case "rename":
                    base = name
                    i = 2
                    while f"{base} ({i})" in [s.name for s in self.wb.sheets]:
                        i += 1
                    name = f"{base} ({i})"

        # --- 2. 位置決定 ---
        if position == "end":
            target_sh = self.wb.sheets.add(name, after=self.wb.sheets[-1])
        else:
            ref_sh = self.wb.sheets[reference] if reference is not None else self.sh
            target_sh = self.wb.sheets.add(name, before=ref_sh if position == "before" else None,
                                                after=ref_sh if position == "after"  else None)
            
        if activate:
            target_sh.activate()
            self.sh = target_sh  # 更新內部目前指向

        return target_sh
    
    def rename_sheet(
        self,
        sheet: str | int | xw.Sheet,
        new_name: str,
        *,
        if_exists: Literal["error", "rename", "swap"] = "error"
    ) -> xw.Sheet:
        """
        將指定工作表改名為 `new_name`，並回傳該工作表物件。

        Parameters
        ----------
        sheet : str | int | xw.Sheet
            要改名的工作表，可用名稱、索引或 `xw.Sheet` 物件表示。
        new_name : str
            欲更改成的名稱。
        if_exists : {"error", "rename", "swap"}
            - error  (default) : 若 `new_name` 已存在則拋錯。
            - rename           : 自動在 `new_name` 後加序號直到不衝突。
            - swap             : 若 `new_name` 已存在，與其對調名稱。

        使用範例：
            with ExcelSession("report.xlsx") as xls:
                # 將 "Summary" 改名為 "Dashboard"，若 "Dashboard" 已存在就換個編號
                xls.rename_sheet("Summary", "Dashboard", if_exists="rename")

                # 交換 "Draft" 與 "Final" 兩張表名稱
                xls.rename_sheet("Draft", "Final", if_exists="swap")

                # 直接改名（假設無衝突）
                new_sheet = xls.rename_sheet(xls.sh, "CurrentData")
                new_sheet.range("A1").value = "已重新命名！"
        
        關鍵註解摘要:
            - swap 策略：常用於「先複製成 Draft → 改好 → 與正式版本對調」的場景，僅花 O(1) 時間。
            
            - rename 策略：與 add_sheet 行為一致，使批次產出報表更直覺。

            - 內部同步：保證後續呼叫 xls.range() 等方法仍操作到正確的工作表。
        """
        # --- 1. 解析 sheet 參數為 Sheet 物件 ---
        target_sh: xw.Sheet = (
            sheet if isinstance(sheet, xw.main.Sheet) else self.wb.sheets[sheet]
        )
        # --- 2. 衝突處理 ---
        existing_names = [s.name for s in self.wb.sheets]

        if new_name in existing_names:
            match if_exists:
                case "error":
                    raise ValueError(f"Worksheet '{new_name}' already exists.")
                case "rename":
                    base = new_name
                    i = 2
                    while f"{base} ({i})" in existing_names:
                        i += 1
                    new_name = f"{base} ({i})"
                case "swap":
                    other_sh = self.wb.sheets[new_name]
                    temp = "__tmp_swap_name__"
                    other_sh.name = temp
                    target_sh.name = new_name
                    other_sh.name = sheet if isinstance(sheet, str) else target_sh.name
                    # 若 target_sh 就是 self.sh，也要更新 self.sh
                    if target_sh == self.sh:
                        self.sh = target_sh
                    return target_sh

        # --- 3. 真正改名 ---
        target_sh.name = new_name

        # --- 4. 同步內部指標 ---
        if target_sh == self.sh:
            self.sh = target_sh

        return target_sh

    # ---------- with 支援 ----------
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb):
        self.save()
        if self._auto_close:           # ★ 只在需要時才 close
            self.close()
