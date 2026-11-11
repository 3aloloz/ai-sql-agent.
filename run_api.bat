@echo off
title AI-Powered SQL Agent - FastAPI Backend
cd /d "%~dp0"
echo Starting FastAPI Server on http://127.0.0.1:8000 ...
call .venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
