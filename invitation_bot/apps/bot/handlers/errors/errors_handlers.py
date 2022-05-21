import logging

from aiogram import Dispatcher, Router
from loguru import logger

router = Router()
#
# log = logging.getLogger()
#

async def error_handler(update, exception):
    logger.error(f"{exception}|{update}")
    # log.exception(f"{exception}|{update}")
    # logging.Logger
    return True


def register_error(dp: Dispatcher):
    dp.include_router(router)
    router.errors.register(error_handler)
