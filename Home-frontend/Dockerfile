# 生产环境 Dockerfile
# 此镜像用于部署已构建的前端静态文件
# 请先在本地运行: npm run build

FROM nginx:alpine

# 复制已构建的前端静态文件
COPY dist/ /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 5173

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:5173/ || exit 1

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
