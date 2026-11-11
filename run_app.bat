@echo off
title AI-Powered SQL Agent - Streamlit UI
cd /d "%~dp0"
echo Starting Streamlit Web Interface on port 8505...
call .venv\Scripts\activate
streamlit run frontend\streamlit_app.py --server.port 8505
pause
