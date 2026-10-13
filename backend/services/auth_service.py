
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from config import settings


# ============================================
# 1. 密码加密与验证
# ============================================

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    return password_hasher.verify(
        password,
        hashed_password
    )


# ============================================
# 2. JWT 配置
# ============================================

JWT_ALGORITHM = "HS256"

if not settings.JWT_SECRET_KEY:
    raise RuntimeError(
        "未配置 JWT_SECRET_KEY"
    )

if settings.JWT_EXPIRE_MINUTES <= 0:
    raise RuntimeError(
        "JWT_EXPIRE_MINUTES 必须大于 0"
    )


# ============================================
# 3. 生成 JWT
# ============================================

def create_access_token(user_id: int) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


# ============================================
# 4. 解析并验证 JWT
# ============================================

def decode_access_token(token: str) -> int:

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={
            "require": ["sub", "exp"]
        }
    )

    user_id = payload["sub"]

    if (
        not isinstance(user_id, str)
        or not user_id.isdigit()
        or int(user_id) <= 0
    ):
        raise jwt.InvalidTokenError(
            "无效的用户 ID"
        )

    return int(user_id)
