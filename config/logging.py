import logging

import structlog

from config.settings import settings


def _resolve_log_level(log_level: str) -> int:
    return getattr(logging, log_level.upper(), logging.INFO)


_log_level = _resolve_log_level(settings.log_level)

logging.basicConfig(
    level=_log_level,
    format="%(message)s",
)

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(_log_level),
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()
