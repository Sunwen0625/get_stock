@echo off
chcp 65001 >nul
echo 📦 啟動 Python 虛擬環境與自動更新...

REM 確認 poetry 是否存在
where poetry >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 找不到 poetry，請先安裝：https://python-poetry.org/docs/
    pause
    exit /b 1
)

REM 使用 poetry 安裝依賴（會自動啟動虛擬環境）
echo 🔍 檢查套件是否需要更新...
poetry install
if %errorlevel% neq 0 (
    echo ❌ Poetry 安裝依賴失敗
    pause
    exit /b 1
)

REM 執行 read.py（會在 poetry 虛擬環境中執行）
echo ▶️ 執行 Python 程式 read.py...
poetry run python read.py

pause
