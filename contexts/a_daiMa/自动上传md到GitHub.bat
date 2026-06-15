@echo off
cd /d C:\Users\homerun\.claude

git add commands/ contexts/

git status --short > nul 2>&1
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo No changes to commit.
) else (
    git commit -m "auto update %date:~0,10% %time:~0,8%"
    git push origin main
)