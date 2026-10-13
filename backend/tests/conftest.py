
import os

import pytest


# ============================================
# 1. 在导入应用前设置测试环境
# ============================================

TEST_DB_NAME = "papermind_pytest_db"

test_password = os.getenv(
    "PAPERMIND_TEST_DB_PASSWORD"
)

if not test_password:
    raise RuntimeError(
        "未配置 PAPERMIND_TEST_DB_PASSWORD，"
        "请先设置测试数据库专用密码"
    )

os.environ["PAPERMIND_TESTING"] = "1"
os.environ["DB_NAME"] = TEST_DB_NAME
os.environ["DB_USER"] = "papermind_tester"
os.environ["DB_PASSWORD"] = test_password


# ============================================
# 2. 环境配置完成后才能导入
# ============================================

from fastapi.testclient import TestClient

from database import Base, engine
import models
from main import app


# ============================================
# 3. 测试数据库安全检查
# ============================================

@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():

    if engine.url.database != TEST_DB_NAME:
        raise RuntimeError(
            "危险操作已阻止：数据库不是测试数据库"
        )

    if engine.url.username != "papermind_tester":
        raise RuntimeError(
            "测试必须使用专用数据库账号"
        )

    # 只在测试数据库中建立缺失的表
    Base.metadata.create_all(bind=engine)

    yield

    # 不使用 drop_all()
    # 避免意外清空整个测试数据库


# ============================================
# 4. FastAPI 测试客户端
# ============================================

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
