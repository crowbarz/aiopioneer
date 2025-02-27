"""Pioneer AVR command queue class."""

import asyncio
import itertools
import logging
from typing import Self

_LOGGER = logging.getLogger(__name__)


class CommandQueueItem:
    """Command queue item."""

    def __init__(
        self, command: str, *args, insert_at: int = None, skip_if_queued: bool = None
    ):
        self.command = command
        self.args = args
        self.insert_at = -1 if insert_at is None else insert_at
        self.skip_if_queued = False if skip_if_queued is None else skip_if_queued

    def __eq__(self, value: Self):
        return self.command == value.command and self.args == value.args

    def __repr__(self) -> str:
        return f"Item({repr(self.command)}, args={repr(self.args)})"


class CommandQueue:
    """Command queue class."""

    def __init__(self, num_queues: int = 2):
        self._num_queues = num_queues
        self._queue: list[list[CommandQueueItem]] = [[] for _ in range(num_queues)]
        self._execute_lock = asyncio.Lock()

    def __iter__(self):
        return itertools.chain.from_iterable(self._queue)

    async def __aenter__(self):
        await self._execute_lock.acquire()

    async def __aexit__(self, exc_type, exc, tb):
        self._execute_lock.release()

    @property
    def commands(self) -> list[str]:
        """Get list of commands in the command queue."""
        return [item.command for item in self]

    def purge(self):
        """Purge the command queues."""
        self._queue = [[] for _ in range(self._num_queues)]

    def enqueue(
        self,
        item: CommandQueueItem,
        queue_id: int = 0,
        skip_if_queued: bool = None,
        insert_at: int = None,
    ):
        """Enqueue an item in the specified command queue."""
        if skip_if_queued is None:
            skip_if_queued = item.skip_if_queued
        if insert_at is None:
            insert_at = item.insert_at
        if insert_at < 0:
            insert_at = len(self._queue[queue_id]) + 1 + insert_at
        elif self.is_executing():
            if queue_id == self.active_queue():
                insert_at += 1  ## skip executing command at front of active queue
        if skip_if_queued and item in self:
            _LOGGER.debug("%s already queued, skipping", item)
            return
        _LOGGER.debug("queuing %s at %d", item, insert_at)
        self._queue[queue_id].insert(insert_at, item)

    def active_queue(self):
        """Return index of active command queue."""
        for queue_id in range(self._num_queues):
            if self._queue[queue_id]:
                return queue_id
        return None

    def peek(self, queue_id: int = None, queue_pos: int = 0) -> CommandQueueItem | None:
        """Peek first element of the command queues."""
        if queue_id is not None:
            if self._queue[queue_id]:
                return self._queue[queue_id][queue_pos]
            return None
        for queue in self._queue:
            if queue:
                return queue[queue_pos]
        return None

    def pop(self, queue_id: int = None) -> CommandQueueItem | None:
        """Pop first element of the command queues."""
        if queue_id is not None:
            if self._queue[queue_id]:
                return self._queue[queue_id].pop(0)
            return None
        for queue in self._queue:
            if queue:
                _LOGGER.debug("popping %s", item := queue.pop(0))
                return item
                # return queue.pop()
        return None

    def is_executing(self):
        """Return whether command queue is executing."""
        return self._execute_lock.locked()
