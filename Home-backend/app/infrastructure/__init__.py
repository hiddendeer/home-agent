"""基础设施模块。

包含应用的核心基础设施组件：
- config: 配置管理
- database: 数据库连接
- dependencies: 依赖注入
- celery_app: Celery 任务队列配置
"""

from app.infrastructure.config import get_settings, Settings
from app.infrastructure.database import (
    init_databases,
    close_databases,
    Base,
    engine,
    async_session_maker,
)
from app.infrastructure.dependencies import (
    SettingsDep,
    MySQLSessionDep,
    MilvusDep,
    LLMServiceDep,
    EmbeddingServiceDep,
    MilvusServiceDep,
    PasswordServiceDep,
)
from app.infrastructure.celery_app import celery_app

__all__ = [
    # Config
    "get_settings",
    "Settings",
    # Database
    "init_databases",
    "close_databases",
    "Base",
    "engine",
    "async_session_maker",
    # Dependencies
    "SettingsDep",
    "MySQLSessionDep",
    "MilvusDep",
    "LLMServiceDep",
    "EmbeddingServiceDep",
    "MilvusServiceDep",
    "PasswordServiceDep",
    # Celery
    "celery_app",
]
