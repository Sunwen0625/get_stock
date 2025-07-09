import json
import os

EXAMPLE_PATH = "setting-example.json"
LOCAL_PATH = "setting.json"
OUTPUT_PATH = "setting.json"  # 直接覆蓋，建議可再自訂備份策略
IGNORE_KEYS = {"stock_code"}   # 加入你要排除比對/同步的欄位名稱

def load_json(path):
    if not os.path.exists(path):
        print(f"[WARN] {path} 不存在，將使用空資料")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def merge_settings(example, local,path=""):
    """
    合併設定，只保留 example 定義的欄位，local 有值則優先用 local，無則用範本預設。
    支援巢狀 dict。
    """
    merged = {}
    for key, default_val in example.items():
        if key in IGNORE_KEYS and path == "":
            # 最上層指定欄位直接用 local 的
            if key in local:
                merged[key] = local[key]
            else:
                merged[key] = default_val
            continue
        if key in local:
            if isinstance(default_val, dict) and isinstance(local[key], dict):
                merged[key] = merge_settings(default_val, local[key], path + "." + key if path else key)
            else:
                merged[key] = local[key]
        else:
            merged[key] = default_val
    # 針對 ignore 欄位，若 local 多出 example 沒有的，也一起補進來
    if path == "":
        for key in IGNORE_KEYS:
            if key in local and key not in merged:
                merged[key] = local[key]
    return merged

def find_missing_keys(example, local, path=""):
    """
    回傳 local 裡缺少 example 欄位的清單
    """
    missing = []
    for key, val in example.items():
        if key in IGNORE_KEYS and path == "":
            continue
        cur_path = f"{path}.{key}" if path else key
        if key not in local:
            missing.append(cur_path)
        elif isinstance(val, dict) and isinstance(local.get(key), dict):
            sub_missing = find_missing_keys(val, local[key], cur_path)
            missing.extend(sub_missing)
    return missing

def find_extra_keys(local, example, path=""):
    """
    回傳 local 有、但 example 沒有的多餘欄位（支援巢狀）
    """
    extras = []
    for key, val in local.items():
        if key in IGNORE_KEYS and path == "":
            continue
        cur_path = f"{path}.{key}" if path else key
        if key not in example:
            extras.append(cur_path)
        elif isinstance(val, dict) and isinstance(example.get(key), dict):
            sub_extras = find_extra_keys(val, example[key], cur_path)
            extras.extend(sub_extras)
    return extras

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    example = load_json(EXAMPLE_PATH)
    local = load_json(LOCAL_PATH)

    # 1️⃣ 找出缺少欄位
    missing = find_missing_keys(example, local)
    if missing:
        print("⚠️  你的 setting.json 缺少以下欄位（已自動補齊）:")
        for k in missing:
            print("  -", k)
    else:
        print("✅  你的 setting.json 沒有缺少欄位")

    # 2️⃣ 找出多餘欄位
    extras = find_extra_keys(local, example)
    if extras:
        print("⚠️  你的 setting.json 有以下已被範本移除的欄位（已自動剃除）:")
        for k in extras:
            print("  -", k)
    else:
        print("✅  沒有發現多餘欄位")

    # 3️⃣ 合併、補新欄位、刪多餘欄位
    merged = merge_settings(example, local)
    save_json(OUTPUT_PATH, merged)
    print(f"✅ 已合併並儲存到 {OUTPUT_PATH}")
