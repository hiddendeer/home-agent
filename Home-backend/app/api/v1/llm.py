"""LLM 路由模块。"""

from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends

from app.infrastructure.dependencies import LLMServiceDep
from app.schemas.llm import LLMRequest, LLMResponse

router = APIRouter()


@router.post(
    "/generate",
    response_model=LLMResponse,
    status_code=200,
    summary="生成文本",
    description="调用 LLM 生成文本回复"
)
async def generate_text(
    request: LLMRequest,
    llm_service: LLMServiceDep
):
    """调用 LLM 生成文本。

    Args:
        request: LLM 请求数据
        llm_service: LLM 服务依赖

    Returns:
        LLM 生成的回复

    Raises:
        HTTPException: LLM 调用失败时
    """
    try:
        response = await llm_service.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt
        )

        return LLMResponse(
            response=response,
            model=llm_service.settings.llm_model
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM 调用失败: {str(e)}"
        )
