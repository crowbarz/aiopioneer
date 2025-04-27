"""Pioneer AVR command queue class."""

import asyncio
import itertools
import logging
from typing import Self, Callable, Awaitable

from .const import Zone
from .exceptions import AVRUnavailableError
from .params import AVRParams, PARAM_DEBUG_COMMAND_QUEUE
from .util import cancel_task

_LOGGER = logging.getLogger(__name__)


class CommandItem:
    """Command queue item."""

    def __init__(
        self,
        command: str,
        *args,
        zone: Zone = Zone.Z1,
        ignore_error: bool = False,
        rate_limit: bool = True,
        skip_if_starting: bool = False,
        skip_if_refreshing: bool = False,
        skip_if_queued: bool = True,
        queue_id: int = 1,
        insert_at: int = -1,
    ):
        self.command = command
        self.args = args
        self.zone = zone
        self.ignore_error = ignore_error
        self.rate_limit = rate_limit
        self.skip_if_starting = skip_if_starting
        self.skip_if_refreshing = skip_if_refreshing
        self.skip_if_queued = skip_if_queued
        self.queue_id = queue_id
        self.insert_at = insert_at

    def __eq__(self, value: Self):
        if self.command in ["_delayed_query_basic"]:
            return self.command == value.command
        ## NOTE: assumes queue_item is lhs for `in` comparison
        if self.command == "_full_refresh" and value.command in [
            "_refresh_zone",
            "_delayed_refresh_zone",
        ]:
            return True
        return self.command == value.command and self.args == value.args

    def __repr__(self) -> str:
        flags_str = ", ".join(
            (["ignore_error"] if self.ignore_error else [])
            + (["rate_limit"] if self.rate_limit else [])
            + (["skip_if_starting"] if self.skip_if_starting else [])
            + (["skip_if_refreshing"] if self.skip_if_refreshing else [])
            + (["skip_if_queued"] if self.skip_if_queued else [])
        )
        return (
            f"Item({repr(self.command)}, args={repr(self.args)}, "
            + f"zone={self.zone.name}"
            + (", " + flags_str if flags_str else "")
            + ")"
        )


class CommandQueue:
    """
    Command queue class.

    queue 0: volume step, AM frequency step
    queue 1: all other commands
    queue 2: zone refresh commands
    queue 3: basic queries and internal state updates (listening mode)
    """

    def __init__(self, params: AVRParams, num_queues: int = 4):
        self._debug = bool(params.get_param(PARAM_DEBUG_COMMAND_QUEUE))
        self._num_queues = num_queues
        self._queue: list[list[CommandItem]] = [[] for _ in range(num_queues)]
        self._task = None
        self._execute_callback: Callable[[CommandItem], Awaitable[None]] = None
        self._command_exceptions: list[Exception] = []
        self._execute_lock = asyncio.Lock()
        self.startup_lock = asyncio.Lock()
        self.zones_pending_refresh: set[Zone] = set()

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
        self.zones_pending_refresh = set()

    def enqueue(
        self,
        item: CommandItem,
        queue_id: int = None,
        skip_if_starting: bool = None,
        skip_if_queued: bool = None,
        skip_if_refreshing: bool = None,
        insert_at: int = None,
        start_executing=True,
    ) -> None:
        """Enqueue a CommandItem in the specified command queue."""
        if not isinstance(item, CommandItem):
            raise ValueError(f"queuing invalid command: {item}")
        if skip_if_starting is None:
            skip_if_starting = item.skip_if_starting
        if skip_if_starting and self.is_starting():
            if self._debug:
                _LOGGER.debug("not queuing %s: module is starting", item)
            return
        if skip_if_refreshing is None:
            skip_if_refreshing = item.skip_if_refreshing
        if skip_if_refreshing and self.is_refreshing(item.zone):
            if self._debug:
                _LOGGER.debug("not queuing %s: zone is refreshing", item)
            return
        if skip_if_queued is None:
            skip_if_queued = item.skip_if_queued
        if queue_id is None:
            queue_id = item.queue_id
        if insert_at is None:
            insert_at = item.insert_at
        if insert_at < 0:
            insert_at = len(self._queue[queue_id]) + 1 + insert_at
        elif self.is_executing() and queue_id == self.active_queue():
            ## skip executing command at front of active queue
            insert_at += 1
        if skip_if_queued and item in self:
            if self._debug:
                _LOGGER.debug("not queuing %s: already queued", item)
            return
        _LOGGER.debug("queuing %s at pos %d in queue #%d", item, insert_at, queue_id)
        self._queue[queue_id].insert(insert_at, item)
        if start_executing:
            self.schedule()

    def extend(self, items: list[CommandItem]) -> None:
        """Extend the command queue with a list of CommandItems."""
        for item in items:
            self.enqueue(item, start_executing=False)
        self.schedule()

    def active_queue(self) -> int | None:
        """Return index of active command queue."""
        for queue_id in range(self._num_queues):
            if self._queue[queue_id]:
                return queue_id
        return None

    def peek(
        self, queue_id: int = None, queue_pos: int = 0
    ) -> tuple[int, CommandItem] | None:
        """Peek first element of the command queues."""
        if queue_id is None:
            if (queue_id := self.active_queue()) is None:
                return None
        if self._queue[queue_id]:
            return queue_id, self._queue[queue_id][queue_pos]
        return None

    def pop(self, queue_id: int = None) -> CommandItem | None:
        """Pop first element of the command queues."""
        if queue_id is not None:
            if self._queue[queue_id]:
                item = self._queue[queue_id].pop(0)
                if self._debug:
                    _LOGGER.debug("popping %s from queue #%d", item, queue_id)
                return item
            return None
        for queue in self._queue:
            if queue:
                item = queue.pop(0)
                if self._debug:
                    _LOGGER.debug("popping %s", item)
                return item
        return None

    def is_executing(self) -> bool:
        """Return whether command queue is executing."""
        return self._execute_lock.locked()

    def is_starting(self) -> bool:
        """Return whether AVR is starting."""
        return self.startup_lock.locked()

    def is_refreshing(self, zone: Zone) -> bool:
        """Return whether a zone is refreshing."""
        if zone is Zone.ALL:
            return bool(self.zones_pending_refresh)
        return zone in self.zones_pending_refresh

    async def _execute(self) -> None:
        """Execute commands from the command queue."""
        _LOGGER.debug(">> command queue started")
        async with self:
            ## Keep command in queue until it has finished executing
            while (command_peek := self.peek()) is not None:
                queue_id, command_item = command_peek
                command = command_item.command
                if self._debug:
                    _LOGGER.debug("command queue executing %s", command_item)
                try:
                    await self._execute_callback(command_item)
                except AVRUnavailableError:
                    _LOGGER.debug(">> command queue detected AVR unavailable")
                    break
                except asyncio.CancelledError:
                    _LOGGER.debug(">> command queue task cancelled")
                    break
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.error(
                        "exception executing command %s: %s", command, repr(exc)
                    )
                    self._command_exceptions.append(exc)

                self.pop(queue_id=queue_id)  ## pop from active queue

        _LOGGER.debug(">> command queue completed")

    def register_execute_callback(self, callback: Callable[[CommandItem], None]):
        """Register command queue execute callback."""
        self._execute_callback = callback

    def schedule(self) -> None:
        """Schedule command queue task."""
        if self.peek() is None:
            return

        ## NOTE: does not create new task if one already exists
        if self._task:
            if self._task.done():
                if exc := self._task.exception():
                    _LOGGER.error("command queue task exception: %s", repr(exc))
                self._task = None
        if self._task is None:
            if self._debug:
                _LOGGER.debug("creating command queue task")
            self._task = asyncio.create_task(self._execute(), name="avr_command_queue")
            self._command_exceptions = []

    async def cancel(self, ignore_exceptions: bool = False) -> None:
        """Cancel command queue task and purge the command queue."""
        if self._task:
            await cancel_task(
                self._task,
                debug=self._debug,
                ignore_exceptions=ignore_exceptions,
            )
            self._task = None
        self.purge()

    async def wait(self) -> None:
        """Wait until command queue has finished executing."""
        await asyncio.sleep(0)  ## yield to command queue task
        if self._task is None:
            return

        if self._debug:
            _LOGGER.debug("waiting for command queue to be flushed")
        await asyncio.wait([self._task])
        if self._task is None:  ## task cancelled due to shutdown
            raise AVRUnavailableError
        if exc := self._task.exception():
            ## Command queue task raised uncaught exception
            _LOGGER.error("command queue task exception: %s", repr(exc))
            return

        self._task = None
        if excs := self._command_exceptions:
            if self._debug:
                _LOGGER.debug("command queue exceptions: %s", repr(excs))

            ## Re-raise command exceptions during command queue execution
            self._command_exceptions = []
            if len(excs) == 1:
                raise excs[0]
            raise ExceptionGroup("command queue exceptions", excs)


## Test list in operator comparison order
if CommandItem("_refresh_zone") not in [CommandItem("_full_refresh")]:
    _LOGGER.warning("unexpected list membership comparison order detected")
