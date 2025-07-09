import json
from pathlib import Path
import os
import shutil
from datetime import datetime
def backup_excel(file_path, backup_path, backup_format):
    filename_no_ext = os.path.splitext(os.path.basename(file_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_filename = backup_format.format(filename=filename_no_ext, timestamp=timestamp)
    os.makedirs(backup_path, exist_ok=True)
    backup_full_path = os.path.join(backup_path, backup_filename)
    shutil.copy(file_path, backup_full_path)
    print(f"備份完成：{backup_full_path}")


CONFIG_PATH = Path("setting.json")

with CONFIG_PATH.open(encoding="utf-8") as f:
    config  = json.load(f)


print(config )
excel_config = config.get("excel_config", {})
save_backup = excel_config .get("save", False)
backup_path = excel_config.get("backup_path", "./excel備份")
backup_format = excel_config.get("backup_filename_format", "{filename}_backup_{timestamp}.xlsx")

if __name__ == "__main__":
    if save_backup:
        source_file = config["read_excel"]["file"]
        backup_excel(source_file, backup_path, backup_format)
        
    else:
        print("備份功能未啟用。")