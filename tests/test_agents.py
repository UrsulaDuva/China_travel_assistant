# tests/test_agents.py
"""
Agent tests.
"""
import pytest


@pytest.mark.asyncio
async def test_weather_agent():
    """测试天气 Agent"""
    from src.agents.weather_agent.agent import WeatherAgent

    agent = WeatherAgent()
    result = await agent.invoke("北京今天天气怎么样", "test-session")

    assert result["is_task_complete"] == True
    assert "content" in result
    assert result["content"] != ""


@pytest.mark.asyncio
async def test_transport_agent():
    """测试交通 Agent"""
    from src.agents.transport_agent.agent import TransportAgent

    agent = TransportAgent()
    result = await agent.invoke("北京到上海的高铁", "test-session")

    assert result["is_task_complete"] == True
    assert "content" in result


@pytest.mark.asyncio
async def test_weather_agent_city_extraction():
    """测试城市提取"""
    from src.agents.weather_agent.agent import WeatherAgent

    agent = WeatherAgent()

    assert agent._extract_city("北京今天天气怎么样") == "北京"
    assert agent._extract_city("上海明天会下雨吗") == "上海"
    assert agent._extract_city("杭州需要带伞吗") == "杭州"