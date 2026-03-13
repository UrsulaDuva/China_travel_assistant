# src/orchestrator/routing/layer1.py
"""
Layer 1 Router - 第一层路由器
决定请求应该路由到哪个 Agent 或工作流。
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from src.shared.models import IntentType, RoutingDecision, RoutingResult

logger = logging.getLogger(__name__)


class Layer1Router:
    """
    第一层路由器

    路由决策：
    1. WORKFLOW - 进入工作流状态机
    2. AGENT - 直接调用 Agent
    3. TOOL - 调用工具
    4. CLARIFY - 需要澄清
    """

    # 意图到 Agent 的映射
    INTENT_AGENT_MAP = {
        IntentType.SEARCH_WEATHER: "weather",
        IntentType.SEARCH_TRANSPORT: "transport",
        IntentType.SEARCH_POI: "attraction",
        IntentType.SEARCH_DINING: "food",
        IntentType.SEARCH_STAY: "hotel",
        IntentType.SEARCH_GUIDE: "guide",
    }

    # 工作流意图
    WORKFLOW_INTENTS = {
        IntentType.START_TRIP_PLANNING,
        IntentType.CONTINUE_CLARIFICATION,
        IntentType.APPROVE_TRIP_SPEC,
        IntentType.APPROVE_ITINERARY,
        IntentType.START_BOOKING,
        IntentType.CONFIRM_BOOKING,
        IntentType.MODIFY_TRIP,
        IntentType.MODIFY_BOOKING,
        IntentType.CANCEL_BOOKING,
    }

    def route(
        self,
        intent: IntentType,
        context: Optional[dict[str, Any]] = None,
    ) -> RoutingResult:
        """
        根据意图进行路由

        Args:
            intent: 用户意图
            context: 上下文信息

        Returns:
            路由结果
        """
        # 检查是否是工作流意图
        if intent in self.WORKFLOW_INTENTS:
            return RoutingResult(
                decision=RoutingDecision.WORKFLOW,
                confidence=1.0,
                intent=intent,
            )

        # 检查是否是 Agent 意图
        if intent in self.INTENT_AGENT_MAP:
            return RoutingResult(
                decision=RoutingDecision.AGENT,
                confidence=1.0,
                intent=intent,
                target_agent=self.INTENT_AGENT_MAP[intent],
            )

        # 默认需要澄清
        return RoutingResult(
            decision=RoutingDecision.CLARIFY,
            confidence=0.5,
            intent=intent,
            clarification_prompt=self._get_clarification_prompt(intent),
        )

    def _get_clarification_prompt(self, intent: IntentType) -> str:
        """获取澄清提示"""
        prompts = {
            IntentType.GENERAL_QUESTION: "请告诉我您具体想了解什么？我可以帮您查询天气、交通、景点、美食等信息。",
            IntentType.HELP: "我是旅行助手，可以帮您：\n1. 规划行程\n2. 查询天气\n3. 查询交通\n4. 推荐景点\n5. 推荐美食\n6. 预订酒店",
            IntentType.STATUS: "请问您想查询什么状态？我可以帮您查看行程进度或预订状态。",
        }
        return prompts.get(intent, "请问您需要什么帮助？")