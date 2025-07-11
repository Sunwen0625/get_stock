import sys
from pathlib import Path

    # 讓本模組可以從 CLI 執行
sys.path.append(str(Path(__file__).resolve().parents[1]))
from 股票.backup_excel import backup_excel


if __name__ == "__main__":
    
    backup_excel("default.xlsx", "./excel備份", "{filename}_backup_{timestamp}.xlsx")
    