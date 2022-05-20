from telethon import tl
from telethon.tl.types import messages

from invitation_bot.apps.bot.callback_data.base_callback import AccountCallback, Action, ChatCallback
from invitation_bot.apps.bot.markups.utils import get_inline_keyboard, get_as_column
from invitation_bot.db.models import Account
from invitation_bot.loader import _


def view_accounts(accounts: list[Account]):
    keyboard = (
        ((account.first_name, AccountCallback(pk=account.pk, action=Action.view).pack()),) for account in accounts
    )
    return get_inline_keyboard(keyboard)


def view_account(account: Account):
    keyboard = [
        ((_("Показать чаты для спама"), AccountCallback(pk=account.api_id, action=Action.chats).pack()),),
        ((_("❌ Удалить"), AccountCallback(pk=account.pk, action=Action.delete).pack()),),
    ]
    return get_inline_keyboard(keyboard)


def view_account_chats(account: AccountCallback, chats: list[tl.types.Chat]):
    keyboard = (
        (chat.title, ChatCallback(account_pk=account.pk, id=chat.id, action=Action.view).pack())
        for chat in chats
    )
    return get_inline_keyboard(get_as_column(keyboard, col=3))
