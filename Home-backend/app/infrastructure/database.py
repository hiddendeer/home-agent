"""数据库连接模块。

此模块负责管理 MySQL 和 Milvus 数据库的连接、初始化和关闭。
提供了数据库会话的依赖注入功能，确保连接的正确管理和释放。
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from pymilvus import connections, MilvusException
from typing import Optional
import logging

from app.infrastructure.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# SQLAlchemy Base - 用于声明 ORM 模型
Base = declarative_base()

# MySQL 异步引擎和会话工厂
# engine: 异步数据库引擎，负责连接池管理
# async_session_maker: 会话工厂，用于创建数据库会话
engine: Optional[AsyncEngine] = None
async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def init_mysql() -> None:
    """初始化 MySQL 数据库连接。

    创建异步引擎和会话工厂，配置连接池参数。
    连接池配置:
    - pool_size=10: 保持 10 个连接在池中
    - max_overflow=20: 最多可以额外创建 20 个连接
    - pool_pre_ping=True: 使用连接前先 ping，确保连接有效

    Raises:
        Exception: 数据库连接初始化失败时抛出异常
    """
    global engine, async_session_maker

    try:
        engine = create_async_engine(
            settings.mysql_url,
            echo=settings.debug,  # 调试模式下打印 SQL 语句
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            # 设置数据库连接的会话时区为东八区（北京时间）
            connect_args={"init_command": "SET time_zone='+08:00'"}
        )
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # 提交后不过期对象，避免延迟加载问题
            autocommit=False,
            autoflush=False,
        )
        logger.info(f"MySQL 连接已初始化: {settings.mysql_host}:{settings.mysql_port}")
    except Exception as e:
        logger.error(f"MySQL 连接初始化失败: {e}")
        raise


async def get_mysql_session() -> AsyncSession:
    """获取 MySQL 数据库会话（依赖注入函数）。

    这是一个生成器函数，使用 FastAPI 的依赖注入系统。
    自动处理会话的生命周期、事务提交/回滚和连接释放。

    Yields:
        AsyncSession: 异步数据库会话

    Raises:
        RuntimeError: 数据库未初始化时抛出异常

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_mysql_session)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    if async_session_maker is None:
        raise RuntimeError("MySQL 未初始化，请先调用 init_mysql()")

    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            await session.close()


async def close_mysql():
    """关闭 MySQL 数据库连接。"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("MySQL 连接已关闭")


# Milvus 连接管理
milvus_connected: bool = False


def init_milvus() -> bool:
    """初始化 Milvus 向量数据库连接。

    连接到 Milvus 服务器，用于存储和检索行为向量化数据。

    Returns:
        bool: 连接是否成功

    Note:
        如果 Milvus 连接失败，仅记录警告日志而不中断应用启动。
        这允许应用在没有向量数据库的情况下继续运行基本功能。
    """
    global milvus_connected

    try:
        connections.connect(
            alias="default",
            host=settings.milvus_host,
            port=settings.milvus_port,
            user=settings.milvus_user or None,
            password=settings.milvus_password or None,
        )
        milvus_connected = True
        logger.info(f"Milvus 连接已初始化: {settings.milvus_host}:{settings.milvus_port}")
        return True
    except MilvusException as e:
        logger.warning(f"Milvus 连接失败: {e}")
        milvus_connected = False
        return False


def get_milvus_connection():
    """获取 Milvus 连接。

    Returns:
        Milvus 连接对象
    """
    if not milvus_connected:
        raise RuntimeError("Milvus 未连接，请先调用 init_milvus()")
    return connections


def close_milvus():
    """关闭 Milvus 连接。"""
    global milvus_connected
    try:
        connections.disconnect("default")
        milvus_connected = False
        logger.info("Milvus 连接已关闭")
    except MilvusException as e:
        logger.warning(f"Milvus 断开连接时出错: {e}")


async def init_databases() -> None:
    """初始化所有数据库连接。

    在应用启动时调用，初始化 MySQL 和 Milvus 连接。
    注意：init_mysql() 虽然不是异步函数，但可以同步调用。
    """
    init_mysql()
    init_milvus()


async def close_databases() -> None:
    """关闭所有数据库连接。

    在应用关闭时调用，优雅地关闭所有数据库连接。
    """
    await close_mysql()
    close_milvus()
