
import pytest

from pydantic import ValidationError

from main import (
    SearchRequest,
    AskRequest,
    RegisterRequest
)


# 1. 正常搜索参数
def test_valid_search_request():
    request = SearchRequest(
        query="ResNet 为什么使用残差连接？",
        top_k=3
    )

    assert request.top_k == 3


# 2. top_k 不能小于 1
def test_invalid_top_k_zero():
    with pytest.raises(ValidationError):
        SearchRequest(
            query="ResNet",
            top_k=0
        )


# 3. top_k 不能超过 10
def test_invalid_top_k_too_large():
    with pytest.raises(ValidationError):
        SearchRequest(
            query="ResNet",
            top_k=11
        )


# 4. AI 问题不能为空
def test_empty_question():
    with pytest.raises(ValidationError):
        AskRequest(
            question="",
            top_k=3
        )


# 5. 注册密码至少 8 位
def test_short_password():
    with pytest.raises(ValidationError):
        RegisterRequest(
            username="test_user",
            password="1234567"
        )


# 6. 正常注册参数
def test_valid_register():
    request = RegisterRequest(
        username="test_user",
        password="12345678"
    )

    assert request.username == "test_user"
