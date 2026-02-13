"""Embedding 服务模块。"""

import httpx
import logging
from typing import List
from app.infrastructure.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class EmbeddingService:
    """Embedding 服务类, 直接调用 ZhipuAI API。"""

    def __init__(self):
        self.api_key = settings.embedding_api_key
        self.api_base = settings.embedding_api_base
        self.model = settings.embedding_model
        self.dimensions = settings.embedding_dimensions

    async def get_embeddings(self, text: str) -> List[float]:
        """获取文本的 Embedding 向量。

        Args:
            text: 输入文本

        Returns:
            List[float]: 向量
        """
        if not self.api_key:
            logger.error("EMBEDDING_API_KEY 未配置")
            raise ValueError("EMBEDDING_API_KEY is not configured")

        url = f"{self.api_base.rstrip('/')}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "input": text,
            "dimensions": self.dimensions if "embedding-3" in self.model else None
        }
        # Remove dimensions if None
        payload = {k: v for k, v in payload.items() if v is not None}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]
            except Exception as e:
                logger.error(f"ZhipuAI Embedding 调用失败: {e}")
                raise
