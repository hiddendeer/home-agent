"""API v1 路由模块。"""

from fastapi import APIRouter
from app.api.v1 import users, llm, behavior, notifications

api_router = APIRouter()

# 注册所有路由
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(llm.router, prefix="/llm", tags=["LLM 服务"])
api_router.include_router(behavior.router, prefix="/behavior", tags=["行为记录"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["消息中心"])


# 在这里添加更多路由
# api_router.include_router(items.router, prefix="/items", tags=["物品管理"])
