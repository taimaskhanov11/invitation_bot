from aiogram import Dispatcher, Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext

from invitation_bot.apps.bot.callback_data.base_callback import AccountCallback, Action
from invitation_bot.apps.bot.filters.base_filters import UserFilter
from invitation_bot.db.models import User

router = Router()


async def current_accounts(call: types.CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    pass


def register_common(dp: Dispatcher):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    callback(current_accounts, AccountCallback.filter(F.action == Action.current))
    callback(start, UserFilter(), text="start", state="*")
