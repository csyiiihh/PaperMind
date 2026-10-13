
from unittest.mock import patch

import httpx
import pytest

from fastapi import HTTPException
from openai import APITimeoutError

from services.llm_service import generate_answer


def test_llm_timeout():

    # 构造模拟的 HTTP 请求
    request = httpx.Request(
        "POST",
        "https://api.deepseek.com/chat/completions"
    )

    # 模拟 DeepSeek 超时异常
    timeout_error = APITimeoutError(
        request=request
    )

    # 用 Mock 替代真实 API 调用
    with patch(
        "services.llm_service.client.chat.completions.create",
        side_effect=timeout_error
    ):

        with pytest.raises(HTTPException) as exc_info:
            generate_answer("测试超时")

    # 检查 FastAPI 返回的状态码
    assert exc_info.value.status_code == 504

    # 检查错误提示
    assert "超时" in exc_info.value.detail

from types import SimpleNamespace

from openai import (
    RateLimitError,
    APIConnectionError
)


# ============================================
# 1. 模拟 API 限流
# ============================================

def test_llm_rate_limit():

    request = httpx.Request(
        "POST",
        "https://api.deepseek.com/chat/completions"
    )

    response = httpx.Response(
        status_code=429,
        request=request
    )

    error = RateLimitError(
        "Rate limit exceeded",
        response=response,
        body=None
    )

    with patch(
        "services.llm_service.client.chat.completions.create",
        side_effect=error
    ):
        with pytest.raises(HTTPException) as exc_info:
            generate_answer("测试限流")

    assert exc_info.value.status_code == 503


# ============================================
# 2. 模拟网络连接失败
# ============================================

def test_llm_connection_error():

    request = httpx.Request(
        "POST",
        "https://api.deepseek.com/chat/completions"
    )

    error = APIConnectionError(
        message="Connection failed",
        request=request
    )

    with patch(
        "services.llm_service.client.chat.completions.create",
        side_effect=error
    ):
        with pytest.raises(HTTPException) as exc_info:
            generate_answer("测试连接失败")

    assert exc_info.value.status_code == 503


# ============================================
# 3. 模拟空回答
# ============================================

def test_llm_empty_answer():

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(content="")
            )
        ],
        usage=None
    )

    with patch(
        "services.llm_service.client.chat.completions.create",
        return_value=fake_response
    ):
        with pytest.raises(HTTPException) as exc_info:
            generate_answer("测试空回答")

    assert exc_info.value.status_code == 502


# ============================================
# 4. 模拟输出达到 Token 上限
# ============================================

def test_llm_token_limit():

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason="length",
                message=SimpleNamespace(
                    content="这是一段尚未完成的回答"
                )
            )
        ],
        usage=None
    )

    with patch(
        "services.llm_service.client.chat.completions.create",
        return_value=fake_response
    ):
        with pytest.raises(HTTPException) as exc_info:
            generate_answer("测试 Token 上限")

    assert exc_info.value.status_code == 502
    assert "Token" in exc_info.value.detail
