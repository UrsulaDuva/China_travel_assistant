# China Travel Pro 部署指南

## 目录

1. [环境要求](#环境要求)
2. [本地开发部署](#本地开发部署)
3. [Docker 部署](#docker-部署)
4. [生产环境部署](#生产环境部署)
5. [配置说明](#配置说明)
6. [常见问题](#常见问题)

---

## 环境要求

### 后端
- Python 3.11+
- uv 包管理器

### 前端
- Node.js 18+
- npm 或 pnpm

### 外部服务
- 阿里云 DashScope API Key (Qwen 大模型)
- 高德地图 API Key
- (可选) 12306 MCP 服务 URL

---

## 本地开发部署

### 1. 克隆项目

```bash
git clone https://github.com/UrsulaDuva/A2A_China_travel_assistant.git
cd A2A_China_travel_assistant
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的 API Keys：

```env
# 必需 - 阿里云 DashScope (Qwen 大模型)
DASHSCOPE_API_KEY=your_dashscope_api_key

# 必需 - 高德地图 API
AMAP_API_KEY=your_amap_api_key

# 可选 - 12306 MCP 服务
RAILWAY_12306_MCP_URL=https://mcp.api-inference.modelscope.net/mcp
```

### 3. 安装依赖

**后端：**
```bash
# 安装 uv (如果未安装)
pip install uv

# 安装项目依赖
uv sync
```

**前端：**
```bash
cd src/frontend
npm install
```

### 4. 启动服务

**方式一：分别启动前后端**

```bash
# 终端 1 - 启动后端 API
uv run python -m src.run_orchestrator

# 终端 2 - 启动前端开发服务器
cd src/frontend
npm run dev
```

**方式二：一键启动**

```bash
uv run python -m src.run_all
```

### 5. 访问服务

- 前端界面: http://localhost:5173
- API 文档: http://localhost:10000/docs
- 健康检查: http://localhost:10000/health

---

## Docker 部署

### 方式一：使用 Docker Compose (推荐)

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式二：单独构建镜像

```bash
# 构建镜像
docker build -t china-travel-pro .

# 运行容器
docker run -d \
  --name china-travel-pro \
  -p 10000:10000 \
  -e DASHSCOPE_API_KEY=your_key \
  -e AMAP_API_KEY=your_key \
  china-travel-pro
```

### Docker Compose 配置说明

`docker-compose.yml` 配置了以下服务：

| 服务 | 端口 | 说明 |
|------|------|------|
| backend | 10000 | FastAPI 后端服务 |
| frontend | 80 | Nginx 托管的前端 |

---

## 生产环境部署

### 1. 环境变量配置

在生产环境中，建议使用环境变量或密钥管理服务：

```bash
# 设置环境变量
export DASHSCOPE_API_KEY=your_production_key
export AMAP_API_KEY=your_production_key
```

### 2. 使用 Gunicorn (推荐)

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务 (多 worker)
gunicorn src.orchestrator.api.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:10000 \
  --timeout 120
```

### 3. 前端构建

```bash
cd src/frontend
npm run build
```

构建产物在 `src/frontend/dist/` 目录，可由 Nginx 托管。

### 4. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/china-travel-pro/src/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:10000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /chat {
        proxy_pass http://127.0.0.1:10000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. systemd 服务配置

创建 `/etc/systemd/system/china-travel-pro.service`:

```ini
[Unit]
Description=China Travel Pro API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/china-travel-pro
Environment="DASHSCOPE_API_KEY=your_key"
Environment="AMAP_API_KEY=your_key"
ExecStart=/path/to/china-travel-pro/.venv/bin/gunicorn src.orchestrator.api.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:10000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动服务
sudo systemctl enable china-travel-pro
sudo systemctl start china-travel-pro
```

---

## 配置说明

### 必需的环境变量

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key | [阿里云控制台](https://dashscope.console.aliyun.com/) |
| `AMAP_API_KEY` | 高德地图 Web服务 API Key | [高德开放平台](https://console.amap.com/dev/key/app) |

### 可选的环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `RAILWAY_12306_MCP_URL` | - | 12306 MCP 服务地址 |
| `DOUYIN_MCP_URL` | - | 抖音攻略 MCP 服务地址 |
| `REDIS_URL` | - | Redis 连接地址 (会话持久化) |
| `LOG_LEVEL` | `INFO` | 日志级别 |

---

## 常见问题

### Q: 启动报错 "Module not found"

**A:** 确保已安装所有依赖：
```bash
uv sync
```

### Q: API 请求返回 500 错误

**A:** 检查以下几点：
1. 确认 `.env` 文件中的 API Key 是否正确
2. 检查网络是否能访问外部 API
3. 查看后端日志获取详细错误信息

### Q: 前端无法连接后端 API

**A:** 检查：
1. 后端服务是否正常运行 (访问 http://localhost:10000/health)
2. 前端代理配置是否正确 (`src/frontend/vite.config.js`)

### Q: Docker 容器启动失败

**A:** 检查：
1. 端口是否被占用 (`lsof -i :10000`)
2. Docker 日志 (`docker logs container_name`)
3. 环境变量是否正确设置

### Q: 如何更新依赖

**A:**
```bash
# 后端
uv lock --upgrade
uv sync

# 前端
cd src/frontend
npm update
```

---

## 技术支持

如有问题，请提交 Issue: https://github.com/UrsulaDuva/A2A_China_travel_assistant/issues