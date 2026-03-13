"""
LangChain Tools wrapping MCP Clients
=====================================

These tools provide a LangChain-compatible interface for the MCP clients,
allowing them to be used by LangChain agents.
"""

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, Any
import asyncio
import sys
import os
import importlib

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Lazy imports to avoid encoding issues
def _get_moji_weather_client():
    module = importlib.import_module('mcp_clients.moji_weather_client')
    return module.MojiWeatherClient

def _get_amap_client():
    module = importlib.import_module('mcp_clients.amap_client')
    return module.AmapClient

def _get_railway_client():
    module = importlib.import_module('mcp_clients.railway12306_client')
    return module.Railway12306Client

def _get_douyin_client():
    module = importlib.import_module('mcp_clients.douyin_client')
    return module.DouyinClient


class WeatherInput(BaseModel):
    """Input for weather tool."""
    city: str = Field(description="城市名称，如'北京'、'上海'")


class AttractionInput(BaseModel):
    """Input for attraction tool."""
    city: str = Field(description="城市名称")
    category: Optional[str] = Field(default=None, description="景点类别，如'景点'、'公园'")


class FoodInput(BaseModel):
    """Input for food tool."""
    city: str = Field(description="城市名称")
    cuisine_type: Optional[str] = Field(default=None, description="菜系类型")


class RailwayInput(BaseModel):
    """Input for railway tool."""
    from_station: str = Field(description="出发站")
    to_station: str = Field(description="到达站")
    date: str = Field(description="出发日期，格式YYYY-MM-DD")


class GuideInput(BaseModel):
    """Input for guide tool."""
    city: str = Field(description="城市名称")
    limit: Optional[int] = Field(default=5, description="返回数量")


class AmapInput(BaseModel):
    """Input for Amap tool."""
    keywords: str = Field(description="搜索关键词")
    city: str = Field(description="城市名称")
    location: Optional[str] = Field(default=None, description="中心点坐标")


class WeatherTool(BaseTool):
    """Tool for getting weather information."""
    name: str = "weather"
    description: str = "获取指定城市的天气信息，包括温度、湿度、天气状况等。输入城市名称。"
    args_schema: Type[BaseModel] = WeatherInput

    async def _arun(self, city: str) -> str:
        """Async implementation."""
        MojiWeatherClient = _get_moji_weather_client()
        async with MojiWeatherClient() as client:
            result = await client.get_weather(city)
            if result:
                return f"{result.get('city', city)}天气：{result.get('temp', '--')}°C，{result.get('description', '未知')}，湿度{result.get('humidity', '--')}%，{result.get('tips', '')}"
            return f"无法获取{city}的天气信息"

    def _run(self, city: str) -> str:
        """Sync implementation."""
        return asyncio.run(self._arun(city))


class AttractionTool(BaseTool):
    """Tool for getting attraction information."""
    name: str = "attractions"
    description: str = "获取指定城市的景点推荐列表。输入城市名称，返回热门景点信息。"
    args_schema: Type[BaseModel] = AttractionInput

    async def _arun(self, city: str, category: Optional[str] = None) -> str:
        """Async implementation."""
        AmapClient = _get_amap_client()
        async with AmapClient() as client:
            result = await client.search_poi(
                keywords=category or "景点",
                city=city,
                citylimit=True
            )
            if result:
                pois = result.get("pois", [])[:5]
                output = f"{city}热门景点推荐：\n"
                for i, poi in enumerate(pois, 1):
                    output += f"{i}. {poi.get('name')} - {poi.get('address', '地址未知')}\n"
                return output
            return f"未找到{city}的景点信息"

    def _run(self, city: str, category: Optional[str] = None) -> str:
        """Sync implementation."""
        return asyncio.run(self._arun(city, category))


class FoodTool(BaseTool):
    """Tool for getting food/restaurant information."""
    name: str = "food"
    description: str = "获取指定城市的美食推荐。输入城市名称，返回当地特色美食和餐厅推荐。"
    args_schema: Type[BaseModel] = FoodInput

    async def _arun(self, city: str, cuisine_type: Optional[str] = None) -> str:
        """Async implementation."""
        AmapClient = _get_amap_client()
        async with AmapClient() as client:
            result = await client.search_poi(
                keywords=cuisine_type or "美食",
                city=city,
                citylimit=True
            )
            if result:
                pois = result.get("pois", [])[:5]
                output = f"{city}美食推荐：\n"
                for i, poi in enumerate(pois, 1):
                    output += f"{i}. {poi.get('name')} - {poi.get('address', '地址未知')}\n"
                return output
            return f"未找到{city}的美食信息"

    def _run(self, city: str, cuisine_type: Optional[str] = None) -> str:
        """Sync implementation."""
        return asyncio.run(self._arun(city, cuisine_type))


class RailwayTool(BaseTool):
    """Tool for querying train tickets."""
    name: str = "railway"
    description: str = "查询火车票信息。输入出发站、到达站和日期，返回可用车次信息。"
    args_schema: Type[BaseModel] = RailwayInput

    async def _arun(self, from_station: str, to_station: str, date: str) -> str:
        """Async implementation."""
        Railway12306Client = _get_railway_client()
        async with Railway12306Client() as client:
            result = await client.query_trains(
                from_station=from_station,
                to_station=to_station,
                date=date
            )
            if result and result.get("trains"):
                trains = result.get("trains", [])[:5]
                output = f"{from_station}到{to_station} ({date}) 车次：\n"
                for train in trains:
                    output += f"- {train.get('train_code')} {train.get('departure_time')}-{train.get('arrival_time')} 历时{train.get('duration')}\n"
                return output
            return f"未找到{from_station}到{to_station}的车次信息"

    def _run(self, from_station: str, to_station: str, date: str) -> str:
        """Sync implementation."""
        return asyncio.run(self._arun(from_station, to_station, date))


class GuideTool(BaseTool):
    """Tool for getting travel guides from Douyin."""
    name: str = "guides"
    description: str = "获取指定城市的旅游攻略，来自抖音达人推荐。输入城市名称。"
    args_schema: Type[BaseModel] = GuideInput

    async def _arun(self, city: str, limit: int = 5) -> str:
        """Async implementation."""
        DouyinClient = _get_douyin_client()
        async with DouyinClient() as client:
            result = await client.get_travel_guides(city, limit=limit)
            if result:
                output = f"{city}旅游攻略推荐：\n"
                for i, guide in enumerate(result[:limit], 1):
                    output += f"{i}. {guide.get('title')} - {guide.get('description', '')[:50]}...\n"
                return output
            return f"未找到{city}的攻略信息"

    def _run(self, city: str, limit: int = 5) -> str:
        """Sync implementation."""
        return asyncio.run(self._arun(city, limit))


class AmapTool(BaseTool):
    """Tool for Amap POI search."""
    name: str = "amap_search"
    description: str = "高德地图POI搜索。输入关键词和城市，返回地点信息。"
    args_schema: Type[BaseModel] = AmapInput

    async def _arun(self, keywords: str, city: str, location: Optional[str] = None) -> str:
        """Async implementation."""
        AmapClient = _get_amap_client()
        async with AmapClient() as client:
            result = await client.search_poi(
                keywords=keywords,
                city=city,
                location=location
            )
            if result:
                pois = result.get("pois", [])[:5]
                output = f"{city} '{keywords}' 搜索结果：\n"
                for i, poi in enumerate(pois, 1):
                    output += f"{i}. {poi.get('name')} - {poi.get('address', '地址未知')}\n"
                return output
            return f"未找到相关地点"

    def _run(self, keywords: str, city: str, location: Optional[str] = None) -> str:
        """Sync implementation."""
        return asyncio.run(self._arun(keywords, city, location))


# Tool registry for easy access
ALL_TOOLS = [
    WeatherTool(),
    AttractionTool(),
    FoodTool(),
    RailwayTool(),
    GuideTool(),
    AmapTool(),
]

TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}