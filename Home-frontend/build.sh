#!/bin/bash

echo "🚀 开始构建前端项目..."

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 清理旧的构建产物
echo "🧹 清理旧的构建产物..."
rm -rf dist

# 构建生产版本
echo "🔨 构建生产版本..."
npm run build

# 检查构建是否成功
if [ -d "dist" ]; then
    echo "✅ 构建成功！"
    echo "📁 构建产物位于: ./dist/"
    echo "📊 构建产物大小:"
    du -sh dist

    # 显示文件列表
    echo ""
    echo "📄 构建产物文件列表:"
    ls -lh dist/

    echo ""
    echo "💡 现在可以部署到服务器了！"
else
    echo "❌ 构建失败！"
    exit 1
fi
