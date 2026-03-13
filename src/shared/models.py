# src/shared/models.py
"""
Core data models for China Travel A2A system.
Based on the reference project multi-agent-travel-planner-a2a.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Enums
# =============================================================================

class ConsultationStatus(str, Enum):
    """会话状态"""
    DRAFT = "draft"
    CLARIFICATION = "clarification"
    DISCOVERY = "discovery"
    PLANNING = "planning"
    READY_TO_BOOK = "ready_to_book"
    BOOKING = "booking"
    PARTIALLY_BOOKED = "partially_booked"
    FULLY_BOOKED = "fully_booked"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class BookingStatus(str, Enum):
    """预订状态"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    MODIFIED = "modified"
    CANCELLED = "cancelled"
    FAILED = "failed"


class BookingAction(str, Enum):
    """预订操作"""
    CREATE = "create"
    MODIFY = "modify"
    CANCEL = "cancel"


class BudgetMode(str, Enum):
    """预算模式"""
    PROPOSE = "propose"
    VALIDATE = "validate"
    TRACK = "track"
    REALLOCATE = "reallocate"


class IntentType(str, Enum):
    """用户意图类型"""
    # 工作流意图
    START_TRIP_PLANNING = "start_trip_planning"
    CONTINUE_CLARIFICATION = "continue_clarification"
    APPROVE_TRIP_SPEC = "approve_trip_spec"
    APPROVE_ITINERARY = "approve_itinerary"
    START_BOOKING = "start_booking"
    CONFIRM_BOOKING = "confirm_booking"

    # 查询意图
    SEARCH_WEATHER = "search_weather"
    SEARCH_POI = "search_poi"
    SEARCH_STAY = "search_stay"
    SEARCH_TRANSPORT = "search_transport"
    SEARCH_DINING = "search_dining"
    SEARCH_GUIDE = "search_guide"

    # 修改意图
    MODIFY_TRIP = "modify_trip"
    MODIFY_BOOKING = "modify_booking"
    CANCEL_BOOKING = "cancel_booking"

    # 元意图
    HELP = "help"
    STATUS = "status"
    CANCEL = "cancel"
    GENERAL_QUESTION = "general_question"


class RoutingDecision(str, Enum):
    """路由决策"""
    WORKFLOW = "workflow"      # 进入工作流状态机
    AGENT = "agent"            # 直接调用Agent
    TOOL = "tool"              # 调用工具
    CLARIFY = "clarify"        # 需要澄清


class HealthStatus(str, Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# =============================================================================
# Common Primitives
# =============================================================================

class Source(BaseModel):
    """数据来源"""
    model_config = ConfigDict(extra="forbid")
    title: str
    url: str


# =============================================================================
# Clarifier Agent Models
# =============================================================================

class TripSpec(BaseModel):
    """行程需求规格"""
    model_config = ConfigDict(extra="forbid")
    destination_city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    num_travelers: int = Field(default=1, ge=1, description="旅行人数")
    budget_per_person: float = Field(default=5000.0, ge=0, description="人均预算")
    budget_currency: str = Field(default="CNY", description="货币单位")
    origin_city: str = Field(default="北京", description="出发城市")
    interests: List[str] = Field(default_factory=list, description="兴趣标签")
    constraints: List[str] = Field(default_factory=list, description="约束条件")


class ClarifierResponse(BaseModel):
    """Clarifier Agent响应"""
    model_config = ConfigDict(extra="forbid")
    trip_spec: Optional[TripSpec] = None
    response: Optional[str] = None


# =============================================================================
# Weather Agent Models
# =============================================================================

class WeatherInfo(BaseModel):
    """天气信息"""
    model_config = ConfigDict(extra="forbid")
    city: str
    date: str
    weather: str
    temperature_high: int
    temperature_low: int
    humidity: Optional[int] = None
    wind: Optional[str] = None
    tips: Optional[str] = None


class WeatherResponse(BaseModel):
    """Weather Agent响应"""
    model_config = ConfigDict(extra="forbid")
    weather_info: Optional[WeatherInfo] = None
    forecast: List[WeatherInfo] = Field(default_factory=list)
    response: Optional[str] = None


# =============================================================================
# Transport Agent Models
# =============================================================================

TransportMode = Literal["flight", "train", "bus", "car"]


class TransportOption(BaseModel):
    """交通选项"""
    model_config = ConfigDict(extra="forbid")
    mode: TransportMode
    route: str                           # e.g., "北京 -> 上海"
    provider: Optional[str] = None       # e.g., "中国国航", "G1"
    train_number: Optional[str] = None   # 车次/航班号
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration_mins: Optional[int] = None
    price: Optional[float] = None
    currency: str = "CNY"
    available: bool = True
    source: Optional[Source] = None


class TransportOutput(BaseModel):
    """交通输出"""
    model_config = ConfigDict(extra="forbid")
    transport_options: List[TransportOption] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class TransportResponse(BaseModel):
    """Transport Agent响应"""
    model_config = ConfigDict(extra="forbid")
    transport_output: Optional[TransportOutput] = None
    response: Optional[str] = None


# =============================================================================
# POI/Attraction Agent Models
# =============================================================================

class POI(BaseModel):
    """景点信息"""
    model_config = ConfigDict(extra="forbid")
    name: str
    city: str
    area: Optional[str] = None
    category: Optional[str] = None           # e.g., "自然风光", "人文历史"
    tags: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    ticket_price: Optional[float] = None
    currency: str = "CNY"
    open_time: Optional[str] = None
    duration_hours: Optional[float] = None   # 建议游览时长
    description: Optional[str] = None
    source: Optional[Source] = None


class POISearchOutput(BaseModel):
    """POI搜索输出"""
    model_config = ConfigDict(extra="forbid")
    pois: List[POI] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class POISearchResponse(BaseModel):
    """POI Agent响应"""
    model_config = ConfigDict(extra="forbid")
    search_output: Optional[POISearchOutput] = None
    response: Optional[str] = None


# =============================================================================
# Food/Dining Agent Models
# =============================================================================

class Restaurant(BaseModel):
    """餐厅信息"""
    model_config = ConfigDict(extra="forbid")
    name: str
    city: str
    area: Optional[str] = None
    cuisine: Optional[str] = None           # e.g., "本帮菜", "川菜"
    price_range: Optional[str] = None       # e.g., "¥¥", "¥¥¥"
    avg_price: Optional[float] = None
    rating: Optional[float] = None
    signature_dishes: List[str] = Field(default_factory=list)
    address: Optional[str] = None
    opening_hours: Optional[str] = None
    source: Optional[Source] = None


class DiningOutput(BaseModel):
    """美食输出"""
    model_config = ConfigDict(extra="forbid")
    restaurants: List[Restaurant] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class DiningResponse(BaseModel):
    """Dining Agent响应"""
    model_config = ConfigDict(extra="forbid")
    dining_output: Optional[DiningOutput] = None
    response: Optional[str] = None


# =============================================================================
# Hotel/Stay Agent Models
# =============================================================================

class Hotel(BaseModel):
    """酒店信息"""
    model_config = ConfigDict(extra="forbid")
    name: str
    city: str
    area: Optional[str] = None
    star_rating: Optional[int] = None
    price_per_night: Optional[float] = None
    currency: str = "CNY"
    rating: Optional[float] = None
    amenities: List[str] = Field(default_factory=list)
    address: Optional[str] = None
    distance_to_center: Optional[float] = None  # km
    source: Optional[Source] = None


class StayOutput(BaseModel):
    """住宿输出"""
    model_config = ConfigDict(extra="forbid")
    hotels: List[Hotel] = Field(default_factory=list)
    recommended_areas: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class StayResponse(BaseModel):
    """Stay Agent响应"""
    model_config = ConfigDict(extra="forbid")
    stay_output: Optional[StayOutput] = None
    response: Optional[str] = None


# =============================================================================
# Guide Agent Models
# =============================================================================

class GuideNote(BaseModel):
    """攻略笔记"""
    model_config = ConfigDict(extra="forbid")
    title: str
    author: Optional[str] = None
    city: str
    summary: str
    tags: List[str] = Field(default_factory=list)
    likes: Optional[int] = None
    url: Optional[str] = None


class GuideOutput(BaseModel):
    """攻略输出"""
    model_config = ConfigDict(extra="forbid")
    guides: List[GuideNote] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)


class GuideResponse(BaseModel):
    """Guide Agent响应"""
    model_config = ConfigDict(extra="forbid")
    guide_output: Optional[GuideOutput] = None
    response: Optional[str] = None


# =============================================================================
# Itinerary Models
# =============================================================================

class ItinerarySlot(BaseModel):
    """行程时间槽"""
    model_config = ConfigDict(extra="forbid")
    start_time: str                         # HH:MM
    end_time: str                           # HH:MM
    activity: str                           # 活动内容
    location: Optional[str] = None
    category: str                           # poi/dining/transport/event/hotel
    item_ref: Optional[str] = None          # 引用的具体项目ID
    estimated_cost: Optional[float] = None
    currency: str = "CNY"
    notes: Optional[str] = None


class ItineraryDay(BaseModel):
    """单日行程"""
    model_config = ConfigDict(extra="forbid")
    date: str                               # YYYY-MM-DD
    weekday: Optional[str] = None           # 周几
    slots: List[ItinerarySlot] = Field(default_factory=list)
    day_summary: Optional[str] = None
    total_cost: Optional[float] = None


class Itinerary(BaseModel):
    """完整行程"""
    model_config = ConfigDict(extra="forbid")
    days: List[ItineraryDay] = Field(default_factory=list)
    total_estimated_cost: Optional[float] = None
    currency: str = "CNY"
    notes: List[str] = Field(default_factory=list)


class RouteResponse(BaseModel):
    """Route Agent响应"""
    model_config = ConfigDict(extra="forbid")
    itinerary: Optional[Itinerary] = None
    response: Optional[str] = None


# =============================================================================
# Budget Agent Models
# =============================================================================

class BudgetAllocation(BaseModel):
    """预算分配"""
    model_config = ConfigDict(extra="forbid")
    category: str
    amount: float
    currency: str = "CNY"


class BudgetProposal(BaseModel):
    """预算建议"""
    model_config = ConfigDict(extra="forbid")
    total_budget: float
    currency: str = "CNY"
    allocations: List[BudgetAllocation] = Field(default_factory=list)
    rationale: Optional[str] = None


class BudgetValidation(BaseModel):
    """预算验证"""
    model_config = ConfigDict(extra="forbid")
    valid: bool
    total_budget: float
    total_cost: float
    currency: str = "CNY"
    over_budget: bool = False
    warnings: List[str] = Field(default_factory=list)


class BudgetResponse(BaseModel):
    """Budget Agent响应"""
    model_config = ConfigDict(extra="forbid")
    mode: Optional[BudgetMode] = None
    proposal: Optional[BudgetProposal] = None
    validation: Optional[BudgetValidation] = None
    response: Optional[str] = None


# =============================================================================
# Validator Agent Models
# =============================================================================

class ValidationIssue(BaseModel):
    """验证问题"""
    model_config = ConfigDict(extra="forbid")
    severity: str                           # error/warning/info
    category: str                           # time/budget/distance/availability
    message: str
    suggestion: Optional[str] = None


class ValidationResult(BaseModel):
    """验证结果"""
    model_config = ConfigDict(extra="forbid")
    passed: bool
    score: float = 0.0                      # 0-100
    issues: List[ValidationIssue] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ValidatorResponse(BaseModel):
    """Validator Agent响应"""
    model_config = ConfigDict(extra="forbid")
    validation_result: Optional[ValidationResult] = None
    response: Optional[str] = None


# =============================================================================
# Booking Agent Models
# =============================================================================

class BookingItem(BaseModel):
    """预订项目"""
    model_config = ConfigDict(extra="forbid")
    id: Optional[str] = None
    type: str                               # hotel/flight/train/ticket
    name: str
    provider: Optional[str] = None
    status: BookingStatus = BookingStatus.PENDING
    confirmation_number: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    price: Optional[float] = None
    currency: str = "CNY"


class BookingResult(BaseModel):
    """预订结果"""
    model_config = ConfigDict(extra="forbid")
    success: bool
    booking_id: Optional[str] = None
    status: BookingStatus = BookingStatus.PENDING
    error_message: Optional[str] = None
    details: Optional[BookingItem] = None


class BookingResponse(BaseModel):
    """Booking Agent响应"""
    model_config = ConfigDict(extra="forbid")
    action: Optional[BookingAction] = None
    result: Optional[BookingResult] = None
    response: Optional[str] = None


# =============================================================================
# Aggregator Agent Models
# =============================================================================

class DiscoveryResults(BaseModel):
    """Discovery阶段汇总结果"""
    model_config = ConfigDict(extra="forbid")
    weather: Optional[WeatherOutput] = None
    transport: Optional[TransportOutput] = None
    attractions: Optional[POISearchOutput] = None
    dining: Optional[DiningOutput] = None
    hotels: Optional[StayOutput] = None
    guides: Optional[GuideOutput] = None


class AggregatorResponse(BaseModel):
    """Aggregator Agent响应"""
    model_config = ConfigDict(extra="forbid")
    aggregated_results: Optional[DiscoveryResults] = None
    response: Optional[str] = None


# =============================================================================
# Orchestrator Models
# =============================================================================

class OrchestratorAction(str, Enum):
    """Orchestrator动作"""
    CALL_AGENTS = "call_agents"
    REQUEST_APPROVAL = "request_approval"
    UPDATE_STATE = "update_state"
    RESPOND_TO_USER = "respond_to_user"


class OrchestratorOutput(BaseModel):
    """Orchestrator输出"""
    model_config = ConfigDict(extra="forbid")
    action: OrchestratorAction
    agents: List[str] = Field(default_factory=list)
    message: Optional[str] = None
    checkpoint_type: Optional[str] = None
    summary: Optional[str] = None
    available_actions: List[str] = Field(default_factory=list)


class OrchestratorResponse(BaseModel):
    """Orchestrator响应"""
    model_config = ConfigDict(extra="forbid")
    orchestrator_output: Optional[OrchestratorOutput] = None
    response: Optional[str] = None


class RoutingResult(BaseModel):
    """路由结果"""
    model_config = ConfigDict(extra="forbid")
    decision: RoutingDecision
    confidence: float = Field(..., ge=0.0, le=1.0)
    intent: Optional[IntentType] = None
    target_agent: Optional[str] = None
    clarification_prompt: Optional[str] = None


# =============================================================================
# Health Check Models
# =============================================================================

class HealthResponse(BaseModel):
    """健康检查响应"""
    model_config = ConfigDict(extra="forbid")
    status: HealthStatus = HealthStatus.HEALTHY
    agent_name: str
    version: str
    message: Optional[str] = None


# =============================================================================
# Consultation/Session Models
# =============================================================================

class Consultation(BaseModel):
    """旅行咨询会话"""
    model_config = ConfigDict(extra="forbid")
    id: str = Field(..., pattern=r"^cons_")
    session_id: str
    trip_spec: Optional[TripSpec] = None
    discovery_results: Optional[DiscoveryResults] = None
    itinerary: Optional[Itinerary] = None
    status: ConsultationStatus = ConsultationStatus.DRAFT
    bookings: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class WorkflowState(BaseModel):
    """工作流状态"""
    model_config = ConfigDict(extra="forbid")
    session_id: str
    consultation_id: Optional[str] = None
    phase: str = "draft"
    checkpoint: Optional[str] = None
    current_step: int = 0
    retry_count: int = 0
    failed_agents: List[str] = Field(default_factory=list)
    cached_results: dict[str, Any] = Field(default_factory=dict)