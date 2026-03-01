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
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, BackgroundTasks, Query
from sqlalchemy import update

from app.infrastructure.dependencies import MySQLSessionDep, LLMServiceDep, EmbeddingServiceDep, MilvusServiceDep
from app.models.behavior import Behavior
from app.schemas.behavior import BehaviorCreate, BehaviorResponse

router = APIRouter()
logger = logging.getLogger(__name__)


async def process_semantic_memory(
    behavior_id: int,
    user_id: int,
    raw_content: str,
    details: dict,
    llm_service: LLMServiceDep,
    embedding_service: EmbeddingServiceDep,
    milvus_service: MilvusServiceDep
):
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
        llm_service: LLM 服务（依赖注入）
        embedding_service: Embedding 服务（依赖注入）
        milvus_service: Milvus 服务（依赖注入）

    Note:
        此函数在后台任务中执行，不会阻塞主请求响应。
        如果处理失败，仅记录日志而不影响主流程。
    """
    import app.infrastructure.database

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
        if app.infrastructure.database.async_session_maker is None:
            app.infrastructure.database.init_mysql()

        async with app.infrastructure.database.async_session_maker() as session:
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
    db: MySQLSessionDep,
    llm_service: LLMServiceDep,
    embedding_service: EmbeddingServiceDep,
    milvus_service: MilvusServiceDep
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
        llm_service: LLM 服务
        embedding_service: Embedding 服务
        milvus_service: Milvus 服务

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
        details_dict,
        llm_service,
        embedding_service,
        milvus_service
    )
    logger.info(f"后台任务已触发: behavior_id={b_id}")

    # 步骤 3: 模式识别与关怀推送 —— 深夜回家模式
    # 规则：设备是 door/unlock_door，且时间在晚上20:00之后到次日凌晨04:00之前
    # 使用标准库实现时区感知的时间检查 (Asia/Shanghai = UTC+8)
    shanghai_tz = timezone(timedelta(hours=8))
    now_shanghai = datetime.now(shanghai_tz)
    hour = now_shanghai.hour
    
    logger.info(f"检查深夜回家模式: device_id={behavior_in.device_id}, action_type={behavior_in.action_type}, hour={hour}")
    
    if (behavior_in.action_type in ["unlock_door", "open"]) and (behavior_in.device_id in ["door", "unlock_door"]):
        if hour >= 20 or hour < 4:
            from app.tasks.care_tasks import send_late_night_care_notification
            send_late_night_care_notification.delay(u_id)
            logger.info(f"深夜回家模式触发成功: 触发关怀任务 for user_id={u_id}")
        else:
            logger.info(f"深夜回家模式未触发: 当前小时({hour})不在 20:00-04:00 范围内")
    else:
        logger.info(f"深夜回家模式未触发: 动作或设备不匹配 (expected: door or unlock_door, got: {behavior_in.device_id}/{behavior_in.action_type})")

    return new_behavior


@router.get(
    "/",
    response_model=List[BehaviorResponse],
    summary="查询行为记录",
    description="从数据库查询用户行为记录，支持按用户筛选和限制数量"
)
async def get_behaviors(
    db: MySQLSessionDep,
    user_id: Annotated[int | None, Query(description="用户ID，不传则查询所有用户")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="返回的最大记录数")] = 10
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
