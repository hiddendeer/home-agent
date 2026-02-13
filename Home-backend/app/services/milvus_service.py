"""Milvus 服务模块。"""

import logging
from typing import List, Dict, Any
from pymilvus import (
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
    connections
)
from app.infrastructure.config import get_settings
from app.infrastructure.database import init_milvus

logger = logging.getLogger(__name__)
settings = get_settings()

class MilvusService:
    """Milvus 服务类, 处理向量存储。"""

    def __init__(self):
        self.collection_name = "home_behaviors"
        self.dim = settings.embedding_dimensions
        self._ensure_connection()
        self._init_collection()

    def _ensure_connection(self):
        """确保 Milvus 已连接。"""
        try:
            connections.get_connection("default")
        except Exception:
            init_milvus()

    def _init_collection(self):
        """初始化 Milvus 集合。"""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            logger.info(f"Milvus 集合 {self.collection_name} 已存在")
        else:
            # 定义字段
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True, description="Primary Key"),
                FieldSchema(name="user_id", dtype=DataType.INT64, description="User ID"),
                FieldSchema(name="behavior_id", dtype=DataType.INT64, description="MySQL Record ID"),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dim, description="Embedding Vector"),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=1000, description="Semantic Content"),
                FieldSchema(name="timestamp", dtype=DataType.INT64, description="Unix Timestamp")
            ]
            schema = CollectionSchema(fields, description="Smart Home AI Agent Behavior Semantic Memory")
            self.collection = Collection(self.collection_name, schema)
            
            # 创建索引
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            self.collection.create_index(field_name="vector", index_params=index_params)
            logger.info(f"Milvus 集合 {self.collection_name} 创建成功, 维度: {self.dim}")

    async def insert_behavior(self, behavior_id: int, user_id: int, content: str, vector: List[float], timestamp: int):
        """插入行为向量。"""
        data = [
            [user_id],
            [behavior_id],
            [vector],
            [content],
            [timestamp]
        ]
        try:
            self.collection.insert(data)
            self.collection.flush()
            logger.info(f"行为向量已存储到 Milvus: behavior_id={behavior_id}")
        except Exception as e:
            logger.error(f"Milvus 插入失败: {e}")
            raise

    async def search_behavior(self, user_id: int, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """搜索相似行为。"""
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        try:
            self.collection.load()
            results = self.collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=limit,
                expr=f"user_id == {user_id}",
                output_fields=["behavior_id", "content", "timestamp"]
            )
            
            hits = []
            for hit in results[0]:
                hits.append({
                    "behavior_id": hit.entity.get("behavior_id"),
                    "content": hit.entity.get("content"),
                    "timestamp": hit.entity.get("timestamp"),
                    "distance": hit.distance
                })
            return hits
        except Exception as e:
            logger.error(f"Milvus 搜索失败: {e}")
            raise
