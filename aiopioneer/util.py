""" Pioneer AVR utils. """
import asyncio
import socket
import random
import logging

RECONNECT_DELAY_MAX = 64

_LOGGER = logging.getLogger(__name__)

## Source: https://stackoverflow.com/a/7205107
## Modified so b overwrites a where there is a conflict
def merge(a, b, path=None):  # pylint: disable=invalid-name
    """ Recursively merges dict b into dict a. """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif a[key] is None and isinstance(b[key], dict):
                a[key] = b[key]  # copy key from b to a
            elif b[key] is None and isinstance(a[key], dict):
                pass  # leave key in a alone
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key].extend(b[key])  # append list b to list a
            else:
                a[key] = b[key]  # b overwrites a
        else:
            a[key] = b[key]
    return a


## Source: https://stackoverflow.com/questions/12248132/how-to-change-tcp-keepalive-timer-using-python-script
def sock_set_keepalive(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    if sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)


def get_backoff_delay(retry_count):
    """ Calculate exponential backoff with random jitter delay. """
    delay = round(
        min(RECONNECT_DELAY_MAX, (2 ** max(retry_count, 2)))
        + (random.randint(0, 1000) / 1000),
        4,
    )
    return delay


async def cancel_task(task, task_name=None):
    """ Cancels a task and waits for it to finish. """
    if task:
        current_task = asyncio.Task.current_task()
        if current_task is not None and task == current_task:
            _LOGGER.debug(
                ">> cancel_task(%s): ignoring cancellation of current task", task_name
            )
            return
        if not task_name:
            task_name = task.get_name()
        if not task.done():
            _LOGGER.debug(">> cancel_task(%s): requesting cancellation", task_name)
            task.cancel()
            _LOGGER.debug(">> cancel_task(%s): waiting for task to complete", task_name)
            try:
                await task
            except asyncio.CancelledError:
                _LOGGER.debug(">> cancel_task(%s): task cancel exception", task_name)
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.debug(
                    ">> cancel_task(%s): task returned exception: %s", task_name, exc
                )
            else:
                _LOGGER.debug(">> cancel_task(%s): task completed", task_name)
        else:
            _LOGGER.debug(">> cancel_task(%s): task already completed", task_name)
            exc = task.exception()
            if exc:
                _LOGGER.debug(
                    ">> cancel_task(%s): task returned exception: %s", task_name, exc
                )
