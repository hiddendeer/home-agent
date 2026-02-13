"""LLM 服务模块。"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.infrastructure.config import Settings, get_settings


class LLMService:
    """LLM 服务类,封装 LangChain 的 LLM 调用。"""

    def __init__(self, settings: Settings | None = None) -> None:
        """初始化 LLM 服务。

        Args:
            settings: 应用配置,如果不提供则使用默认配置
        """
        self.settings = settings or get_settings()
        self.llm = self._create_llm()

    def _create_llm(self) -> ChatOpenAI:
        """创建 LLM 实例。

        Returns:
            ChatOpenAI 实例
        """
        return ChatOpenAI(
            model=self.settings.llm_model,
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_api_base,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
            timeout=self.settings.llm_timeout,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> str:
        """生成文本回复。

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词(可选)

        Returns:
            LLM 生成的回复文本

        Raises:
            Exception: LLM 调用失败时
        """
        messages: list[HumanMessage | SystemMessage | AIMessage] = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        messages.append(HumanMessage(content=prompt))

        response = await self.llm.ainvoke(messages)
        return response.content
