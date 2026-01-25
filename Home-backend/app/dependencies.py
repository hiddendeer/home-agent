"""依赖注入模块。"""

from typing import Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_mysql_session, get_milvus_connection
from app.config import Settings, get_settings
from app.services.llm_service import LLMService

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

