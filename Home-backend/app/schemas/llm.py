"""LLM 相关的数据验证模式。"""

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    """LLM 请求模型。"""

    prompt: str = Field(..., min_length=1, max_length=4000, description="用户输入的提示词")
    system_prompt: str | None = Field(None, max_length=2000, description="系统提示词")


class LLMResponse(BaseModel):
    """LLM 响应模型。"""

    response: str = Field(..., description="LLM 生成的回复")
    model: str = Field(..., description="使用的模型名称")
