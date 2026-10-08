@echo off
echo ========================================
echo  AI Financial Analyst - Server Startup
echo ========================================
echo.

REM Kill any existing processes on ports 8000 and 5173
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul

echo.
echo Starting Backend Server (Port 8000)...
start "FastAPI Backend" cmd /k "py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server (Port 5173)...
cd frontend-web
start "React Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo  Servers Starting...
echo ========================================
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo  API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
