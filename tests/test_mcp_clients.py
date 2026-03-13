# tests/test_mcp_clients.py
"""
MCP Client tests.
"""
import pytest


@pytest.mark.asyncio
async def test_moji_weather_client():
    """测试墨迹天气客户端"""
    from src.mcp_clients import MojiWeatherClient

    async with MojiWeatherClient() as client:
        # 测试 mock 数据
        weather = client._get_mock_weather("北京")
        assert weather["city"] == "北京"
        assert "weather" in weather
        assert "temperature" in weather


@pytest.mark.asyncio
async def test_railway12306_client():
    """测试 12306 客户端"""
    from src.mcp_clients import Railway12306Client

    async with Railway12306Client() as client:
        # 测试 mock 数据
        trains = client._get_mock_trains("北京站", "上海站", "2024-01-01")
        assert len(trains) > 0
        assert trains[0]["train_no"] == "G1"


@pytest.mark.asyncio
async def test_amap_client():
    """测试高德地图客户端"""
    from src.mcp_clients import AmapClient

    async with AmapClient() as client:
        # 测试 mock 数据
        pois = client._get_mock_pois("景点", "北京", "景点")
        assert len(pois) > 0
        assert "name" in pois[0]