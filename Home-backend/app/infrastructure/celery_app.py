from celery import Celery
from app.infrastructure.config import get_settings

settings = get_settings()

celery_app = Celery(
    "home_backend",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

from celery.schedules import crontab

# 可选：配置 Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    # 增加重连设置和超时设置，应对远程 Redis 连接不稳定的问题
    broker_connection_retry_on_startup=True,
    broker_transport_options={
        "visibility_timeout": 3600,
        "socket_timeout": 30,
        "socket_connect_timeout": 30,
        "socket_keepalive": True,
    },
    redis_backend_health_check_interval=30,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    "daily-hydration-check": {
        "task": "app.tasks.hydration_tasks.trigger_daily_hydration_checks",
        "schedule": crontab(minute="*/10"),  # 每10分钟执行一次，以配合10小时提醒窗口
    },
}

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"], force=True)

# 显式导入任务模块以确保注册
import app.tasks.hydration_tasks  # noqa: F401
