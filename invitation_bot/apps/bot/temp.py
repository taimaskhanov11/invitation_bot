import collections
from asyncio import Queue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from invitation_bot.apps.controller.controller import Controller

controller_codes_queue: dict[int, Queue] = {}
controllers: dict[int, dict[int, 'Controller']] = collections.defaultdict(dict)
