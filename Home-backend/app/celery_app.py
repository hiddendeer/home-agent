import eventlet
eventlet.monkey_patch()

from celery import Celery
from app.config import get_settings

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
    "daily-email-today": {
        "task": "app.tasks.email_tasks.send_test_email",
        "schedule": crontab(hour=16, minute=40),  # 今天下午 4:30 (16:30)
    },
}

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"], force=True)

# 显式导入任务模块以确保注册
import app.tasks.email_tasks
