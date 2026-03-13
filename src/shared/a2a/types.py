# src/shared/a2a/types.py
"""
Simple types for agent communication.
"""
from pydantic import BaseModel, Field
from typing import Optional


class AgentSkill(BaseModel):
    """Agent skill definition"""
    id: str
    name: str
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)


class AgentCapabilities(BaseModel):
    """Agent capabilities"""
    streaming: bool = False
    push_notifications: bool = False


class AgentCard(BaseModel):
    """Agent card for discovery"""
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    defaultInputModes: list[str] = Field(default_factory=lambda: ["text"])
    defaultOutputModes: list[str] = Field(default_factory=lambda: ["text"])
    capabilities: Optional[AgentCapabilities] = None
    skills: list[AgentSkill] = Field(default_factory=list)


class HealthStatus:
    """Health status enum"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"