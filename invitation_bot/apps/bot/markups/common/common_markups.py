from invitation_bot.apps.bot.callback_data.base_callback import Action, AccountCallback
from invitation_bot.apps.bot.markups.utils import get_inline_keyboard
from invitation_bot.loader import _


def start_menu():
    keyboard = [
        # ((_("👤 Мой профиль"), "profile"),),
        ((_("👥 Текущие аккаунты"), AccountCallback(action=Action.current).pack()),),
        ((_("👤 Добавить аккаунт"), AccountCallback(action=Action.connect).pack()),),
        # ((_("👤 Статистика"), "statistic"),),
    ]
    return get_inline_keyboard(keyboard)


def menu_button():
    keyboard = [
        ((_("Главное меню"), "start"),),
    ]
    return get_inline_keyboard(keyboard)


def choice():
    keyboard = [
        ((_("Да"), "yes"),),
        ((_("Нет"), "no"),),
    ]
    return get_inline_keyboard(keyboard)
