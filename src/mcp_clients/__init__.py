# src/mcp_clients/__init__.py
"""
MCP Clients for China Travel A2A.

Provides clients for:
- 墨迹天气 (Moji Weather)
- 12306 火车票
- 飞常准航空 (Variflight)
- 高德地图 (Amap)
- 抖音攻略 (Douyin)
- 小红书笔记 (Xiaohongshu)
- AI支付 (Bailian Payment)
"""
from .base_mcp_client import BaseMCPClient
from .moji_weather_client import MojiWeatherClient
from .railway12306_client import Railway12306Client
from .amap_client import AmapClient
from .douyin_client import DouyinClient
from .xiaohongshu_client import XiaohongshuClient, search_xiaohongshu_notes

__all__ = [
    "BaseMCPClient",
    "MojiWeatherClient",
    "Railway12306Client",
    "AmapClient",
    "DouyinClient",
    "XiaohongshuClient",
    "search_xiaohongshu_notes",
]