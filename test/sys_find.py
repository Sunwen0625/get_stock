import sys
from pathlib import Path

# 讓本模組可以從 CLI 執行
sys.path.append(str(Path(__file__).resolve().parents[1]))

for p in sys.path:
    print(p)