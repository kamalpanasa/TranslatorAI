import re
import time
from typing import Callable, Any
from app.utils.logger import get_logger

logger = get_logger("app.utils.helpers")


def clean_text(text: str) -> str:
    """
    Cleans raw text by stripping leading/trailing whitespace, normalizing newlines,
    and removing excessive consecutive whitespace/null bytes.
    """
    if not text:
        return ""
    # Remove null bytes
    text = text.replace("\x00", "")
    # Normalize whitespaces and newlines
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def measure_execution_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to measure execution time of functions.
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        logger.info(
            f"Function '{func.__name__}' completed execution in {elapsed:.4f} seconds"
        )
        return result
    return wrapper
