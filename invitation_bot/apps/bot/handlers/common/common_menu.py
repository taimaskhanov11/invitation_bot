from aiogram import Dispatcher, Router, types
from aiogram.dispatcher.fsm.context import FSMContext

from invitation_bot.apps.bot.filters.base_filters import UserFilter
from invitation_bot.apps.bot.markups.common import common_markups
from invitation_bot.db.models import User

router = Router()


async def start(message: types.Message | types.CallbackQuery, user: User, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message
    await message.answer("Стартовое меню!", reply_markup=common_markups.start_menu())


def register_common(dp: Dispatcher):
    dp.include_router(router)

    callback = router.callback_query.register
    message = router.message.register

    message(start, UserFilter(), commands="start", state="*")
    callback(start, UserFilter(), text="start", state="*")
