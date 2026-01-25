"""行为记录 API。

此模块提供用户行为记录的 CRUD 接口，并支持异步语义记忆处理。
行为记录流程：
1. 接收行为数据并存入 MySQL（结构化数据）
2. 触发后台任务进行语义处理：
   - 使用 LLM 生成自然语言描述
   - 将描述转换为向量 Embedding
   - 存入 Milvus 向量数据库用于语义搜索
   - 更新 MySQL 记录的语义化描述
"""

import time
import logging
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.database import get_mysql_session
from app.models.behavior import Behavior
from app.schemas.behavior import BehaviorCreate, BehaviorResponse, BehaviorQuery
from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.milvus_service import MilvusService
from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

# 初始化服务实例
# 注意：这些是无状态的服务类，可以安全地在模块级别初始化
llm_service = LLMService()
embedding_service = EmbeddingService()
milvus_service = MilvusService()


async def process_semantic_memory(behavior_id: int, user_id: int, raw_content: str, details: dict):
    """异步处理语义记忆（后台任务）。

    此函数在后台异步执行，将原始行为数据转换为语义记忆：
    1. 调用 LLM 生成自然语言描述
    2. 将描述转换为向量 Embedding
    3. 存入 Milvus 向量数据库
    4. 更新 MySQL 记录

    Args:
        behavior_id: 行为记录 ID
        user_id: 用户 ID
        raw_content: 原始行为描述
        details: 行为细节参数

    Note:
        此函数在后台任务中执行，不会阻塞主请求响应。
        如果处理失败，仅记录日志而不影响主流程。
    """
    import app.database

    try:
        # 步骤 1: 使用 LLM 生成语义化描述
        prompt = (
            f"根据以下信息，生成一句简洁、地道的中文自然语言描述：\n"
            f"- 原始操作: {raw_content}\n"
            f"- 详细参数: {details}\n"
            f"要求：包含动词、设备名、状态及关键参数(如有)。例如：'陈先生开启了空调，温度设为24°C'。"
        )
        system_prompt = "你是一个智能家居管家。请描述用户的最新动作。"

        logger.info(f"开始 LLM 语义化处理: behavior_id={behavior_id}")
        semantic_content = await llm_service.generate(prompt, system_prompt)
        semantic_content = semantic_content.strip('"').strip("'").strip()
        logger.info(f"LLM 语义化完成: behavior_id={behavior_id}, content={semantic_content}")

        # 步骤 2: 获取文本的 Embedding 向量
        logger.debug(f"开始生成 Embedding: behavior_id={behavior_id}")
        vector = await embedding_service.get_embeddings(semantic_content)

        # 步骤 3: 存入 Milvus 向量数据库（用于语义搜索）
        timestamp = int(time.time())
        await milvus_service.insert_behavior(
            behavior_id=behavior_id,
            user_id=user_id,
            content=semantic_content,
            vector=vector,
            timestamp=timestamp
        )
        logger.info(f"向量已存入 Milvus: behavior_id={behavior_id}")

        # 步骤 4: 更新 MySQL 记录（补充语义化描述）
        # 注意：需要重新创建数据库会话，因为原会话已关闭
        if app.database.async_session_maker is None:
            app.database.init_mysql()

        async with app.database.async_session_maker() as session:
            await session.execute(
                update(Behavior)
                .where(Behavior.id == behavior_id)
                .values(semantic_content=semantic_content)
            )
            await session.commit()
            logger.info(f"MySQL 记录已更新: behavior_id={behavior_id}")

    except Exception as e:
        # 后台任务失败不应影响主流程，记录日志便于排查问题
        logger.error(f"语义记忆处理失败: behavior_id={behavior_id}, error={str(e)}", exc_info=True)

@router.post(
    "/",
    response_model=BehaviorResponse,
    status_code=201,
    summary="记录用户行为",
    description="记录用户行为并触发异步语义化处理"
)
async def record_behavior(
    behavior_in: BehaviorCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_mysql_session)
):
    """记录用户行为并触发异步语义化处理。

    流程说明：
    1. 将行为数据存入 MySQL 数据库（结构化存储）
    2. 触发后台任务进行语义处理（非阻塞）
       - LLM 生成自然语言描述
       - 生成向量 Embedding
       - 存入 Milvus 向量数据库

    Args:
        behavior_in: 行为创建数据
        background_tasks: FastAPI 后台任务管理器
        db: 数据库会话

    Returns:
        BehaviorResponse: 创建的行为记录

    Note:
        语义处理在后台异步执行，API 会立即返回行为记录。
        semantic_content 字段在后台处理完成后更新。
    """
    # 步骤 1: 存入 MySQL（结构化日志）
    new_behavior = Behavior(
        user_id=behavior_in.user_id,
        device_id=behavior_in.device_id,
        action_type=behavior_in.action_type,
        details=behavior_in.details,
        raw_content=behavior_in.raw_content
    )
    db.add(new_behavior)
    await db.commit()
    await db.refresh(new_behavior)
    logger.info(f"行为记录已创建: id={new_behavior.id}, user_id={new_behavior.user_id}")

    # 步骤 2: 触发后台任务（语义记忆处理）
    # 重要：提取基础类型避免 SQLAlchemy 对象的会话闭包问题
    b_id = int(new_behavior.id)
    u_id = int(new_behavior.user_id)
    content = str(new_behavior.raw_content or new_behavior.action_type)
    details_dict = dict(new_behavior.details) if new_behavior.details else {}

    background_tasks.add_task(
        process_semantic_memory,
        b_id,
        u_id,
        content,
        details_dict
    )
    logger.info(f"后台任务已触发: behavior_id={b_id}")

    return new_behavior


@router.get(
    "/",
    response_model=List[BehaviorResponse],
    summary="查询行为记录",
    description="从数据库查询用户行为记录，支持按用户筛选和限制数量"
)
async def get_behaviors(
    user_id: Annotated[int | None, Query(description="用户ID，不传则查询所有用户")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="返回的最大记录数")] = 10,
    db: AsyncSession = Depends(get_mysql_session)
):
    """从数据库查询行为记录。

    Args:
        user_id: 可选的用户ID筛选条件
        limit: 返回记录的最大数量（1-100）
        db: 数据库会话

    Returns:
        List[BehaviorResponse]: 行为记录列表，按时间倒序排列
    """
    from sqlalchemy import select

    query = select(Behavior)
    if user_id:
        query = query.where(Behavior.user_id == user_id)

    # 按时间倒序排列，最新的在前
    query = query.order_by(Behavior.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    behaviors = result.scalars().all()

    logger.info(f"查询行为记录: user_id={user_id}, count={len(behaviors)}")
    return behaviors
