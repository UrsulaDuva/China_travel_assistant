# src/run_frontend.py
"""
启动前端 API 服务（简化版，直接使用 Orchestrator API）
"""
import logging
import os

import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    from orchestrator.api.app import app

    port = int(os.getenv("ORCHESTRATOR_PORT", "10000"))
    host = os.getenv("ORCHESTRATOR_BIND_HOST", "0.0.0.0")

    logger.info("=" * 50)
    logger.info("中国旅游助手 - 前端 API 服务")
    logger.info("=" * 50)
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info("=" * 50)

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()