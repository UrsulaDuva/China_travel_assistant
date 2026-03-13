# src/agents/transport_agent/agent.py
"""
Transport Agent implementation.
交通查询 Agent，使用 12306 MCP 和飞常准 MCP。
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from src.shared.a2a.base_agent import BaseAgentFrameworkAgent
from src.shared.models import TransportResponse, TransportOutput, TransportOption

logger = logging.getLogger(__name__)


class TransportAgent(BaseAgentFrameworkAgent):
    """
    交通 Agent

    功能：
    - 查询火车票
    - 查询机票
    - 比较不同交通方式
    """

    def get_agent_name(self) -> str:
        return "交通查询助手"

    def get_prompt_name(self) -> str:
        return "transport"

    def get_response_format(self) -> Any:
        return TransportResponse

    async def invoke(
        self,
        user_input: str,
        session_id: str,
        history: list[dict] | None = None,
        history_seq: int | None = None,
    ) -> dict[str, Any]:
        """处理交通查询请求"""
        from src.mcp_clients import Railway12306Client

        # 解析输入
        params = self._parse_input(user_input)
        from_city = params.get("from_city", "北京")
        to_city = params.get("to_city", "上海")
        date = params.get("date", self._get_default_date())
        transport_type = params.get("type", "train")

        transport_options = []

        # 查询火车票
        if transport_type in ["train", "all"]:
            async with Railway12306Client() as client:
                trains = await client.search_trains(
                    from_station=from_city,
                    to_station=to_city,
                    date=date,
                )
                for train in trains[:5]:  # 最多返回5个
                    transport_options.append(TransportOption(
                        mode="train",
                        route=f"{from_city} -> {to_city}",
                        provider=train.get("from_station", ""),
                        train_number=train.get("train_no", ""),
                        departure_time=train.get("departure_time", ""),
                        arrival_time=train.get("arrival_time", ""),
                        duration_mins=self._parse_duration(train.get("duration", "")),
                        price=list(train.get("prices", {}).values())[0] if train.get("prices") else None,
                        currency="CNY",
                        available=True,
                    ))

        # 构建响应
        output = TransportOutput(
            transport_options=transport_options,
            notes=[f"查询日期：{date}", f"共找到 {len(transport_options)} 个交通选项"],
        )

        response = TransportResponse(
            transport_output=output,
            response=self._format_transport_response(from_city, to_city, date, transport_options),
        )

        return {
            "is_task_complete": True,
            "require_user_input": False,
            "content": response.response,
            "data": response.model_dump(),
        }

    def parse_response(self, message: Any) -> dict[str, Any]:
        return {
            "is_task_complete": True,
            "require_user_input": False,
            "content": str(message),
        }

    def _parse_input(self, text: str) -> dict[str, Any]:
        """解析输入参数"""
        params = {}

        # 提取出发城市
        from_keywords = ["从", "出发", "起点"]
        for kw in from_keywords:
            if kw in text:
                idx = text.find(kw)
                # 提取后面的城市名
                for city in self._get_common_cities():
                    if text[idx:idx+10].find(city) != -1:
                        params["from_city"] = city
                        break

        # 提取到达城市
        to_keywords = ["到", "去", "前往", "终点"]
        for kw in to_keywords:
            if kw in text:
                idx = text.find(kw)
                for city in self._get_common_cities():
                    if text[idx:idx+10].find(city) != -1:
                        params["to_city"] = city
                        break

        # 提取日期
        if "明天" in text:
            params["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "后天" in text:
            params["date"] = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            params["date"] = self._get_default_date()

        # 提取交通类型
        if "飞机" in text or "航班" in text:
            params["type"] = "flight"
        elif "火车" in text or "高铁" in text or "动车" in text:
            params["type"] = "train"
        else:
            params["type"] = "all"

        return params

    def _get_common_cities(self) -> list[str]:
        """获取常见城市列表"""
        return ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "南京", "武汉", "重庆",
                "苏州", "天津", "长沙", "郑州", "青岛", "大连", "厦门", "昆明", "三亚", "桂林"]

    def _get_default_date(self) -> str:
        """获取默认日期（明天）"""
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    def _parse_duration(self, duration: str) -> int:
        """解析时长为分钟数"""
        if not duration:
            return 0
        # 格式: "4小时30分"
        hours = 0
        mins = 0
        if "小时" in duration:
            parts = duration.split("小时")
            hours = int(parts[0]) if parts[0].isdigit() else 0
            if len(parts) > 1 and "分" in parts[1]:
                mins = int(parts[1].replace("分", "")) if parts[1].replace("分", "").isdigit() else 0
        return hours * 60 + mins

    def _format_transport_response(
        self,
        from_city: str,
        to_city: str,
        date: str,
        options: list[TransportOption],
    ) -> str:
        """格式化交通响应"""
        lines = [f"🚄 {from_city} → {to_city} 交通查询结果\n"]
        lines.append(f"📅 查询日期：{date}\n")

        if not options:
            lines.append("未找到符合条件的交通选项，请尝试其他日期或路线。")
            return "\n".join(lines)

        lines.append("📋 可选车次/航班：\n")

        for i, opt in enumerate(options[:5], 1):
            if opt.mode == "train":
                lines.append(f"{i}. 🚄 {opt.train_number}")
                lines.append(f"   ⏰ {opt.departure_time} - {opt.arrival_time}")
                if opt.duration_mins:
                    hours = opt.duration_mins // 60
                    mins = opt.duration_mins % 60
                    lines.append(f"   ⏱️ {hours}小时{mins}分钟")
                if opt.price:
                    lines.append(f"   💰 ¥{opt.price}")
                lines.append("")

        return "\n".join(lines)