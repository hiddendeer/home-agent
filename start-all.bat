@echo off
REM Home Agent 项目启动脚本
REM 同时启动前端和后端开发服务器

echo ========================================
echo   Home Agent Development Environment
echo ========================================
echo.
echo Starting services...
echo.

REM 获取脚本所在目录
set PROJECT_ROOT=%~dp0

REM 启动后端服务 (新窗口)
echo [1/2] Starting Backend (FastAPI)...
start "Home-Backend" cmd /k "cd /d %PROJECT_ROOT%Home-backend && call .venv\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8002"

REM 等待 2 秒让后端先启动
timeout /t 2 /nobreak >nul

REM 启动前端服务 (新窗口)
echo [2/2] Starting Frontend (Vite)...
start "Home-Frontend" cmd /k "cd /d %PROJECT_ROOT%Home-frontend && npm run dev"

echo.
echo ========================================
echo   All services started!
echo ========================================
echo.
echo Backend: http://localhost:8002
echo Frontend: http://localhost:5173 (or port shown in frontend window)
echo API Docs:  http://localhost:8002/docs
echo.
echo Press any key to close this window (services will continue running)...
pause >nul
