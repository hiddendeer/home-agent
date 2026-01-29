#!/bin/bash
# FastAPI 开发服务器启动脚本 (Linux/Mac)

echo "Starting FastAPI development server..."
echo ""

# 启动服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8002
