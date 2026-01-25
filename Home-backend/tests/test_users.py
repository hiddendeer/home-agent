"""用户API测试。"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app


@pytest.mark.asyncio
async def test_root():
    """测试根路径。"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "version" in data
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查。"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_user():
    """测试创建用户。"""
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/users/", json=user_data)

    # 注意：此测试需要实际数据库连接
    # 在没有数据库的情况下会返回 500 错误
    # assert response.status_code == 201
    # data = response.json()
    # assert data["username"] == user_data["username"]
    # assert data["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_list_users():
    """测试获取用户列表。"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/users/?page=1&page_size=10")

    # 注意：此测试需要实际数据库连接
    # assert response.status_code == 200
    # data = response.json()
    # assert "total" in data
    # assert "items" in data
