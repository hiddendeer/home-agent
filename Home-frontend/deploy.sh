#!/bin/bash

# 前端部署脚本
# 用于打包已构建的前端文件并上传到服务器

SERVER_USER="your-user"              # 服务器用户名
SERVER_HOST="your-server-ip"         # 服务器 IP
SERVER_PATH="/opt/home-agent"        # 服务器部署路径

echo "📦 开始部署前端到服务器..."

# 检查 dist 是否存在
if [ ! -d "dist" ]; then
    echo "❌ 错误: dist 目录不存在！"
    echo "💡 请先运行构建命令:"
    echo "   Linux/Mac: ./build.sh"
    echo "   Windows:   build.bat"
    exit 1
fi

# 打包 dist 目录
echo "🗜️  打包 dist 目录..."
tar -czf home-frontend-dist.tar.gz dist/ nginx.conf Dockerfile

# 上传到服务器
echo "⬆️  上传到服务器..."
scp home-frontend-dist.tar.gz ${SERVER_USER}@${SERVER_HOST}:/tmp/

# 在服务器上解压
echo "📂 在服务器上解压..."
ssh ${SERVER_USER}@${SERVER_HOST} << EOF
    cd ${SERVER_PATH}/Home-frontend
    tar -xzf /tmp/home-frontend-dist.tar.gz
    rm /tmp/home-frontend-dist.tar.gz
    echo "✅ 文件已上传并解压"
EOF

# 删除本地临时文件
rm home-frontend-dist.tar.gz

echo "✅ 部署完成！"
echo "💡 在服务器上运行以下命令重启前端服务:"
echo "   cd ${SERVER_PATH}"
echo "   docker-compose up -d --build frontend"
