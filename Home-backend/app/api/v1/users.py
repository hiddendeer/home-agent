"""用户路由模块。

提供用户的 CRUD 操作接口，包括创建、查询、更新和删除用户。
所有密码操作均使用 bcrypt 加密存储，确保安全性。
"""

from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func

from app.infrastructure.dependencies import MySQLSessionDep
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=201, summary="创建用户")
async def create_user(
    user_data: UserCreate,
    db: MySQLSessionDep
):
    """创建新用户。

    执行流程：
    1. 检查用户名是否已存在
    2. 检查邮箱是否已存在
    3. 使用 bcrypt 加密密码
    4. 创建用户记录

    Args:
        user_data: 用户创建数据
        db: 数据库会话

    Returns:
        创建的用户信息（不包含密码）

    Raises:
        HTTPException: 用户名或邮箱已存在时返回 400 错误
    """
    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="邮箱已存在"
        )

    # 使用 bcrypt 加密密码
    # bcrypt 会自动加盐并生成哈希值，安全性很高
    from app.core.security import hash_password
    hashed_password = hash_password(user_data.password)

    # 创建用户记录
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,  # 存储加密后的密码
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/", response_model=UserListResponse, summary="获取用户列表")
async def list_users(
    db: MySQLSessionDep,
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="每页数量")] = 20,
):
    """获取用户列表（分页）。

    Args:
        db: 数据库会话
        page: 页码（从1开始）
        page_size: 每页数量

    Returns:
        用户列表响应
    """
    # 计算总数
    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar()

    # 分页查询
    offset = (page - 1) * page_size
    result = await db.execute(
        select(User)
        .offset(offset)
        .limit(page_size)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return UserListResponse(
        total=total,
        items=users,
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户详情")
async def get_user(
    user_id: int,
    db: MySQLSessionDep
):
    """根据ID获取用户详情。

    Args:
        user_id: 用户ID
        db: 数据库会话

    Returns:
        用户信息

    Raises:
        HTTPException: 用户不存在时
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: MySQLSessionDep
):
    """更新用户信息。

    支持更新邮箱、全名、密码和激活状态。
    如果提供新密码，会自动使用 bcrypt 加密。

    Args:
        user_id: 用户ID
        user_data: 用户更新数据
        db: 数据库会话

    Returns:
        更新后的用户信息

    Raises:
        HTTPException: 用户不存在时返回 404 错误
    """
    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )

    # 更新字段（只更新提供的字段）
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password" and value:
            # 密码需要加密后存储到 hashed_password 字段
            from app.core.security import hash_password
            hashed_password = hash_password(value)
            setattr(user, "hashed_password", hashed_password)
        else:
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=204, summary="删除用户")
async def delete_user(
    user_id: int,
    db: MySQLSessionDep
):
    """删除用户。

    Args:
        user_id: 用户ID
        db: 数据库会话

    Raises:
        HTTPException: 用户不存在时
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    await db.delete(user)
    await db.commit()
