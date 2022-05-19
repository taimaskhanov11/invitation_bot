from aiogram import Dispatcher, F, Router, types
from aiogram.dispatcher.fsm.context import FSMContext

from invitation_bot.config.config import config

router = Router()


async def admin_start(message: types.CallbackQuery | types.Message, state: FSMContext):
    await state.clear()
    if isinstance(message, types.CallbackQuery):
        message = message.message

    await message.answer("Админ панель")


def register_admin(dp: Dispatcher):
    dp.include_router(router)
    router.message.filter(F.from_user.id.in_(config.bot.admins))

    callback = router.callback_query.register
    message = router.message.register

    message(admin_start, commands="admin", state="*")
    callback(admin_start, text="admin", state="*")
