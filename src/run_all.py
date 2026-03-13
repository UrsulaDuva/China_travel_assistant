# src/run_all.py
"""
启动所有 Agent 服务
"""
import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Agent 配置：名称 -> (端口环境变量, 默认端口)
AGENTS = {
    "weather": ("WEATHER_AGENT_PORT", "10008"),
    "transport": ("TRANSPORT_AGENT_PORT", "10009"),
    "attraction": ("ATTRACTION_AGENT_PORT", "10010"),
    "food": ("FOOD_AGENT_PORT", "10011"),
    "hotel": ("HOTEL_AGENT_PORT", "10012"),
}


def run_agent(agent_name: str, port_env: str, default_port: str):
    """运行单个 Agent"""
    port = os.getenv(port_env, default_port)
    module_path = f"src.agents.{agent_name}_agent.server"

    logger.info(f"启动 {agent_name} Agent，端口: {port}")

    return subprocess.Popen(
        [sys.executable, "-m", module_path],
        env={**os.environ, port_env: port},
    )


def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("=" * 50)
    logger.info("中国旅游助手 - Agent 集群启动")
    logger.info("=" * 50)

    processes = []

    try:
        # 启动所有 Agent
        for agent_name, (port_env, default_port) in AGENTS.items():
            proc = run_agent(agent_name, port_env, default_port)
            processes.append((agent_name, proc))
            logger.info(f"✓ {agent_name} Agent 已启动 (PID: {proc.pid})")

        logger.info("=" * 50)
        logger.info("所有 Agent 已启动，按 Ctrl+C 停止")
        logger.info("=" * 50)

        # 等待所有进程
        for agent_name, proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        logger.info("\n正在停止所有 Agent...")

        for agent_name, proc in processes:
            logger.info(f"停止 {agent_name} Agent...")
            proc.terminate()

        logger.info("所有 Agent 已停止")


if __name__ == "__main__":
    main()