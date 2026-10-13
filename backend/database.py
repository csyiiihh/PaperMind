
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# ============================================
# 1. 读取数据库配置
# ============================================

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_NAME = os.getenv("DB_NAME", "papermind")

IS_TESTING = (
    os.getenv("PAPERMIND_TESTING") == "1"
)

TEST_DB_NAME = "papermind_pytest_db"


if not DB_PASSWORD:
    raise RuntimeError(
        "请先设置 DB_PASSWORD 环境变量"
    )


# ============================================
# 2. 数据库环境安全检查
# ============================================

if IS_TESTING:

    if DB_NAME != TEST_DB_NAME:
        raise RuntimeError(
            "安全检查失败：pytest 环境只能使用 "
            f"{TEST_DB_NAME} 数据库"
        )

else:

    if DB_NAME == TEST_DB_NAME:
        raise RuntimeError(
            "安全检查失败：正常运行环境不允许 "
            "连接 pytest 测试数据库"
        )


# ============================================
# 3. 创建数据库连接地址
# ============================================

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host="127.0.0.1",
    port=3306,
    database=DB_NAME,
    query={
        "charset": "utf8mb4"
    },
)


# ============================================
# 4. 创建 SQLAlchemy Engine
# ============================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# ============================================
# 5. 创建数据库会话工厂
# ============================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# ============================================
# 6. ORM 模型基类
# ============================================

class Base(DeclarativeBase):
    pass
