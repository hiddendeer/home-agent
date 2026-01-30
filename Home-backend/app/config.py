"""应用配置模块。

使用 Pydantic Settings 管理应用配置，支持从环境变量和 .env 文件读取配置。
配置项包括：应用信息、数据库连接、LLM 服务、Embedding 服务等。
"""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类。

    所有配置项都可以通过环境变量覆盖，环境变量名格式为大写加下划线。
    例如：app_name 对应环境变量 APP_NAME

    Example:
        # .env 文件示例
        APP_NAME=My API
        MYSQL_HOST=localhost
        MYSQL_PORT=3306
        LLM_API_KEY=sk-xxxxx
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # 环境变量不区分大小写
        extra="ignore"  # 忽略额外的环境变量
    )

    # ============== 应用配置 ==============
    app_name: str = Field(default="Home Backend API", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本号")
    debug: bool = Field(default=True, description="调试模式（开启后会打印 SQL 语句）")
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 路径前缀")
    timezone: str = Field(default="Asia/Shanghai", description="应用时区")

    # ============== 服务器配置 ==============
    host: str = Field(default="0.0.0.0", description="服务器监听地址")
    port: int = Field(default=8002, description="服务器监听端口")

    # ============== 安全配置 ==============
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT 签名密钥（生产环境必须修改）"
    )
    algorithm: str = Field(default="HS256", description="JWT 签名算法")
    access_token_expire_minutes: int = Field(
        default=30,
        description="访问令牌过期时间（分钟）"
    )

    # ============== MySQL 数据库配置 ==============
    db_url: str | None = Field(
        default=None,
        description="完整的数据库连接 URL（如果提供则优先使用，格式：mysql+aiomysql://user:pass@host:port/db）"
    )
    mysql_host: str = Field(default="localhost", description="MySQL 服务器地址")
    mysql_port: int = Field(default=3306, description="MySQL 服务器端口")
    mysql_user: str = Field(default="", description="MySQL 用户名")
    mysql_password: str = Field(default="", description="MySQL 密码")
    mysql_database: str = Field(default="home_backend", description="MySQL 数据库名")

    @property
    def mysql_url(self) -> str:
        """构建 MySQL 数据库连接 URL。

        优先使用 db_url，如果未提供则根据其他配置构建 URL。
        使用 aiomysql 驱动支持异步操作。

        Returns:
            str: SQLAlchemy 异步连接 URL
        """
        if self.db_url:
            return self.db_url
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    # ============== Milvus 向量数据库配置 ==============
    milvus_host: str = Field(default="localhost", description="Milvus 服务器地址")
    milvus_port: int = Field(default=19530, description="Milvus 服务器端口")
    milvus_user: str = Field(default="", description="Milvus 用户名（可选）")
    milvus_password: str = Field(default="", description="Milvus 密码（可选）")

    # ============== CORS 跨域配置 ==============
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="允许的跨域源（逗号分隔的字符串列表）"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """将 CORS 源字符串转换为列表。

        Returns:
            list[str]: CORS 允许的源列表
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # ============== 日志配置 ==============
    log_level: str = Field(
        default="INFO",
        description="日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）"
    )

    # ============== LLM 服务配置 ==============
    llm_provider: str = Field(default="openai", description="LLM 提供商（openai, zhipuai 等）")
    llm_api_key: str = Field(default="", description="LLM API 密钥")
    llm_api_base: str | None = Field(
        default=None,
        description="自定义 API 端点 URL（例如：https://api.openai.com/v1）"
    )
    llm_model: str = Field(default="gpt-3.5-turbo", description="LLM 模型名称")
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="生成温度（0.0-2.0，越高越随机）"
    )
    llm_max_tokens: int = Field(
        default=2000,
        gt=0,
        description="最大生成 token 数"
    )
    llm_timeout: int = Field(
        default=60,
        gt=0,
        description="LLM 请求超时时间（秒）"
    )

    # ============== Embedding 服务配置 ==============
    embedding_provider: str = Field(default="zhipuai", description="Embedding 提供商")
    embedding_api_key: str = Field(default="", description="Embedding API 密钥")
    embedding_api_base: str = Field(
        default="https://open.bigmodel.cn/api/paas/v4",
        description="Embedding API 端点 URL"
    )
    embedding_model: str = Field(
        default="embedding-3",
        description="Embedding 模型名称"
    )
    embedding_dimensions: int = Field(
        default=384,
        gt=0,
        description="Embedding 向量维度（必须与模型输出维度匹配）"
    )

    # ============== Redis 配置 ==============
    redis_host: str = Field(default="localhost", description="Redis 服务器地址")
    redis_port: int = Field(default=6379, description="Redis 服务器端口")
    redis_password: str | None = Field(default=None, description="Redis 密码")
    redis_db: int = Field(default=0, description="Redis 数据库编号")

    # ============== Celery 配置 ==============
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Celery 代理 URL (Broker URL)"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1",
        description="Celery 结果后端 URL (Result Backend)"
    )



@lru_cache()
def get_settings() -> Settings:
    """获取配置单例。

    使用 lru_cache 装饰器确保配置只加载一次，提高性能。
    后续调用会返回缓存的配置实例。

    Returns:
        Settings: 应用配置实例

    Note:
        由于使用了缓存，修改 .env 文件后需要重启应用才能生效。
    """
    return Settings()
