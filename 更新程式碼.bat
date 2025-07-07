@echo off
REM 設定編碼為 UTF-8，避免中文亂碼
chcp 65001 >nul

REM === 設定檔名變數（可擴充支援多個設定檔） ===
set SETTING_FILE=setting.json

echo 🔐 正在暫存你的個人化設定：%SETTING_FILE%
git stash push -u -m "backup personal setting" %SETTING_FILE%


echo ⬇️ 正在從遠端拉取變更...
git pull --rebase
if %errorlevel% neq 0 (
    echo ❌ git pull 發生錯誤，停止還原本地修改
    pause
    exit /b 1
)

REM 檢查是否有 stash，再還原
git stash list | findstr "backup personal setting" >nul
if %errorlevel%==0 (
    echo 📦 發現設定檔暫存，正在還原個人設定...
    git stash pop
    if %errorlevel% neq 0 (
        echo ⚠️ 發生衝突，請手動合併：%SETTING_FILE%
    ) else (
        echo ✅ setting.json 還原完成！
    )
) else (
    echo 📦 無設定檔暫存紀錄，跳過還原。
)

echo ✅ 完成！目前 Git 狀態如下：
git status

pause
