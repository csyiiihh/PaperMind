
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import settings


# ============================================
# 1. 检查数据库密码
# ============================================

if not settings.DB_PASSWORD:
    raise RuntimeError(
        "请先设置 DB_PASSWORD 环境变量"
    )


# ============================================
# 2. 数据库环境安全检查
# ============================================

if settings.IS_TESTING:

    # pytest 只能连接专用测试数据库
    if settings.DB_NAME != settings.TEST_DB_NAME:
        raise RuntimeError(
            "安全检查失败：pytest 环境只能使用 "
            f"{settings.TEST_DB_NAME} 数据库"
        )

    # pytest 必须使用专用数据库用户
    if settings.DB_USER != "papermind_tester":
        raise RuntimeError(
            "安全检查失败：pytest 必须使用专用数据库用户"
        )

else:

    # 正常运行禁止误连 pytest 测试库
    if settings.DB_NAME == settings.TEST_DB_NAME:
        raise RuntimeError(
            "安全检查失败：正常运行环境不允许"
            "连接 pytest 测试数据库"
        )


# ============================================
# 3. 创建数据库连接地址
# ============================================

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",

    username=settings.DB_USER,
    password=settings.DB_PASSWORD,

    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,

    query={
        "charset": "utf8mb4"
    }
)


# ============================================
# 4. 创建 SQLAlchemy Engine
# ============================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================
# 5. 创建数据库 Session 工厂
# ============================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ============================================
# 6. ORM 模型基类
# ============================================

class Base(DeclarativeBase):
    pass
