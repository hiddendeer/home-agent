# Home Backend

基于 FastAPI 的后端项目模板，支持 MySQL 和 Milvus。

## 技术栈

- **Python**: 3.11+
- **Web 框架**: FastAPI 0.128+
- **ASGI 服务器**: Uvicorn
- **数据库**: MySQL (异步 aiomysql)
- **向量数据库**: Milvus
- **ORM**: SQLAlchemy 2.0+
- **数据验证**: Pydantic 2.0+
- **依赖管理**: UV

## 项目结构

```
Home-backend/
├── .env                  # 环境变量配置
├── .env.example          # 环境变量示例
├── pyproject.toml        # UV 项目配置
├── main.py              # 应用入口
├── start.bat            # Windows 启动脚本
├── start_dev.bat        # Windows 开发模式启动脚本
├── start_dev.sh         # Linux/Mac 启动脚本
├── app/
│   ├── __init__.py
│   ├── config.py        # 配置管理
│   ├── database.py      # 数据库连接 (MySQL, Milvus)
│   ├── dependencies.py  # 依赖注入
│   ├── models/          # SQLAlchemy 数据库模型
│   │   ├── __init__.py
│   │   └── user.py      # 示例：用户模型
│   ├── schemas/         # Pydantic 数据验证模式
│   │   ├── __init__.py
│   │   └── user.py      # 示例：用户 Schema
│   └── api/             # API 路由
│       └── v1/          # API v1 版本
│           ├── __init__.py
│           └── users.py  # 示例：用户路由
└── tests/               # 测试目录
    ├── __init__.py
    └── test_users.py
```

## 快速开始

### 1. 安装 UV

```powershell
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### 2. 创建虚拟环境

```powershell
cd Home-backend
uv venv --python 3.11
```

### 3. 安装依赖

依赖已安装到系统 Python 环境。如需安装到虚拟环境：

```powershell
.venv\Scripts\activate
uv pip install fastapi uvicorn[standard] sqlalchemy pymysql cryptography aiomysql pymilvus pydantic pydantic-settings python-jose passlib[bcrypt] python-multipart email-validator httpx python-dotenv pytest pytest-asyncio
```

### 4. 配置环境变量

编辑 `.env` 文件，配置数据库连接：

```env
# MySQL 配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=home_backend

# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=
MILVUS_PASSWORD=
```

### 5. 运行项目

**Windows:**
```powershell
# 方式1: 使用启动脚本
start_dev.bat

# 方式2: 直接运行
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 方式3: 运行 main.py
python main.py
```

**Linux/Mac:**
```bash
chmod +x start_dev.sh
./start_dev.sh
```

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 系统端点
- `GET /` - 根路径，返回应用信息
- `GET /health` - 健康检查

### 用户管理 (示例)
- `POST /api/v1/users/` - 创建用户
- `GET /api/v1/users/` - 获取用户列表 (分页)
- `GET /api/v1/users/{user_id}` - 获取用户详情
- `PUT /api/v1/users/{user_id}` - 更新用户
- `DELETE /api/v1/users/{user_id}` - 删除用户

## 开发指南

### 添加新的 API 端点

#### 1. 创建数据库模型 (`app/models/`)

```python
# app/models/product.py
from sqlalchemy import Column, Integer, String
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
```

#### 2. 创建 Pydantic Schema (`app/schemas/`)

```python
# app/schemas/product.py
from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    price: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True
```

#### 3. 创建路由 (`app/api/v1/`)

```python
# app/api/v1/products.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import MySQLSessionDep
from app.schemas.product import ProductCreate, ProductResponse
from app.models.product import Product

router = APIRouter()

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: MySQLSessionDep
):
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product
```

#### 4. 注册路由 (`app/api/v1/__init__.py`)

```python
from app.api.v1 import products

api_router.include_router(
    products.router,
    prefix="/products",
    tags=["商品管理"]
)
```

### 数据库操作示例

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 查询
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalars().first()

# 创建
new_user = User(username="test", email="test@example.com")
db.add(new_user)
await db.commit()

# 更新
user.email = "newemail@example.com"
await db.commit()

# 删除
await db.delete(user)
await db.commit()
```

### Milvus 向量数据库使用

```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# 连接已在启动时自动建立
# 在需要使用 Milvus 的路由中：

from app.dependencies import MilvusDep

@router.post("/vectors")
async def search_vectors(milvus: MilvusDep):
    # 使用 Milvus 连接
    from pymilvus import utility
    collections = utility.list_collections()
    return {"collections": collections}
```

## 运行测试

```powershell
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_users.py

# 查看详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 代码质量

```powershell
# 格式化代码
black .

# 代码检查
ruff check .

# 自动修复可修复的问题
ruff check --fix .

# 类型检查
mypy app/
```

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `APP_NAME` | 应用名称 | Home Backend API |
| `APP_VERSION` | 应用版本 | 1.0.0 |
| `DEBUG` | 调试模式 | True |
| `HOST` | 服务器主机 | 0.0.0.0 |
| `PORT` | 服务器端口 | 8000 |
| `SECRET_KEY` | JWT 密钥 | your-secret-key |
| `MYSQL_HOST` | MySQL 主机 | localhost |
| `MYSQL_PORT` | MySQL 端口 | 3306 |
| `MYSQL_USER` | MySQL 用户名 | - |
| `MYSQL_PASSWORD` | MySQL 密码 | - |
| `MYSQL_DATABASE` | MySQL 数据库名 | home_backend |
| `MILVUS_HOST` | Milvus 主机 | localhost |
| `MILVUS_PORT` | Milvus 端口 | 19530 |
| `CORS_ORIGINS` | CORS 允许的源 | localhost:3000,localhost:5173 |

## 架构特点

1. **简洁高效**: 扁平化结构，避免过度嵌套
2. **异步支持**: 全异步设计，高性能 I/O 操作
3. **关注点分离**: models、schemas、api 各司其职
4. **依赖注入**: 统一的数据库和配置管理
5. **类型安全**: 完整的类型提示
6. **自动化文档**: OpenAPI/Swagger 自动生成

## 生产部署

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy pymysql aiomysql pymilvus pydantic pydantic-settings

# 复制应用代码
COPY ./app /app/app
COPY main.py .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 使用多 Worker

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## License

MIT

