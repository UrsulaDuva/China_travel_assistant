#!/bin/bash
# =============================================================================
# China Travel Pro - 一键启动脚本 (Linux/macOS/Git Bash)
# =============================================================================
# 使用说明:
#   ./start.sh          - 启动所有服务
#   ./start.sh backend  - 仅启动后端
#   ./start.sh frontend - 仅启动前端
#
# 前置条件:
#   1. Python 3.11+ 已安装
#   2. Node.js 18+ 已安装
#   3. LM Studio 已安装并运行本地模型 (可选)
#   4. 已配置 .env 文件 (复制 .env.example)
# =============================================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# 端口配置
BACKEND_PORT=10001
FRONTEND_PORT=5173

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "\n${CYAN}============================================================${NC}"
echo -e "${CYAN}     China Travel Pro - AI 旅游规划系统${NC}"
echo -e "${CYAN}============================================================${NC}\n"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${RED}[错误] .env 文件不存在${NC}"
    echo -e "\n${YELLOW}请执行以下步骤:${NC}"
    echo "  1. cp .env.example .env"
    echo "  2. 编辑 .env 填写 API Keys"
    exit 1
fi

# 检查 Python 虚拟环境
if [ ! -f ".venv/bin/activate" ]; then
    echo -e "${YELLOW}[警告] Python 虚拟环境不存在，正在创建...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
else
    source .venv/bin/activate
fi

# 检查前端依赖
if [ ! -d "src/frontend/node_modules" ]; then
    echo -e "${YELLOW}[警告] 前端依赖未安装，正在安装...${NC}"
    cd src/frontend
    npm install
    cd "$SCRIPT_DIR"
fi

# 检查 LM Studio (可选)
echo -e "${CYAN}[检查] LM Studio 本地模型服务...${NC}"
if curl -s --connect-timeout 2 http://127.0.0.1:1234/v1/models > /dev/null 2>&1; then
    echo -e "${GREEN}[正常] LM Studio 已运行${NC}"
else
    echo -e "${YELLOW}[提示] LM Studio 未运行，意图识别将使用备用方案${NC}"
    echo "       如需本地模型支持，请启动 LM Studio 并加载模型"
fi
echo

# 解析命令行参数
MODE="${1:-all}"
echo -e "${GREEN}启动模式: $MODE${NC}\n"

# 启动后端
start_backend() {
    echo -e "${CYAN}[启动] 后端服务 (端口: $BACKEND_PORT)${NC}"
    if command -v osascript &> /dev/null; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && source .venv/bin/activate && python -m uvicorn src.orchestrator.api.app:app --host 0.0.0.0 --port $BACKEND_PORT --reload\""
    else
        # Linux/Git Bash
        (python -m uvicorn src.orchestrator.api.app:app --host 0.0.0.0 --port $BACKEND_PORT --reload &) &
    fi
    echo -e "${GREEN}[完成] 后端服务已启动${NC}"
    echo -e "       API 文档: http://localhost:$BACKEND_PORT/docs"
}

# 启动前端
start_frontend() {
    echo -e "${CYAN}[启动] 前端服务 (端口: $FRONTEND_PORT)${NC}"
    if command -v osascript &> /dev/null; then
        osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/src/frontend' && npm run dev\""
    else
        (cd src/frontend && npm run dev &) &
    fi
    echo -e "${GREEN}[完成] 前端服务已启动${NC}"
    echo -e "       访问地址: http://localhost:$FRONTEND_PORT"
}

# 根据模式启动
case "$MODE" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all)
        start_backend
        sleep 3
        start_frontend

        echo -e "\n${GREEN}============================================================${NC}"
        echo -e "${GREEN}  所有服务已启动!${NC}"
        echo -e "${GREEN}============================================================${NC}\n"

        echo -e "  ${CYAN}前端地址:${NC}  http://localhost:$FRONTEND_PORT"
        echo -e "  ${CYAN}后端 API:${NC}  http://localhost:$BACKEND_PORT"
        echo -e "  ${CYAN}API 文档:${NC}  http://localhost:$BACKEND_PORT/docs"

        echo -e "\n  ${YELLOW}提示:${NC}"
        echo -e "  - 使用 './stop.sh' 停止所有服务"
        echo -e "  - 或使用 'pkill -f uvicorn' 和 'pkill -f vite'\n"
        ;;
    *)
        echo -e "${RED}[错误] 未知模式: $MODE${NC}"
        echo "用法: $0 [backend|frontend|all]"
        exit 1
        ;;
esac