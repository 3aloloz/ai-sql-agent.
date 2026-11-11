@echo off
title AI-Powered SQL Agent - Automated Tests
cd /d "%~dp0"
echo Running Assignment Benchmark and Security Tests...
call .venv\Scripts\activate
python -u tests\test_agent.py
pause
