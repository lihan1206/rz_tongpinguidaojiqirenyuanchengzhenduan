import logging
import sys


def setup_logging(app_name: str) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s %(levelname)s {app_name} %(name)s: %(message)s",
        stream=sys.stdout,
    )
