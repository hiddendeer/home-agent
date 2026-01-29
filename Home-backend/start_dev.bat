@echo off
REM FastAPI 开发服务器启动脚本 (使用 uvicorn --reload)
echo Starting FastAPI development server with auto-reload...
echo.
REM 检查虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: uv venv --python 3.11
    pause
    exit /b 1
)

REM 启动服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8002

pause
