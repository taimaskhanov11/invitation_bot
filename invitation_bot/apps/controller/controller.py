import asyncio
from asyncio import Queue
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import BaseModel
from telethon import TelegramClient, events
from telethon.tl import patched

from invitation_bot.apps.bot import temp
from invitation_bot.apps.bot.markups.common import common_markups
from invitation_bot.apps.bot.temp import controller_codes_queue, controllers
from invitation_bot.db.models.account import Account
from invitation_bot.loader import bot, _, storage

SESSION_PATH = Path(Path(__file__).parent, "sessions")


class AbstractController(BaseModel):
    user_id: int
    username: Optional[str]
    client: Optional[TelegramClient]

    class Config:
        arbitrary_types_allowed = True

    async def listening(self):
        """Прослушка входящих сообщений"""
        logger.success(f"Прослушивание сообщений {self} запущено")

        @self.client.on(events.NewMessage(incoming=True))
        async def message_handler(event: events.NewMessage.Event):
            message: patched.Message = event.message
            pass

        await self.client.run_until_disconnected()


class Controller(AbstractController):
    phone: str
    api_id: int
    api_hash: str
    path: Optional[Path]

    def __str__(self):
        return f"{self.username}[{self.user_id}][app{self.api_id}]"

    def _init(self):
        logger.debug(f"Инициализация клиента {self}")
        self.path = Path(SESSION_PATH, f"{self.api_id}_{self.user_id}.session")
        self.client = TelegramClient(str(self.path), self.api_id, self.api_hash)
        controllers[self.user_id] = self

    async def start(self):
        """Создать новый client и запустить"""
        self._init()
        logger.debug(f"Контроллер создан")
        await self.client.connect()
        # await self.listening()

    async def stop(self):
        """Приостановить client и удалить"""
        await self.client.disconnect()
        del temp.controllers[self.user_id]
        logger.info(f"Контроллер {self} приостановлен и удален")


class ConnectAccountController(Controller):
    async def _get_code(self):
        logger.info(f"Ожидание кода {self}")
        queue: Queue = controller_codes_queue.get(self.user_id)
        code = await queue.get()
        queue.task_done()
        del queue
        return code

    async def clearing(self):
        await bot.send_message(
            self.user_id, _("🚫 Ошибка, отмена привязки ... Попробуйте отключить Двухэтапную аутентификацию")
        )
        await self.client.disconnect()
        del controllers[self.user_id]
        self.path.unlink()
        del controller_codes_queue[self.user_id]
        logger.info(f"Временные файлы очищены {self}")

    async def get_code(self):
        try:
            return await asyncio.wait_for(self._get_code(), timeout=30)
        except Exception as e:
            logger.warning(f"Не удалось получить код для подключения {self} {e}")
            await storage.finish(user=self.user_id)
            await bot.send_message(
                self.user_id,
                "🚫 Ошибка, отмена привязки ...\nПовторите попытку",
                # reply_markup=markups.common_menu.start_menu(self.user_id),
            )
            await self.client.disconnect()
            del controllers[self.user_id]
            self.path.unlink()
            del controller_codes_queue[self.user_id]
            logger.info(f"Временные файлы очищены {self}")

    async def connect_finished_message(self):
        await self.client.send_message("me", "✅ Бот успешно подключен")
        await bot.send_message(
            self.user_id, "✅ Бот успешно подключен", reply_markup=common_markups.start_menu()
        )
        logger.success(f"Аккаунт пользователя {self} успешно подключен")

    async def _2auth(self):
        raise ValueError("Двухэтапная аутентификация")

    async def try_connect(self):
        await self.client.start(
            lambda: self.phone, password=lambda: self._2auth(), code_callback=lambda: self._get_code()
        )

    async def connect_account(self):
        """Подключение аккаунта и создание сессии"""
        logger.debug(f"Подключение аккаунта {self}")
        try:
            await asyncio.wait_for(self.try_connect(), timeout=30)
        except Exception as e:
            logger.warning(f"Не удалось получить код для подключения {self} {e}")
            await self.clearing()
            return

        await storage.set_state(bot, self.user_id)
        await storage.set_data(bot, self.user_id, {})
        # await storage.storage.,
        # todo 5/20/2022 12:45 AM taima:
        await self.connect_finished_message()
        # await User.connect_account(self)
        await Account.connect(self)
        logger.success(f"Аккаунт пользователя {self} успешно подключен")

    async def start(self):
        self._init()
        logger.debug(f"Контроллер создан")
        await self.connect_account()
        await self.listening()


async def start_controller(acc: Account):
    acc_data = dict(acc)
    del acc_data["user_id"]
    controller = Controller(
        user_id=acc.user.user_id,
        username=acc.user.username,
        **acc_data,
        # chats={chat.chat_id: chat for chat in acc.chats} or {},
    )
    asyncio.create_task(controller.start())
    logger.info(f"Контроллер {controller} запущен")


async def restart_controller(user):
    account = await Account.get(user=user).prefetch_related(
        "chats__message_filter__user_filters",
        "chats__message_filter__word_filter",
        "chats__chat_storage",
        "user",
    )
    await start_controller(account)
    # await controller.client.send_message("me", _("✅ Бот успешно подключен"))


async def init_controllers():
    logger.debug("Инициализация контролеров")
    return
    for acc in await Account.all().prefetch_related(
            # for acc in await Account.filter(api_id=16629671).prefetch_related(
            "chats__message_filter__user_filters",
            "chats__message_filter__word_filter",
            "chats__chat_storage",
            "user",
    ):
        await start_controller(acc)
    logger.info("Контроллеры проинициализированы")


if __name__ == "__main__":
    pass
