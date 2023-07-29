from yaml import safe_load
from typing import Dict, Any
from app.config import settings


def get_log_config() -> Dict[str, Any]:
    with open(settings.LOGGER_CONFIG, "r", encoding=settings.ENCODING) as cfg:
        return safe_load(cfg)
