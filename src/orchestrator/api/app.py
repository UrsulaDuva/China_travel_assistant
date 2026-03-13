# src/orchestrator/api/app.py
"""
Orchestrator API - FastAPI 应用
提供前端 API 接口，集成 Multi-Agent 智能层。
"""
from __future__ import annotations

import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..executor import OrchestratorExecutor
from ..session_manager import SessionManager

# Multi-Agent imports
import sys
print("=" * 50)
print("Loading Multi-Agent module...")
print(f"Python path: {sys.path[:3]}")
try:
    from src.agent_core.graph import SimpleOrchestrator, MemoryManager
    MULTI_AGENT_ENABLED = True
    print("Multi-Agent module loaded successfully!")
except Exception as e:
    MULTI_AGENT_ENABLED = False
    MemoryManager = None
    print(f"Multi-Agent module load failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
print("=" * 50)

logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str = Field(..., description="响应消息")
    session_id: str = Field(..., description="会话ID")
    consultation_id: Optional[str] = Field(None, description="咨询ID")
    data: Optional[dict[str, Any]] = Field(None, description="附加数据")


class SessionStateResponse(BaseModel):
    """会话状态响应"""
    session_id: str
    phase: Optional[str] = None
    checkpoint: Optional[str] = None
    messages: list[dict[str, Any]] = []
    trip_spec: Optional[dict[str, Any]] = None


class SessionEventRequest(BaseModel):
    """会话事件请求"""
    type: str = Field(..., description="事件类型")
    checkpoint_id: Optional[str] = None
    message: Optional[str] = None


# =============================================================================
# FastAPI Application
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    logger.info("正在启动 Orchestrator API...")

    # 初始化组件
    httpx_client = httpx.AsyncClient(timeout=60)
    session_manager = SessionManager()
    executor = OrchestratorExecutor(httpx_client, session_manager)

    # 初始化 Multi-Agent 智能层
    if MULTI_AGENT_ENABLED:
        logger.info("初始化 Multi-Agent 智能层...")
        memory_manager = MemoryManager()
        agent_orchestrator = SimpleOrchestrator(memory_manager=memory_manager)
        logger.info("Multi-Agent 智能层初始化完成")
    else:
        logger.warning("Multi-Agent 模块未加载，将使用基础模式")
        memory_manager = None
        agent_orchestrator = None

    app.state.httpx_client = httpx_client
    app.state.session_manager = session_manager
    app.state.executor = executor
    app.state.memory_manager = memory_manager
    app.state.agent_orchestrator = agent_orchestrator

    logger.info("Orchestrator API 已启动")

    try:
        yield
    finally:
        logger.info("正在关闭 Orchestrator API...")
        await httpx_client.aclose()


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    application = FastAPI(
        title="中国旅游助手 API",
        description="A2A 多 Agent 旅游规划系统",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS 配置
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    _register_routes(application)

    return application


def _register_routes(app: FastAPI):
    """注册路由"""

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """健康检查"""
        return {"status": "healthy", "service": "orchestrator"}

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        """聊天接口 - 集成 Multi-Agent 智能分析"""
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"收到聊天请求: session_id={session_id}, message={request.message[:50]}...")
        logger.info(f"Multi-Agent 状态: enabled={MULTI_AGENT_ENABLED}, orchestrator={app.state.agent_orchestrator is not None}")

        # 尝试使用 Multi-Agent 智能层
        if MULTI_AGENT_ENABLED and app.state.agent_orchestrator:
            try:
                logger.info("使用 Multi-Agent 处理...")
                # 获取当前行程信息
                trip_spec = None
                if app.state.memory_manager:
                    memory = app.state.memory_manager.get_or_create_conversation(session_id)
                    trip_spec = memory.trip_context if memory.trip_context else None
                    logger.info(f"当前 trip_spec: {trip_spec}")

                # 使用 Agent 进行智能分析
                result = await app.state.agent_orchestrator.chat(
                    user_input=request.message,
                    session_id=session_id,
                    trip_spec=trip_spec
                )
                logger.info(f"Multi-Agent 返回: {result}")

                return ChatResponse(
                    message=result.get("message", "处理完成"),
                    session_id=session_id,
                    data=result.get("data"),
                )
            except Exception as e:
                logger.error(f"Multi-Agent 处理失败: {e}")
                import traceback
                traceback.print_exc()
                # 降级到基础处理
                pass

        # 基础处理模式
        logger.info("使用基础处理模式...")
        executor: OrchestratorExecutor = app.state.executor

        # 处理消息
        final_message = ""
        final_data: dict[str, Any] = {}

        async for chunk in executor.process(request.message, session_id):
            if chunk.get("content"):
                final_message = chunk["content"]
            if chunk.get("data"):
                final_data = chunk["data"]

        return ChatResponse(
            message=final_message,
            session_id=session_id,
            data=final_data,
        )

    @app.get("/chat/stream")
    async def chat_stream(
        message: str = Query(..., description="用户消息"),
        session_id: str = Query(None, description="会话ID"),
    ) -> StreamingResponse:
        """流式聊天接口"""

        actual_session_id = session_id or str(uuid.uuid4())
        executor: OrchestratorExecutor = app.state.executor

        async def event_generator():
            async for chunk in executor.process(message, actual_session_id):
                import json
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
        )

    @app.get("/sessions/{session_id}", response_model=SessionStateResponse)
    async def get_session(session_id: str) -> SessionStateResponse:
        """获取会话状态"""
        session_manager: SessionManager = app.state.session_manager
        session = await session_manager.get(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        return SessionStateResponse(
            session_id=session_id,
            phase=session.get("phase"),
            checkpoint=session.get("checkpoint"),
            messages=session.get("messages", []),
            trip_spec=session.get("trip_spec"),
        )

    @app.post("/sessions/{session_id}/event", response_model=SessionStateResponse)
    async def send_event(session_id: str, request: SessionEventRequest) -> SessionStateResponse:
        """发送会话事件"""
        executor: OrchestratorExecutor = app.state.executor
        session_manager: SessionManager = app.state.session_manager

        session = await session_manager.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 处理事件
        event = {"type": request.type}
        if request.message:
            event["message"] = request.message

        async for chunk in executor.process(request.message or request.type, session_id, event):
            pass

        session = await session_manager.get(session_id)
        return SessionStateResponse(
            session_id=session_id,
            phase=session.get("phase"),
            checkpoint=session.get("checkpoint"),
            messages=session.get("messages", []),
            trip_spec=session.get("trip_spec"),
        )

    @app.get("/agents")
    async def list_agents() -> list[dict[str, Any]]:
        """列出所有 Agent - Multi-Agent 架构"""
        host = os.getenv("SERVER_URL", "localhost")

        # 基础 MCP 服务
        base_agents = [
            {"id": "weather", "name": "天气查询助手", "url": f"http://{host}:10008", "status": "healthy", "type": "mcp"},
            {"id": "transport", "name": "交通查询助手", "url": f"http://{host}:10009", "status": "healthy", "type": "mcp"},
            {"id": "attraction", "name": "景点推荐助手", "url": f"http://{host}:10010", "status": "healthy", "type": "mcp"},
            {"id": "food", "name": "美食推荐助手", "url": f"http://{host}:10011", "status": "healthy", "type": "mcp"},
            {"id": "hotel", "name": "酒店预订助手", "url": f"http://{host}:10012", "status": "healthy", "type": "mcp"},
        ]

        # Multi-Agent 智能层
        if MULTI_AGENT_ENABLED:
            intelligent_agents = [
                {"id": "coordinator", "name": "主协调器", "status": "active", "type": "langchain", "description": "分析用户意图，协调专业Agent"},
                {"id": "trip_planning", "name": "行程规划专家", "status": "active", "type": "langchain", "description": "制定整体旅行方案"},
                {"id": "attraction_agent", "name": "景点推荐专家", "status": "active", "type": "langchain", "description": "提供景点信息和游玩建议"},
                {"id": "food_agent", "name": "美食推荐专家", "status": "active", "type": "langchain", "description": "介绍特色美食和餐厅"},
                {"id": "transport_agent", "name": "交通出行专家", "status": "active", "type": "langchain", "description": "提供交通信息和出行方案"},
                {"id": "budget_agent", "name": "预算规划专家", "status": "active", "type": "langchain", "description": "帮助合理安排旅行预算"},
            ]
            return base_agents + intelligent_agents

        return base_agents

    @app.post("/api/trip-context")
    async def update_trip_context(
        session_id: str = Query(..., description="会话ID"),
        trip_spec: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """更新行程上下文 - 用于 Multi-Agent 智能分析"""
        if not MULTI_AGENT_ENABLED or not app.state.memory_manager:
            return {"success": False, "error": "Multi-Agent 模块未启用"}

        try:
            memory = app.state.memory_manager.get_or_create_conversation(session_id)
            if trip_spec:
                memory.update_trip_context(trip_spec)
            return {
                "success": True,
                "session_id": session_id,
                "trip_context": memory.trip_context
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/agent-status")
    async def get_agent_status() -> dict[str, Any]:
        """获取 Multi-Agent 状态"""
        return {
            "multi_agent_enabled": MULTI_AGENT_ENABLED,
            "langchain_available": True if MULTI_AGENT_ENABLED else False,
            "memory_manager": "active" if MULTI_AGENT_ENABLED and app.state.memory_manager else "inactive",
            "architecture": {
                "framework": "LangChain + LangGraph",
                "llm": "Qwen-Plus (DashScope)",
                "memory": "ConversationMemory + VectorMemory",
                "tools": ["Weather", "Attraction", "Food", "Railway", "Guide", "Amap"]
            }
        }

    @app.get("/api/weather/{city}")
    async def get_weather(city: str, date: str = Query(None)) -> dict[str, Any]:
        """获取城市天气 - MCP实时数据，支持指定日期"""
        from src.mcp_clients import MojiWeatherClient
        from datetime import datetime, timedelta

        # 省份到省会城市映射
        province_to_city = {
            "云南": "昆明", "四川": "成都", "广东": "广州", "浙江": "杭州",
            "江苏": "南京", "山东": "济南", "河南": "郑州", "湖北": "武汉",
            "湖南": "长沙", "福建": "福州", "海南": "三亚", "贵州": "贵阳",
            "黑龙江": "哈尔滨", "辽宁": "沈阳", "吉林": "长春", "陕西": "西安",
            "山西": "太原", "河北": "石家庄", "安徽": "合肥", "江西": "南昌",
            "甘肃": "兰州", "青海": "西宁", "内蒙古": "呼和浩特", "广西": "南宁",
            "西藏": "拉萨", "宁夏": "银川", "新疆": "乌鲁木齐", "北京": "北京",
            "上海": "上海", "天津": "天津", "重庆": "重庆",
        }

        # 如果输入是省份，转换为省会城市
        actual_city = province_to_city.get(city, city)

        try:
            async with MojiWeatherClient() as client:
                # 如果有指定日期，获取天气预报
                if date:
                    try:
                        target_date = datetime.strptime(date, "%Y-%m-%d")
                        days_ahead = (target_date - datetime.now()).days + 1
                        if days_ahead > 0 and days_ahead <= 15:
                            # 获取天气预报
                            forecast = await client.get_forecast(actual_city, days=days_ahead)
                            if forecast and len(forecast) >= days_ahead:
                                weather_data = forecast[days_ahead - 1]
                                weather_data["query_date"] = date
                                weather_data["city"] = city  # 返回原始输入的城市名
                                return {"success": True, "data": weather_data}
                    except ValueError:
                        pass

                # 默认获取当天天气
                weather_data = await client.get_current_weather(actual_city)
                weather_data["city"] = city  # 返回原始输入的城市名
                return {"success": True, "data": weather_data}
        except Exception as e:
            logger.error(f"获取天气失败: {e}")
            return {"success": False, "error": str(e), "data": None}

    @app.get("/api/attractions/{city}")
    async def get_attractions(city: str, category: str = Query(None)) -> dict[str, Any]:
        """获取城市景点 - 高德MCP实时数据"""
        from src.mcp_clients import AmapClient

        try:
            async with AmapClient() as client:
                attractions = await client.search_attractions(city, category, page_size=10)
                return {"success": True, "data": attractions, "city": city}
        except Exception as e:
            logger.error(f"获取景点失败: {e}")
            return {"success": False, "error": str(e), "data": []}

    @app.get("/api/food/{city}")
    async def get_food(city: str, cuisine: str = Query(None)) -> dict[str, Any]:
        """获取城市美食 - 高德MCP实时数据"""
        from src.mcp_clients import AmapClient

        try:
            async with AmapClient() as client:
                restaurants = await client.search_restaurants(city, cuisine, page_size=10)
                return {"success": True, "data": restaurants, "city": city}
        except Exception as e:
            logger.error(f"获取美食失败: {e}")
            return {"success": False, "error": str(e), "data": []}

    @app.get("/api/hotels/{city}")
    async def get_hotels(city: str, area: str = Query(None)) -> dict[str, Any]:
        """获取城市酒店 - 高德MCP实时数据"""
        from src.mcp_clients import AmapClient

        try:
            async with AmapClient() as client:
                hotels = await client.search_hotels(city, area, page_size=10)
                return {"success": True, "data": hotels, "city": city}
        except Exception as e:
            logger.error(f"获取酒店失败: {e}")
            return {"success": False, "error": str(e), "data": []}

    @app.get("/api/guide/{city}")
    async def get_guides(city: str, keywords: str = Query(None)) -> dict[str, Any]:
        """获取城市攻略 - 小红书笔记"""
        from src.mcp_clients.xiaohongshu_client import search_xiaohongshu_notes

        all_guides = []

        try:
            # 获取小红书笔记
            search_keyword = f"{city}{keywords}攻略" if keywords else f"{city}旅游攻略"
            xhs_notes = await search_xiaohongshu_notes(search_keyword, limit=10)
            all_guides.extend(xhs_notes)
        except Exception as e:
            logger.error(f"获取小红书笔记失败: {e}")

        return {"success": True, "data": all_guides, "city": city}

    @app.get("/api/trains")
    async def get_trains(
        from_station: str = Query(..., description="出发站"),
        to_station: str = Query(..., description="到达站"),
        date: str = Query(None, description="日期 YYYY-MM-DD"),
    ) -> dict[str, Any]:
        """查询火车票 - 12306实时数据"""
        from src.mcp_clients import Railway12306Client
        from datetime import datetime

        # 如果没有指定日期，使用今天
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        try:
            async with Railway12306Client() as client:
                # 获取真实12306数据
                trains_data = await client.search_trains(from_station, to_station, date)

                if trains_data:
                    # 转换数据格式
                    trains = []
                    for train in trains_data:
                        # 解析座位信息 - 确保是列表格式
                        seats = train.get("seats", [])
                        if isinstance(seats, dict):
                            # 从 seats dict 转换为列表
                            seats_dict = seats
                            prices_dict = train.get("prices", {})
                            seats = []
                            for seat_name, availability in seats_dict.items():
                                if availability == "有" or availability == "有票":
                                    count = 50
                                elif availability == "无" or availability == "无票":
                                    count = 0
                                else:
                                    # 尝试解析数字
                                    try:
                                        count = int(availability)
                                    except:
                                        count = 10
                                seats.append({
                                    "name": seat_name,
                                    "count": count,
                                    "count_display": ">50张" if count >= 50 else f"{count}张",
                                    "price": prices_dict.get(seat_name, 0)
                                })

                        trains.append({
                            "train_no": train.get("train_no", ""),
                            "train_type": "高铁" if train.get("train_no", "").startswith("G") else "动车",
                            "from_station": train.get("from_station", from_station),
                            "to_station": train.get("to_station", to_station),
                            "start_time": train.get("departure_time", train.get("start_time", "")),
                            "end_time": train.get("arrival_time", train.get("end_time", "")),
                            "duration": train.get("duration", ""),
                            "seats": seats
                        })

                    if trains:
                        return {
                            "success": True,
                            "data": trains,
                            "from": from_station,
                            "to": to_station,
                            "date": date,
                            "total": len(trains),
                            "source": "12306实时数据"
                        }
        except Exception as e:
            logger.error(f"获取12306数据失败: {e}")
            import traceback
            traceback.print_exc()

        # 如果12306查询失败，返回错误
        return {
            "success": False,
            "error": "无法获取12306数据，请稍后重试",
            "data": [],
            "from": from_station,
            "to": to_station,
            "date": date,
            "total": 0
        }


# 创建默认应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("ORCHESTRATOR_PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)