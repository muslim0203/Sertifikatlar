@echo off
chcp 65001 >nul
echo GitHub username ni kiriting (masalan: myusername):
set /p GITHUB_USER=
if "%GITHUB_USER%"=="" (
  echo Username bo'sh. Chiqish.
  pause
  exit /b 1
)
echo.
set REPO_NAME=Sertifikatlar
set /p REPO_NAME=Repo nomi [Enter = Sertifikatlar]:
if "%REPO_NAME%"=="" set REPO_NAME=Sertifikatlar
echo.
echo Remote qo'shilmoqda: https://github.com/%GITHUB_USER%/%REPO_NAME%.git
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
git branch -M main
echo.
echo Push qilinmoqda...
git push -u origin main
echo.
pause
