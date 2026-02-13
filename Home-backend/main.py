"""FastAPI 应用主入口。"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.infrastructure.config import get_settings
from app.infrastructure.database import init_databases, close_databases
from app.api.v1 import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。

    启动和关闭时执行的操作。
    """
    # 启动时执行
    logger.info("🚀 应用启动中...")
    await init_databases()
    logger.info("✅ 数据库连接已初始化")

    yield

    # 关闭时执行
    logger.info("🛑 应用关闭中...")
    await close_databases()
    logger.info("✅ 数据库连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于 FastAPI 的后端服务",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器。"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )


# 健康检查
@app.get("/", tags=["系统"])
async def root():
    """根路径。"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点。"""
    return {"status": "healthy"}


# 注册路由
app.include_router(api_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
