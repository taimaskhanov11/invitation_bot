from telethon import helpers
from telethon.tl.custom import dialog

from invitation_bot.apps.bot.callback_data.base_callback import AccountCallback, Action, ChatCallback, ChatAction
from invitation_bot.apps.bot.markups.utils import get_inline_keyboard, get_as_column, get_reply_keyboard
from invitation_bot.db.models import Account
from invitation_bot.loader import _


def view_accounts(accounts: list[Account]):
    keyboard = (
        ((account.first_name, AccountCallback(pk=account.pk, action=Action.view).pack()),) for account in accounts
    )
    return get_inline_keyboard(keyboard)


def view_account(account: Account):
    keyboard = [
        # todo 5/21/2022 4:13 PM taima: Включить
        # ((_("Показать чаты для спама"), AccountCallback(pk=account.api_id, action=Action.chats).pack()),),
        ((_("Создание спама"), AccountCallback(pk=account.pk, api_id=account.api_id, action=Action.spam).pack()),),
        ((_("❌ Удалить"), AccountCallback(pk=account.pk, action=Action.delete).pack()),),
    ]
    return get_inline_keyboard(keyboard)


def view_account_chats(account: AccountCallback, chats: helpers.TotalList[dialog.Dialog]):
    keyboard = [
        # (chat.title, ChatCallback(controller_id=account.pk, id=chat.id, action=ChatAction.view).pack())
        (chat.title, ChatCallback(controller_id=account.pk, id=chat.id, action=ChatAction.view).pack()) for chat in
        # chats if isinstance(chat.input_entity, tl.types.Chat)
        chats
    ]
    c_keyboard = get_as_column(keyboard, col=3)
    c_keyboard.append(
        (("Добавить новый чат", ChatCallback(controller_id=account.pk, action=ChatAction.new).pack()),)
    )
    return get_inline_keyboard(c_keyboard)


def view_account_chat(chat: ChatCallback):
    keyboard = [
        ((_("Спамить пользователям этого чата"),
          ChatCallback(controller_id=chat.controller_id, id=chat.id, action=ChatAction.spam).pack()),),
    ]
    return get_inline_keyboard(keyboard)


def spam_count():
    keyboard = [
        "2-5",
        "3-7",
        "6-15"
    ]
    return get_reply_keyboard(get_as_column(keyboard))
