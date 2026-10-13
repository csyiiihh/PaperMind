
import jwt

from uuid import UUID
from models import Paper

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import SessionLocal
from models import User
from services.auth_service import decode_access_token


security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    auth_error = HTTPException(
        status_code=401,
        detail="登录已失效，请重新登录",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if credentials is None:
        raise auth_error

    try:
        user_id = decode_access_token(
            credentials.credentials
        )
    except jwt.InvalidTokenError:
        raise auth_error

    with SessionLocal() as db:
        user = db.get(User, user_id)

        if user is None:
            raise auth_error

        return {
            "id": user.id,
            "username": user.username
        }

def get_owned_paper(paper_id: UUID, user_id: int):
    """检查论文是否属于指定用户。"""

    with SessionLocal() as db:
        paper = db.get(Paper, str(paper_id))

        if paper is None or paper.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="论文不存在"
            )

        return paper