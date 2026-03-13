# src/agents/transport_agent/server.py
"""
Transport Agent A2A Server.
"""
import logging
import os
from contextlib import asynccontextmanager

import httpx
from src.shared.a2a.types import AgentCapabilities, AgentCard, AgentSkill
from starlette.applications import Starlette
from starlette.routing import Route

from src.shared.a2a.base_server import BaseA2AServer, create_health_endpoint
from .agent import TransportAgent

logger = logging.getLogger(__name__)

AGENT_NAME = "交通查询助手"
AGENT_VERSION = "1.0.0"


class TransportA2AServer(BaseA2AServer):
    """交通 Agent A2A 服务器"""

    def build_agent_card(self) -> AgentCard:
        capabilities = AgentCapabilities(streaming=True)

        skill = AgentSkill(
            id="search_transport",
            name="查询交通",
            description=(
                "查询火车票、机票等交通信息，支持高铁、动车、航班查询。"
                "提供价格、时刻表、余票等信息。"
            ),
            tags=["transport", "交通", "火车", "高铁", "机票", "航班"],
            examples=[
                "北京到上海的高铁",
                "明天杭州到南京的火车",
                "下周去成都的机票",
            ],
        )

        return AgentCard(
            name=AGENT_NAME,
            description="提供火车票、机票查询服务，帮助用户找到最合适的交通方式。",
            url=f"http://{self.host}:{self.port}/",
            version=AGENT_VERSION,
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities=capabilities,
            skills=[skill],
        )

    def build_agent_executor(self) -> TransportAgent:
        return TransportAgent()


_server: TransportA2AServer | None = None


@asynccontextmanager
async def lifespan(app: Starlette):
    global _server

    logger.info("正在启动交通 Agent...")

    host = os.getenv("SERVER_URL", "localhost")
    port = int(os.getenv("TRANSPORT_AGENT_PORT", "10009"))

    httpx_client = httpx.AsyncClient(timeout=30)
    _server = TransportA2AServer(httpx_client, host=host, port=port)

    app.router.routes.extend(list(_server.a2a_app().routes))

    app.state.httpx_client = httpx_client
    app.state.server = _server

    logger.info(f"交通 Agent 已启动: http://{host}:{port}")

    try:
        yield
    finally:
        logger.info("正在关闭交通 Agent...")
        await httpx_client.aclose()


def create_app() -> Starlette:
    health_endpoint = create_health_endpoint(AGENT_NAME, AGENT_VERSION)

    app = Starlette(
        routes=[
            Route("/health", health_endpoint, methods=["GET"]),
        ],
        lifespan=lifespan,
    )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("TRANSPORT_AGENT_PORT", "10009"))
    uvicorn.run(app, host="0.0.0.0", port=port)