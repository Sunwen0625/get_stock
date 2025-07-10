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

def ensure_code_sheets(
        session: ExcelSession, 
        codes: list[str] ,
        ) -> None:
    """
    確保一組 `codes` 都各自擁有對應的工作表，若缺少則立即建立。

    此函式會檢查指定的股票代碼是否都有對應的工作表，對於缺少的代碼會自動建立新的工作表。
    支援從列表或字典格式的代碼輸入，並可選擇是否依照位置排序。

    Parameters
    ----------
    session : ExcelSession
        Excel 會話物件，包含已開啟的工作簿和相關操作方法。
    codes : list[str] 
        目標股票代碼集合。
        - 若為 list[str]：直接使用代碼列表
    Returns
    -------
    None
        此函式無回傳值，直接對工作簿進行修改。

    Notes
    -----
    - 代碼會透過 normalize_code() 函式進行正規化處理
    - 新工作表一律建立在工作簿尾端，避免干擾現有排序
    - 使用 if_exists="return" 避免重複建立已存在的工作表
    - 新建立的工作表不會自動啟用（activate=False）

    """

    # 2. 正規化
    normalized: set[str] = {normalize_code(c) for c in codes}

    # 3. 取得現有工作表名
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
