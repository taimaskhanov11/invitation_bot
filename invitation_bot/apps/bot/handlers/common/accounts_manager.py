from aiogram import Dispatcher, Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext

from invitation_bot.apps.bot.callback_data.base_callback import AccountCallback, Action, ChatCallback
from invitation_bot.apps.bot.filters.base_filters import UserFilter
from invitation_bot.apps.bot.markups.common import accounts_markups
from invitation_bot.apps.bot.temp import controllers
from invitation_bot.db.models import User, Account
from invitation_bot.loader import _

router = Router()


async def view_accounts(call: types.CallbackQuery, user: User, state: FSMContext):
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
    chats = await controller.get_chats()
    # await call.message.answer(_("Выберите чат для спама"), 'markdown', reply_markup=accounts_markups.view_account_chats(chats))
    await call.message.edit_reply_markup(accounts_markups.view_account_chats(callback_data, chats))


async def view_account_chat(call: types.CallbackQuery, callback_data: ChatCallback, state: FSMContext):
    await state.clear()
    account = await Account.get(pk=callback_data.pk)
    await call.message.answer(str(account), 'markdown', reply_markup=accounts_markups.view_account(account))


def register_accounts_manager(dp: Dispatcher):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(view_accounts, UserFilter(), AccountCallback.filter(F.action == Action.current))
    callback(view_account, UserFilter(), AccountCallback.filter(F.action == Action.view))

    callback(view_account_chats, UserFilter(), AccountCallback.filter(F.action == Action.chats))
    callback(view_account_chat, UserFilter(), ChatCallback.filter(F.action == Action.view))
