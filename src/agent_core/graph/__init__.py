"""
LangGraph Workflow for Travel Planning
======================================

Orchestrates multiple agents using LangGraph for complex travel planning tasks.
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..agents import (
    CoordinatorAgent,
    TripPlanningAgent,
    AttractionAgent,
    FoodAgent,
    TransportAgent,
    BudgetAgent,
    AGENTS
)
from ..tools import ALL_TOOLS, TOOL_MAP
from ..memory import ConversationMemory, MemoryManager


class TravelState(TypedDict):
    """State for the travel planning graph."""
    session_id: str
    user_input: str
    intent: Dict[str, Any]
    context: str
    tool_calls: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    messages: List[str]
    final_response: str
    trip_spec: Dict[str, Any]


class TravelPlanningGraph:
    """LangGraph-based travel planning workflow."""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.memory_manager = memory_manager or MemoryManager()

        # Initialize agents
        self.coordinator = CoordinatorAgent()
        self.planning_agent = TripPlanningAgent()
        self.attraction_agent = AttractionAgent()
        self.food_agent = FoodAgent()
        self.transport_agent = TransportAgent()
        self.budget_agent = BudgetAgent()

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(TravelState)

        # Add nodes
        workflow.add_node("analyze", self._analyze_intent)
        workflow.add_node("gather_info", self._gather_information)
        workflow.add_node("plan_attractions", self._plan_attractions)
        workflow.add_node("plan_food", self._plan_food)
        workflow.add_node("plan_transport", self._plan_transport)
        workflow.add_node("synthesize", self._synthesize_response)

        # Define edges
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "gather_info")
        workflow.add_conditional_edges(
            "gather_info",
            self._route_from_gather,
            {
                "attractions": "plan_attractions",
                "food": "plan_food",
                "transport": "plan_transport",
                "synthesize": "synthesize"
            }
        )
        workflow.add_edge("plan_attractions", "synthesize")
        workflow.add_edge("plan_food", "synthesize")
        workflow.add_edge("plan_transport", "synthesize")
        workflow.add_edge("synthesize", END)

        return workflow.compile()

    async def _analyze_intent(self, state: TravelState) -> Dict:
        """Analyze user intent."""
        user_input = state["user_input"]
        session_id = state.get("session_id", "default")

        # Get conversation memory
        memory = self.memory_manager.get_or_create_conversation(session_id)
        context = memory.get_context_string()

        # Analyze intent
        intent = await self.coordinator.analyze_intent(user_input, context)

        # Update memory
        memory.add_message("user", user_input)

        return {
            "intent": intent,
            "context": context,
            "messages": [f"分析意图: {intent.get('intent', 'unknown')}"]
        }

    async def _gather_information(self, state: TravelState) -> Dict:
        """Gather basic information."""
        intent = state["intent"]
        tool_results = {}
        tool_calls = []

        cities = intent.get("cities", [])
        city = cities[0] if cities else None

        if city:
            # Get weather if needed
            if intent.get("needs_weather"):
                try:
                    weather_tool = TOOL_MAP["weather"]
                    weather_result = await weather_tool._arun(city)
                    tool_results["weather"] = weather_result
                    tool_calls.append({"tool": "weather", "city": city})
                except Exception as e:
                    tool_results["weather"] = f"天气查询失败: {str(e)}"

            # Get attractions if needed
            if intent.get("needs_attractions"):
                try:
                    attraction_tool = TOOL_MAP["attractions"]
                    attraction_result = await attraction_tool._arun(city)
                    tool_results["attractions"] = attraction_result
                    tool_calls.append({"tool": "attractions", "city": city})
                except Exception as e:
                    tool_results["attractions"] = f"景点查询失败: {str(e)}"

            # Get food if needed
            if intent.get("needs_food"):
                try:
                    food_tool = TOOL_MAP["food"]
                    food_result = await food_tool._arun(city)
                    tool_results["food"] = food_result
                    tool_calls.append({"tool": "food", "city": city})
                except Exception as e:
                    tool_results["food"] = f"美食查询失败: {str(e)}"

        return {
            "tool_results": tool_results,
            "tool_calls": tool_calls,
            "messages": state.get("messages", []) + ["收集信息完成"]
        }

    def _route_from_gather(self, state: TravelState) -> str:
        """Route to next node based on intent."""
        intent = state.get("intent", {})

        if intent.get("needs_attractions") and intent.get("intent") == "attraction":
            return "attractions"
        if intent.get("needs_food") and intent.get("intent") == "food":
            return "food"
        if intent.get("needs_transport") and intent.get("intent") == "transport":
            return "transport"

        return "synthesize"

    async def _plan_attractions(self, state: TravelState) -> Dict:
        """Plan attractions."""
        intent = state["intent"]
        cities = intent.get("cities", [])
        city = cities[0] if cities else "未知城市"

        try:
            attraction_tool = TOOL_MAP["attractions"]
            guide_tool = TOOL_MAP["guides"]

            results = []
            results.append(await attraction_tool._arun(city))
            results.append(await guide_tool._arun(city))

            return {
                "tool_results": {**state.get("tool_results", {}), "attraction_details": "\n".join(results)},
                "messages": state.get("messages", []) + ["景点规划完成"]
            }
        except Exception as e:
            return {
                "messages": state.get("messages", []) + [f"景点规划失败: {str(e)}"]
            }

    async def _plan_food(self, state: TravelState) -> Dict:
        """Plan food."""
        intent = state["intent"]
        cities = intent.get("cities", [])
        city = cities[0] if cities else "未知城市"

        try:
            food_tool = TOOL_MAP["food"]
            result = await food_tool._arun(city)

            return {
                "tool_results": {**state.get("tool_results", {}), "food_details": result},
                "messages": state.get("messages", []) + ["美食规划完成"]
            }
        except Exception as e:
            return {
                "messages": state.get("messages", []) + [f"美食规划失败: {str(e)}"]
            }

    async def _plan_transport(self, state: TravelState) -> Dict:
        """Plan transportation."""
        intent = state["intent"]
        trip_spec = state.get("trip_spec", {})

        from_city = trip_spec.get("origin_city", "北京")
        to_city = intent.get("cities", ["上海"])[0] if intent.get("cities") else "上海"
        date = trip_spec.get("start_date", "")

        if not date:
            from datetime import datetime, timedelta
            date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        try:
            railway_tool = TOOL_MAP["railway"]
            result = await railway_tool._arun(from_city, to_city, date)

            return {
                "tool_results": {**state.get("tool_results", {}), "transport_details": result},
                "messages": state.get("messages", []) + ["交通规划完成"]
            }
        except Exception as e:
            return {
                "messages": state.get("messages", []) + [f"交通规划失败: {str(e)}"]
            }

    async def _synthesize_response(self, state: TravelState) -> Dict:
        """Synthesize final response."""
        intent = state.get("intent", {})
        tool_results = state.get("tool_results", {})
        user_input = state.get("user_input", "")

        # Build response based on intent and tool results
        response_parts = []

        if intent.get("response"):
            response_parts.append(intent["response"])

        if tool_results.get("weather"):
            response_parts.append(f"\n{tool_results['weather']}")

        if tool_results.get("attractions"):
            response_parts.append(f"\n{tool_results['attractions']}")

        if tool_results.get("food"):
            response_parts.append(f"\n{tool_results['food']}")

        if tool_results.get("transport_details"):
            response_parts.append(f"\n{tool_results['transport_details']}")

        if not response_parts:
            response_parts.append("我很乐意帮助您规划旅行！请告诉我您的目的地和出行日期。")

        final_response = "\n".join(response_parts)

        # Update memory
        session_id = state.get("session_id", "default")
        memory = self.memory_manager.get_or_create_conversation(session_id)
        memory.add_message("assistant", final_response)

        return {
            "final_response": final_response,
            "messages": state.get("messages", []) + ["响应生成完成"]
        }

    async def run(self, user_input: str, session_id: str = "default", trip_spec: Dict = None) -> Dict[str, Any]:
        """Run the travel planning workflow."""
        initial_state = {
            "session_id": session_id,
            "user_input": user_input,
            "intent": {},
            "context": "",
            "tool_calls": [],
            "tool_results": {},
            "messages": [],
            "final_response": "",
            "trip_spec": trip_spec or {}
        }

        # Update trip context if provided
        if trip_spec:
            memory = self.memory_manager.get_or_create_conversation(session_id)
            memory.update_trip_context(trip_spec)

        result = await self.graph.ainvoke(initial_state)

        return {
            "message": result.get("final_response", "处理完成"),
            "data": {
                "intent": result.get("intent"),
                "tool_results": result.get("tool_results"),
                "trip_spec": trip_spec
            }
        }


# Simple orchestrator for quick use
class SimpleOrchestrator:
    """Simple orchestrator for direct agent invocation - 专注于多轮对话收集用户需求."""

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.coordinator = CoordinatorAgent()
        self.memory_manager = memory_manager or MemoryManager()

    async def chat(self, user_input: str, session_id: str = "default", trip_spec: Dict = None) -> Dict:
        """Process a chat message - 专注于收集用户需求，使用 LLM 进行智能对话."""
        from datetime import datetime, timedelta

        memory = self.memory_manager.get_or_create_conversation(session_id)

        if trip_spec:
            memory.update_trip_context(trip_spec)

        # 获取上下文
        context = memory.get_context_string()

        # 使用 LLM 分析意图
        intent = await self.coordinator.analyze_intent(user_input, context)

        # 获取当前旅行信息
        current_city = memory.trip_context.get("destination_city") if memory.trip_context else None
        current_start = memory.trip_context.get("start_date") if memory.trip_context else None
        current_end = memory.trip_context.get("end_date") if memory.trip_context else None
        current_travelers = memory.trip_context.get("num_travelers", 1) if memory.trip_context else 1

        # 从意图中提取新信息
        cities = intent.get("cities", [])
        city = cities[0] if cities else current_city

        # 更新日期
        if intent.get("update_date"):
            extracted = intent.get("extracted_date", {})
            month = extracted.get("month", datetime.now().month)
            day = extracted.get("day", datetime.now().day)
            year = extracted.get("year", datetime.now().year)
            if not year:
                year = datetime.now().year
                if month < datetime.now().month:
                    year += 1
            current_start = datetime(year, month, day).strftime("%Y-%m-%d")

        # 更新天数
        if intent.get("update_duration"):
            duration = intent.get("extracted_duration", 3)
            if current_start:
                start = datetime.strptime(current_start, "%Y-%m-%d")
                current_end = (start + timedelta(days=duration - 1)).strftime("%Y-%m-%d")

        # 更新人数
        if intent.get("update_travelers"):
            current_travelers = intent.get("extracted_travelers", 1)

        # 更新旅行上下文 - 增量更新，保留已有值
        update_data = {}

        # 只更新有新值的字段，不要用空字符串覆盖已有值
        if city:
            update_data["destination_city"] = city
        if current_start:
            update_data["start_date"] = current_start
        if current_end:
            update_data["end_date"] = current_end

        update_data["num_travelers"] = current_travelers
        update_data["origin_city"] = memory.trip_context.get("origin_city", "出发地") if memory.trip_context else "出发地"

        memory.update_trip_context(update_data)

        # 构建响应 - 优先使用 LLM 返回的 follow_up_message
        if intent.get("response"):
            # LLM 已经生成了智能响应
            response = intent["response"]
        else:
            # 构建标准响应
            response = self._build_response(city, current_start, current_end, current_travelers, intent)

        # 保存消息
        memory.add_message("user", user_input)
        memory.add_message("assistant", response)

        return {
            "message": response,
            "data": {
                "intent": intent,
                "trip_spec": memory.trip_context,
                "is_complete": bool(city and current_start and current_end)
            }
        }

    def _build_response(self, city: str, start_date: str, end_date: str, travelers: int, intent: Dict) -> str:
        """构建响应消息."""
        # 检查缺失信息
        missing = []
        if not city:
            missing.append("目的地")
        if not start_date:
            missing.append("出发日期")
        if not end_date:
            missing.append("行程天数")

        if city or start_date or end_date:
            # 有新信息更新
            response = "好的，已记录您的信息：\n"
            if city:
                response += f"📍 目的地：{city}\n"
            if start_date:
                response += f"📅 出发日期：{start_date}\n"
            if end_date:
                response += f"📅 返程日期：{end_date}\n"
            response += f"👥 出行人数：{travelers}人\n"

            if missing:
                response += f"\n请告诉我您的{'、'.join(missing)}。"
            else:
                response += "\n✅ 信息已完整，点击「查看行程」查看详细规划！"
        else:
            # 没有提取到信息
            if missing:
                response = f"您好！请告诉我您的{'、'.join(missing)}，我来帮您规划行程。"
            else:
                response = "请告诉我您想去哪里旅游？什么时候出发？"

        return response