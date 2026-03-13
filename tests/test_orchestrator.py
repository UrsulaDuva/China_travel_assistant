# tests/test_orchestrator.py
"""
Orchestrator tests.
"""
import pytest


@pytest.mark.asyncio
async def test_session_manager():
    """测试会话管理器"""
    from src.orchestrator.session_manager import SessionManager

    manager = SessionManager()

    # 创建会话
    session = await manager.get_or_create("test-session")
    assert session["session_id"] == "test-session"
    assert session["phase"] == "draft"

    # 更新会话
    await manager.update("test-session", {"phase": "planning"})
    session = await manager.get("test-session")
    assert session["phase"] == "planning"

    # 删除会话
    deleted = await manager.delete("test-session")
    assert deleted == True

    # 确认删除
    session = await manager.get("test-session")
    assert session is None


@pytest.mark.asyncio
async def test_llm_classifier():
    """测试 LLM 分类器"""
    from src.orchestrator.classification.llm_classify import LLMClassifier

    classifier = LLMClassifier()

    # 测试规则分类
    result = await classifier.classify("北京今天天气怎么样", {})
    assert result.intent.value == "search_weather"

    result = await classifier.classify("北京到上海的高铁", {})
    assert result.intent.value == "search_transport"


@pytest.mark.asyncio
async def test_layer1_router():
    """测试第一层路由"""
    from src.orchestrator.routing.layer1 import Layer1Router
    from src.shared.models import IntentType, RoutingDecision

    router = Layer1Router()

    # 测试 Agent 路由
    result = router.route(IntentType.SEARCH_WEATHER)
    assert result.decision == RoutingDecision.AGENT
    assert result.target_agent == "weather"

    # 测试工作流路由
    result = router.route(IntentType.START_TRIP_PLANNING)
    assert result.decision == RoutingDecision.WORKFLOW