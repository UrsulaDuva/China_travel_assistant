# src/mcp_clients/base_mcp_client.py
"""
Base MCP Client implementation.
支持 MCP streamableHttp 协议。
"""
from __future__ import annotations

import json
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, AsyncGenerator

import httpx

logger = logging.getLogger(__name__)


class BaseMCPClient(ABC):
    """
    MCP 客户端基类

    支持 MCP streamableHttp 协议：
    - 使用 JSON-RPC 2.0 格式
    - 支持 tools/call 调用
    - 支持流式响应
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._request_id = 0

    async def __aenter__(self) -> "BaseMCPClient":
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _ensure_client(self) -> httpx.AsyncClient:
        """确保 HTTP 客户端已创建"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self._build_headers(),
            )
        return self._client

    def _build_headers(self) -> dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    def get_server_name(self) -> str:
        """返回 MCP 服务器名称"""
        raise NotImplementedError

    def _next_request_id(self) -> int:
        """生成下一个请求 ID"""
        self._request_id += 1
        return self._request_id

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """
        调用 MCP 工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        client = await self._ensure_client()

        # 构建 JSON-RPC 请求
        request_body = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            }
        }

        try:
            logger.info(f"MCP调用: {self.get_server_name()} - {tool_name}")
            logger.debug(f"参数: {arguments}")

            response = await client.post(
                self.base_url,
                json=request_body,
            )
            response.raise_for_status()

            # 解析响应
            result = response.json()

            if "error" in result:
                logger.error(f"MCP错误: {result['error']}")
                raise Exception(f"MCP Error: {result['error']}")

            # 提取内容
            content = result.get("result", {}).get("content", [])
            if content and len(content) > 0:
                text_content = content[0].get("text", "")
                try:
                    return json.loads(text_content)
                except json.JSONDecodeError:
                    return {"text": text_content}

            return result.get("result", {})

        except httpx.HTTPStatusError as e:
            logger.error(f"MCP调用失败: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"MCP调用错误: {e}")
            raise

    async def list_tools(self) -> list[dict[str, Any]]:
        """列出可用工具"""
        client = await self._ensure_client()

        request_body = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/list",
        }

        try:
            response = await client.post(self.base_url, json=request_body)
            response.raise_for_status()
            result = response.json()
            return result.get("result", {}).get("tools", [])
        except Exception as e:
            logger.error(f"获取工具列表失败: {e}")
            return []

    async def stream_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        流式调用 MCP 工具

        Yields:
            流式结果块
        """
        client = await self._ensure_client()

        request_body = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            }
        }

        try:
            async with client.stream(
                "POST",
                self.base_url,
                json=request_body,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            yield {"text": data}

        except Exception as e:
            logger.error(f"MCP流式调用错误: {e}")
            raise

    async def health_check(self) -> bool:
        """检查 MCP 服务健康状态"""
        try:
            tools = await self.list_tools()
            return len(tools) > 0
        except Exception:
            return False

    # 兼容旧接口
    async def _get(self, path: str, params: Optional[dict] = None) -> dict[str, Any]:
        """发送 GET 请求（兼容旧接口）"""
        client = await self._ensure_client()
        url = f"{self.base_url}{path}"

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MCP GET error: {e}")
            raise

    async def _post(self, path: str, data: Optional[dict] = None) -> dict[str, Any]:
        """发送 POST 请求（兼容旧接口）"""
        client = await self._ensure_client()
        url = f"{self.base_url}{path}"

        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MCP POST error: {e}")
            raise