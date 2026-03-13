# src/shared/a2a/base_agent.py
"""
Base Agent Framework implementation.
Provides common functionality for all agents using DashScope LLM.
"""
from __future__ import annotations

import json
import logging
import os
from abc import abstractmethod
from pathlib import Path
from typing import Any, AsyncGenerator, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class BaseAgentFrameworkAgent:
    """
    Agent 框架基类

    所有 Agent 都继承此类，实现：
    - get_agent_name(): 返回 Agent 名称
    - get_prompt_name(): 返回提示词文件名
    - get_response_format(): 返回响应格式
    - parse_response(): 解析响应
    """

    def __init__(self):
        self.llm_client = None
        self.model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
        self._init_llm_client()
        self._prompt_cache: dict[str, str] = {}

    def _init_llm_client(self):
        """初始化 LLM 客户端"""
        try:
            import dashscope
            from dashscope import Generation

            api_key = os.getenv("DASHSCOPE_API_KEY")
            if api_key:
                dashscope.api_key = api_key
            self.llm_client = Generation
            logger.info(f"Initialized DashScope LLM client with model: {self.model}")
        except ImportError:
            logger.warning("DashScope not installed, using mock responses")
            self.llm_client = None

    @abstractmethod
    def get_agent_name(self) -> str:
        """返回 Agent 名称"""
        raise NotImplementedError

    @abstractmethod
    def get_prompt_name(self) -> str:
        """返回提示词文件名（不含扩展名）"""
        raise NotImplementedError

    def get_response_format(self) -> Any:
        """返回响应格式（Pydantic 模型类）"""
        return None

    def get_tools(self) -> list[Any]:
        """返回工具列表（可被子类覆盖）"""
        return []

    def load_prompt(self) -> str:
        """加载系统提示词"""
        prompt_name = self.get_prompt_name()
        if prompt_name in self._prompt_cache:
            return self._prompt_cache[prompt_name]

        # 查找提示词文件
        prompt_paths = [
            Path(__file__).parent.parent.parent / "prompts" / f"{prompt_name}.txt",
            Path(__file__).parent.parent.parent / "prompts" / f"{prompt_name}.md",
        ]

        for path in prompt_paths:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                self._prompt_cache[prompt_name] = content
                return content

        # 返回默认提示词
        default_prompt = f"你是{self.get_agent_name()}，一个专业的旅行助手。"
        self._prompt_cache[prompt_name] = default_prompt
        return default_prompt

    async def invoke(
        self,
        user_input: str,
        session_id: str,
        history: Optional[list[dict]] = None,
        history_seq: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        同步调用 Agent

        Args:
            user_input: 用户输入
            session_id: 会话ID
            history: 对话历史
            history_seq: 历史序列号

        Returns:
            响应字典，包含 is_task_complete, require_user_input, content
        """
        system_prompt = self.load_prompt()

        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_input})

        # 调用 LLM
        try:
            if self.llm_client:
                response = await self._call_llm(messages)
            else:
                response = self._mock_response(user_input)

            return self.parse_response(response)

        except Exception as e:
            logger.error(f"Agent invoke failed: {e}", exc_info=True)
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"抱歉，处理请求时出现错误：{str(e)}",
            }

    async def stream(
        self,
        user_input: str,
        session_id: str,
        history: Optional[list[dict]] = None,
        history_seq: Optional[int] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        流式调用 Agent

        Yields:
            响应块
        """
        # 目前实现为同步调用后一次性返回
        result = await self.invoke(user_input, session_id, history, history_seq)
        yield result

    async def _call_llm(self, messages: list[dict]) -> str:
        """调用 LLM"""
        import asyncio

        def _sync_call():
            response = self.llm_client.call(
                model=self.model,
                messages=messages,
                result_format="message",
            )
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                raise Exception(f"LLM call failed: {response.message}")

        # 在线程池中执行同步调用
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_call)

    def _mock_response(self, user_input: str) -> str:
        """Mock 响应（用于测试）"""
        return json.dumps({
            "response": f"收到您的请求：{user_input[:50]}... 我是{self.get_agent_name()}，正在为您处理。"
        })

    @abstractmethod
    def parse_response(self, message: Any) -> dict[str, Any]:
        """
        解析 LLM 响应

        Args:
            message: LLM 返回的消息

        Returns:
            响应字典，包含：
            - is_task_complete: bool
            - require_user_input: bool
            - content: str
        """
        raise NotImplementedError