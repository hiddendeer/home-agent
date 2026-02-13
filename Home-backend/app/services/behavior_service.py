"""行为处理服务模块。

提供行为记录的语义处理等业务逻辑。
"""

import time
import logging
from sqlalchemy import update

from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.milvus_service import MilvusService
from app.models.behavior import Behavior

logger = logging.getLogger(__name__)


class BehaviorService:
    """行为处理服务类。

    封装行为记录的语义处理相关业务逻辑，包括：
    - LLM 语义化描述生成
    - 向量 Embedding 生成
    - Milvus 向量存储
    - MySQL 记录更新
    """

    def __init__(
        self,
        llm_service: LLMService,
        embedding_service: EmbeddingService,
        milvus_service: MilvusService
    ):
        """初始化行为服务。

        Args:
            llm_service: LLM 服务
            embedding_service: Embedding 服务
            milvus_service: Milvus 服务
        """
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.milvus_service = milvus_service

    async def process_semantic_memory(
        self,
        behavior_id: int,
        user_id: int,
        raw_content: str,
        details: dict
    ) -> str:
        """处理语义记忆。

        将原始行为数据转换为语义记忆：
        1. 调用 LLM 生成自然语言描述
        2. 将描述转换为向量 Embedding
        3. 存入 Milvus 向量数据库
        4. 返回语义化内容供调用方更新 MySQL

        Args:
            behavior_id: 行为记录 ID
            user_id: 用户 ID
            raw_content: 原始行为描述
            details: 行为细节参数

        Returns:
            语义化描述内容

        Raises:
            Exception: 处理失败时抛出异常
        """
        # 步骤 1: 使用 LLM 生成语义化描述
        prompt = (
            f"根据以下信息，生成一句简洁、地道的中文自然语言描述：\n"
            f"- 原始操作: {raw_content}\n"
            f"- 详细参数: {details}\n"
            f"要求：包含动词、设备名、状态及关键参数(如有)。"
            f"例如：'陈先生开启了空调，温度设为24°C'。"
        )
        system_prompt = "你是一个智能家居管家。请描述用户的最新动作。"

        logger.info(f"开始 LLM 语义化处理: behavior_id={behavior_id}")
        semantic_content = await self.llm_service.generate(prompt, system_prompt)
        semantic_content = semantic_content.strip('"').strip("'").strip()
        logger.info(
            f"LLM 语义化完成: behavior_id={behavior_id}, "
            f"content={semantic_content}"
        )

        # 步骤 2: 获取文本的 Embedding 向量
        logger.debug(f"开始生成 Embedding: behavior_id={behavior_id}")
        vector = await self.embedding_service.get_embeddings(semantic_content)

        # 步骤 3: 存入 Milvus 向量数据库（用于语义搜索）
        timestamp = int(time.time())
        await self.milvus_service.insert_behavior(
            behavior_id=behavior_id,
            user_id=user_id,
            content=semantic_content,
            vector=vector,
            timestamp=timestamp
        )
        logger.info(f"向量已存入 Milvus: behavior_id={behavior_id}")

        return semantic_content
