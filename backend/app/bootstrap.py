import logging

import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging
from app.seed import seed_data


def main() -> None:
    setup_logging(settings.app_name)
    logging.getLogger(__name__).info("启动引导：初始化数据库与种子数据")
    seed_data()

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
