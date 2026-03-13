# src/orchestrator/executor.py
"""
Orchestrator Executor - 主执行器
负责意图分类、任务路由、Agent调用协调。
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, AsyncGenerator, Optional

import httpx

from src.shared.models import (
    IntentType,
    RoutingDecision,
    RoutingResult,
    TripSpec,
    ConsultationStatus,
)

from .session_manager import SessionManager
from .classification.llm_classify import LLMClassifier
from .routing.layer1 import Layer1Router
from .discovery.parallel_executor import ParallelDiscoveryExecutor

logger = logging.getLogger(__name__)


class OrchestratorExecutor:
    """
    Orchestrator 执行器

    职责：
    1. 意图分类 - 理解用户想做什么
    2. 路由决策 - 决定调用哪个 Agent
    3. 并行执行 - 同时调用多个 Discovery Agent
    4. 状态管理 - 维护会话状态
    5. 结果聚合 - 汇总各 Agent 结果
    """

    def __init__(
        self,
        httpx_client: httpx.AsyncClient,
        session_manager: Optional[SessionManager] = None,
    ):
        self.httpx_client = httpx_client
        self.session_manager = session_manager or SessionManager()

        # 初始化组件
        self.classifier = LLMClassifier()
        self.router = Layer1Router()
        self.discovery_executor = ParallelDiscoveryExecutor(httpx_client)

        # Agent URLs
        self.agent_urls = self._build_agent_urls()

    def _build_agent_urls(self) -> dict[str, str]:
        """构建 Agent URL 映射"""
        host = os.getenv("SERVER_URL", "localhost")
        return {
            "clarifier": f"http://{host}:{os.getenv('CLARIFIER_AGENT_PORT', '10007')}",
            "weather": f"http://{host}:{os.getenv('WEATHER_AGENT_PORT', '10008')}",
            "transport": f"http://{host}:{os.getenv('TRANSPORT_AGENT_PORT', '10009')}",
            "attraction": f"http://{host}:{os.getenv('ATTRACTION_AGENT_PORT', '10010')}",
            "food": f"http://{host}:{os.getenv('FOOD_AGENT_PORT', '10011')}",
            "hotel": f"http://{host}:{os.getenv('HOTEL_AGENT_PORT', '10012')}",
            "guide": f"http://{host}:{os.getenv('GUIDE_AGENT_PORT', '10013')}",
            "aggregator": f"http://{host}:{os.getenv('AGGREGATOR_AGENT_PORT', '10014')}",
            "budget": f"http://{host}:{os.getenv('BUDGET_AGENT_PORT', '10015')}",
            "route": f"http://{host}:{os.getenv('ROUTE_AGENT_PORT', '10016')}",
            "validator": f"http://{host}:{os.getenv('VALIDATOR_AGENT_PORT', '10017')}",
            "booking": f"http://{host}:{os.getenv('BOOKING_AGENT_PORT', '10018')}",
        }

    def _extract_city(self, text: str) -> Optional[str]:
        """从文本中提取城市名"""
        # 省份列表（返回省会或主要城市）
        provinces = {
            "四川": "成都", "四川省": "成都",
            "广东": "广州", "广东省": "广州",
            "浙江": "杭州", "浙江省": "杭州",
            "江苏": "南京", "江苏省": "南京",
            "山东": "济南", "山东省": "济南",
            "河南": "郑州", "河南省": "郑州",
            "湖北": "武汉", "湖北省": "武汉",
            "湖南": "长沙", "湖南省": "长沙",
            "福建": "福州", "福建省": "福州",
            "云南": "昆明", "云南省": "昆明",
            "海南": "三亚", "海南省": "三亚",
            "贵州": "贵阳", "贵州省": "贵阳",
            "安徽": "合肥", "安徽省": "合肥",
            "江西": "南昌", "江西省": "南昌",
            "山西": "太原", "山西省": "太原",
            "河北": "石家庄", "河北省": "石家庄",
            "陕西": "西安", "陕西省": "西安",
            "甘肃": "兰州", "甘肃省": "兰州",
            "青海": "西宁", "青海省": "西宁",
            "辽宁": "沈阳", "辽宁省": "沈阳",
            "吉林": "长春", "吉林省": "长春",
            "黑龙江": "哈尔滨", "黑龙江省": "哈尔滨",
            "广西": "桂林", "广西省": "桂林", "广西壮族自治区": "桂林",
            "内蒙古": "呼和浩特", "内蒙古自治区": "呼和浩特",
            "新疆": "乌鲁木齐", "新疆维吾尔自治区": "乌鲁木齐",
            "西藏": "拉萨", "西藏自治区": "拉萨",
            "宁夏": "银川", "宁夏回族自治区": "银川",
        }

        # 先检查省份
        for province, city in provinces.items():
            if province in text:
                return city

        # 城市名称列表
        cities = [
            "北京", "北京市", "上海", "上海市", "广州", "广州市", "深圳", "深圳市",
            "杭州", "杭州市", "成都", "成都市", "西安", "西安市", "南京", "南京市",
            "武汉", "武汉市", "重庆", "苏州市", "苏州", "天津", "天津市",
            "长沙", "长沙市", "郑州", "郑州市", "青岛", "青岛市", "大连", "大连市",
            "厦门", "厦门市", "昆明", "昆明市", "三亚", "三亚市", "桂林", "桂林市",
            "丽江", "大理", "张家界", "黄山", "九寨沟", "西塘", "乌镇", "周庄",
            "珠海", "汕头", "佛山", "东莞", "惠州", "中山", "江门",
            "无锡", "常州", "南通", "扬州", "镇江", "徐州", "淮安",
            "宁波", "温州", "绍兴", "嘉兴", "金华", "台州", "舟山",
            "福州", "泉州", "漳州", "龙岩", "三明", "莆田",
            "济南", "烟台", "威海", "潍坊", "淄博", "日照", "泰安",
            "沈阳", "大连", "鞍山", "抚顺",
            "哈尔滨", "齐齐哈尔", "牡丹江", "佳木斯",
            "长春", "吉林", "四平",
            "呼和浩特", "包头", "鄂尔多斯",
            "乌鲁木齐", "克拉玛依",
            "拉萨", "日喀则",
            "西宁", "格尔木",
            "兰州", "天水", "敦煌",
            "银川", "石嘴山",
            "贵阳", "遵义", "安顺",
            "南宁", "柳州", "北海", "阳朔",
        ]

        for city in cities:
            if city in text:
                # 返回不带"市"的城市名
                return city.replace("市", "")

        return None

    def _extract_dates(self, text: str) -> tuple[Optional[str], Optional[str], int]:
        """
        从文本中提取日期和天数

        Returns:
            (start_date, end_date, days) - 开始日期、结束日期、天数
        """
        import re
        from datetime import datetime, timedelta

        today = datetime.now()
        start_date = None
        end_date = None
        days = 3  # 默认3天

        def chinese_to_number(chinese: str) -> int:
            """将中文数字转换为阿拉伯数字"""
            chinese_nums = {
                '零': 0, '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4,
                '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                '廿': 20, '卅': 30
            }

            # 纯数字
            if chinese.isdigit():
                return int(chinese)

            # 单个中文数字
            if chinese in chinese_nums:
                return chinese_nums[chinese]

            # 处理组合数字
            result = 0
            if '十' in chinese:
                parts = chinese.split('十')
                if parts[0]:
                    result = chinese_nums.get(parts[0], 1) * 10
                else:
                    result = 10
                if parts[1]:
                    result += chinese_nums.get(parts[1], 0)
                return result

            # 廿一、廿二等
            if chinese.startswith('廿'):
                result = 20
                if len(chinese) > 1:
                    result += chinese_nums.get(chinese[1], 0)
                return result

            # 卅一、卅二等
            if chinese.startswith('卅'):
                result = 30
                if len(chinese) > 1:
                    result += chinese_nums.get(chinese[1], 0)
                return result

            return 0

        def extract_number(text: str) -> int:
            """从文本中提取数字（支持中文和阿拉伯数字）"""
            # 先尝试阿拉伯数字
            match = re.search(r'\d+', text)
            if match:
                return int(match.group())

            # 尝试中文数字
            chinese_pattern = r'[一二三四五六七八九十廿卅]+'
            match = re.search(chinese_pattern, text)
            if match:
                return chinese_to_number(match.group())

            return 0

        # 1. 先尝试提取日期范围：从X月X日到X月X日
        range_pattern = r'([一二三四五六七八九十\d]+)[月/-]([一二三四五六七八九十\d]+)[日号]?\s*[到至\-~]\s*([一二三四五六七八九十\d]+)[月/-]?([一二三四五六七八九十\d]+)?[日号]?'
        range_match = re.search(range_pattern, text)
        if range_match:
            groups = range_match.groups()
            start_month = extract_number(groups[0])
            start_day = extract_number(groups[1])
            end_month = extract_number(groups[2])
            end_day = extract_number(groups[3]) if groups[3] else start_day

            try:
                start_dt = datetime(today.year, start_month, start_day)
                end_dt = datetime(today.year, end_month, end_day)

                if start_dt < today:
                    start_dt = datetime(today.year + 1, start_month, start_day)
                    end_dt = datetime(today.year + 1, end_month, end_day)

                start_date = start_dt.strftime("%Y-%m-%d")
                end_date = end_dt.strftime("%Y-%m-%d")
                days = (end_dt - start_dt).days + 1

                return start_date, end_date, days
            except ValueError:
                pass

        # 2. 提取天数模式：X天游、X日游（支持中文数字）
        tour_pattern = r'([一二三四五六七八九十\d]+)[天日]游'
        tour_match = re.search(tour_pattern, text)
        if tour_match:
            days = extract_number(tour_match.group(1))

        # 3. 提取"玩X天"模式
        play_pattern = r'玩([一二三四五六七八九十\d]+)[天日]'
        play_match = re.search(play_pattern, text)
        if play_match:
            days = extract_number(play_match.group(1))

        # 4. 提取具体日期（支持中文数字）
        date_patterns = [
            (r'(\d{4})[年/-]([一二三四五六七八九十\d]+)[月/-]([一二三四五六七八九十\d]+)[日号]?', 3),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', 3),
            (r'([一二三四五六七八九十\d]+)[月/-]([一二三四五六七八九十\d]+)[日号]', 2),
        ]

        for pattern, group_count in date_patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if group_count == 3:
                    year = int(groups[0])
                    month = extract_number(groups[1])
                    day = extract_number(groups[2])
                else:
                    year = today.year
                    month = extract_number(groups[0])
                    day = extract_number(groups[1])

                try:
                    extracted_date = datetime(year, month, day)
                    if extracted_date < today:
                        extracted_date = datetime(year + 1, month, day)

                    start_date = extracted_date.strftime("%Y-%m-%d")
                    end_date = (extracted_date + timedelta(days=days - 1)).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    pass

        # 5. 如果没有找到具体日期，检查是否有"下周"、"下个月"等
        if not start_date:
            if '下周' in text:
                days_ahead = 7 - today.weekday()
                start_date = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
                end_date = (today + timedelta(days=days_ahead + days - 1)).strftime("%Y-%m-%d")
            elif '下个月' in text or '下月' in text:
                next_month = today.replace(day=1) + timedelta(days=32)
                start_date = next_month.replace(day=1).strftime("%Y-%m-%d")
                end_date = (next_month.replace(day=1) + timedelta(days=days - 1)).strftime("%Y-%m-%d")

        return start_date, end_date, days

    async def process(
        self,
        message: str,
        session_id: str,
        event: Optional[dict] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        处理用户消息

        Args:
            message: 用户消息
            session_id: 会话ID
            event: 工作流事件（可选）

        Yields:
            处理结果块
        """
        # 获取或创建会话
        session = await self.session_manager.get_or_create(session_id)

        # 处理工作流事件
        if event:
            async for result in self._handle_workflow_event(session, event):
                yield result
            return

        # 意图分类
        routing_result = await self.classifier.classify(message, session)
        logger.info(f"Routing decision: {routing_result.decision}, intent: {routing_result.intent}")

        # 根据路由决策处理
        if routing_result.decision == RoutingDecision.WORKFLOW:
            async for result in self._handle_workflow(session, message, routing_result):
                yield result

        elif routing_result.decision == RoutingDecision.AGENT:
            async for result in self._handle_single_agent(session, message, routing_result):
                yield result

        elif routing_result.decision == RoutingDecision.CLARIFY:
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": routing_result.clarification_prompt or "请提供更多信息。",
            }

        else:
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": "抱歉，我没有理解您的请求。请换一种方式描述。",
            }

    async def _handle_workflow(
        self,
        session: dict,
        message: str,
        routing_result: RoutingResult,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """处理工作流请求"""

        intent = routing_result.intent

        if intent == IntentType.START_TRIP_PLANNING:
            # 尝试从消息中提取城市
            destination = self._extract_city(message)
            if destination:
                # 尝试提取日期
                start_date, end_date, days = self._extract_dates(message)

                # 构建响应消息
                date_hint = ""

                # 如果没有提取到日期，使用默认值（当前日期+7天）
                if not start_date:
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    start_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
                    end_date = (today + timedelta(days=7 + days - 1)).strftime("%Y-%m-%d")
                    date_hint = f"（默认出发日期为{start_date}，如需修改请告诉我具体日期）"
                else:
                    date_hint = "如需修改日期请告诉我。"

                trip_spec = TripSpec(
                    destination_city=destination,
                    origin_city="出发地",
                    start_date=start_date,
                    end_date=end_date,
                    num_travelers=1,
                )
                session["trip_spec"] = trip_spec.model_dump()

                yield {
                    "content": f"好的，我来帮您规划{destination}的{days}天行程。出发日期：{start_date} 至 {end_date}{date_hint}",
                    "is_task_complete": False,
                    "require_user_input": False,
                    "data": {
                        "trip_spec": trip_spec.model_dump(),
                    }
                }
            else:
                yield {
                    "content": "好的，我来帮您规划行程。首先，请告诉我您的目的地是哪里？",
                    "is_task_complete": False,
                    "require_user_input": True,
                    "data": {
                        "phase": "clarification",
                        "checkpoint": "awaiting_destination",
                    }
                }

        elif intent == IntentType.SEARCH_WEATHER:
            # 直接查询天气
            result = await self._call_agent("weather", message)
            # 提取城市并设置 trip_spec
            city = self._extract_city(message)
            if city:
                # 尝试提取日期
                start_date, end_date, days = self._extract_dates(message)
                if not start_date:
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    start_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
                    end_date = (today + timedelta(days=7 + days - 1)).strftime("%Y-%m-%d")
                trip_spec_data = {
                    "destination_city": city,
                    "origin_city": "出发地",
                    "start_date": start_date,
                    "end_date": end_date,
                    "num_travelers": 1,
                }
                session["trip_spec"] = trip_spec_data
                result["data"] = {"trip_spec": trip_spec_data}
            yield result

        elif intent == IntentType.SEARCH_TRANSPORT:
            # 直接查询交通
            result = await self._call_agent("transport", message)
            city = self._extract_city(message)
            if city:
                # 尝试提取日期
                start_date, end_date, days = self._extract_dates(message)
                if not start_date:
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    start_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
                    end_date = (today + timedelta(days=7 + days - 1)).strftime("%Y-%m-%d")
                trip_spec_data = {
                    "destination_city": city,
                    "origin_city": "出发地",
                    "start_date": start_date,
                    "end_date": end_date,
                    "num_travelers": 1,
                }
                session["trip_spec"] = trip_spec_data
                result["data"] = {"trip_spec": trip_spec_data}
            yield result

        elif intent == IntentType.SEARCH_POI:
            # 直接查询景点
            result = await self._call_agent("attraction", message)
            city = self._extract_city(message)
            if city:
                # 尝试提取日期
                start_date, end_date, days = self._extract_dates(message)
                if not start_date:
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    start_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
                    end_date = (today + timedelta(days=7 + days - 1)).strftime("%Y-%m-%d")
                trip_spec_data = {
                    "destination_city": city,
                    "origin_city": "出发地",
                    "start_date": start_date,
                    "end_date": end_date,
                    "num_travelers": 1,
                }
                session["trip_spec"] = trip_spec_data
                result["data"] = {"trip_spec": trip_spec_data}
            yield result

        else:
            # 通用处理 - 尝试提取城市
            city = self._extract_city(message)
            if city:
                # 尝试提取日期
                start_date, end_date, days = self._extract_dates(message)
                if not start_date:
                    from datetime import datetime, timedelta
                    today = datetime.now()
                    start_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
                    end_date = (today + timedelta(days=7 + days - 1)).strftime("%Y-%m-%d")
                trip_spec_data = {
                    "destination_city": city,
                    "origin_city": "出发地",
                    "start_date": start_date,
                    "end_date": end_date,
                    "num_travelers": 1,
                }
                session["trip_spec"] = trip_spec_data
                yield {
                    "content": f"好的，已为您设置目的地为{city}。我来帮您规划行程。",
                    "is_task_complete": False,
                    "require_user_input": False,
                    "data": {"trip_spec": trip_spec_data},
                }
            else:
                yield {
                    "content": f"我理解您想要{intent.value}，让我为您处理。",
                    "is_task_complete": False,
                    "require_user_input": True,
                }

    async def _handle_single_agent(
        self,
        session: dict,
        message: str,
        routing_result: RoutingResult,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """处理单 Agent 调用"""
        target_agent = routing_result.target_agent

        if not target_agent:
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": "请告诉我您需要查询什么信息？",
            }
            return

        result = await self._call_agent(target_agent, message)
        yield result

    async def _handle_workflow_event(
        self,
        session: dict,
        event: dict,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """处理工作流事件"""
        event_type = event.get("type")

        if event_type == "approve_trip_spec":
            # 用户确认 TripSpec，开始 Discovery 阶段
            trip_spec = session.get("trip_spec")
            if trip_spec:
                # 并行调用 Discovery Agents
                async for result in self.discovery_executor.execute(trip_spec):
                    yield result
            else:
                yield {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": "请先告诉我您的行程需求。",
                }

        elif event_type == "approve_itinerary":
            # 用户确认行程，开始预订
            yield {
                "content": "行程已确认！接下来可以开始预订了。",
                "is_task_complete": False,
                "require_user_input": True,
                "data": {"phase": "booking"},
            }

        else:
            yield {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"收到事件：{event_type}",
            }

    async def _call_agent(self, agent_name: str, message: str) -> dict[str, Any]:
        """调用单个 Agent"""
        url = self.agent_urls.get(agent_name)
        if not url:
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"未找到 Agent: {agent_name}",
            }

        try:
            # 构建 A2A 请求
            payload = {
                "jsonrpc": "2.0",
                "method": "tasks/send",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": message}],
                    }
                },
                "id": 1,
            }

            response = await self.httpx_client.post(f"{url}/", json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()
            content = result.get("result", {}).get("artifacts", [{}])[0].get("parts", [{}])[0].get("text", "")

            return {
                "is_task_complete": True,
                "require_user_input": False,
                "content": content,
                "agent": agent_name,
            }

        except Exception as e:
            logger.error(f"调用 Agent {agent_name} 失败: {e}")
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": f"抱歉，{agent_name} 服务暂时不可用，请稍后再试。",
            }


# 用于兼容的别名
OrchestratorAgent = OrchestratorExecutor