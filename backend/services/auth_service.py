import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "120")
)

if not JWT_SECRET_KEY:
    raise RuntimeError("未配置 JWT_SECRET_KEY")


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token: str) -> int:
    """验证 JWT 并返回用户 ID。"""

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["sub", "exp"]}
    )

    user_id = payload["sub"]

    # 用户 ID 必须是正整数
    if (
        not isinstance(user_id, str)
        or not user_id.isdigit()
        or int(user_id) <= 0
    ):
        raise jwt.InvalidTokenError(
            "无效的用户 ID"
        )

    return int(user_id)
