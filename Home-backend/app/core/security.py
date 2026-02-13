"""安全模块。

提供密码哈希和验证等安全相关功能。
"""

from passlib.context import CryptContext

# 密码加密上下文
# 使用 bcrypt 算法，这是目前最安全的密码哈希算法之一
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码。

    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码

    Returns:
        密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """对密码进行哈希。

    Args:
        password: 明文密码

    Returns:
        哈希后的密码
    """
    return pwd_context.hash(password)
