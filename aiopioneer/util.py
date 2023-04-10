""" Pioneer AVR utils. """
import asyncio
import socket
import random
import logging

RECONNECT_DELAY_MAX = 64

_LOGGER = logging.getLogger(__name__)


## Source: https://stackoverflow.com/a/7205107
## Modified so b overwrites a where there is a conflict
def merge(a, b, path=None, force_overwrite=False):  # pylint: disable=invalid-name
    """Recursively merges dict b into dict a."""
    if path is None:
        path = []
    for key in b:
        if key in a:
            if (
                isinstance(a[key], dict)
                and isinstance(b[key], dict)
                and not force_overwrite
            ):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif a[key] is None and isinstance(b[key], dict):
                a[key] = b[key]  # copy key from b to a
            elif b[key] is None and isinstance(a[key], dict):
                pass  # leave key in a alone
            elif (
                isinstance(a[key], list)
                and isinstance(b[key], list)
                and not force_overwrite
            ):
                a[key].extend(b[key])  # append list b to list a
            elif isinstance(b[key], list):
                a[key] = b[key][:]  # replace a[key] with shallow copy of b[key]
            else:
                a[key] = b[key]  # b overwrites a
        elif isinstance(b[key], list):
            a[key] = b[key][:]  # replace a[key] with shallow copy of b[key]
        else:
            a[key] = b[key]
    return a


## Source: https://stackoverflow.com/questions/12248132/how-to-change-tcp-keepalive-timer-using-python-script  # pylint: disable=line-too-long
def sock_set_keepalive(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    if sock:
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
        except:  # pylint: disable=bare-except
            pass  ## ignore if keepalive cannot be set


def get_backoff_delay(retry_count):
    """Calculate exponential backoff with random jitter delay."""
    delay = round(
        min(RECONNECT_DELAY_MAX, (2 ** max(retry_count, 2)))
        + (random.randint(0, 1000) / 1000),
        4,
    )
    return delay


async def safe_wait_for(awt, timeout=None):
    """
    asyncio.wait_for() that re-raises cancellation even if aw is complete.
    Work around issue: https://bugs.python.org/issue42130
    """
    task = asyncio.create_task(awt)
    try:
        await asyncio.wait({task}, timeout=timeout)
        if task.done():
            return task.result()
        else:  # timeout
            try:
                task.cancel()
                await task
            except asyncio.CancelledError:
                ## TODO: what if wait_for is cancelled when waiting for task to be cancelled?
                pass
            raise asyncio.TimeoutError()
    except asyncio.CancelledError as exc:
        raise exc


async def cancel_task(task, task_name=None, debug=False):
    """Cancels a task and waits for it to finish."""
    if task:
        if task_name is None:
            task_name = task.get_name()
        ## Trap exception if not called from a task
        current_task = None
        try:
            current_task = asyncio.Task.current_task()
        except AttributeError:
            pass
        if current_task is not None and task == current_task:
            if debug:
                _LOGGER.debug(
                    ">> cancel_task(%s): ignoring cancellation of current task",
                    task_name,
                )
            return
        if not task.done():
            if debug:
                _LOGGER.debug(">> cancel_task(%s): requesting cancellation", task_name)
            task.cancel()
            if debug:
                _LOGGER.debug(">> cancel_task(%s): waiting for completion", task_name)
            try:
                await task
            except asyncio.CancelledError:
                if debug:
                    _LOGGER.debug(">> cancel_task(%s): cancelled exception", task_name)
            except Exception as exc:  # pylint: disable=broad-except
                if debug:
                    _LOGGER.debug(
                        ">> cancel_task(%s): returned exception: %s", task_name, exc
                    )
            else:
                if debug:
                    _LOGGER.debug(">> cancel_task(%s): completed", task_name)
        else:
            if debug:
                _LOGGER.debug(">> cancel_task(%s): already completed", task_name)
            exc = task.exception()
            if exc:
                if debug:
                    _LOGGER.debug(
                        ">> cancel_task(%s): returned exception: %s", task_name, exc
                    )
