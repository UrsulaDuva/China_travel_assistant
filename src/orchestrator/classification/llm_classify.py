# src/orchestrator/classification/llm_classify.py
"""
LLM Classifier - LLM 意图分类器
使用 DashScope/Qwen 进行意图分类。
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

from src.shared.models import IntentType, RoutingDecision, RoutingResult

logger = logging.getLogger(__name__)


# 意图分类提示词
CLASSIFICATION_PROMPT = """你是一个旅行助手的意图分类器。分析用户输入，判断用户意图。

可能的意图类型：
- start_trip_planning: 开始规划行程
- search_weather: 查询天气
- search_transport: 查询交通（火车、飞机）
- search_poi: 查询景点
- search_dining: 查询美食/餐厅
- search_stay: 查询酒店
- search_guide: 查询攻略
- modify_trip: 修改行程
- cancel_booking: 取消预订
- general_question: 一般问题

请返回 JSON 格式：
{
  "intent": "意图类型",
  "confidence": 0.0-1.0,
  "target_agent": "目标Agent名称（如果有）",
  "reasoning": "判断理由"
}

用户输入：{message}
会话状态：{session_state}
"""


class LLMClassifier:
    """
    LLM 意图分类器

    使用 Qwen 模型进行意图分类。
    """

    def __init__(self):
        self.model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
        self._llm_client = None

    def _get_llm_client(self):
        """获取 LLM 客户端"""
        if self._llm_client is None:
            try:
                import dashscope
                from dashscope import Generation

                api_key = os.getenv("DASHSCOPE_API_KEY")
                if api_key:
                    dashscope.api_key = api_key
                self._llm_client = Generation
            except ImportError:
                logger.warning("DashScope 未安装，使用规则分类")
                self._llm_client = None

        return self._llm_client

    async def classify(
        self,
        message: str,
        session: dict[str, Any],
    ) -> RoutingResult:
        """
        分类用户意图

        Args:
            message: 用户消息
            session: 会话状态

        Returns:
            路由结果
        """
        # 首先尝试规则分类
        rule_result = self._rule_based_classify(message, session)
        if rule_result and rule_result.confidence >= 0.8:
            return rule_result

        # 然后尝试 LLM 分类
        llm_result = await self._llm_classify(message, session)
        if llm_result:
            return llm_result

        # 默认返回通用问题
        return RoutingResult(
            decision=RoutingDecision.CLARIFY,
            confidence=0.5,
            intent=IntentType.GENERAL_QUESTION,
            clarification_prompt="抱歉，我不太理解您的意思。您可以告诉我您想做什么吗？比如：查询天气、规划行程、搜索景点等。",
        )

    def _rule_based_classify(
        self,
        message: str,
        session: dict[str, Any],
    ) -> Optional[RoutingResult]:
        """基于规则的分类"""

        # 城市名称列表
        cities = ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "南京", "武汉", "重庆",
                  "苏州", "天津", "长沙", "郑州", "青岛", "大连", "厦门", "昆明", "三亚", "桂林",
                  "丽江", "大理", "张家界", "黄山", "珠海", "无锡", "宁波", "福州", "济南", "烟台",
                  "沈阳", "哈尔滨", "长春", "呼和浩特", "乌鲁木齐", "拉萨", "西宁", "兰州", "银川",
                  "贵阳", "南宁", "北海", "阳朔", "汕头", "佛山", "东莞", "常州", "南通", "扬州"]

        # 省份列表
        provinces = ["四川", "广东", "浙江", "江苏", "山东", "河南", "湖北", "湖南", "福建", "云南",
                     "海南", "贵州", "安徽", "江西", "山西", "河北", "陕西", "甘肃", "青海", "辽宁",
                     "吉林", "黑龙江", "广西", "内蒙古", "新疆", "西藏", "宁夏"]

        # 检测是否包含城市名或省份
        has_city = any(city in message for city in cities)
        has_province = any(prov in message for prov in provinces)

        # 天气相关
        weather_keywords = ["天气", "气温", "下雨", "晴天", "温度", "穿什么", "带伞"]
        if any(kw in message for kw in weather_keywords):
            return RoutingResult(
                decision=RoutingDecision.AGENT,
                confidence=0.9,
                intent=IntentType.SEARCH_WEATHER,
                target_agent="weather",
            )

        # 交通相关
        transport_keywords = ["火车", "高铁", "动车", "机票", "航班", "飞机", "车票"]
        if any(kw in message for kw in transport_keywords):
            return RoutingResult(
                decision=RoutingDecision.AGENT,
                confidence=0.9,
                intent=IntentType.SEARCH_TRANSPORT,
                target_agent="transport",
            )

        # 如果用户只输入城市名或表达想去某城市，视为开始行程规划
        if has_city or has_province:
            # 检测是否只是城市名或简单的旅游意图
            simple_patterns = ["去", "想去", "旅游", "玩", "攻略", "行程", "规划", "游", "日游", "周游", "玩"]
            planning_patterns = ["规划", "计划", "安排", "推荐", "帮我", "行程"]
            # 如果包含旅游关键词或者规划意图，或者消息很短（可能是城市名）
            if (any(kw in message for kw in simple_patterns) or
                any(kw in message for kw in planning_patterns) or
                len(message) <= 8):
                return RoutingResult(
                    decision=RoutingDecision.WORKFLOW,
                    confidence=0.9,
                    intent=IntentType.START_TRIP_PLANNING,
                )

        # 景点相关
        poi_keywords = ["景点", "好玩", "打卡", "旅游胜地"]
        if any(kw in message for kw in poi_keywords):
            return RoutingResult(
                decision=RoutingDecision.AGENT,
                confidence=0.9,
                intent=IntentType.SEARCH_POI,
                target_agent="attraction",
            )

        # 美食相关
        food_keywords = ["吃", "美食", "餐厅", "饭店", "菜", "好吃"]
        if any(kw in message for kw in food_keywords):
            return RoutingResult(
                decision=RoutingDecision.AGENT,
                confidence=0.9,
                intent=IntentType.SEARCH_DINING,
                target_agent="food",
            )

        # 行程规划相关
        planning_keywords = ["规划行程", "帮我计划", "旅行计划", "行程安排", "日游"]
        if any(kw in message for kw in planning_keywords):
            return RoutingResult(
                decision=RoutingDecision.WORKFLOW,
                confidence=0.85,
                intent=IntentType.START_TRIP_PLANNING,
            )

        return None

    async def _llm_classify(
        self,
        message: str,
        session: dict[str, Any],
    ) -> Optional[RoutingResult]:
        """LLM 分类"""
        import asyncio

        client = self._get_llm_client()
        if not client:
            return None

        try:
            prompt = CLASSIFICATION_PROMPT.format(
                message=message,
                session_state=json.dumps(session, ensure_ascii=False, default=str),
            )

            def _sync_call():
                response = client.call(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    result_format="message",
                )
                if response.status_code == 200:
                    return response.output.choices[0].message.content
                return None

            loop = asyncio.get_event_loop()
            result_text = await loop.run_in_executor(None, _sync_call)

            if result_text:
                # 解析 JSON
                result = json.loads(result_text)
                intent_str = result.get("intent", "general_question")
                confidence = result.get("confidence", 0.5)
                target_agent = result.get("target_agent")

                # 映射意图
                intent = self._map_intent(intent_str)

                decision = RoutingDecision.AGENT if target_agent else RoutingDecision.WORKFLOW

                return RoutingResult(
                    decision=decision,
                    confidence=confidence,
                    intent=intent,
                    target_agent=target_agent,
                )

        except Exception as e:
            logger.error(f"LLM 分类失败: {e}")

        return None

    def _map_intent(self, intent_str: str) -> IntentType:
        """映射意图字符串到枚举"""
        mapping = {
            "start_trip_planning": IntentType.START_TRIP_PLANNING,
            "search_weather": IntentType.SEARCH_WEATHER,
            "search_transport": IntentType.SEARCH_TRANSPORT,
            "search_poi": IntentType.SEARCH_POI,
            "search_dining": IntentType.SEARCH_DINING,
            "search_stay": IntentType.SEARCH_STAY,
            "search_guide": IntentType.SEARCH_GUIDE,
            "modify_trip": IntentType.MODIFY_TRIP,
            "cancel_booking": IntentType.CANCEL_BOOKING,
            "general_question": IntentType.GENERAL_QUESTION,
        }
        return mapping.get(intent_str, IntentType.GENERAL_QUESTION)