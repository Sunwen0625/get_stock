# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Literal
from .excel_utils import ExcelSession
import logging
logger = logging.getLogger(__name__)

def rename_code_only_sheets(
    session: ExcelSession,
    *,
    code_col: str = "B",
    name_col: str = "C",
    start_row: int = 2,
    if_exists: Literal["error", "rename", "swap"] = "swap",
) -> None:
    """
    只將「名稱等於純代碼」的工作表，改成「代碼＋中文名稱」。

    Parameters
    ----------
    session : ExcelSession
        你的封裝；已經打開到含代碼/名稱那張表。
    code_col, name_col : str
        代碼與中文名稱所在欄位（預設 B、C）。
    start_row : int
        資料起始列（1 通常是標題，所以預設 2）。
    if_exists : {"error", "rename", "swap"}
        交給 `ExcelSession.rename_sheet()` 的衝突策略。
        - swap (default)：若 `0050元大台灣50` 已存在，就與之互換名稱。
        - rename       ：若存在，改成 `0050元大台灣50 (2)`。
        - error        ：若存在同名工作表就拋例外。
    """

    # ---- 1. 讀取 B、C 欄取得對照表 ----------------------------------
    code_name_map: dict[str, str] = {}
    row = start_row
    sht = session.sh  # 目前活動工作表
    while True:
        code = sht.range(f"{code_col}{row}").value
        name = sht.range(f"{name_col}{row}").value
        if not code:
            break  # 遇到空白列就停
        code_name_map[str(code).strip()] = str(name or "").strip()
        row += 1

    if not code_name_map:
        logger.info("找不到任何代碼，結束。")
        return

    # ---- 2. 活頁簿現有工作表名稱快照 ---------------------------------
    wb_names = [sht.name for sht in session.wb.sheets]

    # ---- 3. 逐一檢查並改名 ------------------------------------------
    for code, cname in code_name_map.items():
        if not cname:            # 沒抓到名稱就跳過
            continue

        new_name = f"{code}{cname}"
        if code in wb_names and new_name not in wb_names:
            # 只在「純代碼 sheet 存在」且「新名稱未衝突」時才改名
            session.rename_sheet(code, new_name, if_exists=if_exists)
            # 同步更新 wb_names，避免下個循環重複計算
            wb_names.remove(code)
            wb_names.append(new_name)

    logger.info(" 工作表已完成改名 ✅")
