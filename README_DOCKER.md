# 🚀 Home Agent - Docker 部署

快速部署指南 - Home Agent 前后端分离项目

---

## ⚡ 快速开始

### 前置要求

- Docker >= 20.10
- Docker Compose >= 2.0

### 部署步骤

#### 1. 本地构建前端

```bash
cd Home-frontend

# Windows
build.bat

# Linux/Mac
chmod +x build.sh && ./build.sh
```

#### 2. 准备后端文件

将以下文件上传到服务器：
- ✅ 整个 `Home-backend/` 目录
- ✅ `Home-frontend/dist/` (构建产物)
- ✅ `Home-frontend/nginx.conf`
- ✅ `Home-frontend/Dockerfile`
- ✅ `docker-compose.yml`
- ✅ `.env.example` → 复制为 `.env` 并配置

#### 3. 配置环境变量

```bash
cp .env.example .env
vim .env  # 填写实际的配置
```

**必须配置：**
- MYSQL_HOST, MYSQL_PASSWORD
- MILVUS_HOST, MILVUS_PASSWORD
- LLM_API_KEY, EMBEDDING_API_KEY
- CORS_ORIGINS

#### 4. 启动服务

```bash
docker-compose build
docker-compose up -d
```

#### 5. 验证部署

```bash
# 检查状态
docker-compose ps

# 检查健康
curl http://localhost:8002/health

# 访问
# 前端: http://your-server-ip:5173
# 后端: http://your-server-ip:8002/docs
```

---

## 📁 项目结构

```
Home-agent/
├── docker-compose.yml          # Docker Compose 配置
├── .env.example                # 环境变量模板
├── DOCKER_DEPLOYMENT.md        # 详细部署文档
│
├── Home-backend/               # 后端（FastAPI）
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── app/
│
└── Home-frontend/              # 前端（React + Vite）
    ├── build.sh/bat           # 构建脚本
    ├── deploy.sh/bat          # 部署脚本
    ├── dist/                  # 构建产物（上传这个）
    ├── Dockerfile             # 生产镜像
    ├── Dockerfile.dev         # 开发镜像
    └── nginx.conf
```

---

## 📦 部署优化

### 为什么在本地构建？

| 对比项 | 传统方案 | 优化方案 |
|--------|---------|---------|
| 上传大小 | ~500MB | ~5MB |
| 镜像大小 | ~600MB | ~25MB |
| 构建时间 | ~10分钟 | ~2分钟 |
| 服务器资源 | 高消耗 | 低消耗 |

---

## 🛠️ 常用命令

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新前端
docker-compose up -d --build frontend

# 更新后端
docker-compose up -d --build backend
```

---

## 📚 详细文档

完整部署指南请查看：[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)

包含：
- 详细的安装步骤
- 故障排查指南
- 安全建议
- 性能优化

---

## 🎯 优化说明

✅ **前端本地构建** - 只上传 dist/ 目录
✅ **镜像体积小** - 前端 ~25MB，后端 ~500MB
✅ **快速部署** - 2分钟完成构建
✅ **资源优化** - 服务器资源消耗低

---

## 📞 技术支持

遇到问题？
1. 查看日志：`docker-compose logs -f`
2. 检查配置：`docker-compose config`
3. 阅读文档：[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)

---

祝你部署顺利！🎉
