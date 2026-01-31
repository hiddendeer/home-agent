"""
快速插入测试数据
"""
import asyncio
import sys
from datetime import datetime

sys.path.append('.')

async def insert_test_data():
    from app.database import init_databases
    import app.database as db
    from app.models.notification import Notification
    from app.schemas.notification import NotificationCategory

    print("正在初始化数据库连接...")
    await init_databases()

    test_data = [
        {
            'user_id': 101,
            'category': NotificationCategory.REMINDER.value,
            'title': '饮水提醒',
            'content': '温馨提醒：您已经超过10分钟没喝水了，请记得补水哦！',
        },
        {
            'user_id': 101,
            'category': NotificationCategory.SYSTEM.value,
            'title': '系统通知',
            'content': '欢迎使用 Home Agent 智能助手！',
        },
        {
            'user_id': 101,
            'category': NotificationCategory.ALERT.value,
            'title': '安全提醒',
            'content': '检测到异常登录，请确认是否为本人操作',
        },
        {
            'user_id': 101,
            'category': NotificationCategory.REMINDER.value,
            'title': '运动提醒',
            'content': '您已经坐了1小时了，起来活动一下吧！',
        },
        {
            'user_id': 101,
            'category': NotificationCategory.SYSTEM.value,
            'title': '数据同步',
            'content': '您的数据已成功同步到云端',
        },
    ]

    print(f"正在插入 {len(test_data)} 条测试数据...")

    async with db.async_session_maker() as session:
        for data in test_data:
            notification = Notification(
                user_id=data['user_id'],
                category=data['category'],
                title=data['title'],
                content=data['content'],
                is_read=False,
                created_at=datetime.now()
            )
            session.add(notification)

        await session.commit()

    print("✅ 测试数据插入成功！")
    print("\n现在可以刷新前端页面查看通知")

if __name__ == "__main__":
    asyncio.run(insert_test_data())
