from enum import Enum

from aiogram.dispatcher.filters.callback_data import CallbackData


# todo 5/13/2022 3:17 PM taima: добавить Enum

class Action(str, Enum):
    current = "current"
    view = "view"
    connect = "connect"
    delete = "delete"
    chats = "chats"


class UserCallback(CallbackData, prefix="user"):
    pk: int
    action: Action


class AccountCallback(CallbackData, prefix="account"):
    pk: int
    action: Action


class ChatCallback(CallbackData, prefix="chat", sep="="):
    account_pk: int
    id: int
    action: Action
