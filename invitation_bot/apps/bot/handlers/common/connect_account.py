import asyncio
from asyncio import Queue

from aiogram import Dispatcher, types, Router, F
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.fsm.context import FSMContext
from loguru import logger

from invitation_bot.apps.bot.callback_data.base_callback import AccountCallback, Action
from invitation_bot.apps.bot.filters.base_filters import UserFilter
from invitation_bot.apps.bot.markups.common import common_markups
from invitation_bot.apps.bot.temp import controller_codes_queue
from invitation_bot.apps.controller.controller import ConnectAccountController
from invitation_bot.db.models import User
from invitation_bot.loader import _

router = Router()


class ConnectAccount(StatesGroup):
    api = State()
    code = State()


class UnlinkAccount(StatesGroup):
    unlink = State()


async def connect_account(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ConnectAccount.api)
    await call.message.answer(_("Для подключения аккаунта:\n"
                                "1) Отключите двухэтапную аутентификацию (если включена).\n"
                                "2) Создайте приложение по ссылке https://my.telegram.org/auth?to=apps\n"
                                "3) Сохраните свои api_id, api_hash.\n"
                                "4) Отправьте боту Ваши данные в следующем формате: api_id:api_hash:номер_телефона.\n"
                                "Пример корректного ввода:\n123456:ababa123455abab:+79687878788"),
                              reply_markup=common_markups.menu_button(), )


async def connect_account_phone(message: types.Message, user: User, state: FSMContext):
    try:
        api_id, api_hash, phone = tuple(map(lambda x: x.strip(), message.text.split(":")))
        logger.info(f"{user.username}| Полученные данные {api_id}|{api_hash}|{phone}")
        client = ConnectAccountController(
            user_id=user.user_id,
            username=user.username,
            phone=phone,
            api_id=api_id,
            api_hash=api_hash
        )
        controller_codes_queue[user.user_id] = Queue(maxsize=1)
        # asyncio.create_task(client.start())
        asyncio.create_task(client.start())
        await state.set_state(ConnectAccount.code)
        await message.answer(_("Введите код подтверждения из сообщения Телеграмм с префиксом code, "
                               "в только таком виде code<ваш код>. "
                               "Если отправить просто цифры то тг обнулит код\nНапример:\ncode43123"))

    except Exception as e:
        logger.critical(e)
        await message.answer(_("Неправильный ввод"))


async def connect_account_code(message: types.Message, user: User, state: FSMContext):
    code = message.text
    if code.isdigit():
        await message.answer(_(f"❌ Неправильный ввод код.\n"
                               f"Пожалуйста повторите попытку создания с первого этапа и введите "
                               f"код с префиксом code как узказано в примере ниже \n"
                               f"Например:\ncode43123"),
                             reply_markup=common_markups.start_menu())
        await state.clear()
        return
    code = message.text.replace("code", "").strip()
    queue = controller_codes_queue.get(user.user_id)
    queue.put_nowait(code)
    await message.answer(
        _("Код получен, ожидайте завершения\nЕсли все прошло успешно Вам придет сообщение в личный чат."))
    await state.clear()


def register_connect_account(dp: Dispatcher):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(connect_account, UserFilter(), AccountCallback.filter(F.action == Action.connect))
    message(connect_account_phone, UserFilter(), state=ConnectAccount.api)
    message(connect_account_code, UserFilter(), state=ConnectAccount.code)
