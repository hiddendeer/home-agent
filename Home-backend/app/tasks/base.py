"""Celery 任务基类和工具模块。

提供 Celery 任务的基础功能和辅助函数。
"""

from app.core.async_helpers import run_async

__all__ = ["run_async"]
