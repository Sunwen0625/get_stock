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

