import json
import logging
import os
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(
        self,
        record
    ):
        payload = {
            "timestamp": datetime.now().isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            payload["exception"] = self.formatException(
                record.exc_info
            )
        return json.dumps(
            payload,
            ensure_ascii=False
        )


def configure_logging() -> None:
    level = os.getenv(
        "HELIOS_LOG_LEVEL",
        "INFO"
    ).upper()
    handler = logging.StreamHandler()
    if os.getenv(
        "HELIOS_LOG_FORMAT",
        "text"
    ).lower() == "json":
        handler.setFormatter(
            JsonFormatter()
        )
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s"
            )
        )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(
        handler
    )
    root.setLevel(
        level
    )
