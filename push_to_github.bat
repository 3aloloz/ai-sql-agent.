@echo off
title Push AI-Powered SQL Agent to GitHub
cd /d "%~dp0"

:: Ensure Git is on PATH
set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd;%PATH%"

echo ================================================================
echo        Pushing AI SQL Agent to GitHub (3aloloz/AI_SQL_Agent)
echo ================================================================
echo.
echo If prompted, please authorize Git in your browser or enter your
echo GitHub Personal Access Token (PAT).
echo.
git push -u origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo ================================================================
    echo    SUCCESS! Repository is now live on GitHub:
    echo    https://github.com/3aloloz/AI_SQL_Agent
    echo ================================================================
) else (
    echo ================================================================
    echo Push encountered an error. Please verify your GitHub credentials.
    echo ================================================================
)
echo.
pause
