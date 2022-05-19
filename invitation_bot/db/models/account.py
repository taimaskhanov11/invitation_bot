from typing import TYPE_CHECKING

from loguru import logger
from tortoise import models, fields

if TYPE_CHECKING:
    from invitation_bot.apps.controller.controller import ConnectAccountController
    from base import User


class Account(models.Model):
    api_id = fields.BigIntField(unique=True)
    api_hash = fields.CharField(max_length=50)
    phone = fields.CharField(max_length=20)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", index=True)

    @classmethod
    async def connect(cls, controller: "ConnectAccountController"):
        user = await cls.get(user_id=controller.user_id)
        acc, is_create = await Account.get_or_create(
            user=user, defaults={**controller.dict(exclude={"user_id"})}
        )
        if not is_create:
            logger.info(f"{acc} уже существует")
        # await user.save()
