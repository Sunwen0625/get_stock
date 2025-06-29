@echo off
REM 設定編碼為 UTF-8，避免中文亂碼
chcp 65001 >nul

echo 🔐 正在暫存本地變更 (包含未追蹤檔案)...
git stash -a

echo ⬇️ 正在從遠端拉取變更...
git pull --rebase
if %errorlevel% neq 0 (
    echo ❌ git pull 發生錯誤，停止還原本地修改
    pause
    exit /b 1
)

REM 檢查是否有 stash，再還原
git stash list | findstr stash@ >nul
if %errorlevel%==0 (
    echo 📦 發現 stash，正在還原本地變更...
    git stash pop
) else (
    echo 📦 無 stash 紀錄，無需還原
)

echo ✅ 完成！目前 Git 狀態如下：
git status

pause
