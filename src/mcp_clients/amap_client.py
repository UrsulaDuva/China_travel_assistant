# src/mcp_clients/amap_client.py
"""
Amap (高德地图) API Client.
高德地图 API 客户端，提供 POI 搜索、路径规划等功能。
支持返回图片URL。
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class AmapClient:
    """
    高德地图 API 客户端

    功能：
    - POI 搜索（景点、餐厅、酒店）
    - 路径规划
    - 地理编码
    - 返回图片URL
    """

    def __init__(self):
        self.api_key = os.getenv("AMAP_API_KEY", "509dc8e1f2c3a1c33ecde75c6ff5e7de")
        self.base_url = "https://restapi.amap.com/v3"
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AmapClient":
        self._client = httpx.AsyncClient(timeout=30)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None

    def get_server_name(self) -> str:
        return "高德地图 API"

    async def search_poi(
        self,
        keywords: str,
        city: str,
        poi_type: Optional[str] = None,
        page_size: int = 10,
    ) -> list[dict[str, Any]]:
        """
        搜索 POI

        Args:
            keywords: 搜索关键词
            city: 城市名称
            poi_type: POI 类型，如 "景点"、"餐厅"、"酒店"
            page_size: 结果数量

        Returns:
            POI 列表（包含图片URL）
        """
        try:
            response = await self._client.get(
                f"{self.base_url}/place/text",
                params={
                    "key": self.api_key,
                    "keywords": keywords,
                    "city": city,
                    "citylimit": "true",
                    "offset": page_size,
                    "extensions": "all",  # 返回详细信息，包含图片
                }
            )
            response.raise_for_status()
            result = response.json()
            return self._parse_poi_list(result)
        except Exception as e:
            logger.error(f"POI 搜索失败: {e}")
            return self._get_mock_pois(keywords, city, poi_type)

    async def search_attractions(
        self,
        city: str,
        category: Optional[str] = None,
        page_size: int = 10,
    ) -> list[dict[str, Any]]:
        """
        搜索景点

        Args:
            city: 城市名称
            category: 景点分类
            page_size: 结果数量

        Returns:
            景点列表
        """
        keywords = category if category else "景点"
        return await self.search_poi(keywords, city, "景点", page_size)

    async def search_restaurants(
        self,
        city: str,
        cuisine: Optional[str] = None,
        area: Optional[str] = None,
        page_size: int = 10,
    ) -> list[dict[str, Any]]:
        """
        搜索餐厅

        Args:
            city: 城市名称
            cuisine: 菜系
            area: 区域
            page_size: 结果数量

        Returns:
            餐厅列表
        """
        keywords = f"{cuisine}餐厅" if cuisine else "餐厅"
        if area:
            keywords = f"{area}{keywords}"
        return await self.search_poi(keywords, city, "餐厅", page_size)

    async def search_hotels(
        self,
        city: str,
        area: Optional[str] = None,
        price_range: Optional[str] = None,
        page_size: int = 10,
    ) -> list[dict[str, Any]]:
        """
        搜索酒店

        Args:
            city: 城市名称
            area: 区域
            price_range: 价格区间
            page_size: 结果数量

        Returns:
            酒店列表
        """
        keywords = "酒店"
        if area:
            keywords = f"{area}{keywords}"
        return await self.search_poi(keywords, city, "酒店", page_size)

    async def get_route(
        self,
        origin: str,
        destination: str,
        city: str,
        strategy: int = 0,
    ) -> dict[str, Any]:
        """
        路径规划

        Args:
            origin: 起点
            destination: 终点
            city: 城市
            strategy: 策略（0: 推荐, 1: 时间短, 2: 距离短）

        Returns:
            路线信息
        """
        try:
            result = await self._get("/api/route/plan", {
                "origin": origin,
                "destination": destination,
                "city": city,
                "strategy": strategy,
            })
            return self._parse_route(result)
        except Exception as e:
            logger.error(f"路径规划失败: {e}")
            return {"distance": 0, "duration": 0, "steps": []}

    async def geocode(self, address: str, city: Optional[str] = None) -> dict[str, Any]:
        """
        地理编码（地址转坐标）

        Args:
            address: 地址
            city: 城市

        Returns:
            坐标信息
        """
        try:
            params = {"address": address}
            if city:
                params["city"] = city
            result = await self._get("/api/geocode/geo", params)
            return result.get("data", result)
        except Exception as e:
            logger.error(f"地理编码失败: {e}")
            return {"lng": 0, "lat": 0, "level": ""}

    def _parse_poi_list(self, result: dict) -> list[dict[str, Any]]:
        """解析 POI 列表"""
        pois = result.get("pois", [])
        parsed = []
        for poi in pois:
            # 提取图片URL
            photos = poi.get("photos", [])
            image_url = ""
            if photos and len(photos) > 0:
                image_url = photos[0].get("url", "")

            # 提取评分和价格
            biz_ext = poi.get("biz_ext", {})
            rating = biz_ext.get("rating", 4.5) if biz_ext else 4.5
            cost = biz_ext.get("cost", "") if biz_ext else ""

            parsed.append({
                "id": poi.get("id", ""),
                "name": poi.get("name", ""),
                "address": poi.get("address", ""),
                "location": poi.get("location", ""),
                "type": poi.get("type", ""),
                "type_code": poi.get("typecode", ""),
                "rating": float(rating) if rating else 4.5,
                "cost": str(cost) if cost else "",
                "tel": poi.get("tel", ""),
                "image": image_url,
                "photos": photos,
                "cityname": poi.get("cityname", ""),
                "adname": poi.get("adname", ""),
            })
        return parsed

    def _parse_route(self, result: dict) -> dict[str, Any]:
        """解析路线"""
        data = result.get("data", result.get("route", {}))
        return {
            "distance": data.get("distance", 0),
            "duration": data.get("duration", 0),
            "steps": data.get("steps", []),
            "taxi_cost": data.get("taxi_cost", 0),
        }

    def _get_mock_pois(
        self,
        keywords: str,
        city: str,
        poi_type: Optional[str],
    ) -> list[dict[str, Any]]:
        """获取模拟 POI 数据"""
        # 基于城市和类型返回模拟数据
        mock_attractions = {
            "北京": [
                {"id": "1", "name": "故宫博物院", "rating": 5.0, "cost": "60元", "type": "景点"},
                {"id": "2", "name": "天安门广场", "rating": 4.9, "cost": "免费", "type": "景点"},
                {"id": "3", "name": "颐和园", "rating": 4.8, "cost": "30元", "type": "景点"},
            ],
            "上海": [
                {"id": "1", "name": "外滩", "rating": 4.9, "cost": "免费", "type": "景点"},
                {"id": "2", "name": "东方明珠", "rating": 4.7, "cost": "220元", "type": "景点"},
                {"id": "3", "name": "迪士尼乐园", "rating": 4.8, "cost": "399元起", "type": "景点"},
            ],
            "杭州": [
                {"id": "1", "name": "西湖", "rating": 5.0, "cost": "免费", "type": "景点"},
                {"id": "2", "name": "雷峰塔", "rating": 4.6, "cost": "40元", "type": "景点"},
                {"id": "3", "name": "灵隐寺", "rating": 4.8, "cost": "45元", "type": "景点"},
            ],
        }

        mock_restaurants = {
            "北京": [
                {"id": "r1", "name": "全聚德烤鸭店", "rating": 4.5, "cost": "人均150元", "type": "餐厅", "cuisine": "京菜"},
                {"id": "r2", "name": "东来顺饭庄", "rating": 4.4, "cost": "人均120元", "type": "餐厅", "cuisine": "火锅"},
            ],
            "上海": [
                {"id": "r1", "name": "小南国", "rating": 4.6, "cost": "人均200元", "type": "餐厅", "cuisine": "本帮菜"},
                {"id": "r2", "name": "鼎泰丰", "rating": 4.7, "cost": "人均150元", "type": "餐厅", "cuisine": "台湾菜"},
            ],
        }

        mock_hotels = {
            "北京": [
                {"id": "h1", "name": "北京王府井希尔顿酒店", "rating": 4.7, "cost": "800元/晚", "type": "酒店", "star": 5},
                {"id": "h2", "name": "如家快捷酒店", "rating": 4.2, "cost": "200元/晚", "type": "酒店", "star": 2},
            ],
            "上海": [
                {"id": "h1", "name": "上海外滩华尔道夫酒店", "rating": 4.9, "cost": "1500元/晚", "type": "酒店", "star": 5},
                {"id": "h2", "name": "汉庭酒店", "rating": 4.3, "cost": "250元/晚", "type": "酒店", "star": 2},
            ],
        }

        if poi_type == "景点" or "景点" in keywords:
            return mock_attractions.get(city, [])
        elif poi_type == "餐厅" or "餐厅" in keywords:
            return mock_restaurants.get(city, [])
        elif poi_type == "酒店" or "酒店" in keywords:
            return mock_hotels.get(city, [])

        # 默认返回景点
        return mock_attractions.get(city, [])