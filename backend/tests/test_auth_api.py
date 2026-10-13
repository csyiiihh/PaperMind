
import uuid

import pytest
from sqlalchemy import select

from database import SessionLocal
from models import User


# ============================================
# 1. 创建临时测试用户
# ============================================

@pytest.fixture
def registered_user(client):

    username = "pytest_" + uuid.uuid4().hex[:12]
    password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 201

    try:
        yield {
            "username": username,
            "password": password,
            "user_id": response.json()["user_id"]
        }

    finally:
        # 测试结束后清理临时用户
        with SessionLocal() as db:
            user = db.scalar(
                select(User).where(
                    User.username == username
                )
            )

            if user:
                db.delete(user)
                db.commit()


# ============================================
# 2. 测试正常注册
# ============================================

def test_register_success(registered_user):

    assert registered_user["user_id"] > 0


# ============================================
# 3. 测试重复用户名
# ============================================

def test_register_duplicate(client, registered_user):

    response = client.post(
        "/auth/register",
        json={
            "username": registered_user["username"],
            "password": "AnotherPassword123!"
        }
    )

    assert response.status_code == 409
    assert "用户名已存在" in response.json()["detail"]


# ============================================
# 4. 测试正确密码登录
# ============================================

def test_login_success(client, registered_user):

    response = client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


# ============================================
# 5. 测试错误密码
# ============================================

def test_login_wrong_password(client, registered_user):

    response = client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401


# ============================================
# 6. 测试无效或缺失 JWT
# ============================================

def test_invalid_token(client):

    # 没有 JWT
    response = client.get("/auth/me")
    assert response.status_code == 401

    # 无效 JWT
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


# ============================================
# 7. 测试有效 JWT
# ============================================

def test_valid_token(client, registered_user):

    login_response = client.post(
        "/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    user_info = response.json()

    assert user_info["id"] == registered_user["user_id"]
    assert user_info["username"] == registered_user["username"]
