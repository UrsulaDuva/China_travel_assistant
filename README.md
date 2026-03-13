# China Travel Pro

基于 LangChain + LangGraph 的智能多 Agent 中国旅游规划系统

## 项目概述

一站式中国境内智能旅行规划平台，通过 LangChain Multi-Agent 架构，结合 MCP (Model Context Protocol) 数据服务，为用户提供智能化的行程规划、票务查询、美食推荐、景点推荐等全流程服务。

## 技术架构

### Multi-Agent 智能层 (新增)

```
┌─────────────────────────────────────────────────────────────┐
│                    Coordinator Agent                        │
│                  (主协调器 - 意图分析)                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Attraction    │   │    Food       │   │  Transport    │
│   Agent       │   │   Agent       │   │    Agent      │
│ (景点专家)     │   │ (美食专家)     │   │ (交通专家)     │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                       │
│              (工作流编排 - 状态管理)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tools Layer                          │
│    (天气 | 景点 | 美食 | 火车票 | 攻略 | 地图)                 │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

- **前端**: Vue 3 + Vite + Pinia + Tailwind CSS
- **后端**: FastAPI + Python 3.11
- **Agent框架**: LangChain + LangGraph
- **LLM**: Qwen-Plus (DashScope)
- **数据协议**: MCP (Model Context Protocol)
- **向量存储**: FAISS
- **会话管理**: Redis (可选)

## 快速开始

> 详细部署指南请参阅 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 1. 克隆项目

```bash
git clone https://github.com/UrsulaDuva/A2A_China_travel_assistant.git
cd A2A_China_travel_assistant
```

### 2. 安装依赖

```bash
cd china-travel-pro
uv sync
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填写以下 API Keys:
# - DASHSCOPE_API_KEY (阿里云 DashScope)
# - AMAP_API_KEY (高德地图)
# - RAILWAY_12306_MCP_URL (12306 MCP 服务)
```

### 3. 启动服务

```bash
# 启动 Orchestrator API (集成 Multi-Agent)
uv run python -m src.run_orchestrator

# 启动前端 (新终端)
cd src/frontend
npm install && npm run dev
```

### 4. 访问

- 前端: http://localhost:5173
- Orchestrator API: http://localhost:10000
- API 文档: http://localhost:10000/docs

## 项目结构

```
china-travel-pro/
├── src/
│   ├── agent_core/         # Multi-Agent 智能层
│   │   ├── agents/         # 专业 Agent 实现
│   │   ├── tools/          # LangChain Tools (MCP封装)
│   │   ├── graph/          # LangGraph 工作流
│   │   └── memory/         # 对话记忆 & 向量存储
│   ├── orchestrator/       # API 编排层
│   │   ├── api/            # FastAPI 应用
│   │   └── session_manager.py
│   ├── mcp_clients/        # MCP 客户端
│   │   ├── moji_weather_client.py
│   │   ├── amap_client.py
│   │   ├── railway12306_client.py
│   │   └── douyin_client.py
│   ├── shared/             # 共享模块
│   └── frontend/           # Vue3 前端
├── tests/
├── docs/
└── pyproject.toml
```

## Agent 列表

### 智能层 Agent (LangChain)

| Agent | 类型 | 职责 |
|-------|------|------|
| Coordinator | LangChain | 意图分析，任务分配 |
| TripPlanning | LangChain | 整体行程规划 |
| Attraction | LangChain | 景点推荐与游玩建议 |
| Food | LangChain | 美食推荐与餐厅信息 |
| Transport | LangChain | 交通查询与出行建议 |
| Budget | LangChain | 预算规划与费用估算 |

### 数据层 Agent (MCP)

| Agent | 端口 | 数据源 |
|-------|------|--------|
| Weather | MCP | 墨迹天气 |
| Transport | MCP | 12306火车票 |
| Attraction | MCP | 高德地图POI |
| Food | MCP | 高德地图POI |
| Guide | MCP | 抖音达人推荐 |

## API 端点

### 核心接口

- `POST /chat` - 智能对话 (Multi-Agent 处理)
- `GET /api/weather/{city}` - 天气查询
- `GET /api/attractions/{city}` - 景点查询
- `GET /api/food/{city}` - 美食查询
- `GET /api/trains` - 火车票查询
- `GET /api/guide/{city}` - 攻略查询

### Multi-Agent 接口

- `POST /api/trip-context` - 更新行程上下文
- `GET /api/agent-status` - 获取 Agent 状态

## 功能特性

1. **智能意图理解** - 自动分析用户需求，识别城市、日期、意图类型
2. **多维度推荐** - 景点、美食、交通一站式服务
3. **上下文记忆** - 支持多轮对话，记住用户偏好
4. **实时数据** - 接入12306、高德、墨迹天气等真实数据源
5. **优雅降级** - Multi-Agent 不可用时自动降级到基础模式

## 作者

**ursuladuva-vibecoding** 全栈开发

## License

MIT