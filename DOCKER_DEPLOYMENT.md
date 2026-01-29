# 🐳 Docker 部署指南

## 📋 目录

- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [常用运维命令](#常用运维命令)
- [故障排查](#故障排查)
- [安全建议](#安全建议)
- [部署优化说明](#部署优化说明)

---

## 前置要求

### 服务器环境

确保你的服务器已安装以下软件：

- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0

### 检查安装

```bash
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker-compose --version
```

### 如果未安装

**Ubuntu/Debian:**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

**CentOS/RHEL:**
```bash
# 安装 Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

---

## 快速开始

### 1️⃣ 上传代码到服务器

```bash
# 方式1: 使用 Git（推荐）
git clone <your-repo-url> /opt/home-agent
cd /opt/home-agent

# 方式2: 使用 scp 压缩包
# 在本地压缩项目
tar -czf home-agent.tar.gz Home-agent/

# 上传到服务器
scp home-agent.tar.gz user@your-server:/opt/

# 在服务器解压
cd /opt
tar -xzf home-agent.tar.gz
cd Home-agent
```

### 2️⃣ 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
# 或使用 nano: nano .env
```

**必须配置的项：**
- ✅ `MYSQL_HOST`: MySQL 服务器地址
- ✅ `MYSQL_USER`: MySQL 用户名
- ✅ `MYSQL_PASSWORD`: MySQL 密码
- ✅ `MILVUS_HOST`: Milvus 服务器地址
- ✅ `MILVUS_PASSWORD`: Milvus 密码
- ✅ `LLM_API_KEY`: 智谱AI API Key
- ✅ `EMBEDDING_API_KEY`: Embedding API Key
- ✅ `CORS_ORIGINS`: 允许的前端地址（如 `http://your-domain.com:5173`）

### 3️⃣ 构建并启动服务

```bash
# 构建镜像
docker-compose build

# 启动服务（后台运行）
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

### 4️⃣ 验证部署

```bash
# 检查服务状态
docker-compose ps

# 检查后端健康
curl http://localhost:8002/health

# 检查前端（在浏览器访问）
# http://your-server-ip
```

---

## 详细部署步骤

### Step 1: 准备工作目录

```bash
# 创建项目目录
sudo mkdir -p /opt/home-agent
cd /opt/home-agent

# 上传代码（见上面"上传代码"部分）
```

### Step 2: 配置环境变量详解

编辑 `.env` 文件，填写实际配置：

```env
# ========== 数据库配置 ==========
MYSQL_HOST=14.103.138.196        # 你的 MySQL 地址
MYSQL_PORT=33061                  # MySQL 端口
MYSQL_USER=root                   # MySQL 用户名
MYSQL_PASSWORD=your_password      # MySQL 密码
MYSQL_DATABASE=record_info        # 数据库名

# ========== Milvus 配置 ==========
MILVUS_HOST=14.103.138.196        # 你的 Milvus 地址
MILVUS_PORT=19530                 # Milvus 端口
MILVUS_USER=root                  # Milvus 用户名
MILVUS_PASSWORD=your_password     # Milvus 密码

# ========== LLM 配置 ==========
LLM_API_KEY=your_api_key          # 智谱AI API Key
EMBEDDING_API_KEY=your_api_key    # Embedding API Key

# ========== CORS 配置 ==========
CORS_ORIGINS=http://your-domain.com,https://your-domain.com
```

### Step 3: 构建镜像

```bash
# 查看将要构建的镜像
docker-compose config

# 开始构建（可能需要几分钟）
docker-compose build

# 查看构建日志
docker-compose build --progress=plain
```

### Step 4: 启动服务

```bash
# 首次启动
docker-compose up -d

# 查看所有容器状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 只看某个服务的日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Step 5: 验证服务

```bash
# 1. 检查容器是否运行
docker-compose ps

# 应该看到类似输出：
# NAME              IMAGE              STATUS
# home-backend      home-agent-backend   running (healthy)
# home-frontend     home-agent-frontend  running

# 2. 检查后端健康
curl http://localhost:8002/health
# 应该返回: {"status":"healthy"}

# 3. 检查后端 API 文档
# 浏览器访问: http://your-server-ip:8002/docs

# 4. 检查前端
# 浏览器访问: http://your-server-ip

# 5. 检查网络连接
docker network ls | grep home-network
```

---

## 常用运维命令

### 📊 查看状态

```bash
# 查看所有容器状态
docker-compose ps

# 查看容器资源使用
docker stats

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 🔄 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart backend
docker-compose restart frontend

# 停止并重新创建容器
docker-compose up -d --force-recreate
```

### 🛑 停止服务

```bash
# 停止所有服务（保留数据）
docker-compose stop

# 停止并删除容器（保留数据卷）
docker-compose down

# 停止并删除容器和数据卷
docker-compose down -v
```

### 📦 更新代码

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并启动
docker-compose up -d --build

# 3. 只更新某个服务
docker-compose up -d --build backend
```

### 🔍 进入容器调试

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 在容器内执行命令
docker-compose exec backend python -c "print('Hello')"
```

### 📈 查看资源使用

```bash
# 实时查看资源使用
docker stats

# 查看容器详细信息
docker inspect home-backend
docker inspect home-frontend

# 查看磁盘使用
docker system df
```

---

## 故障排查

### 问题1: 容器无法启动

**症状:**
```bash
docker-compose ps
# 显示 Exit 或 Restarting
```

**解决方案:**
```bash
# 1. 查看详细日志
docker-compose logs backend

# 2. 检查配置文件
docker-compose config

# 3. 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 问题2: 后端无法连接数据库

**症状:**
```bash
# 后端日志显示：
# "Can't connect to MySQL server"
```

**解决方案:**
```bash
# 1. 检查 .env 文件配置
cat .env | grep MYSQL

# 2. 测试数据库连接
docker-compose exec backend ping -c 3 <mysql-host>

# 3. 检查数据库是否可访问
docker-compose exec backend nc -zv <mysql-host> 33061
```

### 问题3: 前端无法访问后端 API

**症状:**
```bash
# 浏览器控制台显示：
# "Network Error" 或 CORS 错误
```

**解决方案:**
```bash
# 1. 检查 CORS 配置
cat .env | grep CORS_ORIGINS

# 2. 确保包含你的域名
# 例如: CORS_ORIGINS=http://localhost:80,http://your-domain.com

# 3. 重启后端
docker-compose restart backend
```

### 问题4: 端口冲突

**症状:**
```bash
# 启动失败，日志显示：
# "port is already allocated"
```

**解决方案:**
```bash
# 1. 查看端口占用
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8002

# 2. 修改 docker-compose.yml 中的端口映射
# ports:
#   - "8080:80"  # 改为其他端口

# 3. 重启服务
docker-compose up -d
```

### 问题5: 镜像构建失败

**症状:**
```bash
# 构建时出现错误
```

**解决方案:**
```bash
# 1. 清理缓存重新构建
docker-compose build --no-cache

# 2. 清理 Docker 系统
docker system prune -a

# 3. 检查网络连接
docker-compose exec backend ping -c 3 google.com
```

---

## 安全建议

### 🔐 基本安全措施

1. **不要提交 .env 文件到代码仓库**
   ```bash
   # 确保在 .gitignore 中
   echo ".env" >> .gitignore
   ```

2. **使用强密码和密钥**
   ```bash
   # 生成随机密钥
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **限制容器资源**
   ```yaml
   # 在 docker-compose.yml 中已配置
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 1G
   ```

4. **启用 HTTPS（生产环境）**
   ```bash
   # 使用 Let's Encrypt + Certbot
   # 配置 Nginx 反向代理
   ```

5. **定期更新镜像**
   ```bash
   # 定期重新构建镜像
   docker-compose build --pull
   ```

### 🛡️ 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 22/tcp      # SSH
sudo ufw enable
```

### 📝 日志管理

```bash
# 配置日志轮转
# 在 docker-compose.yml 中添加：
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 📞 技术支持

如果遇到问题：

1. 查看日志: `docker-compose logs -f`
2. 检查配置: `docker-compose config`
3. 重启服务: `docker-compose restart`
4. 查看文档: http://your-server-ip:8002/docs

---

## 🎉 部署成功

部署成功后，你可以通过以下地址访问：

- **前端**: http://your-server-ip:5173
- **后端 API**: http://your-server-ip:8002
- **API 文档**: http://your-server-ip:8002/docs
- **健康检查**: http://your-server-ip:8002/health

祝你使用愉快！🚀

---

## 📦 部署优化说明

### 🎯 为什么采用本地构建方案？

传统部署方式需要在服务器上执行完整的构建流程：
- ❌ 上传所有前端源代码（src/、public/、package.json 等）
- ❌ 上传 node_modules（可能几百MB）
- ❌ 在服务器上运行 `npm install`（耗时且可能失败）
- ❌ 在服务器上运行 `npm run build`（消耗服务器资源）
- ❌ 最终镜像体积大

**优化后的方案：**
- ✅ 在本地/CI 环境完成构建
- ✅ 只上传构建产物 `dist/` 目录（通常只有几MB）
- ✅ 镜像极小（只包含 Nginx + 静态文件）
- ✅ 构建速度快，服务器资源消耗低

---

### 📝 前端部署步骤（优化后）

#### Step 1: 本地构建前端

**Windows:**
```bash
cd Home-frontend
build.bat
```

**Linux/Mac:**
```bash
cd Home-frontend
chmod +x build.sh
./build.sh
```

这会生成 `dist/` 目录，包含所有静态文件。

#### Step 2: 打包并上传到服务器

**方式1: 使用部署脚本（Linux/Mac）**

编辑 `deploy.sh` 中的服务器信息：
```bash
SERVER_USER="your-user"
SERVER_HOST="your-server-ip"
SERVER_PATH="/opt/home-agent"
```

然后运行：
```bash
chmod +x deploy.sh
./deploy.sh
```

**方式2: 手动上传（通用）**

```bash
# 在本地打包
cd Home-frontend
tar -czf home-frontend-dist.tar.gz dist/ nginx.conf Dockerfile

# 上传到服务器
scp home-frontend-dist.tar.gz user@server:/tmp/

# 在服务器上解压
ssh user@server
cd /opt/home-agent/Home-frontend
tar -xzf /tmp/home-frontend-dist.tar.gz
rm /tmp/home-frontend-dist.tar.gz
```

#### Step 3: 启动前端服务

在服务器上：
```bash
cd /opt/home-agent
docker-compose up -d --build frontend
```

---

### 📊 体积对比

| 方案 | 上传内容 | 上传大小 | 镜像大小 | 构建时间 |
|------|---------|---------|---------|---------|
| **传统方案** | 源码 + node_modules | ~500MB | ~600MB | ~10分钟 |
| **优化方案** | dist/ 目录 | ~5MB | ~25MB | ~2分钟 |

---

### 🔧 开发环境部署

如果你需要在开发环境使用自动构建，可以使用 `Dockerfile.dev`：

```yaml
# 修改 docker-compose.yml
frontend:
  build:
    context: ./Home-frontend
    dockerfile: Dockerfile.dev  # 使用开发版 Dockerfile
```

这个版本会在容器内执行完整构建，适合开发测试。

---

### 🎁 提供的脚本说明

**前端构建脚本：**
- `build.sh` (Linux/Mac) - 本地构建前端
- `build.bat` (Windows) - 本地构建前端
- `deploy.sh` (Linux/Mac) - 自动打包并上传到服务器
- `deploy.bat` (Windows) - 打包部署文件

**使用示例：**

```bash
# 1. 本地构建
./build.sh

# 2. 部署到服务器
./deploy.sh

# 3. 服务器上启动
ssh user@server
cd /opt/home-agent
docker-compose up -d --build frontend
```

---

### 💡 最佳实践

1. **本地构建，远程部署**
   - 在本地/CI 环境完成构建
   - 只上传构建产物到服务器

2. **使用 .dockerignore**
   - 确保源代码和依赖不会被打包到镜像中
   - 减小镜像体积和构建时间

3. **版本控制**
   - 建议将 `dist/` 目录也提交到 Git
   - 或者使用 CI/CD 自动构建并上传

4. **缓存优化**
   - 前端静态文件可以使用 CDN
   - Nginx 配置已启用静态文件缓存

---

### 🚀 快速部署检查清单

- [ ] 本地已构建前端 (`npm run build`)
- [ ] `dist/` 目录存在且包含文件
- [ ] 已配置 `.env` 文件
- [ ] 后端文件已上传到服务器
- [ ] 前端 `dist/`、`nginx.conf`、`Dockerfile` 已上传
- [ ] 运行 `docker-compose build`
- [ ] 运行 `docker-compose up -d`
- [ ] 访问 http://your-server-ip 验证

---
