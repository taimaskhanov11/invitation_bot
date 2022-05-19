import asyncio
import logging

from aiogram import Bot
from aiogram.types import BotCommand

from invitation_bot.apps.bot.handlers.common import register_common
from invitation_bot.apps.bot.handlers.common.connect_account import register_connect_account
from invitation_bot.apps.bot.handlers.errors.errors_handlers import register_error
from invitation_bot.config.config import config
from invitation_bot.config.logg_settings import init_logging
from invitation_bot.db import init_db
from invitation_bot.loader import bot, dp


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Главное меню"),
        BotCommand(command="/admin", description="Админ меню"),
    ]
    await bot.set_my_commands(commands)


async def start():
    # Настройка логирования
    init_logging(
        old_logger=True,
        level="TRACE",
        # old_level=logging.DEBUG,
        old_level=logging.INFO,
        steaming=True,
        write=True,
    )

    # dp.startup.register(on_startup)
    # dp.shutdown.register(on_shutdown)

    # Установка команд бота
    await set_commands(bot)

    # Инициализация бд
    await init_db(**config.db.dict())

    # Меню админа

    # Регистрация хэндлеров
    register_common(dp)
    register_error(dp)
    register_connect_account(dp)

    # Регистрация middleware

    # Регистрация фильтров

    await dp.start_polling(bot, skip_updates=True)


def main():
    asyncio.run(start())
    asyncio.get_event_loop()


if __name__ == "__main__":
    main()
