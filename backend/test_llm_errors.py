
from unittest.mock import patch

from fastapi import HTTPException
from openai import APITimeoutError

from services.llm_service import generate_answer


def fake_timeout(*args, **kwargs):
    raise APITimeoutError(request=None)


with patch(
    "services.llm_service.client.chat.completions.create",
    side_effect=fake_timeout
):
    try:
        generate_answer("测试超时处理")
    except HTTPException as error:
        print("HTTP 状态码:", error.status_code)
        print("错误信息:", error.detail)
