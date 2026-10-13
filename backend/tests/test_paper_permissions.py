
import uuid

import pytest

from database import SessionLocal, engine
from models import Paper, User, ChatMessage, MessageSource


# ============================================
# 1. 创建测试用户、论文、消息和来源
# ============================================

@pytest.fixture
def paper_context(client):

    # 双重安全检查
    assert engine.url.database == "papermind_pytest_db"
    assert engine.url.username == "papermind_tester"

    suffix = uuid.uuid4().hex[:12]
    paper_id = str(uuid.uuid4())

    password = "TestPassword123!"

    usernames = [
        f"pytest_a_{suffix}",
        f"pytest_b_{suffix}"
    ]

    user_ids = []

    try:
        # 创建两个测试用户
        for username in usernames:
            response = client.post(
                "/auth/register",
                json={
                    "username": username,
                    "password": password
                }
            )

            assert response.status_code == 201
            user_ids.append(response.json()["user_id"])

        # 论文属于用户 A
        with SessionLocal() as db:

            paper = Paper(
                id=paper_id,
                user_id=user_ids[0],
                filename="pytest_paper.pdf",
                file_path=f"uploads/{paper_id}.pdf",
                index_path=f"vector_stores/{paper_id}.index",
                chunks_path=f"vector_stores/{paper_id}_chunks.json"
            )

            db.add(paper)
            db.flush()

            # 创建一条聊天消息
            message = ChatMessage(
                paper_id=paper_id,
                role="assistant",
                content="这是 pytest 测试回答"
            )

            db.add(message)
            db.flush()

            message_id = message.id

            # 创建引用来源
            source = MessageSource(
                message_id=message_id,
                chunk_id=0,
                page=1,
                score=0.95,
                text="这是 pytest 测试引用来源"
            )

            db.add(source)
            db.flush()

            source_id = source.id

            db.commit()

        # 分别登录并获取 JWT
        tokens = []

        for username in usernames:
            response = client.post(
                "/auth/login",
                json={
                    "username": username,
                    "password": password
                }
            )

            assert response.status_code == 200
            tokens.append(response.json()["access_token"])

        yield {
            "paper_id": paper_id,
            "message_id": message_id,
            "source_id": source_id,
            "user_ids": user_ids,
            "headers_a": {
                "Authorization": f"Bearer {tokens[0]}"
            },
            "headers_b": {
                "Authorization": f"Bearer {tokens[1]}"
            }
        }

    finally:
        # 测试结束后清理自己创建的数据
        with SessionLocal() as db:

            paper = db.get(Paper, paper_id)

            if paper:
                db.delete(paper)
                db.commit()

            for user_id in user_ids:
                user = db.get(User, user_id)

                if user:
                    db.delete(user)

            db.commit()


# ============================================
# 2. 用户 A 能读取自己的聊天历史
# ============================================

def test_owner_can_read_messages(client, paper_context):

    paper_id = paper_context["paper_id"]

    response = client.get(
        f"/papers/{paper_id}/messages",
        headers=paper_context["headers_a"]
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["messages"]) == 1

    message = data["messages"][0]

    assert message["content"] == "这是 pytest 测试回答"
    assert len(message["sources"]) == 1
    assert message["sources"][0]["page"] == 1


# ============================================
# 3. 用户 B 无法操作用户 A 的论文
# ============================================

def test_other_user_cannot_access(client, paper_context):

    paper_id = paper_context["paper_id"]
    headers = paper_context["headers_b"]

    # 不允许读取聊天历史
    response = client.get(
        f"/papers/{paper_id}/messages",
        headers=headers
    )
    assert response.status_code == 404

    # 不允许搜索
    response = client.post(
        f"/papers/{paper_id}/search",
        json={
            "query": "测试检索",
            "top_k": 3
        },
        headers=headers
    )
    assert response.status_code == 404

    # 不允许提问
    response = client.post(
        f"/papers/{paper_id}/ask",
        json={
            "question": "测试提问",
            "top_k": 3
        },
        headers=headers
    )
    assert response.status_code == 404

    # 不允许删除
    response = client.delete(
        f"/papers/{paper_id}",
        headers=headers
    )
    assert response.status_code == 404

    # 确认越权操作没有删除论文
    with SessionLocal() as db:
        assert db.get(Paper, paper_id) is not None


# ============================================
# 4. 删除论文后，消息和来源级联删除
# ============================================

def test_paper_cascade_delete(client, paper_context):

    paper_id = paper_context["paper_id"]
    message_id = paper_context["message_id"]
    source_id = paper_context["source_id"]

    # 所有者 A 删除论文
    response = client.delete(
        f"/papers/{paper_id}",
        headers=paper_context["headers_a"]
    )

    assert response.status_code == 200

    # 检查实际 MySQL 数据
    with SessionLocal() as db:

        # 论文已删除
        assert db.get(Paper, paper_id) is None

        # 关联的聊天消息已删除
        assert db.get(ChatMessage, message_id) is None

        # 引用来源也已删除
        assert db.get(MessageSource, source_id) is None
