# stock_sheet_utils.py
from __future__ import annotations

import re
from .excel_utils import ExcelSession


_DIGIT_ALPHA_RE = re.compile(r"^(\d+)([A-Za-z]*)$")   # ⬅ 允許結尾帶 1~多個字母

def normalize_code(code: str) -> str:
    """
    將輸入代碼正規化為：
        - 數字部分 >= 4 位時保持原樣，< 4 位則補零至 4 位
        - 字母部分轉成大寫
    例如：
        "50"     -> "0050"
        "773b"   -> "0773B"
        "00773B" -> "00773B" (已足 5 位 → 不再補零)
    """
    m = _DIGIT_ALPHA_RE.match(code.strip())
    if not m:
        raise ValueError(f"無法解析代碼格式：{code}")
    num, suffix = m.groups()
    num = num.zfill(4)          # 補到 4 位；若原本 >=4 位則原樣
    return f"{num}{suffix.upper()}"


_CODE_PREFIX_RE = re.compile(r"^(\d{4,6})([A-Za-z]*)")      # 比對「工作表名稱開頭是一串 4~6 位的數字」

def ensure_code_sheets(session: ExcelSession, codes: list[str]) -> None:
    """
    確保一組 `codes` 都各自擁有對應的工作表，若缺少則立即建立。

    Parameters
    ----------
    wb : xw.Book
        已開啟的 xlwings 工作簿物件。
    codes : Iterable[str]
        目標股票代碼列表；可為 str 或 int，函式會自動轉成零填補的 4 位字串。
    create_at_end : bool, default=True
        - True  → 在活頁簿尾端插入新工作表（比較不干擾原本排序）。
        - False → 在第一個工作表之前插入新工作表。
    """
    # ---- 1. 整理輸入代碼成固定 4 位以上的 zero-padded 字串 ----
    normalized : set[str] = {normalize_code(c) for c in codes}

    # ---- 2. 找出活頁簿中「已經存在」且符合命名規則的股票代碼 ----
    existing = {
        normalize_code(m.group())
        for sht in session.wb.sheets
        if (m := _CODE_PREFIX_RE.match(sht.name))
    }

    for code in sorted(normalized - existing):
        session.add_sheet(
            name=code,
            position="end",         # 全部插到最後
            if_exists="return",     # 萬一同事前一秒手動新增了不重複加
            activate=False,
        )