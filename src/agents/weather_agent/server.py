# src/agents/weather_agent/server.py
"""
Weather Agent A2A Server.
"""
import logging
import os
from contextlib import asynccontextmanager

import httpx
from src.shared.a2a.types import AgentCapabilities, AgentCard, AgentSkill
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from src.shared.a2a.base_server import BaseA2AServer, create_health_endpoint
from .agent import WeatherAgent

logger = logging.getLogger(__name__)

AGENT_NAME = "天气查询助手"
AGENT_VERSION = "1.0.0"


class WeatherA2AServer(BaseA2AServer):
    """天气 Agent A2A 服务器"""

    def build_agent_card(self) -> AgentCard:
        """构建 Agent 卡片"""
        capabilities = AgentCapabilities(streaming=True)

        skill = AgentSkill(
            id="query_weather",
            name="查询天气",
            description=(
                "查询指定城市的天气情况，包括实时天气、多日预报、穿衣建议等。"
                "支持全国主要城市的天气查询。"
            ),
            tags=["weather", "天气", "预报", "穿衣"],
            examples=[
                "北京今天天气怎么样",
                "上海未来三天天气预报",
                "杭州需要带伞吗",
                "成都穿什么衣服",
            ],
        )

        return AgentCard(
            name=AGENT_NAME,
            description="提供全国主要城市的天气查询服务，包括实时天气、预报和穿衣建议。",
            url=f"http://{self.host}:{self.port}/",
            version=AGENT_VERSION,
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities=capabilities,
            skills=[skill],
        )

    def build_agent_executor(self) -> WeatherAgent:
        """构建 Agent 执行器"""
        return WeatherAgent()


# 全局变量
_server: WeatherA2AServer | None = None


@asynccontextmanager
async def lifespan(app: Starlette):
    """应用生命周期管理"""
    global _server

    logger.info("正在启动天气 Agent...")

    host = os.getenv("SERVER_URL", "localhost")
    port = int(os.getenv("WEATHER_AGENT_PORT", "10008"))

    httpx_client = httpx.AsyncClient(timeout=30)
    _server = WeatherA2AServer(httpx_client, host=host, port=port)

    # 添加 A2A 路由
    app.router.routes.extend(list(_server.a2a_app().routes))

    app.state.httpx_client = httpx_client
    app.state.server = _server

    logger.info(f"天气 Agent 已启动: http://{host}:{port}")

    try:
        yield
    finally:
        logger.info("正在关闭天气 Agent...")
        await httpx_client.aclose()


def create_app() -> Starlette:
    """创建应用"""
    health_endpoint = create_health_endpoint(AGENT_NAME, AGENT_VERSION)

    app = Starlette(
        routes=[
            Route("/health", health_endpoint, methods=["GET"]),
        ],
        lifespan=lifespan,
    )

    return app


# 用于直接运行
app = create_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("WEATHER_AGENT_PORT", "10008"))
    uvicorn.run(app, host="0.0.0.0", port=port)