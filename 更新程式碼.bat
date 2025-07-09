@echo off
REM 設定編碼為 UTF-8，避免中文亂碼
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🔒 備份本地變更...
git stash push -u -m "backup personal data" 
              
git reset --hard               
git clean -fd  
echo ----------------------------------------
echo 🔄 正在從遠端拉取變更...
git pull --rebase
if !errorlevel! neq 0 (
    echo ❌ git pull 發生錯誤，停止還原本地修改
    pause
    exit /b 1
)

echo ----------------------------------------
git stash list | findstr stash@ >nul
if !errorlevel!==0 (
    echo 📦 發現 stash，正在還原本地變更...
    git stash pop
    if !errorlevel! neq 0 (
        echo ⚠️ git stash pop 發生衝突，請手動處理
        pause
        exit /b 1
    )
) else (
    echo 📦 無 stash 紀錄，無需還原
)

echo ----------------------------------------
echo ✅ Git 狀態如下：
git status

echo ----------------------------------------
echo ⚙️ 初始化或更新 setting.json...
python merge_and_check_setting.py
if !errorlevel! neq 0 (
    echo ❌ Python 腳本執行失敗
    pause
    exit /b 1
)

echo 🎉 所有作業完成！
pause