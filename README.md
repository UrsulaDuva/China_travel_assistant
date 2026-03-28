# China Travel Pro

基于 LangChain + LangGraph 的智能多 Agent 中国旅游规划系统

## 项目概述

一站式中国境内智能旅行规划平台，通过 LangChain Multi-Agent 架构，结合 MCP 数据服务，为用户提供智能化的行程规划、票务查询、美食推荐、景点推荐等全流程服务。

## 技术架构

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
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tools Layer                          │
│    (天气 | 景点 | 美食 | 火车票 | 攻略 | 地图)                 │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + Vite + Pinia + Tailwind CSS |
| **后端** | FastAPI + Python 3.11+ |
| **Agent框架** | LangChain + LangGraph |
| **主LLM** | Qwen-Plus (DashScope) |
| **本地模型** | LM Studio (意图识别) |
| **数据协议** | MCP (Model Context Protocol) |
| **向量存储** | FAISS |

## 快速开始

### 1. 环境准备

确保已安装以下软件：

- **Python 3.11+**
- **Node.js 18+**
- **LM Studio** (可选，用于本地意图识别)

### 2. 安装 LM Studio (推荐)

LM Studio 用于本地意图识别，可减少 API 调用成本：

1. 从 [lmstudio.ai](https://lmstudio.ai/) 下载并安装
2. 启动 LM Studio，加载任意聊天模型
3. 启动本地服务器 (默认端口 `1234`)

如不安装 LM Studio，系统将使用备用正则方案进行意图识别。

### 3. 克隆项目

```bash
git clone https://github.com/UrsulaDuva/A2A_China_travel_assistant.git
cd A2A_China_travel_assistant
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的 API Keys：

```env
# DashScope API (阿里云 Qwen)
DASHSCOPE_API_KEY=your_dashscope_api_key

# 高德地图 API
AMAP_API_KEY=your_amap_api_key

# LM Studio (可选，默认已配置)
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1
LMSTUDIO_MODEL=local-model
```

### 5. 一键启动

**Windows:**
```bash
start.bat          # 启动所有服务
start.bat backend  # 仅启动后端
start.bat frontend # 仅启动前端
stop.bat           # 停止所有服务
```

**Linux/macOS:**
```bash
chmod +x start.sh stop.sh
./start.sh          # 启动所有服务
./start.sh backend  # 仅启动后端
./start.sh frontend # 仅启动前端
./stop.sh           # 停止所有服务
```

### 6. 访问

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:5173 |
| 后端 API | http://localhost:10001 |
| API 文档 | http://localhost:10001/docs |

## 项目结构

```
china-travel-pro/
├── src/
│   ├── agent_core/         # Multi-Agent 智能层
│   │   ├── agents/         # 专业 Agent 实现
│   │   ├── tools/          # LangChain Tools (MCP封装)
│   │   ├── graph/          # LangGraph 工作流
│   │   └── memory/         # 对话记忆
│   ├── orchestrator/       # API 编排层
│   │   └ api/              # FastAPI 应用
│   │   └ session_manager.py
│   ├── mcp_clients/        # MCP 客户端
│   │   ├── moji_weather_client.py
│   │   ├── amap_client.py
│   │   ├── railway12306_client.py
│   │   └── xiaohongshu_client.py
│   ├── shared/             # 共享模块
│   └── frontend/           # Vue3 前端
├── start.bat/sh/ps1        # 一键启动脚本
├── stop.bat/sh/ps1         # 停止脚本
├── .env.example            # 环境变量模板
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

| Agent | 数据源 |
|-------|--------|
| Weather | 墨迹天气 |
| Transport | 12306火车票 |
| Attraction | 高德地图POI |
| Food | 高德地图POI |
| Guide | 小红书笔记 |

## API 端点

### 核心接口

| 接口 | 说明 |
|------|------|
| `POST /chat` | 智能对话 (Multi-Agent 处理) |
| `GET /api/weather/{city}` | 天气查询 |
| `GET /api/attractions/{city}` | 景点查询 |
| `GET /api/food/{city}` | 美食查询 |
| `GET /api/trains` | 火车票查询 |
| `GET /api/guide/{city}` | 攻略查询 |

### Multi-Agent 接口

| 接口 | 说明 |
|------|------|
| `POST /api/trip-context` | 更新行程上下文 |
| `GET /api/agent-status` | 获取 Agent 状态 |

## 功能特性

1. **智能意图理解** - 自动分析用户需求，识别城市、日期、意图类型
2. **多维度推荐** - 景点、美食、交通一站式服务
3. **上下文记忆** - 支持多轮对话，记住用户偏好
4. **实时数据** - 接入12306、高德、墨迹天气等真实数据源
5. **本地模型支持** - LM Studio 本地意图识别，降低 API 成本
6. **优雅降级** - Multi-Agent/LM Studio 不可用时自动降级

## LM Studio 配置说明

LM Studio 是一个本地运行大语言模型的工具，本项目使用它进行意图识别。

### 配置步骤

1. 安装 LM Studio: https://lmstudio.ai/
2. 启动应用，下载模型 (推荐 Qwen 或 Llama 系列)
3. 启动本地服务器:
   - 点击 "Local Server" 标签
   - 端口设置为 `1234`
   - 点击 "Start Server"

### 环境变量

```env
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1
LMSTUDIO_MODEL=<你加载的模型名称>
```

### 注意事项

- LM Studio 未启动时，系统自动使用正则兜底方案
- 本地模型响应可能较慢，建议使用较小模型
- 意图识别模型不需要很强，普通模型即可

## 作者

**ursuladuva-vibecoding** 全栈开发

## License

MIT