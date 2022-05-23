from aiogram import Dispatcher, Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from loguru import logger

from invitation_bot.apps.bot.callback_data.base_callback import AccountCallback, Action, ChatCallback, ChatAction
from invitation_bot.apps.bot.filters.base_filters import UserFilter, ControllerFilter
from invitation_bot.apps.bot.handlers.utils import Spammer
from invitation_bot.apps.bot.markups.common import accounts_markups
from invitation_bot.apps.bot.temp import controllers
from invitation_bot.apps.controller.controller import MethodController
from invitation_bot.db.models import User, Account
from invitation_bot.loader import _

router = Router()


class JoinChatStatesGroup(StatesGroup):
    join = State()


class Spam(StatesGroup):
    text = State()
    count = State()
    interval = State()
    chat = State()


async def view_accounts(call: types.CallbackQuery, user: User, callback_data: AccountCallback, state: FSMContext):
    await state.clear()
    accounts = await user.accounts
    await call.message.answer(_("Текущие аккаунты"), reply_markup=accounts_markups.view_accounts(accounts))


async def view_account(call: types.CallbackQuery, callback_data: AccountCallback, state: FSMContext):
    await state.clear()
    account = await Account.get(pk=callback_data.pk)
    await call.message.answer(str(account), 'markdown', reply_markup=accounts_markups.view_account(account))


async def view_account_chats(call: types.CallbackQuery, callback_data: AccountCallback, state: FSMContext):
    await state.clear()
    controller = controllers[call.from_user.id][callback_data.pk]
    # chats = await controller.get_chats()
    chats = await controller.get_dialogs()
    # await call.message.answer(_("Выберите чат для спама"), 'markdown',
    # reply_markup=accounts_markups.view_account_chats(chats))
    await call.message.edit_reply_markup(accounts_markups.view_account_chats(callback_data, chats))


async def view_account_chat(call: types.CallbackQuery, controller: MethodController, callback_data: ChatCallback,
                            state: FSMContext):
    await state.clear()
    chat = await controller.get_entity(callback_data.id)
    await call.message.answer(chat.stringify(), 'markdown',
                              reply_markup=accounts_markups.view_account_chat(callback_data))


async def add_new_account_chat(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(_("Введите ссылку или пригласительную ссылку для присоединения к новому чату"),
                              reply_markup=ReplyKeyboardRemove())
    await state.set_state(JoinChatStatesGroup.join)


async def add_new_account_chat_join(message: types.Message, controller: MethodController, state: FSMContext):
    try:
        await controller.join_channel(message.text)
        await state.clear()
        await message.answer(_("Пользователь успешно присоединен к чату"))
    except Exception as e:
        logger.warning(e)
        await message.answer(_("Ошибка при присоединении"))


async def spam(call: types.CallbackQuery, callback_data: AccountCallback, state: FSMContext):
    await state.clear()
    await call.message.answer(
        _("Скольким пользователям нужно отправить сообщение. Цифра не должна превышать 100"),
        reply_markup=ReplyKeyboardRemove())
    controller = controllers[call.from_user.id][callback_data.api_id]
    account = await Account.get(pk=callback_data.pk)
    await state.update_data(controller=controller, account=account)
    await state.set_state(Spam.count)


async def spam_count(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        number = int(message.text)
        if 0 < number < 101:
            await state.update_data(count=number)
            await message.answer(_("Введите интервал отправки между сообщениями. Минимальное значение 2 секунды\n"
                                   "Например:\n"
                                   "2-5"), reply_markup=accounts_markups.spam_count())
            await state.set_state(Spam.interval)
            return
    await message.answer(_("Неправильный ввод."))


async def spam_interval(message: types.Message, state: FSMContext):
    try:
        interval = tuple(map(lambda x: int(x.strip()), message.text.split("-")))
        if interval[1] > interval[0] >= 2:
            await state.update_data(interval=interval)
            await message.answer(_("Введите текст для отправки не больше 4000 символов. Язык разметки markdown.\n"
                                   "Для того чтобы телеграмм не обнаружил спам, будет меняться буквы текста на идентичные буквы других языков, "
                                   "визуально не изменяется. Также будут проводится другие изменения для защиты от блокировок.\n"
                                   "Поэтому помещайте ссылки или username бота между таким символом |. Например:\n"
                                   "Подписывайтесь на канал |https://t.me/ru_python_beginners|\nили\n"
                                   "Многофункциональный бот |@MyPaymentTryBot|, запускайте."),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(Spam.text)
            return
    except Exception as e:
        logger.warning(e)
    await message.answer(_("Неправильный ввод."))


async def spam_text(message: types.Message, state: FSMContext):
    if len(message.text) < 4100:
        await state.update_data(text=message.text)
        await message.answer(_("Введите ссылку на чат"))
        await state.set_state(Spam.chat)
        return
    await message.answer(_("Неправильный ввод."))


async def spam_chat(message: types.Message, state: FSMContext):
    try:
        await state.update_data(chat=message.text)
        data = await state.get_data()
        data.update(client=data["controller"].client)
        data.update(user_id=message.from_user.id)
        logger.debug(data)
        spammer = Spammer(**data)
        await spammer.check_chat()
        await message.answer(_("Спам начался, после окончания придет сообщение о завершении"))
        await spammer.spam()
        await state.clear()
    except Exception as e:
        logger.warning(e)
        await message.answer(_("Не получилось получить доступ к группе, повторите попытку"))


def register_accounts_manager(dp: Dispatcher):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(view_accounts, UserFilter(), AccountCallback.filter(F.action == Action.current))
    callback(view_account, UserFilter(), AccountCallback.filter(F.action == Action.view))

    # todo 5/21/2022 4:13 PM taima:
    callback(view_account_chats, UserFilter(), AccountCallback.filter(F.action == Action.chats))
    callback(view_account_chat, UserFilter(), ChatCallback.filter(F.action == Action.view), ControllerFilter())
    callback(add_new_account_chat, UserFilter(), ChatCallback.filter(F.action == ChatAction.new))
    message(add_new_account_chat_join, UserFilter(), ChatCallback.filter(F.action == ChatAction.new),
            ControllerFilter())
    # callback(spam, UserFilter(), ChatCallback.filter(F.action == ChatAction.spam), ControllerFilter())

    callback(spam, UserFilter(), AccountCallback.filter(F.action == Action.spam))
    message(spam_count, state=Spam.count)
    message(spam_interval, state=Spam.interval)
    message(spam_text, state=Spam.text)
    message(spam_chat, state=Spam.chat)
