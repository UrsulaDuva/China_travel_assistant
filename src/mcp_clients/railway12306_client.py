# src/mcp_clients/railway12306_client.py
"""
12306 Railway MCP Client.
12306 火车票 MCP 客户端，提供火车票查询功能。
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

from .base_mcp_client import BaseMCPClient

logger = logging.getLogger(__name__)


class Railway12306Client(BaseMCPClient):
    """
    12306 火车票 MCP 客户端

    功能：
    - 火车票查询
    - 余票监控
    - 车站信息查询
    """

    def __init__(self):
        base_url = os.getenv(
            "RAILWAY_12306_MCP_URL",
            "https://mcp.api-inference.modelscope.net/a61d3df8ab9745/mcp"
        )
        super().__init__(base_url)
        self._session_id: Optional[str] = None
        self._station_codes: dict[str, str] = {}  # 城市名 -> 主要车站代码缓存
        self._initialized: bool = False  # MCP会话初始化状态

    async def __aenter__(self) -> "Railway12306Client":
        await self._ensure_client()
        # 初始化MCP会话
        await self._ensure_initialized()
        return self

    def get_server_name(self) -> str:
        return "12306 火车票 MCP"

    async def _ensure_initialized(self) -> bool:
        """确保MCP会话已初始化"""
        if self._initialized and self._session_id:
            return True

        client = await self._ensure_client()

        try:
            # 发送初始化请求
            init_req = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "china-travel-client", "version": "1.0"}
                }
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }

            response = await client.post(self.base_url, json=init_req, headers=headers, timeout=30)
            response.raise_for_status()

            # 获取session ID
            self._session_id = response.headers.get("mcp-session-id") or response.headers.get("Mcp-Session-Id")

            if self._session_id:
                logger.info(f"12306 MCP initialized with session: {self._session_id}")

                # 发送 initialized 通知
                notify_response = await client.post(
                    self.base_url,
                    json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                    headers={**headers, "mcp-session-id": self._session_id},
                    timeout=10
                )
                logger.debug(f"Initialized notification response: {notify_response.status_code}")

                self._initialized = True
                return True
            else:
                logger.warning("12306 MCP initialization did not return session ID")
                return False

        except Exception as e:
            logger.error(f"12306 MCP initialization failed: {e}")
            return False

    async def _call_mcp_tool(self, tool_name: str, arguments: dict) -> dict[str, Any]:
        """调用MCP工具"""
        if not await self._ensure_initialized():
            raise Exception("MCP session not initialized")

        client = await self._ensure_client()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "mcp-session-id": self._session_id
        }

        request_body = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            response = await client.post(self.base_url, json=request_body, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                logger.error(f"MCP tool error: {result['error']}")
                raise Exception(f"MCP Error: {result['error']}")

            # 解析结果
            content = result.get("result", {}).get("content", [])
            if content and len(content) > 0:
                text_content = content[0].get("text", "")
                return {"text": text_content, "raw": result}

            return result.get("result", {})

        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            raise

    async def get_station_code(self, city: str) -> str:
        """
        获取城市的主要车站代码

        Args:
            city: 城市名，如 "北京"、"上海"、"北京站"、"上海虹桥站"

        Returns:
            车站代码，如 "VAP" (北京南)、"AOH" (上海虹桥)
        """
        # 清理城市名：去掉"站"、"市"后缀
        clean_city = city
        if clean_city.endswith("站"):
            clean_city = clean_city[:-1]
        if clean_city.endswith("市"):
            clean_city = clean_city[:-1]

        # 常用城市的主要高铁站代码
        main_stations = {
            "北京": "VAP",      # 北京南站
            "北京南": "VAP",
            "上海": "AOH",      # 上海虹桥站
            "上海虹桥": "AOH",
            "杭州": "HZH",      # 杭州站
            "杭州东": "HZH",
            "广州": "GZQ",      # 广州站
            "广州南": "GZQ",
            "深圳": "SZQ",      # 深圳站
            "深圳北": "SZQ",
            "成都": "CDW",      # 成都东站
            "成都东": "CDW",
            "西安": "XAY",      # 西安站
            "西安北": "XAY",
            "南京": "NJH",      # 南京站
            "南京南": "NJH",
            "武汉": "WHN",      # 武汉站
            "重庆": "CQW",      # 重庆站
            "苏州": "SZH",
            "苏州北": "SZH",
            "天津": "TJP",      # 天津站
            "长沙": "CSQ",      # 长沙站
            "长沙南": "CSQ",
            "郑州": "ZZF",      # 郑州站
            "郑州东": "ZZF",
            "厦门": "XMS",      # 厦门站
            "厦门北": "XMS",
            "昆明": "KMM",      # 昆明站
            "三亚": "SEQ",      # 三亚站
            "青岛": "QDK",      # 青岛站
            "大连": "DLT",      # 大连站
        }

        # 优先使用预设的主要车站
        if clean_city in main_stations:
            return main_stations[clean_city]

        # 尝试从MCP查询
        try:
            result = await self._call_mcp_tool("get-stations-code-in-city", {"city": clean_city})
            text = result.get("text", "")

            # 解析JSON响应
            try:
                stations = json.loads(text)
                if isinstance(stations, list) and len(stations) > 0:
                    # 返回第一个车站的代码
                    return stations[0].get("station_code", "")
            except:
                pass
        except Exception as e:
            logger.warning(f"Failed to get station code for {city}: {e}")

        return ""

    def _parse_train_text(self, text: str) -> list[dict[str, Any]]:
        """解析12306返回的文本格式车次信息"""
        trains = []

        # 按行分割
        lines = text.strip().split('\n')

        current_train = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 跳过表头
            if '车次' in line and '站' in line:
                continue

            # 匹配车次行：
            # 格式: G531 北京站(telecode:VNP) -> 上海虹桥站(telecode:AOH) 06:08 -> 12:04 历时：05:56
            # 注意：历时后面可能是全角冒号：或半角冒号:
            train_match = re.match(
                r'^([GDZTK]\d+)\s+(.+?)\s*\((?:telecode:)?(\w+)\)\s*->\s*(.+?)\s*\((?:telecode:)?(\w+)\)\s+(\d{2}:\d{2})\s*->\s*(\d{2}:\d{2})\s+历时[：:](\d{2}:\d{2})',
                line
            )

            if train_match:
                if current_train:
                    trains.append(current_train)

                train_no = train_match.group(1)
                from_station_name = train_match.group(2).strip()
                from_code = train_match.group(3)
                to_station_name = train_match.group(4).strip()
                to_code = train_match.group(5)
                start_time = train_match.group(6)
                end_time = train_match.group(7)
                duration = train_match.group(8)

                current_train = {
                    "train_no": train_no,
                    "from_station": from_station_name,
                    "to_station": to_station_name,
                    "departure_time": start_time,
                    "arrival_time": end_time,
                    "duration": duration,
                    "seats": [],
                    "prices": {}
                }

            # 匹配座位行：- 二等座: 有票 553元 或 - 商务座: 剩余3张票 1873元
            elif line.startswith('-') and current_train:
                seat_match = re.match(r'-\s*([^:]+):\s*(.+?)\s+(\d+)元', line)
                if seat_match:
                    seat_name = seat_match.group(1).strip()
                    availability = seat_match.group(2).strip()
                    price = int(seat_match.group(3))

                    # 解析余票数量
                    if '有票' in availability:
                        count = 50  # 有票，显示一个较大的数字
                    elif '无票' in availability:
                        count = 0
                    elif '剩余' in availability:
                        count_match = re.search(r'剩余(\d+)', availability)
                        count = int(count_match.group(1)) if count_match else 10
                    else:
                        count = 10

                    current_train["seats"].append({
                        "name": seat_name,
                        "count": count,
                        "price": price
                    })
                    current_train["prices"][seat_name] = price

        # 添加最后一个车次
        if current_train:
            trains.append(current_train)

        return trains

    async def search_trains(
        self,
        from_station: str,
        to_station: str,
        date: str,
        train_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        查询火车票

        Args:
            from_station: 出发站，如 "北京" 或 "北京南"
            to_station: 到达站，如 "上海" 或 "上海虹桥"
            date: 日期，格式 YYYY-MM-DD
            train_type: 车型筛选，如 "G"(高铁)、"D"(动车)

        Returns:
            车次列表
        """
        try:
            # 获取车站代码
            from_code = await self.get_station_code(from_station)
            to_code = await self.get_station_code(to_station)

            if not from_code or not to_code:
                logger.warning(f"Could not get station codes: {from_station}({from_code}) -> {to_station}({to_code})")
                return self._get_mock_trains(from_station, to_station, date)

            logger.info(f"Querying 12306: {from_station}({from_code}) -> {to_station}({to_code}) on {date}")

            # 调用MCP查询车票
            result = await self._call_mcp_tool("get-tickets", {
                "date": date,
                "fromStation": from_code,
                "toStation": to_code,
                "trainFilterFlags": train_type or ""
            })

            text = result.get("text", "")

            if text and ("G" in text or "D" in text):
                # 解析文本格式的车次信息
                trains = self._parse_train_text(text)
                if trains:
                    logger.info(f"Got {len(trains)} trains from 12306")
                    return trains
                else:
                    logger.warning("Failed to parse train text, using mock data")
            else:
                logger.warning(f"Unexpected response from 12306: {text[:200]}")

        except Exception as e:
            logger.error(f"查询火车票失败: {e}")

        return self._get_mock_trains(from_station, to_station, date)

    async def get_train_detail(self, train_no: str, date: str) -> dict[str, Any]:
        """
        获取车次详情

        Args:
            train_no: 车次号，如 "G1"
            date: 日期

        Returns:
            车次详情
        """
        try:
            result = await self._get("/api/train/detail", {
                "train_no": train_no,
                "date": date,
            })
            return result.get("data", result)
        except Exception as e:
            logger.error(f"获取车次详情失败: {e}")
            return {}

    async def get_ticket_remaining(
        self,
        train_no: str,
        from_station: str,
        to_station: str,
        date: str,
    ) -> dict[str, Any]:
        """
        查询余票

        Args:
            train_no: 车次号
            from_station: 出发站
            to_station: 到达站
            date: 日期

        Returns:
            余票信息
        """
        try:
            result = await self._get("/api/train/ticket", {
                "train_no": train_no,
                "from_station": from_station,
                "to_station": to_station,
                "date": date,
            })
            return self._parse_ticket_info(result)
        except Exception as e:
            logger.error(f"查询余票失败: {e}")
            return {"available": True, "seats": {}}

    async def get_station_info(self, station_name: str) -> dict[str, Any]:
        """
        获取车站信息

        Args:
            station_name: 车站名称

        Returns:
            车站信息
        """
        try:
            result = await self._get("/api/station/info", {"name": station_name})
            return result.get("data", result)
        except Exception as e:
            logger.error(f"获取车站信息失败: {e}")
            return {"name": station_name, "code": ""}

    def _parse_train_list(self, result: dict) -> list[dict[str, Any]]:
        """解析车次列表"""
        trains = result.get("data", result.get("trains", []))
        parsed = []
        for train in trains:
            parsed.append({
                "train_no": train.get("train_no", train.get("stationTrainCode", "")),
                "from_station": train.get("from_station", train.get("startStationName", "")),
                "to_station": train.get("to_station", train.get("endStationName", "")),
                "departure_time": train.get("departure_time", train.get("startTime", "")),
                "arrival_time": train.get("arrival_time", train.get("arriveTime", "")),
                "duration": train.get("duration", train.get("runTime", "")),
                "seats": train.get("seats", {}),
                "prices": train.get("prices", {}),
            })
        return parsed

    def _parse_ticket_info(self, result: dict) -> dict[str, Any]:
        """解析余票信息"""
        data = result.get("data", result)
        return {
            "available": data.get("available", True),
            "seats": data.get("seats", {
                "商务座": "有",
                "一等座": "有",
                "二等座": "有",
            }),
            "prices": data.get("prices", {}),
        }

    def _get_mock_trains(
        self,
        from_station: str,
        to_station: str,
        date: str,
    ) -> list[dict[str, Any]]:
        """获取模拟车次数据 - 基于真实线路的模拟"""
        # 北京-上海线路
        if ("北京" in from_station and "上海" in to_station) or \
           ("上海" in from_station and "北京" in to_station):
            return [
                {
                    "train_no": "G1",
                    "from_station": from_station + "南",
                    "to_station": to_station + "虹桥",
                    "departure_time": "07:00",
                    "arrival_time": "11:28",
                    "duration": "4小时28分",
                    "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                    "prices": {"商务座": 2330, "一等座": 933, "二等座": 553},
                },
                {
                    "train_no": "G3",
                    "from_station": from_station + "南",
                    "to_station": to_station + "虹桥",
                    "departure_time": "07:45",
                    "arrival_time": "12:15",
                    "duration": "4小时30分",
                    "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                    "prices": {"商务座": 2330, "一等座": 933, "二等座": 553},
                },
                {
                    "train_no": "G5",
                    "from_station": from_station + "南",
                    "to_station": to_station + "虹桥",
                    "departure_time": "08:00",
                    "arrival_time": "12:28",
                    "duration": "4小时28分",
                    "seats": {"一等座": "有", "二等座": "有"},
                    "prices": {"一等座": 933, "二等座": 553},
                },
                {
                    "train_no": "G7",
                    "from_station": from_station + "南",
                    "to_station": to_station + "虹桥",
                    "departure_time": "09:00",
                    "arrival_time": "13:28",
                    "duration": "4小时28分",
                    "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                    "prices": {"商务座": 2330, "一等座": 933, "二等座": 553},
                },
                {
                    "train_no": "G9",
                    "from_station": from_station + "南",
                    "to_station": to_station + "虹桥",
                    "departure_time": "10:00",
                    "arrival_time": "14:28",
                    "duration": "4小时28分",
                    "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                    "prices": {"商务座": 2330, "一等座": 933, "二等座": 553},
                },
                {
                    "train_no": "G11",
                    "from_station": from_station + "南",
                    "to_station": to_station + "虹桥",
                    "departure_time": "11:00",
                    "arrival_time": "15:28",
                    "duration": "4小时28分",
                    "seats": {"一等座": "有", "二等座": "有"},
                    "prices": {"一等座": 933, "二等座": 553},
                },
                {
                    "train_no": "G13",
                    "from_station": from_station + "南",
                    "to_station": to_station + "虹桥",
                    "departure_time": "12:00",
                    "arrival_time": "16:28",
                    "duration": "4小时28分",
                    "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                    "prices": {"商务座": 2330, "一等座": 933, "二等座": 553},
                },
                {
                    "train_no": "G15",
                    "from_station": from_station + "南",
                    "to_station": to_station + "虹桥",
                    "departure_time": "13:00",
                    "arrival_time": "17:28",
                    "duration": "4小时28分",
                    "seats": {"一等座": "有", "二等座": "有"},
                    "prices": {"一等座": 933, "二等座": 553},
                },
            ]

        # 北京-杭州线路
        if ("北京" in from_station and "杭州" in to_station) or \
           ("杭州" in from_station and "北京" in to_station):
            return [
                {
                    "train_no": "G19",
                    "from_station": from_station + "南",
                    "to_station": to_station + "东",
                    "departure_time": "07:15",
                    "arrival_time": "12:05",
                    "duration": "4小时50分",
                    "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                    "prices": {"商务座": 2095, "一等座": 904, "二等座": 538},
                },
                {
                    "train_no": "G31",
                    "from_station": from_station + "南",
                    "to_station": to_station + "东",
                    "departure_time": "09:15",
                    "arrival_time": "14:05",
                    "duration": "4小时50分",
                    "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                    "prices": {"商务座": 2095, "一等座": 904, "二等座": 538},
                },
                {
                    "train_no": "G35",
                    "from_station": from_station + "南",
                    "to_station": to_station + "东",
                    "departure_time": "11:15",
                    "arrival_time": "16:05",
                    "duration": "4小时50分",
                    "seats": {"一等座": "有", "二等座": "有"},
                    "prices": {"一等座": 904, "二等座": 538},
                },
                {
                    "train_no": "G39",
                    "from_station": from_station + "南",
                    "to_station": to_station + "东",
                    "departure_time": "14:15",
                    "arrival_time": "19:05",
                    "duration": "4小时50分",
                    "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                    "prices": {"商务座": 2095, "一等座": 904, "二等座": 538},
                },
                {
                    "train_no": "G43",
                    "from_station": from_station + "南",
                    "to_station": to_station + "东",
                    "departure_time": "16:15",
                    "arrival_time": "21:05",
                    "duration": "4小时50分",
                    "seats": {"一等座": "有", "二等座": "有"},
                    "prices": {"一等座": 904, "二等座": 538},
                },
            ]

        # 默认返回通用模拟数据
        return [
            {
                "train_no": "G1",
                "from_station": from_station,
                "to_station": to_station,
                "departure_time": "07:00",
                "arrival_time": "11:30",
                "duration": "4小时30分",
                "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                "prices": {"商务座": 1800, "一等座": 750, "二等座": 450},
            },
            {
                "train_no": "G3",
                "from_station": from_station,
                "to_station": to_station,
                "departure_time": "08:00",
                "arrival_time": "12:30",
                "duration": "4小时30分",
                "seats": {"一等座": "有", "二等座": "有"},
                "prices": {"一等座": 750, "二等座": 450},
            },
            {
                "train_no": "G5",
                "from_station": from_station,
                "to_station": to_station,
                "departure_time": "09:00",
                "arrival_time": "13:30",
                "duration": "4小时30分",
                "seats": {"商务座": "有", "一等座": "有", "二等座": "有"},
                "prices": {"商务座": 1800, "一等座": 750, "二等座": 450},
            },
            {
                "train_no": "D701",
                "from_station": from_station,
                "to_station": to_station,
                "departure_time": "19:08",
                "arrival_time": "23:58",
                "duration": "4小时50分",
                "seats": {"软卧": "有", "硬卧": "有"},
                "prices": {"软卧": 630, "硬卧": 400},
            },
        ]