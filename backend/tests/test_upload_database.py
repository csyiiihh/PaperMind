
import uuid
from pathlib import Path

import numpy as np
import pytest

import main

from database import SessionLocal, engine
from models import User, Paper
from sqlalchemy import select
from services.auth_dependency import get_current_user


# ============================================
# 1. 模拟 FAISS 向量存储
# ============================================

class FakeVectorStore:

    def __init__(self, dimension):
        self.dimension = dimension

    def add(self, embeddings, chunks):
        self.embeddings = embeddings
        self.chunks = chunks

    def save(self, index_path, chunks_path):
        # 模拟成功生成索引和 chunks 文件
        Path(index_path).write_bytes(b"fake-faiss-index")

        Path(chunks_path).write_text(
            "[]",
            encoding="utf-8"
        )


# ============================================
# 2. 创建独立测试环境
# ============================================

@pytest.fixture
def upload_db_context(tmp_path, monkeypatch):

    # 防止误操作正式数据库
    assert engine.url.database == "papermind_pytest_db"
    assert engine.url.username == "papermind_tester"

    upload_dir = tmp_path / "uploads"
    vector_dir = tmp_path / "vector_stores"

    upload_dir.mkdir()
    vector_dir.mkdir()

    monkeypatch.setattr(main, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(main, "VECTOR_STORE_DIR", vector_dir)

    # 模拟 PDF 解析
    monkeypatch.setattr(
        main,
        "extract_pages_from_pdf",
        lambda path: ["测试论文页面"]
    )

    # 模拟文本分块
    monkeypatch.setattr(
        main,
        "split_pages",
        lambda pages: [
            {
                "chunk_id": 0,
                "page": 1,
                "text": "这是一段测试论文内容"
            }
        ]
    )

    # 模拟 Embedding
    monkeypatch.setattr(
        main,
        "encode_texts",
        lambda texts: np.array(
            [[0.1, 0.2, 0.3]],
            dtype=np.float32
        )
    )

    # 替换真正的 FAISS 操作
    monkeypatch.setattr(
        main,
        "VectorStore",
        FakeVectorStore
    )

    # 创建一个真实的测试数据库用户
    username = "pytest_upload_" + uuid.uuid4().hex[:12]

    with SessionLocal() as db:
        user = User(
            username=username,
            password_hash="test-only-not-used"
        )

        db.add(user)
        db.commit()
        user_id = user.id

    # 保留原有的认证依赖配置
    original_overrides = main.app.dependency_overrides.copy()

    main.app.dependency_overrides[get_current_user] = lambda: {
        "id": user_id,
        "username": username
    }

    try:
        yield {
            "user_id": user_id,
            "upload_dir": upload_dir,
            "vector_dir": vector_dir
        }

    finally:
        # 恢复认证依赖
        main.app.dependency_overrides.clear()
        main.app.dependency_overrides.update(
            original_overrides
        )

        # 清理本轮创建的数据库记录
        with SessionLocal() as db:

            papers = db.scalars(
                select(Paper).where(
                    Paper.user_id == user_id
                )
            ).all()

            for paper in papers:
                db.delete(paper)

            db.commit()

            user = db.get(User, user_id)

            if user:
                db.delete(user)
                db.commit()


# ============================================
# 3. 测试上传成功并保存 MySQL
# ============================================

def test_upload_success(client, upload_db_context):

    response = client.post(
        "/papers/upload",
        files={
            "file": (
                "pytest_success.pdf",
                b"%PDF-1.4\nmock content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 200, response.text

    data = response.json()

    paper_id = data["paper_id"]

    assert data["filename"] == "pytest_success.pdf"
    assert data["chunk_count"] == 1

    # 确认 MySQL 已保存论文
    with SessionLocal() as db:
        paper = db.get(Paper, paper_id)

        assert paper is not None
        assert paper.user_id == upload_db_context["user_id"]
        assert paper.filename == "pytest_success.pdf"

    # 确认文件已创建
    upload_dir = upload_db_context["upload_dir"]
    vector_dir = upload_db_context["vector_dir"]

    assert (upload_dir / f"{paper_id}.pdf").exists()
    assert (vector_dir / f"{paper_id}.index").exists()
    assert (vector_dir / f"{paper_id}_chunks.json").exists()


# ============================================
# 4. 测试 MySQL 保存失败后清理文件
# ============================================

def test_upload_database_failure(
    client,
    upload_db_context
):

    # 故意使用不存在的用户 ID
    # 触发 MySQL 外键约束错误
    main.app.dependency_overrides[get_current_user] = lambda: {
        "id": -1,
        "username": "invalid_test_user"
    }

    filename = f"pytest_fail_{uuid.uuid4().hex}.pdf"

    response = client.post(
        "/papers/upload",
        files={
            "file": (
                filename,
                b"%PDF-1.4\nmock content",
                "application/pdf"
            )
        }
    )

    # MySQL 插入失败，后端返回 500
    assert response.status_code == 500, response.text

    # 确认测试数据库中没有保存该论文
    with SessionLocal() as db:
        paper = db.scalar(
            select(Paper).where(
                Paper.filename == filename
            )
        )

        assert paper is None

    # 确认 PDF 和 FAISS 文件全部清理
    assert list(
        upload_db_context["upload_dir"].iterdir()
    ) == []

    assert list(
        upload_db_context["vector_dir"].iterdir()
    ) == []
