@echo off
echo 🚀 开始构建前端项目...

REM 检查 node_modules 是否存在
if not exist "node_modules" (
    echo 📦 安装依赖...
    call npm install
)

REM 清理旧的构建产物
echo 🧹 清理旧的构建产物...
if exist "dist" (
    rmdir /s /q dist
)

REM 构建生产版本
echo 🔨 构建生产版本...
call npm run build

REM 检查构建是否成功
if exist "dist" (
    echo ✅ 构建成功！
    echo 📁 构建产物位于: .\dist\
    echo 💡 现在可以部署到服务器了！
) else (
    echo ❌ 构建失败！
    exit /b 1
)
