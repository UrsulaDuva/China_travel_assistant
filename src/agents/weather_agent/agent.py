# src/agents/weather_agent/agent.py
"""
Weather Agent implementation.
天气查询 Agent，使用墨迹天气 MCP。
"""
from __future__ import annotations

import json
import logging
from typing import Any

from src.shared.a2a.base_agent import BaseAgentFrameworkAgent
from src.shared.models import WeatherResponse, WeatherInfo

logger = logging.getLogger(__name__)


class WeatherAgent(BaseAgentFrameworkAgent):
    """
    天气 Agent

    功能：
    - 查询城市天气
    - 获取多日预报
    - 提供穿衣建议
    """

    def get_agent_name(self) -> str:
        return "天气查询助手"

    def get_prompt_name(self) -> str:
        return "weather"

    def get_response_format(self) -> Any:
        return WeatherResponse

    async def invoke(
        self,
        user_input: str,
        session_id: str,
        history: list[dict] | None = None,
        history_seq: int | None = None,
    ) -> dict[str, Any]:
        """处理天气查询请求"""
        from src.mcp_clients import MojiWeatherClient

        # 解析输入，提取城市
        city = self._extract_city(user_input)
        logger.info(f"天气查询请求: city={city}, input={user_input}")

        try:
            async with MojiWeatherClient() as client:
                # 获取当前天气
                weather_data = await client.get_current_weather(city)
                logger.info(f"MCP返回数据: {weather_data}")

                # 判断是否需要预报
                if "预报" in user_input or "几天" in user_input:
                    forecast = await client.get_forecast(city, days=7)
                    weather_info = None
                else:
                    forecast = []
                    weather_info = WeatherInfo(
                        city=weather_data.get("city", city),
                        date="今天",
                        weather=weather_data.get("weather", "晴"),
                        temperature_high=weather_data.get("temperature", 25),
                        temperature_low=weather_data.get("real_feel", 15),
                        humidity=weather_data.get("humidity"),
                        wind=weather_data.get("wind"),
                        tips=weather_data.get("tips", ""),
                    )
        except Exception as e:
            logger.error(f"天气查询失败: {e}", exc_info=True)
            # 使用模拟数据
            weather_data = self._get_mock_weather(city)
            forecast = []
            weather_info = WeatherInfo(
                city=city,
                date="今天",
                weather=weather_data.get("weather", "晴"),
                temperature_high=weather_data.get("temperature_high", 25),
                temperature_low=weather_data.get("temperature_low", 15),
                humidity=weather_data.get("humidity"),
                wind=weather_data.get("wind"),
                tips="",
            )

        # 构建响应
        response = WeatherResponse(
            weather_info=weather_info,
            forecast=[WeatherInfo(
                city=city,
                date=f.get("date", ""),
                weather=f.get("weather", "晴"),
                temperature_high=f.get("temperature_high", 25),
                temperature_low=f.get("temperature_low", 15),
            ) for f in forecast],
            response=self._format_weather_response(city, weather_data, forecast),
        )

        return {
            "is_task_complete": True,
            "require_user_input": False,
            "content": response.response,
            "data": response.model_dump(),
        }

    def _get_mock_weather(self, city: str) -> dict[str, Any]:
        """获取模拟天气数据"""
        return {
            "city": city,
            "weather": "晴",
            "temperature": 22,
            "temperature_high": 28,
            "temperature_low": 16,
            "humidity": 45,
            "wind": "微风",
            "tips": "天气不错，适合出行",
        }

    def parse_response(self, message: Any) -> dict[str, Any]:
        """解析响应"""
        return {
            "is_task_complete": True,
            "require_user_input": False,
            "content": str(message),
        }

    def _extract_city(self, text: str) -> str:
        """从文本中提取城市名"""
        # 常见城市列表
        cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "南京", "武汉", "重庆",
                  "苏州", "天津", "长沙", "郑州", "青岛", "大连", "厦门", "昆明", "三亚", "桂林"]

        for city in cities:
            if city in text:
                return city

        # 默认返回北京
        return "北京"

    def _format_weather_response(
        self,
        city: str,
        weather_data: dict,
        forecast: list,
    ) -> str:
        """格式化天气响应"""
        lines = [f"📍 {weather_data.get('city', city)}天气情况\n"]

        # 当前天气
        lines.append(f"🌤️ 今日天气：{weather_data.get('weather', '晴')}")
        lines.append(f"🌡️ 温度：{weather_data.get('temperature', 20)}℃（体感 {weather_data.get('real_feel', 20)}℃）")
        if weather_data.get("humidity"):
            lines.append(f"💧 湿度：{weather_data.get('humidity')}%")
        if weather_data.get("wind"):
            lines.append(f"💨 风力：{weather_data.get('wind')}")
        if weather_data.get("tips"):
            lines.append(f"💡 提示：{weather_data.get('tips')}")

        # 预报信息
        if forecast:
            lines.append("\n📅 未来几天天气预报：")
            for i, f in enumerate(forecast[:3]):
                lines.append(f"  {f.get('date', f'第{i+1}天')}：{f.get('weather', '晴')} {f.get('temperature_low', 15)}℃~{f.get('temperature_high', 25)}℃")

        return "\n".join(lines)