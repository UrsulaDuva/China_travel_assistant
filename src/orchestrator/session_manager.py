# src/orchestrator/session_manager.py
"""
Session Manager - 会话管理器
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SessionManager:
    """
    会话管理器

    职责：
    - 创建和管理会话
    - 存储会话状态
    - 会话超时清理
    """

    def __init__(self, ttl_seconds: int = 86400):
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, dict[str, Any]] = {}

    async def get_or_create(self, session_id: str) -> dict[str, Any]:
        """获取或创建会话"""
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "session_id": session_id,
                "phase": "draft",
                "checkpoint": None,
                "trip_spec": None,
                "discovery_results": None,
                "itinerary": None,
                "messages": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            logger.info(f"创建新会话: {session_id}")

        session = self._sessions[session_id]

        # 更新时间
        session["updated_at"] = datetime.now()

        return session

    async def get(self, session_id: str) -> Optional[dict[str, Any]]:
        """获取会话"""
        return self._sessions.get(session_id)

    async def update(self, session_id: str, updates: dict[str, Any]) -> None:
        """更新会话"""
        if session_id in self._sessions:
            self._sessions[session_id].update(updates)
            self._sessions[session_id]["updated_at"] = datetime.now()

    async def delete(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    async def cleanup_expired(self) -> int:
        """清理过期会话"""
        now = datetime.now()
        expired = []

        for session_id, session in self._sessions.items():
            updated = session.get("updated_at", session.get("created_at", now))
            if now - updated > timedelta(seconds=self.ttl_seconds):
                expired.append(session_id)

        for session_id in expired:
            del self._sessions[session_id]

        if expired:
            logger.info(f"清理了 {len(expired)} 个过期会话")

        return len(expired)

    async def list_sessions(self) -> list[dict[str, Any]]:
        """列出所有会话"""
        return list(self._sessions.values())

    async def get_session_count(self) -> int:
        """获取会话数量"""
        return len(self._sessions)