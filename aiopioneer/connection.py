"""Pioneer AVR connection class."""

# pylint: disable=relative-beyond-top-level disable=too-many-lines

import asyncio
import logging
import time
import traceback

from .param import (
    PioneerAVRParams,
    PARAM_COMMAND_DELAY,
    PARAM_ALWAYS_POLL,
    PARAM_DEBUG_LISTENER,
    PARAM_DEBUG_RESPONDER,
    PARAM_DEBUG_COMMAND,
)
from .commands import PIONEER_COMMANDS
from .exceptions import (
    PioneerError,
    AVRUnavailableError,
    AVRUnknownCommandError,
    AVRResponseTimeoutError,
    AVRCommandError,
    PioneerErrorFormatText,
)
from .util import (
    sock_set_keepalive,
    get_backoff_delay,
    cancel_task,
    safe_wait_for,
)
from .const import (
    Zones,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
)

from .parsers.response import Response

_LOGGER = logging.getLogger(__name__)


class PioneerAVRConnection:
    """Pioneer AVR connection class."""

    def __init__(  # pylint: disable=super-init-not-called
        self,
        params: PioneerAVRParams,
        host: str,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ):
        """Initialise the Pioneer AVR connection."""
        _LOGGER.debug(
            '>> PioneerAVRConnection.__init__(host="%s", port=%s, timeout=%s, scan_interval=%d)',
            host,
            port,
            timeout,
            scan_interval,
        )
        self.params = params
        self._host = host
        self._port = port
        self._timeout = timeout
        self.scan_interval = scan_interval

        self.available = False

        ## Internal state
        self.last_updated = None
        self._reconnect = None
        self._last_command_at = None

        self._connect_lock = asyncio.Lock()
        self._disconnect_lock = asyncio.Lock()
        self._request_lock = asyncio.Lock()
        self._listener_task = None
        self._responder_task = None
        self._reconnect_task = None
        self._response_event = asyncio.Event()
        self._response_queue: list[Response] = []
        self._queue_responses = False

        self._reader = None
        self._writer = None

    ## Connection/disconnection
    async def connect(self, reconnect: bool = True) -> None:
        """Open connection to AVR and start listener thread."""
        _LOGGER.debug(">> connect started")

        if self.available:
            raise RuntimeError("AVR is connected, skipping connect")
        if self._connect_lock.locked():
            raise RuntimeError("AVR connection is already connecting")

        async with self._connect_lock:
            _LOGGER.debug("opening AVR connection")
            if self._writer is not None:
                raise RuntimeError("AVR connection already established")

            ## Open new connection
            reader, writer = await asyncio.wait_for(  # pylint: disable=unused-variable
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
            _LOGGER.info("AVR connection established")
            self._reader = reader
            self._writer = writer
            self.available = True
            self._reconnect = reconnect
            await self.on_connect()

        _LOGGER.debug(">> connect completed")

    async def on_connect(self) -> None:
        """Start AVR tasks on connection."""
        self._set_socket_options()
        await self._responder_cancel()
        await self._listener_schedule()
        await asyncio.sleep(0)  # yield to listener task

    async def disconnect(self, reconnect: bool = None) -> None:
        """Shutdown and close connection to AVR."""
        _LOGGER.debug(">> disconnect started")

        if not self.available:
            _LOGGER.warning("AVR not connected, skipping disconnect")
            return
        if self._disconnect_lock.locked():
            raise RuntimeError("AVR connection is already disconnecting")

        await self._reconnect_cancel()
        if reconnect is None:
            reconnect = self._reconnect

        async with self._disconnect_lock:
            _LOGGER.debug("disconnecting AVR connection")
            self.available = False
            await self.on_disconnect()
            if self._writer:
                ## Close AVR connection
                _LOGGER.debug("closing AVR connection")
                self._writer.close()
                try:
                    await self._writer.wait_closed()
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.debug("ignoring disconnect exception: %s", repr(exc))
            self._reader = None
            self._writer = None
            _LOGGER.info("AVR connection closed")

            if reconnect:
                await self._reconnect_schedule()

        _LOGGER.debug(">> disconnect completed")

    async def on_disconnect(self) -> None:
        """Stop tasks on disconnect."""
        await self._responder_cancel(ignore_exception=True)
        await self._listener_cancel(ignore_exception=True)
        await asyncio.sleep(0)  # yield to responder and listener tasks

    async def shutdown(self) -> None:
        """Shutdown the client."""
        _LOGGER.debug(">> shutdown started")
        await self._reconnect_cancel()
        await self.disconnect(reconnect=False)
        await asyncio.sleep(0)  # yield to pending shutdown tasks
        _LOGGER.debug(">> shutdown completed")

    async def _reconnect_avr(self) -> None:
        """Reconnect to an AVR."""
        _LOGGER.debug(">> reconnect started")
        retry = 0
        try:
            while not self.available:
                retry += 1
                delay = get_backoff_delay(retry)
                log_retry = "waiting %.3fs before retrying connection #%d"
                _LOGGER.debug(log_retry, delay, retry)
                await asyncio.sleep(delay)

                try:
                    await self.connect()
                    if self.available:
                        break
                except asyncio.CancelledError:  # pylint: disable=try-except-raise
                    # pass through to outer except
                    raise
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.debug("could not reconnect to AVR: %s", repr(exc))
                    # fall through to reconnect outside try block

                if self.available:
                    await self.disconnect()
        except asyncio.CancelledError:
            _LOGGER.debug(">> reconnect cancelled")

        _LOGGER.debug(">> reconnect completed")

    def _set_socket_options(self) -> None:
        """Set socket keepalive options."""
        sock_set_keepalive(
            self._writer.get_extra_info("socket"),
            after_idle_sec=int(self._timeout),
            interval_sec=int(self._timeout),
            max_fails=3,
        )

    async def set_timeout(self, timeout: float) -> None:
        """Set timeout and update socket keepalive options."""
        self._timeout = timeout
        self._set_socket_options()

    async def _reconnect_schedule(self) -> None:
        """Schedule reconnection to the AVR."""
        if self._reconnect:
            _LOGGER.debug(">> scheduling reconnect")
            reconnect_task = self._reconnect_task
            if reconnect_task:
                await asyncio.sleep(0)  # yield to reconnect task if running
                if reconnect_task.done():
                    if exc := reconnect_task.exception():
                        _LOGGER.error("reconnect task exception: %s", repr(exc))
                    reconnect_task = None  # trigger new task creation
            if reconnect_task is None:
                _LOGGER.info("reconnecting to AVR")
                reconnect_task = asyncio.create_task(
                    self._reconnect_avr(), name="avr_reconnect"
                )
                self._reconnect_task = reconnect_task
            else:
                _LOGGER.error("AVR listener reconnection already running")

    async def _reconnect_cancel(self, ignore_exception=False) -> None:
        """Cancel any active reconnect task."""
        await cancel_task(self._reconnect_task, ignore_exception=ignore_exception)
        self._reconnect_task = None

    async def _connection_listener(self) -> None:
        """AVR connection listener. Parse responses and update state."""
        if self.params.get_param(PARAM_DEBUG_LISTENER):
            _LOGGER.debug(">> listener started")
        while self.available:
            action = "listening for responses"
            debug_listener = self.params.get_param(PARAM_DEBUG_LISTENER)
            try:
                response = await self._read_response()
                ## NOTE: any response from the AVR received within the
                ## scan_interval, including keepalives and responses triggered
                ## via the remote and by other clients, will cause the next
                ## update to be rescheduled to scan_interval after the last
                ## response.
                ##
                ## Keepalives may be sent by the AVR (every 30 seconds on the
                ## VSX-930) when connected to port 8102, but are not sent when
                ## connected to port 23.
                ##
                ## Check for empty response
                if not self.params.get_param(PARAM_ALWAYS_POLL):
                    self.last_updated = time.time()  # consider responses as refresh
                if response is not None and not response:
                    ## Skip processing empty responses (keepalives)
                    if debug_listener:
                        _LOGGER.debug("ignoring empty response")
                    continue
                if debug_listener:
                    _LOGGER.debug("received AVR response: %s", response)

                ## Parse response, update cached properties
                action = "parsing response " + response
                self.parse_response(response)

                ## Queue raw response and signal response handler
                if self._queue_responses:
                    self._response_queue.append(response)
                    self._response_event.set()
                    ## Do not yield, process all responses first

            except asyncio.CancelledError:
                _LOGGER.debug(">> listener task cancelled")
                break
            except (EOFError, TimeoutError):
                _LOGGER.debug(">> listener detected connection closed")
                break
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.error("listener task exception %s: %s", action, repr(exc))
                _LOGGER.error(traceback.format_exc())
                # continue listening on exception

        if not self._disconnect_lock.locked():
            # Trigger disconnection if not already disconnecting
            _LOGGER.debug(">> listener triggering disconnect")
            await self.disconnect()

        _LOGGER.debug(">> listener completed")

    def parse_response(self, response_raw: str) -> None:
        """Callback function for response parser."""
        raise RuntimeError("parse_response not implemented")

    async def _listener_schedule(self) -> None:
        """Schedule the listener task."""
        if self.params.get_param(PARAM_DEBUG_LISTENER):
            _LOGGER.debug(">> scheduling listener")
        await self._listener_cancel()
        self._listener_task = asyncio.create_task(
            self._connection_listener(), name="avr_listener"
        )

    async def _listener_cancel(self, ignore_exception=False) -> None:
        """Cancel the listener task."""
        debug_listener = self.params.get_param(PARAM_DEBUG_LISTENER)
        await cancel_task(
            self._listener_task,
            debug=debug_listener,
            ignore_exception=ignore_exception,
        )
        self._listener_task = None

    ## Reader co-routine
    async def _reader_readuntil(self) -> bytes | None:
        """Read from reader with cancel detection."""
        try:
            return await self._reader.readuntil(b"\n")
        except asyncio.CancelledError:
            _LOGGER.debug(">> responder task cancelled")
            return None

    ## Read responses from AVR
    async def _read_response(self, timeout: float = None) -> str:
        """Wait for a response from AVR and return to all readers."""
        debug_responder = self.params.get_param(PARAM_DEBUG_RESPONDER)
        if debug_responder:
            _LOGGER.debug(">> _read_response(timeout=%s)", timeout)

        ## Schedule responder task if not already created
        responder_task = self._responder_task
        if responder_task:
            if responder_task.done():
                if exc := responder_task.exception():
                    _LOGGER.error("responder task exception: %s", repr(exc))
                responder_task = None  # trigger new task creation
        if responder_task is None:
            responder_task = asyncio.create_task(
                self._reader_readuntil(), name="avr_responder"
            )
            # responder_task = asyncio.create_task(self._reader.readuntil(b"\n"))
            self._responder_task = responder_task
            if debug_responder:
                _LOGGER.debug("scheduled responder task")
        else:
            ## Wait on existing responder task
            if debug_responder:
                _LOGGER.debug("using existing responder task")

        ## Wait for result and process
        if debug_responder:
            _LOGGER.debug("responder waiting for data (timeout=%s)", timeout)
        done, _ = await asyncio.wait([responder_task], timeout=timeout or None)
        if not done:
            _LOGGER.debug("responder timed out waiting for data")
            return None  ## NOTE: does not cancel responder task
        response = responder_task.result().decode().strip()
        if debug_responder:
            _LOGGER.debug("responder received response: %s", response)
        return response

    async def _responder_cancel(self, ignore_exception=False) -> None:
        """Cancel any active responder task."""
        debug_responder = self.params.get_param(PARAM_DEBUG_RESPONDER)
        await cancel_task(
            self._responder_task,
            debug=debug_responder,
            ignore_exception=ignore_exception,
        )
        self._responder_task = None

    ## Send commands and requests to AVR
    async def send_raw_command(self, command: str, rate_limit: bool = True) -> None:
        """Send a raw command to the AVR."""
        debug_command = self.params.get_param(PARAM_DEBUG_COMMAND)
        if not self.available:
            raise AVRUnavailableError

        if rate_limit:
            # Rate limit commands
            command_delay = self.params.get_param(PARAM_COMMAND_DELAY)
            since_command = command_delay + 0.1
            if self._last_command_at:
                since_command = time.time() - self._last_command_at
            if since_command < command_delay:
                delay = command_delay - since_command
                if debug_command:
                    _LOGGER.debug("delaying command for %.3f s", delay)
                await asyncio.sleep(command_delay - since_command)
        _LOGGER.debug("sending command: %s", command)
        self._writer.write(command.encode("ASCII") + b"\r")
        await self._writer.drain()
        self._last_command_at = time.time()

    async def _wait_for_response(self, command: str, response_prefix: str) -> str:
        """Wait for a response to a request."""
        debug_command = self.params.get_param(PARAM_DEBUG_COMMAND)

        while True:
            await self._response_event.wait()
            self._response_event.clear()
            for response in self._response_queue:
                if response.startswith(response_prefix):
                    if debug_command:
                        _LOGGER.debug(
                            "AVR command %s returned response: %s", command, response
                        )
                    return response
                if response.startswith("E"):
                    raise AVRCommandError(response)
            self._response_queue = []

    async def send_raw_request(
        self,
        command: str,
        response_prefix: str,
        rate_limit: bool = True,
    ) -> str:
        """Send a raw command to the AVR and return the response."""
        async with self._request_lock:  ## Only send one request at a time
            self._response_queue = []
            self._queue_responses = (
                True  ## Start queueing responses before sending command
            )
            self._response_event.clear()
            await self.send_raw_command(command, rate_limit=rate_limit)
            try:
                # response = await asyncio.wait_for(
                response = await safe_wait_for(
                    self._wait_for_response(command, response_prefix),
                    timeout=self._timeout,
                    name="avr_wait_for_response",
                )
                await asyncio.sleep(0)  # yield to listener task
            except TimeoutError as exc:  # response timer expired
                raise AVRResponseTimeoutError from exc

            self._queue_responses = False
            self._response_queue = []
            return response

    async def send_command(
        self,
        command: str,
        zone: Zones = Zones.Z1,
        prefix: str = "",
        suffix: str = "",
        ignore_error: bool | None = None,
        rate_limit: bool = True,
    ) -> str | bool | None:
        """Send a command or request to the device."""
        # pylint: disable=unidiomatic-typecheck disable=logging-not-lazy
        debug_command = self.params.get_param(PARAM_DEBUG_COMMAND)
        if debug_command:
            _LOGGER.debug(
                '>> PioneerAVR.send_command("%s", zone="%s", prefix="%s", '
                + "ignore_error=%s, rate_limit=%s, suffix=%s)",
                command,
                zone,
                prefix,
                ignore_error,
                rate_limit,
                suffix,
            )

        async def _send_command():
            raw_command = PIONEER_COMMANDS.get(command, {}).get(zone)
            if type(raw_command) is list:
                if len(raw_command) == 2:
                    # Handle command as request
                    expected_response = raw_command[1]
                    raw_command = raw_command[0]
                    response = await self.send_raw_request(
                        prefix + raw_command + suffix,
                        response_prefix=expected_response,
                        rate_limit=rate_limit,
                    )
                    if debug_command:
                        _LOGGER.debug("send_command received response: %s", response)
                    return response
                raise AVRUnknownCommandError
            elif type(raw_command) is str:
                await self.send_raw_command(
                    prefix + raw_command + suffix, rate_limit=rate_limit
                )
                return True
            raise AVRUnknownCommandError

        if ignore_error is None:
            ## Do not handle exceptions
            return await _send_command()

        # pylint: disable=broad-exception-caught
        try:
            return await _send_command()
        except (PioneerError, Exception) as exc:
            translation_key = getattr(exc, "translation_key", "unknown_exception")
            err = PioneerErrorFormatText.get(translation_key, "unknown_exception")
            err_txt = err.format(command=command, zone=str(zone), exc=repr(exc))
            rc = False if isinstance(exc, AVRCommandError) else None

        if ignore_error:
            _LOGGER.debug(err_txt)
        else:
            _LOGGER.error(err_txt)
        return rc
