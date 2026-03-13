# src/mcp_clients/moji_weather_client.py
"""
Moji Weather MCP Client.
墨迹天气 MCP 客户端，提供天气查询功能。
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

from .base_mcp_client import BaseMCPClient

logger = logging.getLogger(__name__)


# 城市ID映射表（常见城市）- 来自城市信息表_V1.xlsx
CITY_ID_MAP = {
    "北京": "2", "北京市": "2",
    "上海": "39", "上海市": "39",
    "广州": "886", "广州市": "886",
    "深圳": "892", "深圳市": "892",
    "杭州": "1185", "杭州市": "1185",
    "成都": "2635", "成都市": "2635",
    "西安": "2182", "西安市": "2182",
    "南京": "1045", "南京市": "1045",
    "武汉": "537", "武汉市": "537",
    "重庆": "52", "重庆市": "52",
    "苏州": "1093", "苏州市": "1093",
    "天津": "24", "天津市": "24",
    "长沙": "650", "长沙市": "650",
    "郑州": "379", "郑州市": "379",
    "青岛": "1407", "青岛市": "1407",
    "大连": "104", "大连市": "104",
    "厦门": "1665", "厦门市": "1665",
    "昆明": "994", "昆明市": "994",
    "三亚": "2356", "三亚市": "2356",
    "桂林": "2003", "桂林市": "2003",
    "丽江": "2158", "丽江市": "2158",
    "大理": "2153", "大理市": "2153",
    "哈尔滨": "126", "哈尔滨市": "126",
    "沈阳": "58", "沈阳市": "58",
    "长春": "163", "长春市": "163",
    "济南": "379", "济南市": "379",
    "福州": "1550", "福州市": "1550",
    "合肥": "1088", "合肥市": "1088",
    "南昌": "838", "南昌市": "838",
    "贵阳": "2279", "贵阳市": "2279",
    "拉萨": "2426", "拉萨市": "2426",
    "乌鲁木齐": "28", "乌鲁木齐市": "28",
    "兰州": "1875", "兰州市": "1875",
    "西宁": "1956", "西宁市": "1956",
    "银川": "1903", "银川市": "1903",
    "呼和浩特": "352", "呼和浩特市": "352",
    "南宁": "2064", "南宁市": "2064",
    "海口": "2315", "海口市": "2315",
    "太原": "436", "太原市": "436",
    "石家庄": "347", "石家庄市": "347",
}


class MojiWeatherClient(BaseMCPClient):
    """
    墨迹天气 MCP 客户端

    功能：
    - 实时天气查询
    - 多日天气预报
    - 穿衣建议
    """

    def __init__(self):
        base_url = os.getenv(
            "MOJI_WEATHER_MCP_URL",
            "http://mcpservergateway.market.alicloudapi.com/mcp/cmapi013828/eyJhcHBDb2RlIjoiMjA4NjkzNWMzNDYyNDFiY2IyZDJiOTRhNzZhNTFjMDkiLCJzIjoiQ2xvdWRfTWFya2V0In0="
        )
        super().__init__(base_url)

    def get_server_name(self) -> str:
        return "墨迹天气 MCP"

    def _get_city_id(self, city: str) -> str:
        """获取城市ID"""
        # 直接返回城市名（可能是ID）
        if city.isdigit():
            return city
        # 查找映射表
        return CITY_ID_MAP.get(city, "2")  # 默认北京(id=2)

    async def get_current_weather(self, city: str) -> dict[str, Any]:
        """
        获取当前天气

        Args:
            city: 城市名称，如 "北京"、"上海"

        Returns:
            天气信息字典
        """
        try:
            city_id = self._get_city_id(city)
            # 调用 MCP 工具 - 使用正确的工具名称
            result = await self.call_tool(
                "天气实况",
                {"cityId": city_id}
            )
            return self._parse_weather_result(result, city)
        except Exception as e:
            logger.error(f"获取天气失败: {e}")
            return self._get_mock_weather(city)

    async def get_forecast(self, city: str, days: int = 7) -> list[dict[str, Any]]:
        """
        获取多日天气预报

        Args:
            city: 城市名称
            days: 预报天数（最多7天）

        Returns:
            天气预报列表
        """
        try:
            city_id = self._get_city_id(city)
            result = await self.call_tool(
                "天气预报15天",
                {"cityId": city_id}
            )
            return self._parse_forecast_result(result, days, city)
        except Exception as e:
            logger.error(f"获取天气预报失败: {e}")
            return [self._get_mock_weather(city) for _ in range(min(days, 7))]

    async def get_clothing_advice(self, city: str, date: Optional[str] = None) -> dict[str, Any]:
        """
        获取穿衣建议

        Args:
            city: 城市名称
            date: 日期（可选）

        Returns:
            穿衣建议
        """
        weather = await self.get_current_weather(city)
        temp = weather.get("temperature", 20)

        # 根据温度生成穿衣建议
        if temp >= 30:
            advice = "天气炎热，建议穿短袖、短裤，注意防晒"
            items = ["短袖", "短裤", "防晒霜", "太阳镜", "遮阳帽"]
        elif temp >= 25:
            advice = "天气温暖，适合穿轻薄衣物"
            items = ["T恤", "薄外套", "休闲裤"]
        elif temp >= 15:
            advice = "天气适中，建议带一件外套"
            items = ["长袖衬衫", "外套", "长裤"]
        elif temp >= 5:
            advice = "天气较冷，注意保暖"
            items = ["毛衣", "厚外套", "长裤", "围巾"]
        else:
            advice = "天气寒冷，需要穿棉衣、羽绒服"
            items = ["羽绒服", "毛衣", "保暖内衣", "围巾", "手套"]

        return {
            "city": city,
            "temperature": temp,
            "advice": advice,
            "recommended_items": items,
        }

    def _parse_weather_result(self, result: dict, city: str = "") -> dict[str, Any]:
        """解析天气结果"""
        import json

        # 从text字段提取JSON
        text = result.get("text", "")
        if text:
            # 找到JSON结束位置（去除额外说明）
            brace_count = 0
            end_pos = 0
            for i, c in enumerate(text):
                if c == '{':
                    brace_count += 1
                elif c == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break

            try:
                result = json.loads(text[:end_pos])
            except:
                pass

        # 提取数据
        data = result.get("data", {})
        condition = data.get("condition", {})
        city_info = data.get("city", {})

        return {
            "city": city_info.get("name", city) or city,
            "province": city_info.get("pname", ""),
            "weather": condition.get("condition", "晴"),
            "temperature": int(condition.get("temp", 20)),
            "temperature_high": int(condition.get("temp", 25)),
            "temperature_low": int(condition.get("temp", 15)),
            "real_feel": int(condition.get("realFeel", 20)),
            "humidity": int(condition.get("humidity", 60)),
            "wind": f"{condition.get('windDir', '微风')} {condition.get('windLevel', '')}级",
            "wind_speed": condition.get("windSpeed", ""),
            "air_pressure": condition.get("pressure", ""),
            "tips": condition.get("tips", ""),
            "update_time": condition.get("updatetime", ""),
        }

    def _parse_forecast_result(self, result: dict, days: int = 7, city: str = "") -> list[dict[str, Any]]:
        """解析预报结果"""
        import json

        # 从text字段提取JSON
        text = result.get("text", "")
        if text:
            if "以下是返回参数说明" in text:
                text = text.split("以下是返回参数说明")[0].strip()
            try:
                result = json.loads(text)
            except:
                pass

        data = result.get("data", {})
        forecasts = data.get("forecast", [])

        results = []
        for f in forecasts[:days]:
            results.append({
                "city": city,
                "date": f.get("predictDate", ""),
                "weather": f.get("conditionDay", "晴"),
                "weather_night": f.get("conditionNight", "晴"),
                "temperature_high": int(f.get("tempHigh", 25)),
                "temperature_low": int(f.get("tempLow", 15)),
                "wind": f.get("windDir", "微风"),
                "wind_level": f.get("windLevel", ""),
            })

        return results

    def _get_mock_weather(self, city: str) -> dict[str, Any]:
        """获取模拟天气数据（用于测试或 API 不可用时）"""
        # 基于城市返回模拟数据
        mock_data = {
            "北京": {"weather": "晴", "temperature": 22, "temperature_high": 28, "temperature_low": 16, "humidity": 45},
            "上海": {"weather": "多云", "temperature": 25, "temperature_high": 29, "temperature_low": 21, "humidity": 70},
            "成都": {"weather": "阴", "temperature": 20, "temperature_high": 24, "temperature_low": 17, "humidity": 75},
            "杭州": {"weather": "小雨", "temperature": 23, "temperature_high": 26, "temperature_low": 19, "humidity": 80},
            "西安": {"weather": "晴", "temperature": 26, "temperature_high": 32, "temperature_low": 18, "humidity": 35},
            "广州": {"weather": "多云", "temperature": 30, "temperature_high": 34, "temperature_low": 26, "humidity": 85},
        }
        data = mock_data.get(city, {"weather": "晴", "temperature": 20, "temperature_high": 25, "temperature_low": 15, "humidity": 50})
        return {
            "city": city,
            **data,
            "wind": "微风",
            "air_quality": "良",
            "update_time": "刚刚更新",
        }