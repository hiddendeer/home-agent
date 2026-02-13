"""
通知功能调试脚本
用于诊断前端无法显示通知数据的问题
"""
import asyncio
import sys
from datetime import datetime

# 添加项目路径
sys.path.append('.')


async def main():
    print("=" * 60)
    print("🔍 通知功能诊断工具")
    print("=" * 60)

    # 1. 检查数据库连接
    print("\n📌 步骤 1: 检查数据库连接...")
    try:
        from app.infrastructure.config import get_settings
        from app.infrastructure.database import init_databases

        settings = get_settings()
        print(f"✓ 配置加载成功")
        print(f"  - MySQL: {settings.mysql_host}:{settings.mysql_port}")
        print(f"  - 数据库: {settings.mysql_database}")

        await init_databases()
        print("✓ 数据库连接成功")

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return

    # 2. 检查表是否存在
    print("\n📌 步骤 2: 检查 notifications 表...")
    try:
        import app.infrastructure.database as db
        from sqlalchemy import text

        async with db.async_session_maker() as session:
            result = await session.execute(text("SHOW TABLES LIKE 'notifications'"))
            table_exists = result.fetchone()

            if table_exists:
                print("✓ notifications 表存在")
            else:
                print("❌ notifications 表不存在！需要先创建表")
                print("  解决方案: 运行创建表的脚本或 Alembic 迁移")
                return

    except Exception as e:
        print(f"❌ 检查表失败: {e}")
        return

    # 3. 检查表中的数据
    print("\n📌 步骤 3: 检查表中的数据...")
    try:
        from app.models.notification import Notification
        from sqlalchemy import select, func

        async with db.async_session_maker() as session:
            # 统计总记录数
            count_result = await session.execute(select(func.count()).select_from(Notification))
            total_count = count_result.scalar()
            print(f"✓ 表中共有 {total_count} 条通知记录")

            if total_count == 0:
                print("\n⚠️  问题发现：表中没有任何数据！")
                print("\n💡 可能的原因：")
                print("  1. Celery Beat/Worker 未启动，没有生成提醒任务")
                print("  2. 任务未触发或执行失败")
                print("  3. 数据库清空了但未重新生成")

                print("\n🔧 解决方案：")
                print("  方案 A: 手动插入测试数据（推荐，立即可用）")
                print("  方案 B: 启动 Celery Beat/Worker 等待自动生成")

                choice = input("\n是否插入测试数据？(y/n): ").strip().lower()
                if choice == 'y':
                    await insert_test_data(session)
                return

            # 查看各用户的数据分布
            user_dist_result = await session.execute(
                select(Notification.user_id, func.count().label('count'))
                .group_by(Notification.user_id)
            )
            user_dist = user_dist_result.fetchall()

            print(f"\n用户分布:")
            for user_id, count in user_dist:
                print(f"  - 用户 {user_id}: {count} 条")

            # 显示最近几条记录
            recent_result = await session.execute(
                select(Notification)
                .order_by(Notification.created_at.desc())
                .limit(5)
            )
            recent_notifications = recent_result.scalars().all()

            print(f"\n最近的 {len(recent_notifications)} 条通知:")
            for notif in recent_notifications:
                print(f"  - ID: {notif.id}, 用户: {notif.user_id}, 类型: {notif.category}")
                print(f"    标题: {notif.title}")
                print(f"    内容: {notif.content[:50]}..." if len(notif.content or '') > 50 else f"    内容: {notif.content}")
                print(f"    时间: {notif.created_at}")
                print()

    except Exception as e:
        print(f"❌ 查询数据失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. 测试 API 端点
    print("\n📌 步骤 4: 测试 API 端点...")
    try:
        from app.models.notification import Notification
        from sqlalchemy import select

        async with db.async_session_maker() as session:
            # 测试查询 user_id=101 的数据
            test_user_id = 101
            result = await session.execute(
                select(Notification)
                .where(Notification.user_id == test_user_id)
                .order_by(Notification.created_at.desc())
                .limit(10)
            )
            notifications = result.scalars().all()

            print(f"✓ 用户 {test_user_id} 有 {len(notifications)} 条通知")

            if len(notifications) == 0:
                print(f"\n⚠️  用户 {test_user_id} 没有通知数据！")
                print(f"\n💡 前端配置的用户ID是: {test_user_id}")
                print(f"   但数据库中没有该用户的通知")

                print(f"\n🔧 解决方案：")
                print(f"   1. 为用户 {test_user_id} 插入测试数据")
                choice = input("是否插入？(y/n): ").strip().lower()
                if choice == 'y':
                    await insert_test_data_for_user(session, test_user_id)
                return

            print(f"\n✓ 数据验证通过！")
            print(f"  用户 {test_user_id} 应该能看到 {len(notifications)} 条通知")

    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. 检查前端配置
    print("\n📌 步骤 5: 检查前端配置...")
    print(f"✓ 前端 API 地址: http://localhost:8002/api/v1")
    print(f"✓ 前端用户 ID: 101")
    print(f"\n💡 如果前端仍然看不到数据，请检查：")
    print(f"  1. 后端服务是否启动在端口 8002")
    print(f"  2. 浏览器控制台是否有错误")
    print(f"  3. 网络请求是否成功（F12 -> Network）")


async def insert_test_data(session):
    """为多个用户插入测试数据"""
    from app.models.notification import Notification
    from app.schemas.notification import NotificationCategory
    from datetime import datetime

    test_data = [
        {
            'user_id': 101,
            'category': NotificationCategory.REMINDER.value,
            'title': '饮水提醒',
            'content': '温馨提醒：您已经超过10分钟没喝水了，请记得补水哦！'
        },
        {
            'user_id': 101,
            'category': NotificationCategory.SYSTEM.value,
            'title': '系统通知',
            'content': '欢迎使用 Home Agent 智能助手！'
        },
        {
            'user_id': 101,
            'category': NotificationCategory.ALERT.value,
            'title': '安全提醒',
            'content': '检测到异常登录，请确认是否为本人操作'
        },
        {
            'user_id': 102,
            'category': NotificationCategory.REMINDER.value,
            'title': '饮水提醒',
            'content': '该喝水了！'
        },
    ]

    print(f"\n📝 正在插入 {len(test_data)} 条测试数据...")
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
    print(f"✓ 测试数据插入成功！")

    # 验证插入结果
    from sqlalchemy import select, func
    count_result = await session.execute(select(func.count()).select_from(Notification))
    total_count = count_result.scalar()
    print(f"✓ 表中现在共有 {total_count} 条记录")


async def insert_test_data_for_user(session, user_id):
    """为指定用户插入测试数据"""
    from app.models.notification import Notification
    from app.schemas.notification import NotificationCategory
    from datetime import datetime

    test_data = [
        {
            'category': NotificationCategory.REMINDER.value,
            'title': '饮水提醒',
            'content': '温馨提醒：您已经超过10分钟没喝水了，请记得补水哦！'
        },
        {
            'category': NotificationCategory.SYSTEM.value,
            'title': '系统通知',
            'content': '欢迎使用 Home Agent 智能助手！'
        },
        {
            'category': NotificationCategory.ALERT.value,
            'title': '安全提醒',
            'content': '检测到异常登录，请确认是否为本人操作'
        },
    ]

    print(f"\n📝 正在为用户 {user_id} 插入 {len(test_data)} 条测试数据...")
    for data in test_data:
        notification = Notification(
            user_id=user_id,
            category=data['category'],
            title=data['title'],
            content=data['content'],
            is_read=False,
            created_at=datetime.now()
        )
        session.add(notification)

    await session.commit()
    print(f"✓ 测试数据插入成功！")


if __name__ == "__main__":
    try:
        asyncio.run(main())
        print("\n" + "=" * 60)
        print("✓ 诊断完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()
