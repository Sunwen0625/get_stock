# utils/settings_loader.py  （或直接放在現有檔案頂部也可以）
import json
from pathlib import Path
from typing import List

def load_codes(path: str | Path = "setting.json") -> List[str]:
    """
    從 setting.json 讀出要抓的股票／ETF 代碼。
    - 允許 "code": ["0050", "2308"]   # list
            或  "code": {"0050": true, "2308": false}   # dict
    - 發生任何錯誤時回傳空清單並列印警告。
    """
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        codes = data.get("code", [])
        if isinstance(codes, dict):
            codes = list(codes.keys())
        if not isinstance(codes, list):
            raise TypeError("'code' 必須是 list 或 dict")
        return [str(c).strip() for c in codes if str(c).strip()]
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] 讀取 {path} 失敗：{exc}")
        return []
