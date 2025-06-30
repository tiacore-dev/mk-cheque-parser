import time
from functools import wraps

from loguru import logger
from selenium.common.exceptions import StaleElementReferenceException


def retry_on_stale(retries=5, delay=0.5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except StaleElementReferenceException as e:
                    logger.warning(
                        f"""StaleElementReferenceException в {func.__name__} 
                        (попытка {attempt}/{retries}): {e}"""
                    )
                    time.sleep(delay)
                except Exception:
                    # Если словили что-то другое, пробрасываем сразу
                    raise
            logger.error(
                f"""Не удалось выполнить {func.__name__} после {retries} 
                попыток из-за StaleElementReferenceException"""
            )
            raise StaleElementReferenceException(
                f"{func.__name__} не удалось выполнить после {retries} попыток"
            )

        return wrapper

    return decorator
