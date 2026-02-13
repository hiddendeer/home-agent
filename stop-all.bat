@echo off
REM 停止 Home Agent 所有开发服务

echo Stopping Home Agent services...
echo.

REM 通过端口终止进程
echo Stopping Backend (port 8002)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    taskkill /F /PID %%a 2>nul
)

echo Stopping Frontend (port 5173)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo All services stopped!
pause
