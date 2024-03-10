"""Pioneer AVR API (async)."""

# pylint: disable=relative-beyond-top-level disable=too-many-lines


import asyncio
import time
import logging
import re
import math

from collections.abc import Callable
from inspect import isfunction

from .param import (
    PARAM_IGNORED_ZONES,
    PARAM_COMMAND_DELAY,
    PARAM_MAX_SOURCE_ID,
    PARAM_MAX_VOLUME,
    PARAM_MAX_VOLUME_ZONEX,
    PARAM_POWER_ON_VOLUME_BOUNCE,
    PARAM_VOLUME_STEP_ONLY,
    PARAM_IGNORE_VOLUME_CHECK,
    PARAM_DEBUG_LISTENER,
    PARAM_DEBUG_RESPONDER,
    PARAM_DEBUG_UPDATER,
    PARAM_DEBUG_COMMAND,
    PARAM_DEFAULTS,
    PARAM_DEFAULTS_SYSTEM,
    PARAM_MODEL_DEFAULTS,
    PARAM_EXTRA_LISTENING_MODES,
    PARAM_DISABLED_LISTENING_MODES,
    PARAM_ENABLED_LISTENING_MODES,
    PARAM_VIDEO_RESOLUTION_MODES,
    PARAM_ZONE_SOURCES,
    PARAM_ENABLED_FUNCTIONS,
    PARAM_DISABLE_AUTO_QUERY,
    PARAM_TUNER_AM_FREQ_STEP,
    PARAM_QUERY_SOURCES,
    PARAM_ALL_LISTENING_MODES,
    PARAM_AVAILABLE_LISTENING_MODES,
)
from .commands import PIONEER_COMMANDS
from .util import (
    merge,
    sock_set_keepalive,
    get_backoff_delay,
    cancel_task,
    safe_wait_for,
)
from .const import (
    Zones,
    DEFAULT_PORT,
    VERSION,
    LISTENING_MODES,
    DIMMER_MODES,
    TONE_MODES,
    TONE_DB_VALUES,
    SPEAKER_MODES,
    HDMI_OUT_MODES,
    PANEL_LOCK,
    AMP_MODES,
    MEDIA_CONTROL_COMMANDS,
    VIDEO_RESOLUTION_MODES,
    ADVANCED_VIDEO_ADJUST_MODES,
    VIDEO_PURE_CINEMA_MODES,
    VIDEO_STREAM_SMOOTHER_MODES,
    VIDEO_ASPECT_MODES,
    CHANNEL_LEVELS_OBJ,
    DSP_PHASE_CONTROL,
    DSP_SIGNAL_SELECT,
    DSP_DIGITAL_DIALOG_ENHANCEMENT,
    DSP_DUAL_MONO,
    DSP_DRC,
    DSP_HEIGHT_GAIN,
    DSP_VIRTUAL_DEPTH,
    DSP_DIGITAL_FILTER,
)

from .parsers.parse import process_raw_response

_LOGGER = logging.getLogger(__name__)


class PioneerAVR:
    """Pioneer AVR interface."""

    def __init__(
        self,
        host,
        port=DEFAULT_PORT,
        timeout=2,
        scan_interval=60,
        params=None,
    ):
        """Initialise the Pioneer AVR interface."""
        _LOGGER.info("Starting aiopioneer %s", VERSION)
        _LOGGER.debug(
            '>> PioneerAVR.__init__(host="%s", port=%s, timeout=%s, params=%s)',
            host,
            port,
            timeout,
            params,
        )
        self._host = host
        self._port = port
        self._timeout = timeout
        self.scan_interval = scan_interval

        # Public properties
        self.model = None
        self.software_version = None
        self.mac_addr = None
        self.available = False
        self.zones = []
        self.power = {}
        self.volume = {}
        self.max_volume = {}
        self.mute = {}
        self.source = {}
        self.listening_mode = ""
        self.listening_mode_raw = ""
        self.media_control_mode = {}

        # FUNC: TONE
        self.tone = {}

        # FUNC: AMP
        self.amp = {}

        # FUNC: TUNER
        self.tuner = {}

        # Complex object that holds multiple different props for the CHANNEL/DSP functions
        self.channel_levels = {}
        self.dsp = {}
        self.video = {}
        self.system = {}
        self.audio = {}

        # Parameters
        self._default_params = PARAM_DEFAULTS
        self._system_params = PARAM_DEFAULTS_SYSTEM
        self._user_params = None
        self._params = None
        self.set_user_params(params)

        # Internal state
        self._connect_lock = asyncio.Lock()
        self._disconnect_lock = asyncio.Lock()
        self._update_lock = asyncio.Lock()
        self._request_lock = asyncio.Lock()
        self._update_event = asyncio.Event()
        self._response_event = asyncio.Event()
        self._response_queue = []
        self._queue_responses = False
        self._reconnect = True
        self._full_update = True
        self._last_updated = None
        self._last_command = None
        self._reader = None
        self._writer = None
        self._listener_task = None
        self._responder_task = None
        self._reconnect_task = None
        self._updater_task = None
        self._command_queue_task = None
        self._initial_query = True
        # Stores a list of commands to run after receiving an event from the AVR
        self._command_queue = []
        self._power_zone_1 = None
        self._source_name_to_id = {}
        self._source_id_to_name = {}
        self._zone_callback = {}
        # self._update_callback = None

    def __del__(self):
        _LOGGER.debug(">> PioneerAVR.__del__()")

    @property
    def query_sources(self) -> bool:
        """Whether sources have been queried from AVR."""
        return self._system_params.get(PARAM_QUERY_SOURCES)

    def _set_query_sources(self, value: bool) -> None:
        self._system_params[PARAM_QUERY_SOURCES] = value
        self._update_params()

    def get_unique_id(self):
        """Get unique identifier for this instance."""
        return self._host + ":" + str(self._port)

    # Parameter management functions
    def _update_params(self):
        """Set current parameters."""
        self._params = {}
        merge(self._params, self._default_params)
        merge(self._params, self._user_params, force_overwrite=True)
        if (
            PARAM_TUNER_AM_FREQ_STEP in self._params
            and PARAM_TUNER_AM_FREQ_STEP in self._system_params
        ):
            ## defer PARAM_TUNER_AM_FREQ_STEP to _user_params if specified
            del self._system_params[PARAM_TUNER_AM_FREQ_STEP]
        merge(self._params, self._system_params)

    def set_user_params(self, params=None):
        """Set parameters and merge with defaults."""
        _LOGGER.debug(">> PioneerAVR.set_user_params(%s)", params)
        self._user_params = {}
        if params is not None:
            merge(self._user_params, params)
        self._update_params()
        self._update_listening_modes()

    def _set_default_params_model(self):
        """Set default parameters based on device model."""
        model = self.model
        self._default_params = PARAM_DEFAULTS
        if model is not None and model != "unknown":
            for model_regex, model_params in PARAM_MODEL_DEFAULTS.items():
                if re.search(model_regex, model):
                    _LOGGER.info(
                        "applying default parameters for model %s (%s)",
                        model,
                        model_regex,
                    )
                    merge(self._default_params, model_params, force_overwrite=True)
        self._update_params()

    def get_params(self):
        """Get a copy of all current parameters."""
        params = {}
        merge(params, self._params)
        return params

    def get_user_params(self):
        """Get a copy of user parameters."""
        params = {}
        merge(params, self._user_params)
        return params

    def get_default_params(self):
        """Get a copy of current default parameters."""
        params = {}
        merge(params, self._default_params)
        return params

    # Connection/disconnection
    async def connect(self, reconnect=True):
        """Open connection to AVR and start listener thread."""
        _LOGGER.debug(">> PioneerAVR.connect() started")
        if self._connect_lock.locked():
            _LOGGER.warning("AVR connection is already connecting, skipping connect")
            return
        if self.available:
            _LOGGER.warning("AVR is connected, skipping connect")
            return

        async with self._connect_lock:
            _LOGGER.debug("opening AVR connection")
            if self._writer is not None:
                raise RuntimeError("AVR connection already established")

            # Open new connection
            reader, writer = await asyncio.wait_for(  # pylint: disable=unused-variable
                asyncio.open_connection(self._host, self._port), timeout=self._timeout
            )
            _LOGGER.info("AVR connection established")
            self._reader = reader
            self._writer = writer
            self.available = True
            self._reconnect = reconnect
            self._set_socket_options()

            await self._responder_cancel()
            await self._listener_schedule()
            await asyncio.sleep(0)  # yield to listener task
            await self._updater_schedule()
            await asyncio.sleep(0)  # yield to updater task

        _LOGGER.debug(">> PioneerAVR.connect() completed")

    def _set_socket_options(self):
        """Set socket keepalive options."""
        sock_set_keepalive(
            self._writer.get_extra_info("socket"),
            after_idle_sec=int(self._timeout),
            interval_sec=int(self._timeout),
            max_fails=3,
        )

    async def set_timeout(self, timeout):
        """Set timeout and update socket keepalive options."""
        _LOGGER.debug(">> PioneerAVR.set_timeout(%d)", timeout)
        self._timeout = timeout
        self._set_socket_options()

    async def set_scan_interval(self, scan_interval):
        """Set scan interval and restart updater."""
        _LOGGER.debug(">> PioneerAVR.set_scan_interval(%d)", scan_interval)
        if self.scan_interval != scan_interval:
            await self._updater_cancel()
            self.scan_interval = scan_interval
            await self._updater_schedule()

    async def disconnect(self):
        """Shutdown and close telnet connection to AVR."""
        _LOGGER.debug(">> PioneerAVR.disconnect() started")

        if self._disconnect_lock.locked():
            _LOGGER.warning(
                "AVR connection is already disconnecting, skipping disconnect"
            )
            return
        if not self.available:
            _LOGGER.warning("AVR not connected, skipping disconnect")
            return

        async with self._disconnect_lock:
            _LOGGER.debug("disconnecting AVR connection")
            self.available = False
            self._call_zone_callbacks()

            await self._listener_cancel()
            await self._responder_cancel()
            await self._updater_cancel()
            await self._command_queue_cancel()

            writer = self._writer
            if writer:
                # Close AVR connection
                _LOGGER.debug("closing AVR connection")
                self._writer.close()
                try:
                    await self._writer.wait_closed()
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.debug("ignoring responder exception %s", str(exc))
            self._reader = None
            self._writer = None
            _LOGGER.info("AVR connection closed")

            await self._reconnect_schedule()

        _LOGGER.debug(">> PioneerAVR.disconnect() completed")

    async def shutdown(self):
        """Shutdown the client."""
        _LOGGER.debug(">> PioneerAVR.shutdown()")
        self._reconnect = False
        await self._reconnect_cancel()
        await self.disconnect()

    async def reconnect(self):
        """Reconnect to an AVR."""
        _LOGGER.debug(">> PioneerAVR.reconnect() started")
        retry = 0
        try:
            while not self.available:
                delay = get_backoff_delay(retry)
                _LOGGER.debug("waiting %ds before retrying connection", delay)
                await asyncio.sleep(delay)

                retry += 1
                try:
                    await self.connect()
                    # 20201212 removed as connect already schedules full update
                    # _LOGGER.debug("Scheduling full AVR status update")
                    # self._full_update = True
                    # await self.update()
                    if self.available:
                        break
                except asyncio.CancelledError:  # pylint: disable=try-except-raise
                    # pass through to outer except
                    raise
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.debug(
                        "could not reconnect to AVR: %s: %s", type(exc).__name__, exc
                    )
                    # fall through to reconnect outside try block

                if self.available:
                    await self.disconnect()
        except asyncio.CancelledError:
            _LOGGER.debug(">> PioneerAVR.reconnect() cancelled")

        _LOGGER.debug(">> PioneerAVR.reconnect() completed")

    async def _reconnect_schedule(self):
        """Schedule reconnection to the AVR."""
        if self._reconnect:
            _LOGGER.debug(">> PioneerAVR._reconnect_schedule()")
            reconnect_task = self._reconnect_task
            if reconnect_task:
                await asyncio.sleep(0)  # yield to reconnect task if running
                if reconnect_task.done():
                    reconnect_task = None  # trigger new task creation
            if reconnect_task is None:
                _LOGGER.info("reconnecting to AVR")
                reconnect_task = asyncio.create_task(self.reconnect())
                self._reconnect_task = reconnect_task
            else:
                _LOGGER.error("AVR listener reconnection already running")

    async def _reconnect_cancel(self):
        """Cancel any active reconnect task."""
        await cancel_task(self._reconnect_task, "reconnect")
        self._reconnect_task = None

    async def _connection_listener(self):
        """AVR connection listener. Parse responses and update state."""
        if self._params[PARAM_DEBUG_LISTENER]:
            _LOGGER.debug(">> PioneerAVR._connection_listener() started")
        running = True
        while self.available:
            debug_listener = self._params[PARAM_DEBUG_LISTENER]
            action = " listening for responses"
            try:
                response = await self._read_response()
                if response is None:
                    # Connection closed or exception, exit task
                    break

                # Check for empty response
                self._last_updated = time.time()  # include empty responses
                if not response:
                    # Skip processing empty responses (keepalives)
                    if debug_listener:
                        _LOGGER.debug("ignoring empty response")
                    continue
                if debug_listener:
                    _LOGGER.debug("received AVR response: %s", response)

                # Parse response, update cached properties
                action = " parsing response " + response
                parse_result = self._parse_response(response)
                updated_zones = parse_result.get("updated_zones")

                ## Queue raw response and signal response handler
                if self._queue_responses:
                    self._response_queue.append(response)
                    self._response_event.set()
                    ## Do not yield, process all responses first

                # Detect Main Zone power on for volume workaround
                action = ""
                power_on_volume_bounce = self._params[PARAM_POWER_ON_VOLUME_BOUNCE]
                if power_on_volume_bounce and self._power_zone_1 is not None:
                    if not self._power_zone_1 and self.power.get("1"):
                        # Main zone powered on, schedule bounce task
                        _LOGGER.info("scheduling main zone volume workaround")
                        self.queue_command(
                            "volume_up", skip_if_queued=False, insert_at=0
                        )
                        self.queue_command(
                            "volume_down", skip_if_queued=False, insert_at=1
                        )
                self._power_zone_1 = self.power.get("1")  # cache value

                # Implement a command queue so that we can queue commands if we
                # need to update attributes that only get updated when we
                # request them to change.
                if len(self._command_queue) > 0:
                    self._command_queue_schedule()

                # NOTE: to avoid deadlocks, do not run any operations that
                # depend on further responses (returned by the listener) within
                # the listener loop.

                if updated_zones:
                    action = f" while calling zone callbacks for {updated_zones}"
                    # Call zone callbacks for updated zones
                    self._call_zone_callbacks(updated_zones)
                    # NOTE: updating zone 1 does not reset its scan interval -
                    # scan interval is set to a regular timer

            except asyncio.CancelledError:
                if debug_listener:
                    _LOGGER.debug(">> PioneerAVR._connection_listener() cancelled")
                running = False
                break
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.error("listener exception%s: %s", action, str(exc))
                # continue listening on exception

        if running and self.available:
            # Trigger disconnection if not already disconnected
            await self.disconnect()

        _LOGGER.debug(">> PioneerAVR._connection_listener() completed")

    async def _listener_schedule(self):
        """Schedule the listener task."""
        if self._params[PARAM_DEBUG_LISTENER]:
            _LOGGER.debug(">> PioneerAVR._listener_schedule()")
        await self._listener_cancel()
        self._listener_task = asyncio.create_task(self._connection_listener())

    async def _listener_cancel(self):
        """Cancel the listener task."""
        debug_listener = self._params[PARAM_DEBUG_LISTENER]
        await cancel_task(self._listener_task, "listener", debug=debug_listener)
        self._listener_task = None

    # Reader co-routine
    async def _reader_readuntil(self):
        """Read from reader with cancel detection."""
        try:
            return await self._reader.readuntil(b"\n")
        except asyncio.CancelledError:
            if self._params[PARAM_DEBUG_RESPONDER]:
                _LOGGER.debug("reader: readuntil() was cancelled")
            return None

    # Read responses from AVR
    async def _read_response(self, timeout=None):
        """Wait for a response from AVR and return to all readers."""
        debug_responder = self._params[PARAM_DEBUG_RESPONDER]
        if debug_responder:
            _LOGGER.debug(">> PioneerAVR._read_response(timeout=%s)", timeout)

        # Schedule responder task if not already created
        responder_task = self._responder_task
        if responder_task:
            if responder_task.done():
                responder_task = None  # trigger new task creation
        if responder_task is None:
            responder_task = asyncio.create_task(self._reader_readuntil())
            # responder_task = asyncio.create_task(self._reader.readuntil(b"\n"))
            self._responder_task = responder_task
            if debug_responder:
                _LOGGER.debug("created responder task %s", responder_task.get_name())
        else:
            # Wait on existing responder task
            if debug_responder:
                _LOGGER.debug("using responder task %s", responder_task.get_name())

        # Wait for result and process
        task_name = asyncio.current_task().get_name()
        try:
            if timeout:
                if debug_responder:
                    _LOGGER.debug(
                        "%s: waiting for data (timeout=%s)", task_name, timeout
                    )
                done, pending = await asyncio.wait(  # pylint: disable=unused-variable
                    [responder_task], timeout=timeout
                )
                if done:
                    raw_response = responder_task.result()
                else:
                    _LOGGER.debug("%s: timed out waiting for data", task_name)
                    return None
            else:
                if debug_responder:
                    _LOGGER.debug("%s: waiting for data", task_name)
                raw_response = await responder_task
        except (EOFError, TimeoutError):
            # Connection closed
            if debug_responder:
                _LOGGER.debug("%s: connection closed", task_name)
            return None
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.error("%s: exception: %s", task_name, str(exc))
            return None
        if raw_response is None:  # task cancelled
            return None
        response = raw_response.decode().strip()
        if debug_responder:
            _LOGGER.debug("%s: received response: %s", task_name, response)
        return response

    async def _responder_cancel(self):
        """Cancel any active responder task."""
        debug_responder = self._params[PARAM_DEBUG_RESPONDER]
        await cancel_task(self._responder_task, "responder", debug=debug_responder)
        self._responder_task = None

    # Send commands and requests to AVR
    async def send_raw_command(self, command, rate_limit=True):
        """Send a raw command to the AVR."""
        debug_command = self._params[PARAM_DEBUG_COMMAND]
        if debug_command:
            _LOGGER.debug(
                '>> PioneerAVR.send_raw_command("%s", rate_limit=%s)',
                command,
                rate_limit,
            )
        if not self.available:
            raise RuntimeError("AVR connection not available")

        if rate_limit:
            # Rate limit commands
            command_delay = self._params[PARAM_COMMAND_DELAY]
            since_command = command_delay + 0.1
            if self._last_command:
                since_command = time.time() - self._last_command
            if since_command < command_delay:
                delay = command_delay - since_command
                if debug_command:
                    _LOGGER.debug("delaying command for %.3f s", delay)
                await asyncio.sleep(command_delay - since_command)
        _LOGGER.debug("sending command: %s", command)
        self._writer.write(command.encode("ASCII") + b"\r")
        await self._writer.drain()
        self._last_command = time.time()

    async def _wait_for_response(
        self, command: str, response_prefix: str, ignore_error: bool
    ) -> str | bool:
        """Wait for a response to a request."""
        debug_command = self._params[PARAM_DEBUG_COMMAND]

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
                    err = f"AVR command {command} returned error: {response}"
                    if ignore_error is None:
                        raise RuntimeError(err)
                    if ignore_error:
                        _LOGGER.debug(err)
                    else:
                        _LOGGER.error(err)
                    return False
            self._response_queue = []

    async def send_raw_request(
        self,
        command: str,
        response_prefix: str,
        ignore_error: bool | None = None,
        rate_limit: bool = True,
    ) -> str | bool | None:
        """Send a raw command to the AVR and return the response."""
        debug_command = self._params[PARAM_DEBUG_COMMAND]
        if debug_command:
            _LOGGER.debug(
                '>> PioneerAVR.send_raw_request("%s", %s, ignore_error=%s, rate_limit=%s)',
                command,
                response_prefix,
                ignore_error,
                rate_limit,
            )
        async with self._request_lock:  ## Only send one request at a time
            self._response_queue = []
            self._queue_responses = (
                True  ## Start queueing responses before sending command
            )
            self._response_event.clear()
            await self.send_raw_command(command, rate_limit=rate_limit)
            try:
                response = await safe_wait_for(
                    self._wait_for_response(command, response_prefix, ignore_error),
                    timeout=self._timeout,
                )
            except asyncio.TimeoutError:  # response timer expired
                _LOGGER.debug("AVR command %s timed out", command)
                response = None

            self._queue_responses = False
            self._response_queue = []
            return response

    async def send_command(
        self,
        command,
        zone="1",
        prefix="",
        ignore_error=None,
        rate_limit=True,
        suffix="",
    ):
        """Send a command or request to the device."""
        # pylint: disable=unidiomatic-typecheck disable=logging-not-lazy
        debug_command = self._params[PARAM_DEBUG_COMMAND]
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
        raw_command = PIONEER_COMMANDS.get(command, {}).get(zone)
        try:
            if type(raw_command) is list:
                if len(raw_command) == 2:
                    # Handle command as request
                    expected_response = raw_command[1]
                    raw_command = raw_command[0]
                    response = await self.send_raw_request(
                        prefix + raw_command + suffix,
                        expected_response,
                        ignore_error,
                        rate_limit,
                    )
                    if debug_command:
                        _LOGGER.debug("send_command received response: %s", response)
                    return response
                else:
                    _LOGGER.error("invalid request %s for zone %s", raw_command, zone)
                    return None
            elif type(raw_command) is str:
                return await self.send_raw_command(
                    prefix + raw_command + suffix, rate_limit
                )
            else:
                _LOGGER.warning("invalid command %s for zone %s", command, zone)
                return None
        except RuntimeError as exc:
            _LOGGER.error("cannot execute %s command: %s", command, exc)
            return False

    # Initialisation functions
    async def query_zones(self, force_update=False):
        """Query zones on Pioneer AVR by querying power status."""
        _LOGGER.info("querying available zones on AVR")
        ignored_zones = self._params[PARAM_IGNORED_ZONES]
        ignore_volume_check = self._params[PARAM_IGNORE_VOLUME_CHECK]
        added_zones = False
        # Defer updates to after query_zones has completed
        async with self._update_lock:
            if await self.send_command("query_power", "1", ignore_error=True) and (
                ignore_volume_check
                or await self.send_command("query_volume", "1", ignore_error=True)
            ):
                if "1" not in self.zones and "1" not in ignored_zones:
                    _LOGGER.info("Zone 1 discovered")
                    self.zones.append("1")
                    added_zones = True
                    self.max_volume["1"] = self._params[PARAM_MAX_VOLUME]
            else:
                raise RuntimeError("Main Zone not found on AVR")
            if await self.send_command("query_power", "2", ignore_error=True) and (
                ignore_volume_check
                or await self.send_command("query_volume", "2", ignore_error=True)
            ):
                if "2" not in self.zones and "2" not in ignored_zones:
                    _LOGGER.info("Zone 2 discovered")
                    self.zones.append("2")
                    added_zones = True
                    self.max_volume["2"] = self._params[PARAM_MAX_VOLUME_ZONEX]

            if await self.send_command("query_power", "3", ignore_error=True) and (
                ignore_volume_check
                or await self.send_command("query_volume", "3", ignore_error=True)
            ):
                if "3" not in self.zones and "3" not in ignored_zones:
                    _LOGGER.info("Zone 3 discovered")
                    self.zones.append("3")
                    added_zones = True
                    self.max_volume["3"] = self._params[PARAM_MAX_VOLUME_ZONEX]
            if await self.send_command("query_power", "Z", ignore_error=True) and (
                ignore_volume_check
                or await self.send_command("query_volume", "Z", ignore_error=True)
            ):
                if "Z" not in self.zones and "Z" not in ignored_zones:
                    _LOGGER.info("HDZone discovered")
                    self.zones.append("Z")
                    added_zones = True
                    self.max_volume["Z"] = self._params[PARAM_MAX_VOLUME_ZONEX]
        if added_zones or force_update:
            await self.update(full=True)

        self._initial_query = False

    async def update_zones(self):
        """Update zones from ignored_zones and re-query zones."""
        removed_zones = False
        for zone in self._params[PARAM_IGNORED_ZONES]:
            if zone in self.zones:
                zone_name = "HDZone" if zone == "Z" else zone
                _LOGGER.info("Removing zone %s", zone_name)
                self.zones.remove(zone)
                self._call_zone_callbacks([zone])  # update availability
                removed_zones = True
        await self.query_zones(force_update=removed_zones)

    def set_source_dict(self, sources):
        """Manually set source id<->name translation tables."""
        self._set_query_sources(False)
        source_name_to_id = {}
        merge(source_name_to_id, sources)
        self._source_name_to_id = source_name_to_id
        self._source_id_to_name = {v: k for k, v in sources.items()}

    async def build_source_dict(self):
        """Generate source id<->name translation tables."""
        timeouts = 0
        self._set_query_sources(True)
        self._source_name_to_id = {}
        self._source_id_to_name = {}
        await self._command_queue_wait()  ## wait for command queue to complete
        _LOGGER.info("querying AVR source names")
        async with self._update_lock:
            for src_id in range(self._params[PARAM_MAX_SOURCE_ID] + 1):
                response = await self.send_raw_request(
                    "?RGB" + str(src_id).zfill(2),
                    "RGB",
                    ignore_error=True,
                    rate_limit=False,
                )
                await asyncio.sleep(0)  # yield to updater task

                if response is None:
                    timeouts += 1
                    _LOGGER.debug("timeout %d retrieving source %s", timeouts, src_id)
                elif response is not False:
                    timeouts = 0
        if not self._source_name_to_id:
            _LOGGER.warning("no input sources found on AVR")

    def get_source_list(self, zone: str | Zones = Zones.Z1) -> list[str]:
        """Return list of available input sources."""

        source_ids = self._params.get(PARAM_ZONE_SOURCES[Zones(zone)], [])
        return list(
            self._source_name_to_id.keys()
            if not source_ids
            else [
                self._source_id_to_name[s]
                for s in source_ids
                if s in self._source_id_to_name
            ]
        )

    def get_source_dict(self, zone: str | Zones = None) -> dict[str, str]:
        """Return source id<->name translation tables."""

        if zone is None:
            return self._source_name_to_id
        source_ids = self._params.get(PARAM_ZONE_SOURCES[Zones(zone)], [])
        return (
            self._source_name_to_id
            if not source_ids
            else {k: v for k, v in self._source_name_to_id.items() if v in source_ids}
        )

    def get_source_name(self, source_id: str) -> str:
        """Return name for given source ID."""
        return (
            self._source_id_to_name.get(source_id, source_id)
            if self._source_name_to_id
            else source_id
        )

    def clear_source_id(self, source_id: str) -> None:
        """Clear name mapping for given source ID."""
        source_name = None
        if source_id in self._source_id_to_name:
            source_name = self._source_id_to_name[source_id]
            self._source_id_to_name.pop(source_id)
        if source_name in self._source_name_to_id:
            self._source_name_to_id.pop(source_name)

    def get_zone_listening_modes(
        self, zone: str | Zones = Zones.Z1
    ) -> dict[str, str] | None:
        """Return dict of valid listening modes and names for zone."""
        ## Listening modes only supported on main zone
        if Zones(zone) == Zones.Z1:
            multichannel = self.audio.get("input_multichannel")
            listening_modes = self._params.get(PARAM_AVAILABLE_LISTENING_MODES, {})
            zone_listening_modes = {}
            for mode_id, mode_details in listening_modes.items():
                if (multichannel and mode_details[2]) or (
                    not multichannel and mode_details[1]
                ):
                    zone_listening_modes |= {mode_id: mode_details[0]}
            return zone_listening_modes
        return None

    def _update_listening_modes(self):
        """Update list of valid listening modes for AVR."""
        all_listening_modes = LISTENING_MODES | self._params.get(
            PARAM_EXTRA_LISTENING_MODES, {}
        )
        disabled_listening_modes = self._params.get(PARAM_DISABLED_LISTENING_MODES)
        enabled_listening_modes = self._params.get(PARAM_ENABLED_LISTENING_MODES)
        available_listening_modes = {}
        available_listening_mode_names = []

        for mode_id, mode_details in all_listening_modes.items():
            if mode_id in disabled_listening_modes or (
                enabled_listening_modes and mode_id not in enabled_listening_modes
            ):
                pass
            elif mode_details[0] in available_listening_mode_names:
                _LOGGER.error(
                    "ignored duplicate listening mode name: %s", mode_details[0]
                )
            else:
                available_listening_modes |= {mode_id: mode_details}
                available_listening_mode_names.append(mode_details[0])

        _LOGGER.info("determining available listening modes")
        self._system_params[PARAM_ALL_LISTENING_MODES] = all_listening_modes
        self._system_params[PARAM_AVAILABLE_LISTENING_MODES] = available_listening_modes
        self._update_params()

    def get_ipod_control_commands(self):
        """Return a list of all valid iPod control modes."""
        return list(
            [
                k.replace("operation_ipod_", "")
                for k in PIONEER_COMMANDS
                if k.startswith("operation_ipod")
            ]
        )

    def get_tuner_control_commands(self):
        """Return a list of all valid tuner control commands."""
        return list(
            [
                k.replace("operation_tuner_", "")
                for k in PIONEER_COMMANDS
                if k.startswith("operation_tuner")
            ]
        )

    def get_supported_media_controls(self, zone):
        """Return a list of all valid media control actions for a given zone.
        If the provided zone source is not currently compatible with media controls,
        null will be returned."""
        if self.media_control_mode.get(zone) is not None:
            return list(
                [
                    k
                    for k in MEDIA_CONTROL_COMMANDS.get(
                        self.media_control_mode.get(zone)
                    ).keys()
                ]
            )
        else:
            return None

    async def query_device_info(self):
        """Query device information from Pioneer AVR."""
        if self.model or self.mac_addr or self.software_version:
            return
        self.model = "unknown"
        self.mac_addr = "unknown"
        self.software_version = "unknown"

        _LOGGER.info("querying device information from Pioneer AVR")
        await self.send_command("system_query_model", ignore_error=True)
        await self.send_command("system_query_mac_addr", ignore_error=True)
        await self.send_command("system_query_software_version", ignore_error=True)
        await asyncio.sleep(0)  # yield to updater task

        self._set_default_params_model()  # Update default params for this model
        self._update_listening_modes()  # Update valid listening modes

        # It is possible to query via HTML page if all info is not available
        # via API commands: http://avr/1000/system_information.asp
        # However, this is not compliant with Home Assistant ADR-0004:
        #
        # https://github.com/home-assistant/architecture/blob/master/adr/0004-webscraping.md
        #
        # VSX-930 will report model and software version, but not MAC address.
        # It is unknown how iControlAV5 determines this on a routed network.

    # Callback functions
    def set_zone_callback(
        self, zone: Zones | str, callback: Callable[..., None] | None = None
    ):
        """Register a callback for a zone."""
        if str(zone) in self.zones:
            if callback:
                self._zone_callback[str(zone)] = callback
            else:
                self._zone_callback.pop(str(zone))

    def clear_zone_callbacks(self):
        """Clear all callbacks for a zone."""
        self._zone_callback = {}

    def _call_zone_callbacks(self, zones: list[Zones | str] = None):
        """Call callbacks to signal updated zone(s)."""
        if not zones or Zones.ALL in zones:
            zones = self.zones
        for zone in zones:
            if str(zone) in self._zone_callback:
                callback = self._zone_callback[str(zone)]
                if callback:
                    # _LOGGER.debug("calling callback for zone %s", zone)
                    callback()

    # Update functions
    def _parse_response(self, response_raw: str):
        """Parse response and update cached parameters."""
        updated_zones = set()

        parsed_response: list = process_raw_response(response_raw, self._params)
        if parsed_response is not None:
            for response in parsed_response:
                if isfunction(response.base_property):
                    ## Call PioneerAVR class function
                    response.base_property(self)
                elif response.base_property is not None:
                    current_value = getattr(self, response.base_property)
                    if response.property_name is None and response.zone not in [
                        Zones.ALL,
                        None,
                    ]:
                        if current_value.get(response.zone.value) is not response.value:
                            current_value[response.zone.value] = response.value
                            setattr(self, response.base_property, current_value)
                            _LOGGER.info(
                                "Zone %s: %s: %s (%s)",
                                response.zone.value,
                                response.base_property,
                                getattr(self, response.base_property)[
                                    response.zone.value
                                ],
                                response.raw,
                            )

                    elif response.property_name is not None and response.zone not in [
                        Zones.ALL,
                        None,
                    ]:
                        # Set default value first otherwise we hit an exception
                        current_value.setdefault(response.zone.value, {})
                        if (
                            current_value.get(response.zone.value).get(
                                response.property_name
                            )
                            is not response.value
                        ):
                            # Set current_value to response.value for setattr
                            current_value[response.zone.value][
                                response.property_name
                            ] = response.value
                            setattr(self, response.base_property, current_value)
                            _LOGGER.info(
                                "Zone %s: %s.%s: %s (%s)",
                                response.zone.value,
                                response.base_property,
                                response.property_name,
                                getattr(self, response.base_property)[
                                    response.zone.value
                                ][response.property_name],
                                response.raw,
                            )

                    elif response.property_name is None and response.zone in [
                        Zones.ALL,
                        None,
                    ]:
                        if current_value is not response.value:
                            current_value = response.value
                            setattr(self, response.base_property, current_value)
                            _LOGGER.info(
                                "Global: %s: %s (%s)",
                                response.base_property,
                                getattr(self, response.base_property),
                                response.raw,
                            )

                    else:
                        if (
                            current_value.get(response.property_name)
                            is not response.value
                        ):
                            current_value[response.property_name] = response.value
                            setattr(self, response.base_property, current_value)
                            _LOGGER.info(
                                "Global: %s.%s: %s (%s)",
                                response.base_property,
                                response.property_name,
                                getattr(self, response.base_property)[
                                    response.property_name
                                ],
                                response.raw,
                            )

                    # Set updated_zones if response.zone is not None and not already added
                    if response.zone is not None and response.zone not in updated_zones:
                        updated_zones.add(response.zone)

                # Add any requested extra commands to run
                if response.command_queue is not None:
                    for command in response.command_queue:
                        self.queue_command(command)

                # Some specific overrides for the command queue, these are only
                # requested if we are not doing a full update
                if (
                    (response.response_command in ["PWR", "FN", "AUB", "AUA"])
                    and (not self._full_update)
                    and (not self._params.get(PARAM_DISABLE_AUTO_QUERY))
                    and (not self._initial_query)
                    and (
                        self.power.get("1")
                        or self.power.get("2")
                        or self.power.get("3")
                        or self.power.get(
                            "Z"
                        )  # These should only queue if the AVR is on
                    )
                ):
                    ## TODO: not sure why check self.tuner here?
                    if self.tuner is not None:
                        self.queue_command("query_listening_mode")
                        self.queue_command("query_audio_information")
                        self.queue_command("query_video_information")
                    # Queue a full update
                    if self.tuner is None:
                        self.queue_command("FULL_UPDATE")

        result = {"updated_zones": updated_zones}

        return result

    async def _updater(self):
        """Perform update every scan_interval."""
        debug_updater = self._params[PARAM_DEBUG_UPDATER]
        if debug_updater:
            _LOGGER.debug(">> PioneerAVR._updater() started")
        event = self._update_event
        while True:
            debug_updater = self._params[PARAM_DEBUG_UPDATER]
            try:
                event.clear()
                await self._updater_update()
                # await asyncio.wait_for(event.wait(), timeout=self.scan_interval)
                await safe_wait_for(event.wait(), timeout=self.scan_interval)
                if debug_updater:
                    _LOGGER.debug(">> PioneerAVR._updater() signalled")
            except asyncio.TimeoutError:  # update timer expired
                if debug_updater:
                    _LOGGER.debug(">> PioneerAVR._updater() timeout")
                continue
            except asyncio.CancelledError:
                if debug_updater:
                    _LOGGER.debug(">> PioneerAVR._updater() cancelled")
                break
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.error(">> PioneerAVR._updater() exception: %s", str(exc))
                break
        if debug_updater:
            _LOGGER.debug(">> PioneerAVR._updater() completed")

    async def _updater_schedule(self):
        """Schedule/reschedule the update task."""
        if self.scan_interval:
            _LOGGER.debug(">> PioneerAVR._updater_schedule()")
            await self._updater_cancel()
            self._full_update = True  # always perform full update on schedule
            self._updater_task = asyncio.create_task(self._updater())

    async def _updater_cancel(self):
        """Cancel the updater task."""
        debug_updater = self._params[PARAM_DEBUG_UPDATER]
        await cancel_task(self._updater_task, "updater", debug=debug_updater)
        self._updater_task = None

    async def _update_zone(self, zone):
        """Update an AVR zone."""
        # Check for timeouts, but ignore errors (eg. ?V will
        # return E02 immediately after power on)

        if self._params.get(PARAM_DISABLE_AUTO_QUERY):
            query_commands = []
        else:
            query_commands = [
                k
                for k in PIONEER_COMMANDS
                if (k.startswith("query"))
                and (k.split("_")[1] in self._params.get(PARAM_ENABLED_FUNCTIONS))
            ]

        # All zone updates
        if (
            await self.send_command("query_power", zone, ignore_error=True) is None
            or await self.send_command("query_volume", zone, ignore_error=True) is None
            or await self.send_command("query_mute", zone, ignore_error=True) is None
            or await self.send_command("query_source_id", zone, ignore_error=True)
            is None
        ):
            # Timeout occurred, indicates AVR disconnected
            raise TimeoutError("Timeout waiting for data")

        # Zone 1 updates only, we loop through this to allow us to add commands
        # to read without needing to add it here, also only do this if the zone
        # is powered on
        if zone == "1" and bool(self.power.get("1")):
            for comm in query_commands:
                if len(PIONEER_COMMANDS.get(comm)) == 1:
                    await self.send_command(comm, zone, ignore_error=True)

        # Zone 1 or 2 updates only, only available if zone 1 is on
        if (zone in ("1", "2")) and bool(self.power.get("1")):
            for comm in query_commands:
                if len(PIONEER_COMMANDS.get(comm)) == 2:
                    await self.send_command(comm, zone, ignore_error=True)

        # CHANNEL updates are handled differently as it requires more complex
        # logic to send the commands we use the set_channel_levels command
        # and prefix the query to it.
        # Only run this if the main zone is on
        # HDZone does not have any channels
        if ("channels" in self._params.get(PARAM_ENABLED_FUNCTIONS)) and (
            not self._params.get(PARAM_DISABLE_AUTO_QUERY)
        ):
            if bool(self.power.get("1")) and zone != "Z":
                for k in CHANNEL_LEVELS_OBJ:
                    if len(k) == 1:
                        # Add two underscores
                        k = k + "__"
                    elif len(k) == 2:
                        # Add one underscore
                        k = k + "_"
                    await self.send_command(
                        "set_channel_levels", zone, "?" + str(k), ignore_error=True
                    )

    async def _updater_update(self):
        """Update AVR cached status."""
        debug_updater = self._params[PARAM_DEBUG_UPDATER]
        if debug_updater:
            _LOGGER.debug(">> PioneerAVR._updater_update() started")
        if self._update_lock.locked():
            _LOGGER.debug("AVR updates locked, skipping")
            return False
        if not self.available:
            _LOGGER.debug("AVR not connected, skipping update")
            return False

        _rc = True
        async with self._update_lock:
            # Update only if scan_interval has passed
            now = time.time()
            full_update = self._full_update
            scan_interval = self.scan_interval
            since_updated = scan_interval + 1
            since_updated_str = "never"
            if self._last_updated:
                since_updated = now - self._last_updated
                since_updated_str = f"{since_updated:.3f} s ago"

            if full_update or not scan_interval or since_updated > scan_interval:
                _LOGGER.info(
                    "updating AVR status (full=%s, last updated %s)",
                    full_update,
                    since_updated_str,
                )
                self._last_updated = now
                self._full_update = False
                try:
                    ## TODO: update audio, video and display information
                    for zone in self.zones:
                        await self._update_zone(zone)
                    if full_update:
                        # Trigger updates to all zones on full update
                        self._call_zone_callbacks()
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.error(
                        "could not update AVR status: %s: %s",
                        type(exc).__name__,
                        str(exc),
                    )
                    _rc = False
            else:
                # NOTE: any response from the AVR received within
                # scan_interval, including keepalives and responses triggered
                # via the remote and by other clients, will cause the next
                # update to be skipped if that update is scheduled to occur
                # within scan_interval of the response.
                ##
                # Keepalives may be sent by the AVR (every 30 seconds on the
                # VSX-930) when connected to port 8102, but are not sent when
                # connected to port 23.
                _rc = None
                if debug_updater:
                    _LOGGER.debug("skipping update: last updated %s", since_updated_str)
        if _rc is False:
            # Disconnect on error
            await self.disconnect()
        if debug_updater:
            _LOGGER.debug(">> PioneerAVR._updater_update() completed")
        return _rc

    async def update(self, full=False):
        """Update AVR cached status update. Schedule if updater is running."""
        if full:
            self._full_update = True
        if self._updater_task:
            if self._params[PARAM_DEBUG_UPDATER]:
                _LOGGER.debug(">> PioneerAVR.update(): signalling updater task")
            self._update_event.set()
            await asyncio.sleep(0)  # yield to updater task
        else:
            # scan_interval not set, execute update synchronously
            await self._updater_update()

    # State change functions

    def _get_parameter_key_from_value(
        self, val: str, parameters: dict, loose_match: bool = False
    ):
        items = None
        if loose_match:
            items = [k for k, v in parameters.items() if val in v]
        else:
            items = [k for k, v in parameters.items() if v == val]

        if len(items) == 0:
            raise ValueError(f"Parameter {val} does not exist for this option")
        else:
            return str(items[0])

    def _check_zone(self, zone):
        """Check that specified zone is valid."""
        if zone not in self.zones:
            raise ValueError(f"zone {zone} does not exist on AVR")

    async def turn_on(self, zone="1"):
        """Turn on the Pioneer AVR."""
        self._check_zone(zone)
        await self.send_command("turn_on", zone)

    async def turn_off(self, zone="1"):
        """Turn off the Pioneer AVR."""
        self._check_zone(zone)
        await self.send_command("turn_off", zone)

    async def select_source(self, source: str, zone="1"):
        """Select input source."""
        self._check_zone(zone)
        source_id = self._source_name_to_id.get(source)
        if source_id:
            return await self.send_command(
                "select_source", zone, prefix=source_id, ignore_error=False
            )
        else:
            _LOGGER.error("invalid source %s for zone %s", source, zone)
            return False

    async def volume_up(self, zone="1"):
        """Volume up media player."""
        self._check_zone(zone)
        return await self.send_command("volume_up", zone, ignore_error=False)

    async def volume_down(self, zone="1"):
        """Volume down media player."""
        self._check_zone(zone)
        return await self.send_command("volume_down", zone, ignore_error=False)

    async def _execute_command_queue(self):
        """Execute commands from a queue."""
        debug_command = self._params[PARAM_DEBUG_COMMAND]
        if debug_command:
            _LOGGER.debug(">> PioneerAVR._command_queue")
        while len(self._command_queue) > 0:
            # Keep command in queue until it has finished executing
            command = self._command_queue[0]
            if debug_command:
                _LOGGER.debug("command queue executing: %s", command)
            if command == "FULL_UPDATE":
                await self.update(full=True)
            elif command == "_calculate_am_frequency_step":
                await self._calculate_am_frequency_step()
            else:
                await self.send_command(command, ignore_error=True)
            self._command_queue.pop(0)

        if debug_command:
            _LOGGER.debug("command queue finished")
        return True

    async def _command_queue_wait(self):
        """Wait for command queue to be flushed."""
        if self._params[PARAM_DEBUG_COMMAND]:
            _LOGGER.debug(">> PioneerAVR._command_queue_wait()")
        if self._command_queue_task:
            if self._command_queue_task.done():
                self._command_queue_task = None
            else:
                await asyncio.wait([self._command_queue_task])

    async def _command_queue_cancel(self):
        """Cancel any pending commands and the task itself."""
        debug_command = self._params[PARAM_DEBUG_COMMAND]
        await cancel_task(
            self._command_queue_task, "command_queue", debug=debug_command
        )
        self._command_queue_task = None
        self._command_queue = []

    def _command_queue_schedule(self):
        """Schedule commands to queue."""
        if self._params[PARAM_DEBUG_COMMAND]:
            _LOGGER.debug(">> PioneerAVR._command_queue_schedule()")
        ## NOTE: does not create new task if one already exists
        if self._command_queue_task is None or self._command_queue_task.done():
            self._command_queue_task = asyncio.create_task(
                self._execute_command_queue()
            )

    def queue_command(self, command, skip_if_queued=True, insert_at=-1):
        """Add a new command to the queue to run."""
        if self._params[PARAM_DEBUG_COMMAND]:
            _LOGGER.debug(">> PioneerAVR.queue_command(%s)", command)
        if not skip_if_queued or command not in self._command_queue:
            if command == "FULL_UPDATE":
                self._full_update = True
            if insert_at >= 0:
                self._command_queue.insert(insert_at, command)
            else:
                self._command_queue.append(command)
        else:
            if self._params[PARAM_DEBUG_COMMAND]:
                _LOGGER.debug("command %s already queued, skipping", command)

    async def _calculate_am_frequency_step(self):
        """
        Automatically calculate the AM frequency step by stepping the frequency
        up and then down.
        """
        debug_command = self._params[PARAM_DEBUG_COMMAND]
        if debug_command:
            _LOGGER.debug(">> PioneerAVR._calculate_am_frequency_step() ")
        # Try sending the query_tuner_am_step command first.
        await self.send_command(command="query_tuner_am_step", ignore_error=True)

        # Check if freq step is None, band is set to AM and current source is
        # set to tuner for at least one zone. This function otherwise does not work.
        if (
            self._params.get(PARAM_TUNER_AM_FREQ_STEP) is None
            and self.tuner.get("band") == "AM"
            and "02" in self.source.values()
        ):
            current_freq = self.tuner.get("frequency")
            new_freq = current_freq
            count = 5
            while new_freq == current_freq and count > 0:
                await self.send_command("increase_tuner_frequency", ignore_error=False)
                new_freq = self.tuner.get("frequency")
                count -= 1
            if new_freq == current_freq and count == 0:
                _LOGGER.warning("unable to calculate tuner AM frequency step")

            self._system_params[PARAM_TUNER_AM_FREQ_STEP] = new_freq - current_freq
            self._update_params()
            await asyncio.sleep(1)  ## wait for tuner command to complete
            await self.send_command("decrease_tuner_frequency", ignore_error=True)

        return True

    async def set_volume_level(self, target_volume: int, zone="1"):
        """Set volume level (0..185 for Zone 1, 0..81 for other Zones)."""
        self._check_zone(zone)
        current_volume = self.volume.get(zone)
        max_volume = self.max_volume[zone]
        if target_volume < 0 or target_volume > max_volume:
            raise ValueError(f"volume {target_volume} out of range for zone {zone}")
        volume_step_only = self._params[PARAM_VOLUME_STEP_ONLY]
        if volume_step_only:
            start_volume = current_volume
            volume_step_count = 0
            if target_volume > start_volume:  # step up
                while current_volume < target_volume:
                    _LOGGER.debug("current volume: %d", current_volume)
                    await self.volume_up(zone)
                    await asyncio.sleep(0)  # yield to listener task
                    volume_step_count += 1
                    new_volume = self.volume.get(zone)
                    if new_volume <= current_volume:  # going wrong way
                        _LOGGER.warning("set_volume_level stopped stepping up")
                        break
                    if volume_step_count > (target_volume - start_volume):
                        _LOGGER.warning("set_volume_level exceed max steps")
                    current_volume = new_volume
            else:  # step down
                while current_volume > target_volume:
                    _LOGGER.debug("current volume: %d", current_volume)
                    await self.volume_down(zone)
                    await asyncio.sleep(0)  # yield to listener task
                    volume_step_count += 1
                    new_volume = self.volume.get(zone)
                    if new_volume >= current_volume:  # going wrong way
                        _LOGGER.warning("set_volume_level stopped stepping down")
                        break
                    if volume_step_count > (start_volume - target_volume):
                        _LOGGER.warning("set_volume_level exceed max steps")
                    current_volume = self.volume.get(zone)

        else:
            vol_len = 3 if zone == "1" else 2
            vol_prefix = str(target_volume).zfill(vol_len)
            return await self.send_command(
                "set_volume_level", zone, prefix=vol_prefix, ignore_error=False
            )

    async def mute_on(self, zone="1"):
        """Mute AVR."""
        self._check_zone(zone)
        return await self.send_command("mute_on", zone, ignore_error=False)

    async def mute_off(self, zone="1"):
        """Unmute AVR."""
        self._check_zone(zone)
        return await self.send_command("mute_off", zone, ignore_error=False)

    async def set_listening_mode(self, listening_mode: str, zone="1"):
        """Set the listening mode using the predefined list of options in params."""
        self._check_zone(zone)

        listening_modes = self.get_zone_listening_modes(zone)
        if listening_modes:
            for mode_id, mode_name in listening_modes.items():
                if mode_name == listening_mode:
                    return await self.send_command(
                        "set_listening_mode",
                        zone,
                        prefix=mode_id,
                        ignore_error=False,
                    )
        raise ValueError(f"listening mode {listening_mode} not available")

    async def set_panel_lock(self, panel_lock: str, zone="1"):
        """Set the panel lock."""
        self._check_zone(zone)
        return await self.send_command(
            "set_amp_panel_lock",
            zone,
            self._get_parameter_key_from_value(panel_lock, PANEL_LOCK),
            ignore_error=False,
        )

    async def set_remote_lock(self, remote_lock: bool, zone="1"):
        """Set the remote lock."""
        self._check_zone(zone)
        return await self.send_command(
            "set_amp_remote_lock",
            zone,
            ignore_error=False,
            prefix=str(int(remote_lock)),
        )

    async def set_dimmer(self, dimmer: str, zone="1"):
        """Set the display dimmer."""
        self._check_zone(zone)
        return await self.send_command(
            "set_amp_dimmer",
            zone,
            self._get_parameter_key_from_value(dimmer, DIMMER_MODES),
            ignore_error=False,
        )

    async def set_tone_settings(
        self, tone: str = None, treble: int = None, bass: int = None, zone="1"
    ):
        """Set the tone settings for a given zone."""
        # Check the zone supports tone settings
        ## TODO: Refactor to convert to dB directly instead of using TONE_MODES
        if self.tone.get(zone) is not None:
            tone_response, tone_treble, tone_bass = True, True, True
            if tone is not None:
                tone_response = await self.send_command(
                    "set_tone_mode",
                    zone,
                    self._get_parameter_key_from_value(tone, TONE_MODES),
                    ignore_error=False,
                )
            # These actions only work if zone tone is set to "ON"
            if self.tone.get(zone) == "ON":
                if treble is not None:
                    tone_treble = await self.send_command(
                        "set_tone_treble",
                        zone,
                        self._get_parameter_key_from_value(
                            str(treble), TONE_DB_VALUES, loose_match=True
                        ),
                        ignore_error=False,
                    )
                if bass is not None:
                    tone_bass = await self.send_command(
                        "set_tone_bass",
                        zone,
                        self._get_parameter_key_from_value(
                            str(bass), TONE_DB_VALUES, loose_match=True
                        ),
                        ignore_error=False,
                    )

            # Only return true if all responses were true
            if tone_response and tone_bass and tone_treble:
                return True
            else:
                return False

    async def set_amp_settings(
        self,
        speaker_config: str = None,
        hdmi_out: str = None,
        hdmi_audio_output: bool = None,
        pqls: bool = None,
        amp: str = None,
        zone="1",
    ):
        """Set amplifier function settings for a given zone."""
        self._check_zone(zone)

        # FUNC: SPEAKERS (use PARAM_SPEAKER_MODES)
        if self.amp.get("speakers") is not None and speaker_config is not None:
            await self.send_command(
                "set_amp_speaker_status",
                zone,
                self._get_parameter_key_from_value(speaker_config, SPEAKER_MODES),
                ignore_error=False,
            )

        # FUNC: HDMI OUTPUT SELECT (use PARAM_HDMI_OUT_MODES)
        if self.amp.get("hdmi_out") is not None and hdmi_out is not None:
            await self.send_command(
                "set_amp_hdmi_out_status",
                zone,
                self._get_parameter_key_from_value(hdmi_out, HDMI_OUT_MODES),
                ignore_error=False,
            )

        # FUNC: HDMI AUDIO (simple bool, True is on, otherwise audio only goes to amp)
        if self.amp.get("hdmi_audio") is not None and hdmi_audio_output is not None:
            await self.send_command(
                "set_amp_hdmi_audio_status",
                zone,
                str(int(hdmi_audio_output)),
                ignore_error=False,
            )

        # FUNC: PQLS (simple bool, True is auto, False is off)
        if self.amp.get("pqls") is not None and pqls is not None:
            await self.send_command(
                "set_amp_pqls_status", zone, str(int(pqls)), ignore_error=False
            )

        # FUNC: AMP (use PARAM_AMP_MODES)
        if self.amp.get("status") is not None and amp is not None:
            await self.send_command(
                "set_amp_status",
                zone,
                self._get_parameter_key_from_value(amp, AMP_MODES),
                ignore_error=False,
            )

    async def _set_tuner_band(self, band: str = "FM", zone: str = "1"):
        """Set the tuner band."""

        band = band.upper()
        if (self.tuner.get("band") is None) or (self.power.get(zone) is False):
            raise SystemError("tuner is unavailable")
        if band not in ["AM", "FM"]:
            raise ValueError(f"tuner band {band} is invalid")

        # Set the tuner band
        if band != self.tuner.get("band"):
            await self.send_command(
                {"AM": "set_tuner_band_am", "FM": "set_tuner_band_fm"}[band],
                zone,
                ignore_error=False,
            )

    async def _step_tuner_frequency(self, band: str, frequency: float):
        """Step the tuner frequency until requested frequency is reached."""
        current_freq = self.tuner.get("frequency")
        if band == "AM":
            if (freq_step := self._params.get(PARAM_TUNER_AM_FREQ_STEP)) is None:
                raise ValueError(
                    "AM Tuner functions are currently not available. "
                    "Ensure 'am_frequency_step' is set."
                )

            # Divide frequency by freq_step using modf so that the remainder is
            # split out, then select the whole number response and times by
            # freq_step
            # pylint: disable=unsubscriptable-object
            target_freq = (math.modf(frequency / freq_step)[1]) * freq_step
        else:
            # Round the frequency to nearest 0.05
            target_freq = 0.05 * round(frequency / 0.05)

        # Continue adjusting until frequency is set
        resp = True
        count = 100  ## Stop stepping after maximum steps
        if target_freq > current_freq:
            while current_freq < target_freq and count > 0 and resp:
                resp = await self.send_command(
                    "increase_tuner_frequency", ignore_error=False
                )
                if resp is None:  ## ignore timeouts
                    resp = True
                current_freq = self.tuner.get("frequency")
                count -= 1
        elif target_freq < current_freq:
            while current_freq > target_freq and count > 0 and resp:
                resp = await self.send_command(
                    "decrease_tuner_frequency", ignore_error=False
                )
                if resp is None:  ## ignore timeouts
                    resp = True
                current_freq = self.tuner.get("frequency")
                count -= 1

        if count == 0:
            _LOGGER.warning("maximum frequency step count exceeded")
            resp = False
        return resp

    async def set_tuner_frequency(
        self, band: str, frequency: float = None, zone: str = "1"
    ):
        """Set the tuner frequency and band."""
        band = band.upper()
        await self._set_tuner_band(band, zone)
        await self._command_queue_wait()  ## wait for AM step to be calculated

        if frequency is None:
            return True
        elif not isinstance(frequency, float):
            raise ValueError(f"invalid frequency {frequency}")
        elif (band == "AM" and not 530 < frequency < 1700) or (
            band == "FM" and not 87.5 < frequency < 108.0
        ):
            raise ValueError(f"frequency {frequency} out of range for band {band}")

        return await self._step_tuner_frequency(band, frequency)

    async def set_tuner_preset(self, tuner_class: str, preset: int, zone="1"):
        """Set the tuner preset."""
        self._check_zone(zone)
        return await self.send_command(
            "set_tuner_preset",
            zone,
            str(tuner_class).upper() + str(preset).upper().zfill(2),
            ignore_error=False,
        )

    async def set_channel_levels(self, channel: str, level: float, zone="1"):
        """Set the level (gain) for amplifier channel in zone."""
        self._check_zone(zone)

        if self.channel_levels.get(zone) is not None:
            # Check the channel exists
            if self.channel_levels[zone].get(channel.upper()) is not None:
                # Append underscores depending on length
                if len(channel) == 1:
                    channel = channel + "__"
                elif len(channel) == 2:
                    channel = channel + "_"

                # convert the float to correct int
                level = int((level * 2) + 50)
                return await self.send_command(
                    "set_channel_levels", zone, channel + str(level), ignore_error=False
                )
            else:
                raise ValueError(
                    f"The provided channel is invalid ({channel}, {str(level)} for zone {zone}"
                )
        else:
            raise ValueError(f"Invalid zone {zone}")

    async def set_video_settings(self, **arguments):
        """Set video settings for a given zone."""
        zone = arguments.get("zone")
        self._check_zone(zone)

        # This function is only valid for zone 1, no video settings are
        # available for zone 2, 3, 4 and HDZone
        if zone != "1":
            raise ValueError(f"Invalid zone {zone}")

        # This is a complex function and supports handles requests to update any
        # video related parameters
        for arg in arguments:
            if arg != "zone":
                if arguments.get(arg) is not None:
                    if self.video.get(arg) is not arguments.get(arg):
                        if isinstance(arguments.get(arg), str):
                            # Functions to do a lookup here
                            if arg == "resolution":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), VIDEO_RESOLUTION_MODES
                                )
                                if arguments[arg] not in self._params.get(
                                    PARAM_VIDEO_RESOLUTION_MODES
                                ):
                                    raise ValueError(
                                        f"Resolution {arguments.get(arg)} is "
                                        f"not supported by current configuration."
                                    )
                            if arg == "pure_cinema":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), VIDEO_PURE_CINEMA_MODES
                                )
                            if arg == "stream_smoother":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), VIDEO_STREAM_SMOOTHER_MODES
                                )
                            if arg == "advanced_video_adjust":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), ADVANCED_VIDEO_ADJUST_MODES
                                )
                            if arg == "aspect":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), VIDEO_ASPECT_MODES
                                )

                        elif isinstance(arguments.get(arg), bool):
                            arguments[arg] = str(int(arguments.get(arg)))

                        elif isinstance(arguments.get(arg), int):
                            # parameter 0 = 50, so add 50 for all int video parameters
                            arguments[arg] += 50
                            if arg == "prog_motion":
                                arguments[arg] += 50
                            elif arg == "ynr":
                                arguments[arg] += 50
                            elif arg == "cnr":
                                arguments[arg] += 50
                            elif arg == "bnr":
                                arguments[arg] += 50
                            elif arg == "mnr":
                                arguments[arg] += 50

                        await self.send_command(
                            "set_video_" + arg,
                            zone,
                            str(arguments.get(arg)),
                            ignore_error=False,
                        )

    async def set_dsp_settings(self, **arguments):
        """Set the DSP settings for the amplifier."""
        zone = arguments.get("zone")
        self._check_zone(zone)

        if zone != "1":
            raise ValueError(f"Invalid zone {zone}")

        for arg in arguments:
            if arg != "zone":
                if arguments.get(arg) is not None:
                    if self.dsp.get(arg) is not arguments.get(arg):
                        if isinstance(arguments.get(arg), str):
                            # Functions to do a lookup here
                            if arg == "phase_control":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), DSP_PHASE_CONTROL
                                )
                            elif arg == "signal_select":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), DSP_SIGNAL_SELECT
                                )
                            elif arg == "digital_dialog_enhancement":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), DSP_DIGITAL_DIALOG_ENHANCEMENT
                                )
                            elif arg == "dual_mono":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), DSP_DUAL_MONO
                                )
                            elif arg == "drc":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), DSP_DRC
                                )
                            elif arg == "height_gain":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), DSP_HEIGHT_GAIN
                                )
                            elif arg == "virtual_depth":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), DSP_VIRTUAL_DEPTH
                                )
                            elif arg == "digital_filter":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), DSP_DIGITAL_FILTER
                                )
                        elif isinstance(arguments.get(arg), bool):
                            arguments[arg] = str(int(arguments.get(arg)))
                        elif isinstance(arguments.get(arg), float):
                            if arg == "sound_delay":
                                arguments[arg] = str(
                                    int(float(arguments.get(arg)) * 10)
                                ).zfill(3)
                            elif arg == "center_image":
                                arguments[arg] = str(
                                    int(arguments.get(arg)) * 10
                                ).zfill(2)
                        elif isinstance(arguments.get(arg), int):
                            if arg == "lfe_att":
                                arguments[arg] = int((-20 / 5) * -1)
                            elif arg == "dimension":
                                arguments[arg] = arguments.get(arg) + 50
                            elif arg == "effect":
                                arguments[arg] = str(arguments.get(arg) / 10).zfill(2)
                            elif arg == "phase_control_plus":
                                arguments[arg] = str(arguments.get(arg)).zfill(2)
                            elif arg == "center_width":
                                arguments[arg] = str(arguments.get(arg)).zfill(2)

                        await self.send_command(
                            "set_dsp_" + arg,
                            zone,
                            str(arguments.get(arg)),
                            ignore_error=False,
                        )

    async def media_control(self, action: str, zone="1"):
        """
        Perform media control activities such as play, pause, stop, fast forward
        or rewind.
        """
        self._check_zone(zone)
        if self.media_control_mode.get(zone) is not None:
            command = MEDIA_CONTROL_COMMANDS.get(self.media_control_mode.get(zone)).get(
                action
            )
            if command is not None:
                # These commands are ALWAYS sent to zone 1 because each zone
                # does not have unique commands
                return await self.send_command(command, "1", ignore_error=False)
            else:
                raise NotImplementedError(
                    f"Current source ({self.source.get(zone)} does not support action {action}"
                )
        else:
            raise NotImplementedError(
                f"Current source ({self.source.get(zone)}) does not support "
                "media_control activities."
            )

    async def set_source_name(
        self, source_id: str, source_name: str = "", default: bool = False
    ):
        """Renames a given input, set the default parameter to true to reset to default."""
        if default:
            await self.send_command(
                command="set_default_source_name", zone="1", suffix=source_id
            )
        else:
            if len(source_name) > 14:
                raise ValueError(
                    f"New source name ({source_name}) length too long. "
                    "Up to 14 characters are allowed"
                )
            if self._source_id_to_name.get(source_id) is not source_name:
                await self.send_command(
                    command="set_source_name",
                    zone="1",
                    prefix=source_name,
                    suffix=source_id,
                )
        return True
