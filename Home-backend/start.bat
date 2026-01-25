@echo off
REM FastAPI 开发服务器启动脚本

echo Starting FastAPI development server...
echo.

REM 检查虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: uv venv --python 3.11
    pause
    exit /b 1
)

REM 启动服务器
python main.py

pause
