# src/run_orchestrator.py
"""
启动 Orchestrator 服务
"""
import logging
import os

import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    from src.orchestrator.api.app import app

    port = int(os.getenv("ORCHESTRATOR_PORT", "10000"))
    host = os.getenv("ORCHESTRATOR_BIND_HOST", "0.0.0.0")

    logger.info("=" * 50)
    logger.info("中国旅游助手 - Orchestrator 服务")
    logger.info("=" * 50)
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"API 文档: http://{host}:{port}/docs")
    logger.info("=" * 50)

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()