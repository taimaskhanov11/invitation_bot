import time

from loguru import logger


def time_track(func):
    async def wrapper(*args, **kwargs):
        now = time.monotonic()
        res = await func(*args, **kwargs)
        ex_time = time.monotonic() - now
        logger.info(f"{func.__name__} -> Execute time {round(ex_time, 4)}")
        return res

    return wrapper
