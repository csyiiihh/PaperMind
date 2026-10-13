
import pytest

import main
from services.auth_dependency import get_current_user


# ============================================
# 1. 测试夹具：隔离文件目录和认证
# ============================================

@pytest.fixture
def upload_context(tmp_path, monkeypatch):

    upload_dir = tmp_path / "uploads"
    vector_dir = tmp_path / "vector_stores"

    upload_dir.mkdir()
    vector_dir.mkdir()

    # 将上传和索引路径替换为临时目录
    monkeypatch.setattr(
        main,
        "UPLOAD_DIR",
        upload_dir
    )

    monkeypatch.setattr(
        main,
        "VECTOR_STORE_DIR",
        vector_dir
    )

    # 模拟已经通过 JWT 验证的用户
    # 本轮只测试失败路径，不执行数据库写入
    original_overrides = (
        main.app.dependency_overrides.copy()
    )

    main.app.dependency_overrides[
        get_current_user
    ] = lambda: {
        "id": -1,
        "username": "pytest_upload"
    }

    yield {
        "upload_dir": upload_dir,
        "vector_dir": vector_dir
    }

    # 恢复原有依赖配置
    main.app.dependency_overrides.clear()
    main.app.dependency_overrides.update(
        original_overrides
    )


def assert_no_remaining_files(context):
    """确认临时目录中没有残留文件。"""

    assert list(
        context["upload_dir"].iterdir()
    ) == []

    assert list(
        context["vector_dir"].iterdir()
    ) == []


# ============================================
# 2. 伪造 PDF：返回 400
# ============================================

def test_fake_pdf(client, upload_context):

    response = client.post(
        "/papers/upload",
        files={
            "file": (
                "fake.pdf",
                b"this is not a PDF",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400

    assert_no_remaining_files(upload_context)


# ============================================
# 3. 超出大小限制：返回 413
# ============================================

def test_pdf_too_large(
    client,
    upload_context,
    monkeypatch
):

    # 测试时将上限缩小为 1 KB
    monkeypatch.setattr(
        main,
        "MAX_PDF_SIZE",
        1024
    )

    fake_content = (
        b"%PDF-" + b"A" * 2048
    )

    response = client.post(
        "/papers/upload",
        files={
            "file": (
                "large.pdf",
                fake_content,
                "application/pdf"
            )
        }
    )

    assert response.status_code == 413

    assert_no_remaining_files(upload_context)


# ============================================
# 4. PDF 解析失败：返回 422
# ============================================

def test_pdf_parse_failure(
    client,
    upload_context,
    monkeypatch
):

    def fake_extract(*args, **kwargs):
        raise ValueError("模拟 PDF 解析失败")

    monkeypatch.setattr(
        main,
        "extract_pages_from_pdf",
        fake_extract
    )

    response = client.post(
        "/papers/upload",
        files={
            "file": (
                "broken.pdf",
                b"%PDF-1.4\nfake content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 422

    assert_no_remaining_files(upload_context)


# ============================================
# 5. Embedding 失败：返回 500
# ============================================

def test_embedding_failure(
    client,
    upload_context,
    monkeypatch
):

    # 模拟 PDF 解析成功
    monkeypatch.setattr(
        main,
        "extract_pages_from_pdf",
        lambda path: ["模拟的 PDF 页面"]
    )

    # 模拟文本分块成功
    monkeypatch.setattr(
        main,
        "split_pages",
        lambda pages: [
            {
                "chunk_id": 0,
                "page": 1,
                "text": "用于测试的论文片段"
            }
        ]
    )

    # 模拟 Embedding 服务故障
    def fake_embedding(*args, **kwargs):
        raise RuntimeError(
            "模拟 Embedding 生成失败"
        )

    monkeypatch.setattr(
        main,
        "encode_texts",
        fake_embedding
    )

    response = client.post(
        "/papers/upload",
        files={
            "file": (
                "embedding_error.pdf",
                b"%PDF-1.4\nfake content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 500

    assert_no_remaining_files(upload_context)
