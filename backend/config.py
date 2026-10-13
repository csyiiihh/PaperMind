
import os
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv


# ============================================
# 1. 定位并读取 .env 文件
# ============================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    dotenv_path=BASE_DIR / ".env",
    override=False
)


# ============================================
# 2. 集中管理应用配置
# ============================================

@dataclass(frozen=True)
class Settings:

    # MySQL
    DB_HOST: str = os.getenv(
        "DB_HOST", "127.0.0.1"
    )

    DB_PORT: int = int(
        os.getenv("DB_PORT", "3306")
    )

    DB_USER: str = os.getenv(
        "DB_USER", "root"
    )

    DB_PASSWORD: str | None = os.getenv(
        "DB_PASSWORD"
    )

    DB_NAME: str = os.getenv(
        "DB_NAME", "papermind"
    )

    # 测试环境
    IS_TESTING: bool = (
        os.getenv("PAPERMIND_TESTING") == "1"
    )

    TEST_DB_NAME: str = "papermind_pytest_db"

    # JWT
    JWT_SECRET_KEY: str | None = os.getenv(
        "JWT_SECRET_KEY"
    )

    JWT_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_EXPIRE_MINUTES", "120")
    )

    # DeepSeek
    DEEPSEEK_API_KEY: str | None = os.getenv(
        "DEEPSEEK_API_KEY"
    )

    DEEPSEEK_BASE_URL: str = os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com"
    )

    DEEPSEEK_MODEL: str = os.getenv(
        "DEEPSEEK_MODEL",
        "deepseek-flash"
    )


    # DeepSeek 请求超时时间（秒）
    DEEPSEEK_TIMEOUT: float = float(
        os.getenv("DEEPSEEK_TIMEOUT", "60")
    )

    # SDK 自动重试次数
    DEEPSEEK_MAX_RETRIES: int = int(
        os.getenv("DEEPSEEK_MAX_RETRIES", "0")
    )

    # 单次生成的最大 Token 数
    DEEPSEEK_MAX_TOKENS: int = int(
        os.getenv("DEEPSEEK_MAX_TOKENS", "8192")
    )

    # PDF
    MAX_PDF_SIZE: int = int(
        os.getenv(
            "MAX_PDF_SIZE_MB", "20"
        )
    ) * 1024 * 1024


    # PDF 上传目录
    UPLOAD_DIR: Path = (
        BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
    )

    # FAISS 索引目录
    VECTOR_STORE_DIR: Path = (
        BASE_DIR / os.getenv(
            "VECTOR_STORE_DIR",
            "vector_stores"
        )
    )

# ============================================
# 3. 创建统一配置实例
# ============================================

settings = Settings()
