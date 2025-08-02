# modules/error_handler.py

import asyncio
import logging
import os
import random
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import Any, Callable

import openai


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    max_jitter: float = 1.0,
) -> Callable:
    """
    Async decorator for exponential backoff with jitter.
    Retries on OpenAI transient errors up to max_retries.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(func.__module__)

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except (openai.RateLimitError, openai.APIConnectionError) as e:
                    if attempt >= max_retries:
                        logger.error(
                            "Rate limit/connection error after %d attempts",
                            attempt, exc_info=True
                        )
                        raise
                    delay = min(base_delay * 2**attempt + random.uniform(0, max_jitter), max_delay)
                    logger.warning(
                        "OpenAI rate limit/connection error: %s; retrying in %.2fs (attempt %d/%d)",
                        e, delay, attempt + 1, max_retries
                    )
                    await asyncio.sleep(delay)

                except openai.APITimeoutError as e:
                    if attempt >= max_retries:
                        logger.error(
                            "API timeout after %d attempts",
                            attempt, exc_info=True
                        )
                        raise
                    delay = min(base_delay * 2**attempt, max_delay)
                    logger.warning(
                        "API timeout: %s; retrying in %.2fs (attempt %d/%d)",
                        e, delay, attempt + 1, max_retries
                    )
                    await asyncio.sleep(delay)

                except Exception:
                    logger.exception(
                        "Unexpected error in %s (attempt %d/%d)",
                        func.__name__, attempt + 1, max_retries
                    )
                    if attempt >= max_retries:
                        raise
                    await asyncio.sleep(base_delay)

        return wrapper

    return decorator


class RequestIDFilter(logging.Filter):
    """
    Logging filter that ensures every record has a request_id attribute.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", "-")
        return True


class ErrorHandler:
    """
    Configures application-wide logging with rotating file handlers
    and a console handler. Includes debug, info, and error logs.
    """
    def __init__(self) -> None:
        # Ensure log directory exists
        os.makedirs("logs", exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def setup_logging(self, level: str = "INFO") -> None:
        log_format = "%(asctime)s [%(request_id)s] %(name)s %(levelname)s: %(message)s"
        formatter = logging.Formatter(log_format)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.addFilter(RequestIDFilter())

        # Rotating file handlers
        info_handler = RotatingFileHandler("logs/info.log", maxBytes=5_242_880, backupCount=5)
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        info_handler.addFilter(RequestIDFilter())

        error_handler = RotatingFileHandler("logs/error.log", maxBytes=5_242_880, backupCount=5)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        error_handler.addFilter(RequestIDFilter())

        debug_handler = RotatingFileHandler("logs/debug.log", maxBytes=10_485_760, backupCount=3)
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        debug_handler.addFilter(RequestIDFilter())

        # Root logger
        root = logging.getLogger()
        root.setLevel(getattr(logging, level.upper(), logging.INFO))
        root.addHandler(console_handler)
        root.addHandler(info_handler)
        root.addHandler(error_handler)
        root.addHandler(debug_handler)