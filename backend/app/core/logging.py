import logging
import re
from typing import Any

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("buildpermit")

SENSITIVE_PATTERNS = [
    re.compile(r"password['\"]?\s*[:=]\s*['\"]?([^'\"\s]+)", re.IGNORECASE),
    re.compile(r"token['\"]?\s*[:=]\s*['\"]?([^'\"\s]+)", re.IGNORECASE),
    re.compile(r"secret['\"]?\s*[:=]\s*['\"]?([^'\"\s]+)", re.IGNORECASE),
]

def sanitize_log_message(message: str) -> str:
    """Masks sensitive parameters like passwords, tokens, and keys from logs."""
    sanitized = message
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r"\g<0>=[REDACTED]", sanitized)
    return sanitized

def log_info(msg: str, **kwargs: Any) -> None:
    logger.info(sanitize_log_message(msg), **kwargs)

def log_warning(msg: str, **kwargs: Any) -> None:
    logger.warning(sanitize_log_message(msg), **kwargs)

def log_error(msg: str, **kwargs: Any) -> None:
    logger.error(sanitize_log_message(msg), **kwargs)
