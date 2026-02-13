"""时间处理工具模块。

提供时间相关的辅助函数。
"""

from datetime import datetime, timezone


def calculate_minutes_ago(since: datetime, now: datetime | None = None) -> float:
    """计算距离某个时间的分钟数。

    Args:
        since: 过去的时间点
        now: 当前时间（默认使用系统当前时间）

    Returns:
        距离的分钟数
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # 处理时区
    if since.tzinfo:
        now = now.astimezone(since.tzinfo) if now.tzinfo else now
    else:
        now = now.replace(tzinfo=None) if now.tzinfo else now

    return (now - since).total_seconds() / 60


def ensure_timezone_aware(dt: datetime) -> datetime:
    """确保 datetime 对象有时区信息。

    Args:
        dt: datetime 对象

    Returns:
        带有时区信息的 datetime 对象
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
