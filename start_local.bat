@echo off
title FinanceAI - Local Development
color 0B

echo.
echo  ============================================================
echo    FinanceAI - AI Financial Analyst Platform
echo    Backend : http://localhost:8000
echo    Frontend: http://localhost:8501
echo    API Docs: http://localhost:8000/docs
echo  ============================================================
echo.

:: Create required folders
if not exist uploads mkdir uploads
if not exist uploads\reports mkdir uploads\reports

echo  [1/2] Starting FastAPI backend on port 8000...
start "FinanceAI Backend" cmd /k "cd /d %~dp0 && py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo  Waiting for backend to initialise...
timeout /t 5 /nobreak >nul

echo  [2/2] Starting Streamlit frontend on port 8501...
start "FinanceAI Frontend" cmd /k "cd /d %~dp0 && py -m streamlit run frontend/app.py --server.port 8501"

timeout /t 4 /nobreak >nul

echo.
echo  Both services are starting in separate windows.
echo  Opening browser...
start http://localhost:8501

echo.
echo  Press any key to close this window (services keep running).
pause >nul
