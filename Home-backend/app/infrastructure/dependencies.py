"""依赖注入模块。"""

from typing import Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.infrastructure.database import get_mysql_session, get_milvus_connection
from app.infrastructure.config import Settings, get_settings
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.milvus_service import MilvusService
from app.core.security import pwd_context

# 配置依赖
SettingsDep = Annotated[Settings, Depends(get_settings)]

# MySQL 会话依赖
MySQLSessionDep = Annotated[AsyncSession, Depends(get_mysql_session)]

# Milvus 连接依赖


def get_milvus():
    """获取 Milvus 连接依赖。"""
    try:
        return get_milvus_connection()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Milvus 服务不可用: {str(e)}"
        )


MilvusDep = Annotated[object, Depends(get_milvus)]


# 示例：用户依赖（可根据需要扩展）
async def get_current_user(
    db: MySQLSessionDep,
    user_id: int
) -> dict | None:
    """获取当前用户（示例依赖）。

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        用户信息或 None
    """
    # 这里可以添加实际的用户查询逻辑
    # from app.models.user import User
    # result = await db.execute(select(User).filter(User.id == user_id))
    # user = result.scalars().first()
    # return user
    return {"id": user_id, "name": "示例用户"}


# LLM 服务依赖
def get_llm_service() -> LLMService:
    """获取 LLM 服务单例。"""
    return LLMService()


LLMServiceDep = Annotated[LLMService, Depends(get_llm_service)]


# Embedding 服务依赖
def get_embedding_service() -> EmbeddingService:
    """获取 Embedding 服务单例。"""
    return EmbeddingService()


EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_service)]


# Milvus 服务依赖
def get_milvus_service_obj() -> MilvusService:
    """获取 Milvus 服务单例。"""
    return MilvusService()


MilvusServiceDep = Annotated[MilvusService, Depends(get_milvus_service_obj)]


# 密码服务依赖
def get_password_service() -> CryptContext:
    """获取密码服务（密码哈希上下文）。"""
    return pwd_context


PasswordServiceDep = Annotated[CryptContext, Depends(get_password_service)]

