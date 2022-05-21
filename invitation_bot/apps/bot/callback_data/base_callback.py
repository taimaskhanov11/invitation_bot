from enum import Enum
from typing import Optional

from aiogram.dispatcher.filters.callback_data import CallbackData


# todo 5/13/2022 3:17 PM taima: добавить Enum

class Action(str, Enum):
    current = "current"
    view = "view"
    connect = "connect"
    delete = "delete"
    chats = "chats"
    spam = "spam"


class ChatAction(str, Enum):
    current = "current"
    view = "view"
    spam = "spam"
    new = "new"


class UserCallback(CallbackData, prefix="user"):
    pk: int
    action: Action


class AccountCallback(CallbackData, prefix="account"):
    pk: Optional[int]
    api_id: Optional[int]
    action: Action


class ChatCallback(CallbackData, prefix="chat"):
    controller_id: int
    id: Optional[int]
    action: ChatAction
