@echo off
REM 前端部署脚本 (Windows)
REM 用于打包已构建的前端文件并上传到服务器

set SERVER_USER=your-user
set SERVER_HOST=your-server-ip
set SERVER_PATH=/opt/home-agent

echo 📦 开始部署前端到服务器...

REM 检查 dist 是否存在
if not exist "dist" (
    echo ❌ 错误: dist 目录不存在！
    echo 💡 请先运行构建命令: build.bat
    exit /b 1
)

REM 打包 dist 目录
echo 🗜️  打包 dist 目录...
tar -a -c -f home-frontend-dist.tar.gz dist/ nginx.conf Dockerfile

echo ⬆️  请手动上传 home-frontend-dist.tar.gz 到服务器
echo    或者使用 SCP 命令:
echo    scp home-frontend-dist.tar.gz %SERVER_USER%@%SERVER_HOST%:/tmp/
echo.
echo ✅ 打包完成！
echo 💡 上传后在服务器运行:
echo    cd %SERVER_PATH%/Home-frontend
echo    tar -xzf /tmp/home-frontend-dist.tar.gz
echo    cd ..
echo    docker-compose up -d --build frontend
