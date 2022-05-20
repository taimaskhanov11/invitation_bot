import collections
from asyncio import Queue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from invitation_bot.apps.controller.controller import MethodController

controller_codes_queue: dict[int, Queue] = {}
controllers: dict[int, dict[int, 'MethodController']] = collections.defaultdict(dict)
