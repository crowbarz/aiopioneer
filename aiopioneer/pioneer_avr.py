"""Pioneer AVR API (async)."""
# pylint: disable=relative-beyond-top-level disable=too-many-lines


import asyncio
import time
import logging
import re
import math
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
    PARAM_MODEL_DEFAULTS,
    PARAM_DISABLED_LISTENING_MODES,
    PARAM_VIDEO_RESOLUTION_MODES,
    PARAM_HDZONE_SOURCES,
    PARAM_ZONE_2_SOURCES,
    PARAM_ZONE_3_SOURCES,
    PARAM_ENABLED_FUNCTIONS,
    PARAM_DISABLE_AUTO_QUERY,
    PARAM_TUNER_AM_FREQ_STEP,
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
    DEFAULT_PORT,
    VERSION,
    LISTENING_MODES,
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

from .parsers.parse import process_raw

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
        self.listening_mode = {}
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
        self._user_params = None
        self._params = None
        self.set_user_params(params)

        # Internal state
        self._connect_lock = asyncio.Lock()
        self._disconnect_lock = asyncio.Lock()
        self._update_lock = asyncio.Lock()
        self._request_lock = asyncio.Lock()
        self._update_event = asyncio.Event()
        self._reconnect = True
        self._full_update = True
        self._last_updated = 0.0
        self._last_command = 0.0
        self._reader = None
        self._writer = None
        self._listener_task = None
        self._responder_task = None
        self._reconnect_task = None
        self._updater_task = None
        self._command_queue_task = None
        # Stores a list of commands to run after receiving an event from the AVR
        self._command_queue = []
        self._power_zone_1 = None
        self._source_name_to_id = {}
        self._source_id_to_name = {}
        self._zone_callback = {}
        # self._update_callback = None

    def __del__(self):
        _LOGGER.debug(">> PioneerAVR.__del__()")

    def get_unique_id(self):
        """Get unique identifier for this instance."""
        return self._host + ":" + str(self._port)

    # Parameter management functions
    def _update_params(self):
        """Set current parameters."""
        self._params = {}
        merge(self._params, self._default_params)
        merge(self._params, self._user_params)

    def set_user_params(self, params=None):
        """Set parameters and merge with defaults."""
        _LOGGER.debug(">> PioneerAVR.set_user_params(%s)", params)
        self._user_params = {}
        if params is not None:
            self._user_params = params
        self._update_params()

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
                    merge(self._default_params, model_params, forceOverwrite=True)
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
        _LOGGER.debug(">> PioneerAVR._connection_listener() started")
        running = True
        while self.available:
            try:
                response = await self._read_response()
                if response is None:
                    # Connection closed or exception, exit task
                    break

                # Check for empty response
                debug_listener = self._params[PARAM_DEBUG_LISTENER]
                self._last_updated = time.time()  # include empty responses
                if not response:
                    # Skip processing empty responses (keepalives)
                    if debug_listener:
                        _LOGGER.debug("ignoring empty response")
                    continue
                if debug_listener:
                    _LOGGER.debug("AVR listener received response: %s", response)

                # Parse response, update cached properties
                parse_result = self._parse_response(response)
                updated_zones = parse_result.get("updated_zones")

                # Detect Main Zone power on for volume workaround
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
                if len(self._command_queue) > 0 and (
                    self._command_queue_task is None or self._command_queue_task.done()
                ):  # pylint: disable=W0212
                    _LOGGER.info(
                        "Scheduling command queue. (%s)", str(self._command_queue)
                    )
                    await self._command_queue_schedule()

                # NOTE: to avoid deadlocks, do not run any operations that
                # depend on further responses (returned by the listener) within
                # the listener loop.

                if updated_zones:
                    # Call zone callbacks for updated zones
                    self._call_zone_callbacks(updated_zones)
                    # NOTE: updating zone 1 does not reset its scan interval -
                    # scan interval is set to a regular timer

            except asyncio.CancelledError:
                _LOGGER.debug(">> PioneerAVR._connection_listener() cancelled")
                running = False
                break
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.error(
                    ">> PioneerAVR._connection_listener() exception: %s", str(exc)
                )
                print(exc)
                # continue listening on exception

        if running and self.available:
            # Trigger disconnection if not already disconnected
            await self.disconnect()

        _LOGGER.debug(">> PioneerAVR._connection_listener() completed")

    async def _listener_schedule(self):
        """Schedule the listener task."""
        _LOGGER.debug(">> PioneerAVR._listener_schedule()")
        await self._listener_cancel()
        self._listener_task = asyncio.create_task(self._connection_listener())

    async def _listener_cancel(self):
        """Cancel the listener task."""
        await cancel_task(self._listener_task, "listener")
        self._listener_task = None

    # Reader co-routine
    async def _reader_readuntil(self):
        """Read from reader with cancel detection."""
        try:
            return await self._reader.readuntil(b"\n")
        except asyncio.CancelledError:
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
                _LOGGER.debug("created responder task %s", responder_task)
        else:
            # Wait on existing responder task
            if debug_responder:
                _LOGGER.debug("using existing responder task %s", responder_task)

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
        await cancel_task(self._responder_task, "responder")
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
            since_command = time.time() - self._last_command
            command_delay = self._params[PARAM_COMMAND_DELAY]
            if since_command < command_delay:
                delay = command_delay - since_command
                _LOGGER.debug("delaying command for %.3f s", delay)
                await asyncio.sleep(command_delay - since_command)
        _LOGGER.debug("sending AVR command: %s", command)
        self._writer.write(command.encode("ASCII") + b"\r")
        await self._writer.drain()
        self._last_command = time.time()

    async def send_raw_request(
        self, command, response_prefix, ignore_error=None, rate_limit=True
    ):
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
        async with self._request_lock:
            await self.send_raw_command(command, rate_limit=rate_limit)
            while True:
                response = await self._read_response(timeout=self._timeout)

                # Check response
                if response is None:
                    _LOGGER.debug("AVR command %s timed out", command)
                    return None
                elif response.startswith(response_prefix):
                    _LOGGER.debug(
                        "AVR command %s returned response: %s", command, response
                    )
                    return response
                elif response.startswith("E"):
                    err = f"AVR command {command} returned error: {response}"
                    if ignore_error is None:
                        raise RuntimeError(err)
                    elif not ignore_error:
                        _LOGGER.error(err)
                        return False
                    elif ignore_error:
                        _LOGGER.debug(err)
                        return False

    async def send_command(
        self, command, zone="1", prefix="", ignore_error=None, rate_limit=True
    ):
        """Send a command or request to the device."""
        # pylint: disable=unidiomatic-typecheck disable=logging-not-lazy
        debug_command = self._params[PARAM_DEBUG_COMMAND]
        if debug_command:
            _LOGGER.debug(
                '>> PioneerAVR.send_command("%s", zone="%s", prefix="%s", '
                + "ignore_error=%s, rate_limit=%s)",
                command,
                zone,
                prefix,
                ignore_error,
                rate_limit,
            )
        raw_command = PIONEER_COMMANDS.get(command, {}).get(zone)
        try:
            if type(raw_command) is list:
                if len(raw_command) == 2:
                    # Handle command as request
                    expected_response = raw_command[1]
                    raw_command = raw_command[0]
                    response = await self.send_raw_request(
                        prefix + raw_command,
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
                return await self.send_raw_command(prefix + raw_command, rate_limit)
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
                    # Set high level categories if not already set
                    self.audio["1"] = {
                        "input_channels": {},
                        "output_channels": {},
                    }
                    self.tone["1"] = {}
                    self.amp = {}
                    self.tuner = {}
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

                    self.tone["2"] = {}

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
        self._source_name_to_id = sources
        self._source_id_to_name = {v: k for k, v in sources.items()}

    async def build_source_dict(self):
        """Generate source id<->name translation tables."""
        timeouts = 0
        self._source_name_to_id = {}
        self._source_id_to_name = {}
        _LOGGER.info("querying AVR source names")
        max_source_id = self._params[PARAM_MAX_SOURCE_ID]
        async with self._update_lock:
            for src_id in range(max_source_id + 1):
                response = await self.send_raw_request(
                    "?RGB" + str(src_id).zfill(2),
                    "RGB",
                    ignore_error=True,
                    rate_limit=False,
                )
                if response is None:
                    timeouts += 1
                    _LOGGER.debug("timeout %d retrieving source %s", timeouts, src_id)
                elif response is not False:
                    timeouts = 0
                    source_name = response[6:]
                    source_number = str(src_id).zfill(2)
                    self._source_name_to_id[source_name] = source_number
                    self._source_id_to_name[source_number] = source_name
        _LOGGER.debug("source name->id: %s", self._source_name_to_id)
        _LOGGER.debug("source id->name: %s", self._source_id_to_name)
        if not self._source_name_to_id:
            _LOGGER.warning("no input sources found on AVR")

    def get_source_list(self, zone="1"):
        """Return list of available input sources."""
        if zone == "1":
            return list(self._source_name_to_id.keys())
        elif zone == "2":
            return list(
                [
                    k
                    for k, v in self._source_name_to_id.items()
                    if v in self._params.get(PARAM_ZONE_2_SOURCES)
                ]
            )
        elif zone == "3":
            return list(
                [
                    k
                    for k, v in self._source_name_to_id.items()
                    if v in self._params.get(PARAM_ZONE_3_SOURCES)
                ]
            )
        elif zone == "Z":
            return list(
                [
                    k
                    for k, v in self._source_name_to_id.items()
                    if v in self._params.get(PARAM_HDZONE_SOURCES)
                ]
            )

    def get_sound_modes(self, zone):
        """Return list of valid sound modes."""
        # Check if the zone is the main zone or not, listening modes aren't supported on other zones
        if zone == "1":
            # Now check if the current input info is multi channel or not
            if self.audio.get(zone).get("input_multichannel"):
                return list(
                    [
                        v[0]
                        for k, v in LISTENING_MODES.items()
                        if bool(v[2])
                        and k not in self._params.get(PARAM_DISABLED_LISTENING_MODES)
                    ]
                )
            else:
                return list(
                    [
                        v[0]
                        for k, v in LISTENING_MODES.items()
                        if bool(v[1])
                        and k not in self._params.get(PARAM_DISABLED_LISTENING_MODES)
                    ]
                )
        else:
            return None

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

    def get_source_dict(self):
        """Return source id<->name translation tables."""
        return self._source_name_to_id

    def get_source_name(self, source_id):
        """Return name for given source ID."""
        if not self._source_name_to_id:
            return source_id
        else:
            return self._source_id_to_name.get(source_id, source_id)

    async def query_device_info(self):
        """Query device information from Pioneer AVR."""
        if self.model or self.mac_addr or self.software_version:
            return

        _LOGGER.info("querying device information from Pioneer AVR")
        model = None
        mac_addr = None
        software_version = None

        # Query model via command
        data = await self.send_command("system_query_model", ignore_error=True)
        if data:
            matches = re.search(r"<([^>/]{5,})(/.[^>]*)?>", data)
            if matches:
                model = matches.group(1)

        # Query MAC address via command
        data = await self.send_command("system_query_mac_addr", ignore_error=True)
        if data:
            mac_addr = data[0:2] + ":" + data[2:4] + ":" + data[4:6]
            mac_addr += ":" + data[6:8] + ":" + data[8:10] + ":" + data[10:12]

        # Query software version via command
        data = await self.send_command(
            "system_query_software_version", ignore_error=True
        )
        if data:
            matches = re.search(r'SSI"([^)]*)"', data)
            if matches:
                software_version = matches.group(1)

        self.model = "unknown"
        if model:
            self.model = model

        # Update default params for this model
        self._set_default_params_model()
        self.mac_addr = mac_addr if mac_addr else "unknown"
        self.software_version = software_version if software_version else "unknown"

        # It is possible to query via HTML page if all info is not available
        # via API commands: http://avr/1000/system_information.asp
        # However, this is not compliant with Home Assistant ADR-0004:
        #
        # https://github.com/home-assistant/architecture/blob/master/adr/0004-webscraping.md
        #
        # VSX-930 will report model and software version, but not MAC address.
        # It is unknown how iControlAV5 determines this on a routed network.

    # Callback functions
    def set_zone_callback(self, zone, callback):
        """Register a callback for a zone."""
        if zone in self.zones:
            if callback:
                self._zone_callback[zone] = callback
            else:
                self._zone_callback.pop(zone)

    def clear_zone_callbacks(self):
        """Clear all callbacks for a zone."""
        self._zone_callback = {}

    def _call_zone_callbacks(self, zones=None):
        """Call callbacks to signal updated zone(s)."""
        if zones is None:
            zones = self.zones
        for zone in zones:
            if zone in self._zone_callback:
                callback = self._zone_callback[zone]
                if callback:
                    _LOGGER.debug("calling callback for zone %s", zone)
                    callback()

    # Update functions
    def _parse_response(self, response):
        """Parse response and update cached parameters."""
        updated_zones = set()

        parsed_response: list = process_raw(response, self._params)
        if parsed_response is not None:
            for response in parsed_response:
                if response.base_property is not None:
                    current_value = getattr(self, response.base_property)
                    if response.property_name is None:
                        #if current_value[str(p.zone)] is not p.value:
                        current_value[response.zone] = response.value
                        setattr(self, response.base_property, current_value)
                        if response.zone not in updated_zones:
                            updated_zones.add(response.zone)
                        _LOGGER.info("Zone %s: %s: %s",
                                        response.zone,
                                        response.base_property,
                                        getattr(self, response.base_property)[response.zone]
                            )

                    else:
                        current_value.setdefault(response.zone, {})
                        current_value[response.zone][response.property_name] = response.value
                        setattr(self, response.base_property, current_value)
                        if response.zone not in updated_zones:
                            updated_zones.add(response.zone)
                        _LOGGER.info("Zone %s: %s.%s: %s",
                                        response.zone,
                                        response.base_property,
                                        response.property_name,
                                        getattr(self, response.base_property)[response.zone][response.property_name]
                            )

                # Add any requested extra commands to run
                if response.command_queue is not None:
                    for command in response.command_queue:
                        self.queue_command(command)

                # Some specific overrides for the command queue
                if response.response_command in ["PWR", "FN", "AUB", "AUA"]:
                    # Only request these if we're not doing a full update.
                    # If we are doing a full update these will be included anyway
                    if (self._full_update is False) and (
                        self.tone.get("1") is not None
                    ) and (bool(response.value)):
                        self.queue_command("query_listening_mode")
                        self.queue_command("query_audio_information")
                        self.queue_command("query_video_information")
                    # Queue a full update
                    if self.tone.get("1") is None:
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
        await cancel_task(self._updater_task, "updater")
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
            since_updated = now - self._last_updated
            full_update = self._full_update
            scan_interval = self.scan_interval
            if full_update or not scan_interval or since_updated > scan_interval:
                _LOGGER.info(
                    "updating AVR status (full=%s, last updated %.3f s ago)",
                    full_update,
                    since_updated,
                )
                self._last_updated = now
                self._full_update = False
                try:
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
                    _LOGGER.debug(
                        "skipping update: last updated %.3f s ago", since_updated
                    )
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
        # Now schedule a full update of all zones if listening_mode is None.
        # This means that the library connected to the AVR while the AVR was off
        if zone == "1" and self.listening_mode.get("1") is None:
            await self.update(full=True)

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
        """Executes commands from a queue."""
        _LOGGER.debug(">> PioneerAVR._command_queue")
        while len(self._command_queue) > 0:
            # Keep command in queue until it has finished executing
            command = self._command_queue[0]
            _LOGGER.info("Command Queue Executing: %s", command)
            if command == "FULL_UPDATE":
                await self.update(full=True)
            elif command == "_calculate_am_frequency_step":
                await self._calculate_am_frequency_step()
            else:
                await self.send_command(command, ignore_error=True)
            self._command_queue.pop(0)

        _LOGGER.debug("Command Queue Finished.")
        return True

    async def _command_queue_cancel(self):
        """Cancels any pending commands and the task itself."""
        await cancel_task(self._command_queue_task, "command_queue")
        self._command_queue_task = None

    async def _command_queue_schedule(self):
        """Schedule commands to queue."""
        _LOGGER.debug(">> PioneerAVR._command_queue_schedule()")
        await self._command_queue_cancel()
        self._command_queue_task = asyncio.create_task(self._execute_command_queue())

    def queue_command(self, command, skip_if_queued=True, insert_at=-1):
        """Add a new command to the queue to run."""
        _LOGGER.debug(">> PioneerAVR.queue_command(%s)", command)
        if not skip_if_queued or command not in self._command_queue:
            if insert_at >= 0:
                self._command_queue.insert(insert_at, command)
            else:
                self._command_queue.append(command)
        else:
            _LOGGER.debug("command %s already queued, skipping", command)

    async def _calculate_am_frequency_step(self):
        """
        Automatically calculate the AM frequency step by stepping the frequency
        up and then down.
        """
        _LOGGER.debug(">> PioneerAVR._calculate_am_frequency_step() ")
        # Check if freq step is None, band is set to AM and current source is
        # set to tuner for at least one zone. This function otherwise does not work.
        if (
            self._params.get(PARAM_TUNER_AM_FREQ_STEP) is None
            and self.tuner.get("band") == "A"
            and ("02" in list([v for k, v in self.source.items()]))
        ):
            current_f = self.tuner.get("frequency")
            await self.send_command("increase_tuner_frequency", ignore_error=False)
            # Sleep for 1s to allow for other updates and the responses to be parsed
            await asyncio.sleep(1)
            new_f = self.tuner.get("frequency")

            while new_f == current_f:
                _LOGGER.warning(
                    "Frequency increment has not changed value, %s old %s",
                    new_f,
                    current_f,
                )
                # Wait until new_f != current_f
                await self.send_command("increase_tuner_frequency", ignore_error=False)
                # Sleep for 1s to allow for other updates and the responses to be parsed
                await asyncio.sleep(1)
                new_f = self.tuner.get("frequency")

            self._params[PARAM_TUNER_AM_FREQ_STEP] = new_f - current_f
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
        """Sets the listening mode using the predefined list of options in params."""
        self._check_zone(zone)

        if self.audio.get(zone).get("input_multichannel"):
            listening_mode_key = [
                k
                for k, v in LISTENING_MODES.items()
                if bool(v[2]) and v[0] == listening_mode
            ]
        else:
            listening_mode_key = [
                k
                for k, v in LISTENING_MODES.items()
                if bool(v[1]) and v[0] == listening_mode
            ]

        if len(listening_mode_key) == 0:
            raise ValueError(f"Listening mode {listening_mode} not available")

        if len(listening_mode_key) > 1:
            raise ValueError(f"Duplicate listening modes found for {listening_mode}")

        return await self.send_command(
            "set_listening_mode",
            zone,
            prefix=listening_mode_key[0],
            ignore_error=False,
        )

    async def set_panel_lock(self, panel_lock: str, zone="1"):
        """Sets the panel lock."""
        self._check_zone(zone)
        return await self.send_command(
            "set_amp_panel_lock",
            zone,
            self._get_parameter_key_from_value(panel_lock, PANEL_LOCK),
            ignore_error=False,
        )

    async def set_remote_lock(self, remote_lock: bool, zone="1"):
        """Sets the remote lock."""
        self._check_zone(zone)
        return await self.send_command(
            "set_amp_remote_lock",
            zone,
            ignore_error=False,
            prefix=str(int(remote_lock)),
        )

    async def set_dimmer(self, dimmer, zone="1"):
        """Set the display dimmer."""
        self._check_zone(zone)
        return await self.send_command(
            "set_amp_dimmer", zone, ignore_error=False, prefix=dimmer
        )

    async def set_tone_settings(
        self, tone: str = None, treble: int = None, bass: int = None, zone="1"
    ):
        """Set the tone settings of a given zone."""
        # Check the zone supports tone settings
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
        """Set AMP function settings for a given zone."""
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

    async def set_tuner_frequency(self, band: str, frequency: float, zone: str = "1"):
        """Sets the tuner frequency and band."""

        if (self.tuner.get("band") is None) or (self.power.get(zone) is False):
            raise SystemError(
                "Tuner functions are currently not available. "
                "Ensure Zone is on and source is set to tuner."
            )

        if band.upper() == "AM" and self._params.get(PARAM_TUNER_AM_FREQ_STEP) is None:
            raise ValueError(
                "AM Tuner functions are currently not available. "
                "Ensure 'am_frequency_step' is set."
            )

        if band.upper() != "AM" and band.upper() != "FM":
            raise ValueError("The provided band is invalid")

        if band.upper() == "AM" and self.tuner.get("band") == "F":
            band = "A"
            # Set the tuner band
            await self.send_command("set_tuner_band_am", zone, ignore_error=False)
        elif band.upper() == "FM" and self.tuner.get("band") == "A":
            band = "F"
            # Set the tuner band
            await self.send_command("set_tuner_band_fm", zone, ignore_error=False)

        # Round the frequency to nearest 0.05 if band is FM, otherwise divide
        # frequency by 9 using modf so that the remainder is split out, then
        # select the whole number response and times by 9
        if band.upper() == "FM":
            frequency = round(0.05 * round(frequency / 0.05), 2)
        elif band.upper() == "AM":
            frequency = (
                math.modf(frequency / self._params.get(PARAM_TUNER_AM_FREQ_STEP))[1]
            ) * self._params.get(PARAM_TUNER_AM_FREQ_STEP)

        resp = True
        increasing = False
        # Continue adjusting until frequency is set
        while True:
            to_freq = str(frequency)
            current_freq = str(self.tuner.get("frequency"))

            if increasing:
                if current_freq >= to_freq:
                    break
            else:
                if current_freq <= to_freq:
                    break

            # Decrease frequency
            if self.tuner.get("frequency") > frequency:
                resp = await self.send_command(
                    "decrease_tuner_frequency", ignore_error=False
                )
                increasing = False
            else:
                resp = await self.send_command(
                    "increase_tuner_frequency", ignore_error=False
                )
                increasing = True

            if not resp:
                # On error, exit loop
                break

        if resp:
            return True
        else:
            return False

    async def set_channel_levels(self, channel: str, level: float, zone="1"):
        """Sets the level(gain) of each amplifier channel."""
        self._check_zone(zone)

        if self.channel_levels.get(zone) is not None:
            # Check the channel exists
            if self.channel_levels.get(zone).get(channel.upper()) is not None:
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
        """Set video settings for a given zone using provided parameters."""
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
        """Sets the DSP settings for the amplifier."""
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

    async def set_tuner_preset(self, tuner_class: str, tuner_preset: int, zone="1"):
        """Set the tuner preset to the specified class and number."""
        self._check_zone(zone)
        return await self.send_command(
            "set_tuner_preset",
            zone,
            str(tuner_class).upper() + str(tuner_preset).upper().zfill(2),
            ignore_error=False,
        )
