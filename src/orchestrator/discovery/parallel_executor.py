# src/orchestrator/discovery/parallel_executor.py
"""
Parallel Discovery Executor - 并行 Discovery 执行器
同时调用多个 Discovery Agent 获取信息。
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncGenerator

import httpx

from src.shared.models import TripSpec, DiscoveryResults

logger = logging.getLogger(__name__)


class ParallelDiscoveryExecutor:
    """
    并行 Discovery 执行器

    同时调用多个 Agent：
    - Weather Agent
    - Transport Agent
    - Attraction Agent
    - Food Agent
    - Hotel Agent
    - Guide Agent
    """

    def __init__(self, httpx_client: httpx.AsyncClient):
        self.httpx_client = httpx_client

    async def execute(
        self,
        trip_spec: TripSpec,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        执行并行 Discovery

        Args:
            trip_spec: 行程需求

        Yields:
            进度和结果
        """
        destination = trip_spec.destination_city
        origin = trip_spec.origin_city
        start_date = trip_spec.start_date

        # 定义要调用的 Agent
        agents = {
            "weather": self._call_weather_agent,
            "transport": self._call_transport_agent,
            "attraction": self._call_attraction_agent,
            "food": self._call_food_agent,
            "hotel": self._call_hotel_agent,
        }

        # 报告开始
        yield {
            "content": f"正在为您搜索 {destination} 的相关信息...",
            "is_task_complete": False,
            "data": {"phase": "discovery", "status": "started"},
        }

        # 并行执行
        results = {}
        tasks = []

        for agent_name, agent_func in agents.items():
            task = asyncio.create_task(
                self._execute_agent_with_error_handling(agent_name, agent_func, trip_spec)
            )
            tasks.append((agent_name, task))

        # 等待所有任务完成
        for agent_name, task in tasks:
            result = await task
            results[agent_name] = result

            # 报告进度
            yield {
                "content": f"已完成 {self._get_agent_display_name(agent_name)} 查询",
                "is_task_complete": False,
                "data": {
                    "phase": "discovery",
                    "completed_agent": agent_name,
                    "progress": len([r for r in results.values() if r]) / len(agents),
                },
            }

        # 汇总结果
        discovery_results = DiscoveryResults(
            weather=results.get("weather"),
            transport=results.get("transport"),
            attractions=results.get("attraction"),
            dining=results.get("food"),
            hotels=results.get("hotel"),
        )

        # 生成汇总报告
        summary = self._generate_summary(destination, results)

        yield {
            "content": summary,
            "is_task_complete": True,
            "require_user_input": True,
            "data": {
                "phase": "discovery",
                "status": "completed",
                "discovery_results": discovery_results.model_dump(),
            },
        }

    async def _execute_agent_with_error_handling(
        self,
        agent_name: str,
        agent_func,
        trip_spec: TripSpec,
    ) -> Any:
        """执行 Agent 并处理错误"""
        try:
            return await agent_func(trip_spec)
        except Exception as e:
            logger.error(f"Agent {agent_name} 执行失败: {e}")
            return None

    async def _call_weather_agent(self, trip_spec: TripSpec) -> Any:
        """调用天气 Agent"""
        from src.mcp_clients import MojiWeatherClient

        async with MojiWeatherClient() as client:
            weather = await client.get_current_weather(trip_spec.destination_city)
            return weather

    async def _call_transport_agent(self, trip_spec: TripSpec) -> Any:
        """调用交通 Agent"""
        from src.mcp_clients import Railway12306Client

        async with Railway12306Client() as client:
            trains = await client.search_trains(
                from_station=f"{trip_spec.origin_city}站",
                to_station=f"{trip_spec.destination_city}站",
                date=trip_spec.start_date,
            )
            return {"trains": trains}

    async def _call_attraction_agent(self, trip_spec: TripSpec) -> Any:
        """调用景点 Agent"""
        from src.mcp_clients import AmapClient

        async with AmapClient() as client:
            pois = await client.search_attractions(trip_spec.destination_city)
            return {"attractions": pois}

    async def _call_food_agent(self, trip_spec: TripSpec) -> Any:
        """调用美食 Agent"""
        from src.mcp_clients import AmapClient

        async with AmapClient() as client:
            restaurants = await client.search_restaurants(trip_spec.destination_city)
            return {"restaurants": restaurants}

    async def _call_hotel_agent(self, trip_spec: TripSpec) -> Any:
        """调用酒店 Agent"""
        from src.mcp_clients import AmapClient

        async with AmapClient() as client:
            hotels = await client.search_hotels(trip_spec.destination_city)
            return {"hotels": hotels}

    def _get_agent_display_name(self, agent_name: str) -> str:
        """获取 Agent 显示名称"""
        names = {
            "weather": "天气",
            "transport": "交通",
            "attraction": "景点",
            "food": "美食",
            "hotel": "酒店",
            "guide": "攻略",
        }
        return names.get(agent_name, agent_name)

    def _generate_summary(self, destination: str, results: dict) -> str:
        """生成汇总报告"""
        lines = [f"📍 {destination} 旅行信息汇总\n"]

        # 天气
        if results.get("weather"):
            weather = results["weather"]
            lines.append(f"🌤️ 天气：{weather.get('weather', '未知')}，气温 {weather.get('temperature_low', '?')}~{weather.get('temperature_high', '?')}℃")

        # 交通
        if results.get("transport"):
            trains = results["transport"].get("trains", [])
            if trains:
                lines.append(f"🚄 交通：找到 {len(trains)} 趟列车")

        # 景点
        if results.get("attraction"):
            attractions = results["attraction"].get("attractions", [])
            if attractions:
                lines.append(f"🏛️ 景点：推荐 {len(attractions)} 个热门景点")

        # 美食
        if results.get("food"):
            restaurants = results["food"].get("restaurants", [])
            if restaurants:
                lines.append(f"🍜 美食：推荐 {len(restaurants)} 家餐厅")

        # 酒店
        if results.get("hotel"):
            hotels = results["hotel"].get("hotels", [])
            if hotels:
                lines.append(f"🏨 酒店：找到 {len(hotels)} 家酒店")

        lines.append("\n请问是否开始规划详细行程？")

        return "\n".join(lines)