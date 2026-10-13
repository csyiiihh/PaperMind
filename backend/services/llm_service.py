
import os
import logging

from dotenv import load_dotenv
from fastapi import HTTPException

from openai import (
    OpenAI,
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    AuthenticationError,
    APIStatusError,
    APIError,
)


# ============================================
# 1. 加载配置
# ============================================

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("未配置 DEEPSEEK_API_KEY")

base_url = os.getenv(
    "DEEPSEEK_BASE_URL",
    "https://api.deepseek.com"
)

model_name = os.getenv(
    "DEEPSEEK_MODEL",
    "deepseek-flash"
)


# ============================================
# 2. 创建 DeepSeek 客户端
# ============================================

client = OpenAI(
    api_key=api_key,
    base_url=base_url,

    # 单次请求最长等待 60 秒
    timeout=60.0,

    # 暂时关闭 SDK 自动重试
    # 防止重复调用导致额外费用或等待时间过长
    max_retries=0
)


# ============================================
# 3. 调用大模型生成回答
# ============================================

def generate_answer(question: str) -> str:

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一名专业的科研论文助手。"
                        "请根据提供的论文内容，"
                        "使用准确、清晰的中文回答。"
                        "不要编造论文中不存在的信息。"
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            stream=False,
            max_tokens=8192
        )

    # ========================================
    # 4. API 请求异常处理
    # ========================================

    except APITimeoutError as error:

        logger.warning("DeepSeek 请求超时")

        raise HTTPException(
            status_code=504,
            detail="AI 服务响应超时，请稍后重试"
        ) from error

    except RateLimitError as error:

        logger.warning("DeepSeek API 触发限流")

        raise HTTPException(
            status_code=503,
            detail="AI 服务请求过于频繁，请稍后再试"
        ) from error

    except AuthenticationError as error:

        logger.error("DeepSeek API 身份验证失败")

        raise HTTPException(
            status_code=502,
            detail="AI 服务配置异常，请联系管理员"
        ) from error

    except APIConnectionError as error:

        logger.warning("无法连接 DeepSeek 服务")

        raise HTTPException(
            status_code=503,
            detail="暂时无法连接 AI 服务，请稍后重试"
        ) from error

    except APIStatusError as error:

        logger.error(
            "DeepSeek 返回错误状态码：%s",
            error.status_code
        )

        raise HTTPException(
            status_code=502,
            detail="AI 服务调用失败，请稍后重试"
        ) from error

    except APIError as error:

        logger.error(
            "DeepSeek SDK 错误：%s",
            type(error).__name__
        )

        raise HTTPException(
            status_code=502,
            detail="AI 服务发生异常，请稍后重试"
        ) from error

    # ========================================
    # 5. 检查响应结构
    # ========================================

    if not response.choices:
        logger.error("DeepSeek 返回空 choices")

        raise HTTPException(
            status_code=502,
            detail="AI 服务没有返回回答结果"
        )

    choice = response.choices[0]

    finish_reason = choice.finish_reason

    answer = choice.message.content or ""

    # ========================================
    # 6. 记录调试信息
    # ========================================

    logger.info(
        "DeepSeek 请求完成 model=%s finish_reason=%s",
        model_name,
        finish_reason
    )

    if response.usage:
        logger.info(
            "Token 使用情况：prompt=%s completion=%s",
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )

        details = response.usage.completion_tokens_details

        if details:
            logger.info(
                "Reasoning tokens=%s",
                details.reasoning_tokens
            )

    logger.info(
        "AI 回答字符数：%s",
        len(answer)
    )

    # ========================================
    # 7. 检查回答是否完整
    # ========================================

    if finish_reason == "length":

        logger.warning(
            "DeepSeek 输出达到 Token 限制，回答可能被截断"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "AI 回答达到 Token 上限，"
                "结果可能不完整，请缩小提问范围后重试"
            )
        )

    # ========================================
    # 8. 检查回答是否为空
    # ========================================

    if not answer.strip():

        logger.error(
            "DeepSeek 返回空回答，finish_reason=%s",
            finish_reason
        )

        raise HTTPException(
            status_code=502,
            detail="AI 未生成有效回答，请稍后重试"
        )

    # ========================================
    # 9. 返回正常回答
    # ========================================

    return answer.strip()
