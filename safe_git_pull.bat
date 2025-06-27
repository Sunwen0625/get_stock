@echo off
echo 🔐 正在暫存本地變更...
git stash -u

echo ⬇️ 正在從遠端拉取...
git pull --rebase
if %errorlevel% neq 0 (
    echo ❌ git pull 發生錯誤，停止還原修改
    exit /b 1
)

echo 📦 還原本地變更中...
git stash pop

echo ✅ 完成！目前的 Git 狀態如下：
git status

pause
