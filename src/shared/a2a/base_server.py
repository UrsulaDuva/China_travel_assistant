# src/shared/a2a/base_server.py
"""
Base A2A Server implementation.
Provides common functionality for all A2A agents.
"""
from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from .types import AgentCard, AgentCapabilities, AgentSkill
from ..models import HealthResponse, HealthStatus

logger = logging.getLogger(__name__)


class BaseA2AServer:
    """
    A2A Server 基础类

    所有 Agent 服务都继承此类，实现：
    - build_agent_card(): 返回 Agent 卡片
    - build_agent_executor(): 返回 Agent 执行器
    """

    def __init__(
        self,
        httpx_client: httpx.AsyncClient,
        host: str = "localhost",
        port: int = 10000,
    ):
        self.httpx_client = httpx_client
        self.host = host
        self.port = port
        self._agent_executor = None

    @abstractmethod
    def build_agent_card(self) -> AgentCard:
        """构建 Agent 卡片，子类必须实现"""
        raise NotImplementedError

    @abstractmethod
    def build_agent_executor(self) -> Any:
        """构建 Agent 执行器，子类必须实现"""
        raise NotImplementedError

    def get_agent_executor(self) -> Any:
        """获取 Agent 执行器（懒加载）"""
        if self._agent_executor is None:
            self._agent_executor = self.build_agent_executor()
        return self._agent_executor

    async def handle_a2a_request(self, request: Request) -> JSONResponse:
        """
        处理 A2A 协议请求

        支持：
        - tasks/send: 同步任务
        - tasks/sendSubscribe: 流式任务
        """
        try:
            body = await request.json()
            executor = self.get_agent_executor()

            # 解析 A2A 请求
            method = body.get("method", "tasks/send")
            params = body.get("params", {})

            # 提取消息内容
            message = params.get("message", {})
            text_content = self._extract_text(message)
            session_id = params.get("sessionId", "default")

            if method == "tasks/sendSubscribe":
                # 流式响应
                return await self._handle_streaming(executor, text_content, session_id, body)
            else:
                # 同步响应
                return await self._handle_sync(executor, text_content, session_id, body)

        except Exception as e:
            logger.error(f"A2A request failed: {e}", exc_info=True)
            return JSONResponse(
                {"error": {"code": -32603, "message": str(e)}},
                status_code=500,
            )

    async def _handle_sync(
        self,
        executor: Any,
        text_content: str,
        session_id: str,
        request_body: dict,
    ) -> JSONResponse:
        """处理同步请求"""
        result = await executor.invoke(text_content, session_id)

        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {
                "status": {"state": "completed"},
                "artifacts": [{
                    "name": "result",
                    "parts": [{"kind": "text", "text": result.get("content", "")}]
                }]
            },
            "id": request_body.get("id", 1)
        })

    async def _handle_streaming(
        self,
        executor: Any,
        text_content: str,
        session_id: str,
        request_body: dict,
    ) -> StreamingResponse:
        """处理流式请求"""

        async def event_generator():
            async for chunk in executor.stream(text_content, session_id):
                yield f"data: {chunk}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
        )

    def _extract_text(self, message: dict) -> str:
        """从 A2A 消息中提取文本内容"""
        parts = message.get("parts", [])
        for part in parts:
            if part.get("kind") == "text":
                return part.get("text", "")
        return ""

    async def get_agent_card(self, request: Request) -> JSONResponse:
        """返回 Agent 卡片"""
        card = self.build_agent_card()
        return JSONResponse(card.model_dump())

    def a2a_app(self) -> Starlette:
        """创建 A2A 应用"""
        routes = [
            Route("/", self.handle_a2a_request, methods=["POST"]),
            Route("/.well-known/agent-card.json", self.get_agent_card, methods=["GET"]),
        ]
        return Starlette(routes=routes)


def create_health_endpoint(agent_name: str, version: str):
    """创建健康检查端点"""
    async def health_check(request: Request) -> JSONResponse:
        response = HealthResponse(
            status=HealthStatus.HEALTHY,
            agent_name=agent_name,
            version=version,
        )
        return JSONResponse(response.model_dump())
    return health_check