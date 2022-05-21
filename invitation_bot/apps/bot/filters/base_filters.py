from aiogram import types
from aiogram.dispatcher.filters import BaseFilter
from loguru import logger

from invitation_bot.apps.bot.callback_data.base_callback import ChatCallback
from invitation_bot.apps.bot.temp import controllers
from invitation_bot.apps.controller.controller import MethodController
from invitation_bot.db.models import User


class UserFilter(BaseFilter):
    async def __call__(self, update: types.CallbackQuery | types.Message) -> dict[str, User]:
        user = update.from_user
        user, is_new = await User.get_or_create(
            user_id=user.id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language": user.language_code,
            },
        )
        if is_new:
            logger.info(f"Новый пользователь {user=}")
        data = {"user": user}
        return data


class ControllerFilter(BaseFilter):
    async def __call__(self, update: types.CallbackQuery | types.Message, **kwargs) -> dict[str, MethodController]:
        return {"controller": controllers[update.from_user.id][ChatCallback.unpack(update.data).controller_id]}
