import asyncio
import random
import re

from aiocache import cached
from loguru import logger
from pydantic import BaseModel
from telethon import helpers, TelegramClient
from telethon.errors import FloodWaitError, PeerFloodError
from telethon.tl import types

from invitation_bot.db.models import Account
from invitation_bot.loader import bot


async def part_sending(message, answer):
    if len(answer) > 4096:
        for x in range(0, len(answer), 4096):
            y = x + 4096
            await message.answer(answer[x:y])
    else:
        await message.answer(answer)


SINGS_RU = 'УКЕНХВАРОСМТукепнхваросмт'
SINGS_EN = 'YKEHXBAPOCMTykenHxBapocmt'


class Spammer(BaseModel):
    # controller: MethodController
    # controller_api_id: int
    client: TelegramClient
    account: Account
    user_id: int
    count: int
    interval: tuple[int, int]
    text: str
    chat: str
    successfully_sent: int = 0

    class Config:
        arbitrary_types_allowed = True

    async def send_message(self, entity, text):
        await self.client.send_message(entity, text)

    @cached(20)
    async def get_entity(self, entity):
        return await self.client.get_entity(entity)

    @cached(60 * 5)
    async def get_chat_users(self, chat, limit=5000) -> helpers.TotalList[types.User]:
        return await self.client.get_participants(chat, limit=limit)

    # todo 5/21/2022 6:40 PM taima: помещать количество букв в кеш
    @staticmethod
    def replace_sings(for_change: str):
        r_count = random.randrange(len(SINGS_RU))
        for_replace_sings = random.sample(SINGS_RU, r_count)

        for sing in for_replace_sings:
            sings_count = for_change.count(sing)
            if sings_count:
                replace_sing_count = random.randint(1, sings_count)
                for_change = for_change.replace(sing, SINGS_EN[SINGS_RU.index(sing)], replace_sing_count)
        return for_change

    def prepare_text(self):
        const = re.match(r".*\|(.+)\|.*", self.text)
        # const = re.match(r".+\|(.+)\|.+", self.text)
        for_change = re.sub(r"(\|)(.+)(\|)", lambda x: f"{x.group(1)}{x.group(3)}", self.text)
        change = self.replace_sings(for_change)
        if const:
            change = re.sub(r"\|\|", const.group(1), change)
        return change

    async def check_chat(self):
        await self.client.connect()
        # await self.controller.get_entity(self.chat)
        # await self.controller.get_chat_users(self.chat, limit=1)
        await self.get_entity(self.chat)
        await self.get_chat_users(self.chat, limit=1)

    async def spam(self):
        # await self.client.connect()
        users = await self.get_chat_users(self.chat)
        true_users: list[types.User] = random.sample(users, self.count)
        from_ = self.interval[0] - 1
        to_ = self.interval[1] + 1
        for u in true_users:
            try:
                random_sleep = random.uniform(from_, to_)
                await asyncio.sleep(random_sleep)
                pre_text = self.prepare_text()
                await self.send_message(u, pre_text)
                await bot.send_message(self.user_id,
                                       f"{self.account.first_name}->Успешно отправлено {u.first_name}[{u.username}]")
                logger.debug(f"{u.first_name}|{pre_text}")
                self.successfully_sent += 1
            except FloodWaitError as e:
                logger.exception(e)
                await bot.send_message(self.user_id,
                                       f"Аккаунт {self.account.first_name}.\nФлуд повторите попытку через {e.seconds} секунд")
                break
            except PeerFloodError as e:
                logger.exception(e)
                await bot.send_message(self.user_id,
                                       f"Аккаунт {self.account.first_name}.\nСлишком много запросов повторите через 15-30 минут")
                break
            except Exception as e:
                logger.warning(e)
        await bot.send_message(self.user_id, f"Аккаунт {self.account.first_name}.\n"
                                             f"Сообщение успешно отправлено {self.successfully_sent} пользователям")
