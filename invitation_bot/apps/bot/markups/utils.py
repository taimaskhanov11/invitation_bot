from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def get_as_column(arr: Iterable, col=2):
    if not isinstance(arr, list):
        arr = list(arr)
    return [arr[i: i + col] for i in range(0, len(arr), col)]


def get_inline_button(bnt_data):
    return InlineKeyboardButton(text=bnt_data[0], callback_data=bnt_data[1])


def get_inline_url_button(bnt_data):
    return InlineKeyboardButton(text=bnt_data[0], url=bnt_data[1])


# todo 5/13/2022 5:39 PM taima: change to tuple or frozenset
def get_inline_keyboard(ikm_data: Iterable[Iterable]):
    inline_keyboard = [list(map(get_inline_button, btn)) for btn in ikm_data]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_inline_url_keyboard(ikm_data: Iterable[Iterable]):
    inline_keyboard = [list(map(get_inline_url_button, btn)) for btn in ikm_data]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_keyboard(km_data: list[tuple[str]]):
    return ReplyKeyboardMarkup()
