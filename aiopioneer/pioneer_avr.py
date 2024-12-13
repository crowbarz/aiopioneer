"""Pioneer AVR API (async)."""

# pylint: disable=relative-beyond-top-level disable=too-many-lines

import asyncio
import logging
import math
import time

from collections.abc import Callable
from inspect import isfunction

from .param import (
    PARAM_IGNORED_ZONES,
    PARAM_MAX_SOURCE_ID,
    PARAM_MAX_VOLUME,
    PARAM_MAX_VOLUME_ZONEX,
    PARAM_POWER_ON_VOLUME_BOUNCE,
    PARAM_VOLUME_STEP_ONLY,
    PARAM_IGNORE_VOLUME_CHECK,
    PARAM_DEBUG_UPDATER,
    PARAM_DEBUG_COMMAND_QUEUE,
    PARAM_VIDEO_RESOLUTION_MODES,
    PARAM_AVAILABLE_LISTENING_MODES,
    PARAM_ENABLED_FUNCTIONS,
    PARAM_DISABLE_AUTO_QUERY,
    PARAM_TUNER_AM_FREQ_STEP,
    PARAM_QUERY_SOURCES,
)
from .commands import PIONEER_COMMANDS
from .connection import PioneerAVRConnection
from .exceptions import (
    AVRResponseTimeoutError,
    AVRCommandError,
)
from .param import PioneerAVRParams
from .properties import PioneerAVRProperties
from .util import cancel_task
from .const import (
    Zones,
    TunerBand,
    VERSION,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    MIN_RESCAN_INTERVAL,
    SOURCE_TUNER,
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

from .parsers import process_raw_response

_LOGGER = logging.getLogger(__name__)


class PioneerAVR(PioneerAVRConnection):
    """Pioneer AVR interface."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
        params: dict[str, str] = None,
    ):
        """Initialise the Pioneer AVR interface."""
        _LOGGER.info("Starting aiopioneer %s", VERSION)
        self.params = PioneerAVRParams(params)
        self.properties = PioneerAVRProperties(self.params)
        super().__init__(
            params=self.params,
            host=host,
            port=port,
            timeout=timeout,
            scan_interval=scan_interval,
        )

        ## Public properties
        self.initial_refresh: set[Zones] = set()

        ## Internal state
        self._update_lock = asyncio.Lock()
        self._updater_task = None
        self._command_queue_task = None
        self._command_queue: list[str] = []  # queue of commands to execute
        self._power_zone_1 = None
        self._zone_callback = {}

    ## Connection/disconnection
    async def on_connect(self) -> None:
        """Start AVR tasks on connection."""
        await super().on_connect()
        await self._updater_schedule()
        await asyncio.sleep(0)  # yield to updater task

    async def on_disconnect(self) -> None:
        """Stop AVR tasks on disconnection."""
        self._call_zone_callbacks()
        await self._command_queue_cancel()
        await self._updater_cancel()
        await asyncio.sleep(0)  # yield to command queue and updater tasks
        await super().on_disconnect()

    async def set_scan_interval(self, scan_interval: int) -> None:
        """Set scan interval and restart updater."""
        _LOGGER.debug(">> set_scan_interval(%d)", scan_interval)
        if self.scan_interval != scan_interval:
            await self._updater_cancel()
            self.scan_interval = scan_interval
            await self._updater_schedule()

    ## Initialisation functions
    async def query_zones(self) -> None:
        """Query zones on Pioneer AVR by querying power status."""
        _LOGGER.info("querying available zones on AVR")
        ignored_zones = [Zones(z) for z in self.params.get_param(PARAM_IGNORED_ZONES)]
        ignore_volume_check = self.params.get_param(PARAM_IGNORE_VOLUME_CHECK)
        # Defer updates to after query_zones has completed

        async def query_zone(zone: Zones, max_volume: int) -> bool | None:
            if await self.send_command("query_power", zone, ignore_error=True) and (
                ignore_volume_check
                or await self.send_command("query_volume", zone, ignore_error=True)
            ):
                if zone not in ignored_zones:
                    _LOGGER.info("zone %s discovered", zone)
                    if zone not in self.properties.zones:
                        self.properties.zones.append(zone)
                        self.properties.max_volume[zone.value] = max_volume
                    return True
                return False
            return None

        async with self._update_lock:
            if not await query_zone(Zones.Z1, self.params.get_param(PARAM_MAX_VOLUME)):
                _LOGGER.warning("zone 1 not discovered on AVR, assuming present")
            for zone in [Zones.Z2, Zones.Z3, Zones.HDZ]:
                await query_zone(zone, self.params.get_param(PARAM_MAX_VOLUME_ZONEX))

    async def build_source_dict(self) -> None:
        """Generate source id<->name translation tables."""
        timeouts = 0
        self.params.set_system_param(PARAM_QUERY_SOURCES, True)
        self.properties.source_name_to_id = {}
        self.properties.source_id_to_name = {}
        await self._command_queue_wait()  ## wait for command queue to complete
        _LOGGER.info("querying AVR source names")
        async with self._update_lock:
            for src_id in range(self.params.get_param(PARAM_MAX_SOURCE_ID) + 1):
                try:
                    response = await self.send_command(
                        "query_source_name",
                        suffix=str(src_id).zfill(2),
                        rate_limit=False,
                    )
                except (AVRCommandError, AVRResponseTimeoutError):
                    response = None
                await asyncio.sleep(0)  # yield to updater task

                if response is None:
                    timeouts += 1
                    _LOGGER.debug("timeout %d retrieving source %s", timeouts, src_id)
                elif response is not False:
                    timeouts = 0
        if not self.properties.source_name_to_id:
            _LOGGER.warning("no input sources found on AVR")

    def get_listening_modes(self) -> dict[str, str] | None:
        """Return dict of valid listening modes and names for Zone 1."""
        multichannel = self.properties.audio.get("input_multichannel")
        listening_modes = self.params.get_param(PARAM_AVAILABLE_LISTENING_MODES, {})
        zone_listening_modes = {}
        for mode_id, mode_details in listening_modes.items():
            if (multichannel and mode_details[2]) or (
                not multichannel and mode_details[1]
            ):
                zone_listening_modes |= {mode_id: mode_details[0]}
        return zone_listening_modes

    async def query_device_model(self) -> None:
        """Query device model from Pioneer AVR."""
        _LOGGER.info("querying device model")
        if await self.send_command("query_model", ignore_error=True):
            self.params.set_default_params_model(
                self.properties.model
            )  # Update default params for this model
            self.params.update_listening_modes()  # Update valid listening modes

    async def query_device_info(self) -> None:
        """Query device information from Pioneer AVR."""
        _LOGGER.info("querying device information")
        commands = [k for k in PIONEER_COMMANDS if k.startswith("system_query_")]
        for command in commands:
            await self.send_command(command, ignore_error=True)

        ## It is possible to query via HTML page if all info is not available
        ## via API commands: http://avr/1000/system_information.asp
        ## However, this is not compliant with Home Assistant ADR-0004:
        ##
        ## https://github.com/home-assistant/architecture/blob/master/adr/0004-webscraping.md
        ##
        ## VSX-930 will report model and software version, but not MAC address.
        ## It will report software version only if Zone 1 is powered on.
        ## It is unknown how iControlAV5 determines this on a routed network.

    ## Client callback functions
    def set_zone_callback(
        self, zone: Zones, callback: Callable[..., None] | None = None
    ) -> None:
        """Register a callback for a zone."""
        if zone in self.properties.zones or zone is Zones.ALL:
            if callback:
                self._zone_callback[zone] = callback
            else:
                self._zone_callback.pop(zone)

    def clear_zone_callbacks(self) -> None:
        """Clear callbacks for all zones."""
        self._zone_callback = {}

    def _call_zone_callbacks(self, zones: list[Zones] = None) -> None:
        """Call callbacks to signal updated zone(s)."""
        if zones is None:
            zones = self.properties.zones + [Zones.ALL]
        for zone in zones:
            if zone in self._zone_callback:
                callback = self._zone_callback[zone]
                if callback:
                    callback()

    ## Response handling callbacks
    def parse_response(self, response_raw: str) -> set:
        """Parse response and update cached parameters."""
        updated_zones = set()

        ## TODO: use PioneerAVRParams object rather than dict
        parsed_response = process_raw_response(response_raw, self.params.params_all)
        if parsed_response is not None:
            for response in parsed_response:
                current_base = current_value = None
                if isfunction(response.base_property):
                    ## Call a function
                    response.base_property(self)
                elif response.base_property is not None:
                    current_base = current_value = getattr(
                        self.properties, response.base_property
                    )
                    is_global = response.zone in [Zones.ALL, None]
                    if response.property_name is None and not is_global:
                        current_value = current_base.get(response.zone)
                        if current_value != response.value:
                            current_base[response.zone] = response.value
                            setattr(
                                self.properties, response.base_property, current_base
                            )
                            _LOGGER.info(
                                "Zone %s: %s: %s -> %s (%s)",
                                response.zone,
                                response.base_property,
                                current_value,
                                response.value,
                                response.raw,
                            )
                    elif response.property_name is not None and not is_global:
                        ## Default zone dict first, otherwise we hit an exception
                        current_base.setdefault(response.zone, {})
                        current_prop = current_base.get(response.zone)
                        current_value = current_prop.get(response.property_name)
                        if current_value != response.value:
                            current_base[response.zone][
                                response.property_name
                            ] = response.value
                            setattr(
                                self.properties, response.base_property, current_base
                            )
                            _LOGGER.info(
                                "Zone %s: %s.%s: %s -> %s (%s)",
                                response.zone,
                                response.base_property,
                                response.property_name,
                                current_value,
                                response.value,
                                response.raw,
                            )
                    elif response.property_name is None and is_global:
                        if current_base != response.value:
                            setattr(
                                self.properties, response.base_property, response.value
                            )
                            _LOGGER.info(
                                "Global: %s: %s -> %s (%s)",
                                response.base_property,
                                current_base,
                                response.value,
                                response.raw,
                            )
                    else:  # response.property_name is not None and is_global:
                        current_value = current_base.get(response.property_name)
                        if current_value != response.value:
                            current_base[response.property_name] = response.value
                            setattr(
                                self.properties, response.base_property, current_base
                            )
                            _LOGGER.info(
                                "Global: %s.%s: %s -> %s (%s)",
                                response.base_property,
                                response.property_name,
                                current_value,
                                response.value,
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
                # requested if we are not doing a full refresh
                if (
                    response.base_property == "power"
                    and response.value
                    and response.zone not in self.initial_refresh
                    and not self._update_lock.locked()
                ):
                    ## Perform full refresh on zone first power on
                    self.queue_command("_sleep(2)")
                    self.queue_command(f"_refresh_zone({response.zone})")
                elif (
                    (
                        response.base_property in ["power", "source"]
                        or response.response_command in ["AUB", "AUA"]
                    )
                    and not self.params.get_param(PARAM_DISABLE_AUTO_QUERY)
                    and any(self.properties.power.values())
                    and not self._update_lock.locked()
                ):
                    self.queue_command("_delayed_query_basic_information")

        return updated_zones

    def handle_response(self, updated_zones: set) -> None:
        """Handle responses."""
        ## TODO: move workarounds in parse_response to here

        ## Detect Zone 1 power on for volume workaround
        power_on_volume_bounce = self.params.get_param(PARAM_POWER_ON_VOLUME_BOUNCE)
        if power_on_volume_bounce and self._power_zone_1 is not None:
            if not self._power_zone_1 and self.properties.power.get(Zones.Z1):
                ## Zone 1 powered on, schedule bounce task
                _LOGGER.info("scheduling main zone volume workaround")
                self.queue_command("volume_up", skip_if_queued=False, insert_at=0)
                self.queue_command("volume_down", skip_if_queued=False, insert_at=1)
        self._power_zone_1 = self.properties.power.get(Zones.Z1)  # cache value

        # Implement a command queue so that we can queue commands if we
        # need to update attributes that only get updated when we
        # request them to change.
        # self.command_queue_schedule()
        ## Now scheduled within queue_command

        # NOTE: to avoid deadlocks, do not run any operations that
        # depend on further responses (returned by the listener) within
        # the listener loop.

        if updated_zones:
            # Call zone callbacks for updated zones
            self._call_zone_callbacks(updated_zones)
            # NOTE: updating zone 1 does not reset its scan interval -
            # scan interval is set to a regular timer

    ## AVR Updater
    async def _updater(self) -> None:
        """Queue a full refresh every scan interval."""
        debug_updater = self.params.get_param(PARAM_DEBUG_UPDATER)
        if debug_updater:
            _LOGGER.debug(">> updater started")
        while True:
            debug_updater = self.params.get_param(PARAM_DEBUG_UPDATER)
            try:
                ## Calculate scan_interval from time of last response
                sleep_time = self.scan_interval
                if last_updated := self.last_updated:
                    sleep_time = self.scan_interval - (time.time() - last_updated)
                await asyncio.sleep(max(MIN_RESCAN_INTERVAL, sleep_time))

                ## Perform full refresh if AVR has not been updated since sleep
                if self.last_updated == last_updated:
                    if debug_updater:
                        _LOGGER.debug("updater triggered full refresh")
                    self.queue_command("_full_refresh")
            except asyncio.CancelledError:
                if debug_updater:
                    _LOGGER.debug("updater cancelled")
                break
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.error("updater exception: %s", repr(exc))
                break

        _LOGGER.debug(">> updater completed")

    async def _updater_schedule(self) -> None:
        """Schedule/reschedule the update task."""
        _LOGGER.debug(">> scheduling updater")
        await self._updater_cancel()
        if self.scan_interval:
            self._updater_task = asyncio.create_task(
                self._updater(), name="avr_updater"
            )

    async def _updater_cancel(self) -> None:
        """Cancel the updater task."""
        debug_updater = self.params.get_param(PARAM_DEBUG_UPDATER)
        await cancel_task(self._updater_task, "updater", debug=debug_updater)
        self._updater_task = None

    async def _refresh_zone(self, zone: Zones) -> None:
        """Perform full refresh an AVR zone."""
        ## Refresh only if zone is powered on
        await self.send_command("query_power", zone)
        if not bool(self.properties.power.get(zone)):
            return

        ## Check for timeouts, but ignore errors (eg. ?V will
        # return E02 immediately after power on)
        if (
            await self.send_command("query_volume", zone, ignore_error=True) is None
            or await self.send_command("query_mute", zone, ignore_error=True) is None
            or await self.send_command("query_source_id", zone, ignore_error=True)
            is None
        ):
            ## Timeout occurred, AVR may be disconnected
            raise TimeoutError("Timeout waiting for data")

        ## Zone-specific updates, if enabled
        if self.params.get_param(PARAM_DISABLE_AUTO_QUERY):
            return

        ## Loop through PIONEER_COMMANDS to allow us to add query commands
        ## without needing to add it here
        for comm, supported_zones in PIONEER_COMMANDS.items():
            if zone in supported_zones:
                if comm.startswith("query_") and comm.split("_")[
                    1
                ] in self.params.get_param(PARAM_ENABLED_FUNCTIONS):
                    await self.send_command(comm, zone, ignore_error=True)
                elif (
                    comm == "set_channel_levels"
                    and "channels" in self.params.get_param(PARAM_ENABLED_FUNCTIONS)
                    and bool(self.properties.power.get(Zones.Z1))
                ):
                    ## Channel level updates are handled differently as it
                    ## requires more complex logic to send the commands we use
                    ## the set_channel_levels command and prefix the query to it
                    for k in CHANNEL_LEVELS_OBJ:
                        await self.send_command(
                            comm,
                            zone,
                            prefix="?" + k.ljust(3, "_"),
                            ignore_error=True,
                        )

    async def _refresh_zones(self, zones: set[Zones]) -> None:
        """Refresh AVR zones."""
        if not self.available:
            _LOGGER.debug("AVR not connected, skipping refresh")
            return False
        if not self.properties.zones:
            _LOGGER.debug("AVR zones not discovered yet, skipping refresh")
            return False

        now = time.time()
        last_updated_str = "never"
        if self.last_updated:
            last_updated_str = f"{(now - self.last_updated):.3f}s ago"
        log_refresh = "refreshing AVR status (zones=%s, last updated %s)"
        _LOGGER.info(log_refresh, zones, last_updated_str)
        self.last_updated = time.time()
        try:
            for zone in zones:
                await self._refresh_zone(zone)
                if self.properties.power[zone] and zone not in self.initial_refresh:
                    if zone is Zones.Z1:
                        await self.query_device_info()
                    _LOGGER.info("completed initial refresh for zone %s", zone)
                    self.initial_refresh.add(zone)

            ## Trigger callbacks to all zones on refresh
            self._call_zone_callbacks(zones=[Zones.ALL])
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.error("exception refreshing AVR status: %s", repr(exc))

        _LOGGER.debug(">> refresh completed")

    async def update(self, zones: list[Zones] = None, wait: bool = True) -> None:
        """Update AVR cached status."""
        if not zones:
            self.queue_command("_full_refresh")
        else:
            for zone in zones:
                self.queue_command(f"_refresh_zone({zone})")
        if wait:
            await self._command_queue_wait()

    ## Command queue
    async def _execute_command_queue(self) -> None:
        """Execute commands from a queue."""
        debug_command_queue = self.params.get_param(PARAM_DEBUG_COMMAND_QUEUE)

        async def local_command(
            command: str, command_name: str, args: list[str]
        ) -> None:
            if debug_command_queue:
                _LOGGER.debug("running local command %s, args: %s", command, args)
            match command_name:
                case "_full_refresh":
                    await self._refresh_zones(zones=self.properties.zones)
                case "_refresh_zone":
                    if len(args) != 1:
                        raise ValueError("_refresh_zone requires zone argument")
                    await self._refresh_zones(zones=[Zones(args[0])])
                case "_delayed_query_basic_information":
                    self.queue_command("_sleep(4)", insert_at=1)
                    self.queue_command("_query_basic_information", insert_at=2)
                case "_query_basic_information":
                    if any(self.properties.power.values()):
                        for cmd in [
                            "query_listening_mode",
                            "query_basic_audio_information",
                            "query_basic_video_information",
                        ]:
                            await self.send_command(cmd, ignore_error=True)
                case "_calculate_am_frequency_step":
                    await self._calculate_am_frequency_step()
                case "_sleep":
                    if len(args) != 1:
                        raise ValueError("_sleep requires delay argument")
                    delay = float(args[0])
                    await asyncio.sleep(delay)
                case _:
                    raise ValueError(f"unknown local command: {command_name}")

        if debug_command_queue:
            _LOGGER.debug(">> command queue started")
        async with self._update_lock:
            while len(self._command_queue) > 0:
                ## Keep command in queue until it has finished executing
                command = self._command_queue[0]
                _LOGGER.debug("command queue executing %s", command)
                try:
                    if command.startswith("_"):
                        command_tokens = command.split("(", 1)
                        command_name = command_tokens[0]
                        args = []
                        if len(command_tokens) > 1:
                            args_raw = command_tokens[1].split(")", 1)
                            args = [arg.strip() for arg in args_raw[0].split(",")]
                            if len(args_raw) < 2 or args_raw[1] != "":
                                raise ValueError(
                                    f"malformed local command: '{command}'"
                                )
                        await local_command(command, command_name, args)
                    else:
                        await self.send_command(command, ignore_error=False)
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.error(
                        "exception executing command %s: %s", command, repr(exc)
                    )
                self._command_queue.pop(0)

        if debug_command_queue:
            _LOGGER.debug(">> command queue completed")

    async def _command_queue_wait(self) -> None:
        """Wait for command queue to be flushed."""
        debug_command_queue = self.params.get_param(PARAM_DEBUG_COMMAND_QUEUE)
        if self._command_queue_task:
            if self._command_queue_task.done():
                if exc := self._command_queue_task.exception():
                    _LOGGER.error("command queue task exception: %s", repr(exc))
                self._command_queue_task = None
            else:
                if debug_command_queue:
                    _LOGGER.debug("waiting for command queue to be flushed")
                await asyncio.wait([self._command_queue_task])

    async def _command_queue_cancel(self) -> None:
        """Cancel any pending commands and the task itself."""
        debug_command_queue = self.params.get_param(PARAM_DEBUG_COMMAND_QUEUE)
        await cancel_task(
            self._command_queue_task, "command_queue", debug=debug_command_queue
        )
        self._command_queue_task = None
        self._command_queue = []

    def command_queue_schedule(self) -> None:
        """Schedule commands to queue."""
        if len(self._command_queue) == 0:
            return

        ## NOTE: does not create new task if one already exists
        if self._command_queue_task:
            if self._command_queue_task.done():
                if exc := self._command_queue_task.exception():
                    _LOGGER.error("responder task exception: %s", repr(exc))
                self._command_queue_task = None
        if self._command_queue_task is None:
            if self.params.get_param(PARAM_DEBUG_COMMAND_QUEUE):
                _LOGGER.debug("creating command queue task")
            self._command_queue_task = asyncio.create_task(
                self._execute_command_queue(), name="avr_command_queue"
            )

    def queue_command(
        self, command: str, skip_if_queued: bool = True, insert_at: int = -1
    ) -> None:
        """Add a new command to the queue to run."""
        if skip_if_queued and command in self._command_queue:
            _LOGGER.debug("command %s already queued, skipping", command)
            return
        _LOGGER.debug("queuing command %s", command)
        if insert_at >= 0:
            self._command_queue.insert(insert_at, command)
        else:
            self._command_queue.append(command)
        self.command_queue_schedule()

    ## AVR methods
    def _get_parameter_key_from_value(
        self, val: str, parameters: dict, loose_match: bool = False
    ) -> str:
        items = None
        if loose_match:
            items = [k for k, v in parameters.items() if val in v]
        else:
            items = [k for k, v in parameters.items() if v == val]

        if len(items) == 0:
            raise ValueError(f"Parameter {val} does not exist for this option")
        else:
            return str(items[0])

    def _check_zone(self, zone: Zones) -> Zones:
        """Check that specified zone is valid."""
        if zone not in self.properties.zones:
            raise ValueError(f"zone {zone} does not exist on AVR")
        return zone

    async def turn_on(self, zone: Zones = Zones.Z1) -> None:
        """Turn on the Pioneer AVR zone."""
        zone = self._check_zone(zone)
        await self.send_command("turn_on", zone)

    async def turn_off(self, zone: Zones = Zones.Z1) -> None:
        """Turn off the Pioneer AVR zone."""
        zone = self._check_zone(zone)
        await self.send_command("turn_off", zone)

    async def select_source(
        self, source: str = None, source_id: str = None, zone: Zones = Zones.Z1
    ) -> None:
        """Select input source."""
        zone = self._check_zone(zone)
        if source_id is None:
            source_id = self.properties.source_name_to_id.get(source)
        if source_id is None:
            raise ValueError(f"invalid source {source} for zone {zone}")

        await self.send_command("select_source", zone, prefix=source_id)

    async def volume_up(self, zone: Zones = Zones.Z1) -> None:
        """Volume up media player."""
        zone = self._check_zone(zone)
        await self.send_command("volume_up", zone)

    async def volume_down(self, zone: Zones = Zones.Z1) -> None:
        """Volume down media player."""
        zone = self._check_zone(zone)
        await self.send_command("volume_down", zone)

    async def set_volume_level(
        self, target_volume: int, zone: Zones = Zones.Z1
    ) -> bool:
        """Set volume level (0..185 for Zone 1, 0..81 for other Zones)."""
        zone = self._check_zone(zone)
        current_volume = self.properties.volume.get(zone.value)
        max_volume = self.properties.max_volume[zone.value]
        if target_volume < 0 or target_volume > max_volume:
            raise ValueError(f"volume {target_volume} out of range for zone {zone}")
        volume_step_only = self.params.get_param(PARAM_VOLUME_STEP_ONLY)
        if volume_step_only:
            start_volume = current_volume
            volume_step_count = 0
            if target_volume > start_volume:  # step up
                while current_volume < target_volume:
                    _LOGGER.debug("current volume: %d", current_volume)
                    await self.volume_up(zone)
                    volume_step_count += 1
                    new_volume = self.properties.volume.get(zone.value)
                    if new_volume <= current_volume:  # going wrong way
                        _LOGGER.warning("set_volume_level stopped stepping up")
                        return False
                    if volume_step_count > (target_volume - start_volume):
                        _LOGGER.warning("set_volume_level exceed max steps")
                        return False
                    current_volume = new_volume
            else:  # step down
                while current_volume > target_volume:
                    _LOGGER.debug("current volume: %d", current_volume)
                    await self.volume_down(zone)
                    volume_step_count += 1
                    new_volume = self.properties.volume.get(zone.value)
                    if new_volume >= current_volume:  # going wrong way
                        _LOGGER.warning("set_volume_level stopped stepping down")
                        return False
                    if volume_step_count > (start_volume - target_volume):
                        _LOGGER.warning("set_volume_level exceed max steps")
                        return False
                    current_volume = self.properties.volume.get(zone.value)
            return True

        else:
            vol_len = 3 if Zones(zone) is Zones.Z1 else 2
            vol_prefix = str(target_volume).zfill(vol_len)
            return bool(
                await self.send_command(
                    "set_volume_level", zone, prefix=vol_prefix, ignore_error=False
                )
            )

    async def mute_on(self, zone: Zones = Zones.Z1) -> None:
        """Mute AVR."""
        zone = self._check_zone(zone)
        await self.send_command("mute_on", zone, ignore_error=False)

    async def mute_off(self, zone: Zones = Zones.Z1) -> None:
        """Unmute AVR."""
        zone = self._check_zone(zone)
        await self.send_command("mute_off", zone, ignore_error=False)

    async def select_listening_mode(
        self, mode_name: str = None, mode_id: str = None
    ) -> None:
        """Set the listening mode using the predefined list of options in params."""

        if mode_name and mode_id is None:
            listening_modes = self.get_listening_modes()
            if listening_modes:
                for mode_id_item, mode_name_item in listening_modes.items():
                    if mode_name == mode_name_item:
                        mode_id = mode_id_item
                        break
        if mode_id is None:
            raise ValueError(f"listening mode {mode_name} not available")
        await self.send_command("set_listening_mode", prefix=mode_id)

    async def set_panel_lock(self, panel_lock: str) -> None:
        """Set the panel lock."""
        await self.send_command(
            "set_amp_panel_lock",
            prefix=self._get_parameter_key_from_value(panel_lock, PANEL_LOCK),
        )

    async def set_remote_lock(self, remote_lock: bool) -> None:
        """Set the remote lock."""
        await self.send_command("set_amp_remote_lock", prefix=str(int(remote_lock)))

    async def set_dimmer(self, dimmer: str) -> None:
        """Set the display dimmer."""
        await self.send_command(
            "set_amp_dimmer",
            prefix=self._get_parameter_key_from_value(dimmer, DIMMER_MODES),
        )

    async def set_tone_settings(
        self,
        tone: str = None,
        treble: int = None,
        bass: int = None,
        zone: Zones = Zones.Z1,
    ) -> None:
        """Set the tone settings for a given zone."""
        ## Check the zone supports tone settings and that inputs are within range
        zone = self._check_zone(zone)
        if self.properties.tone.get(zone.value) is None:
            raise RuntimeError(f"tone controls are not available for zone {zone}")
        if not -6 <= treble <= 6:
            raise ValueError(f"invalid treble value: {treble}")
        if not -6 <= bass <= 6:
            raise ValueError(f"invalid bass value: {bass}")

        if tone is not None:
            await self.send_command(
                "set_tone_mode",
                zone,
                prefix=self._get_parameter_key_from_value(tone, TONE_MODES),
            )
        ## Set treble and bass only if zone tone status is set to "On"
        if self.properties.tone.get(zone.value, {}).get("status") == "On":
            treble_str = f"{str(treble)}dB"
            bass_str = f"{str(bass)}dB"
            if treble is not None:
                await self.send_command(
                    "set_tone_treble",
                    zone,
                    prefix=self._get_parameter_key_from_value(
                        treble_str, TONE_DB_VALUES
                    ),
                )
            if bass is not None:
                await self.send_command(
                    "set_tone_bass",
                    zone,
                    prefix=self._get_parameter_key_from_value(bass_str, TONE_DB_VALUES),
                )

    async def set_amp_settings(
        self,
        speaker_config: str = None,
        hdmi_out: str = None,
        hdmi_audio_output: bool = None,
        pqls: bool = None,
        amp: str = None,
        zone: Zones = Zones.Z1,
    ) -> None:
        """Set amplifier function settings for a given zone."""
        zone = self._check_zone(zone)

        # FUNC: SPEAKERS (use PARAM_SPEAKER_MODES)
        if (
            self.properties.amp.get("speakers") is not None
            and speaker_config is not None
        ):
            await self.send_command(
                "set_amp_speaker_status",
                zone,
                prefix=self._get_parameter_key_from_value(
                    speaker_config, SPEAKER_MODES
                ),
            )

        # FUNC: HDMI OUTPUT SELECT (use PARAM_HDMI_OUT_MODES)
        if self.properties.amp.get("hdmi_out") is not None and hdmi_out is not None:
            await self.send_command(
                "set_amp_hdmi_out_status",
                zone,
                prefix=self._get_parameter_key_from_value(hdmi_out, HDMI_OUT_MODES),
            )

        # FUNC: HDMI AUDIO (simple bool, True is on, otherwise audio only goes to amp)
        if (
            self.properties.amp.get("hdmi_audio") is not None
            and hdmi_audio_output is not None
        ):
            await self.send_command(
                "set_amp_hdmi_audio_status",
                zone,
                prefix=str(int(hdmi_audio_output)),
            )

        # FUNC: PQLS (simple bool, True is auto, False is off)
        if self.properties.amp.get("pqls") is not None and pqls is not None:
            await self.send_command("set_amp_pqls_status", zone, prefix=str(int(pqls)))

        # FUNC: AMP (use PARAM_AMP_MODES)
        if self.properties.amp.get("status") is not None and amp is not None:
            await self.send_command(
                "set_amp_status",
                zone,
                prefix=self._get_parameter_key_from_value(amp, AMP_MODES),
            )

    async def select_tuner_band(self, band: TunerBand = TunerBand.FM) -> None:
        """Set the tuner band."""
        if not isinstance(band, TunerBand):
            raise ValueError(f"invalid TunerBand specified: {band}")
        if (
            self.properties.tuner.get("band") is None
            or SOURCE_TUNER not in self.properties.source.values()
        ):
            raise RuntimeError("tuner is unavailable")

        ## Set the tuner band
        if band == self.properties.tuner.get("band"):
            return
        tuner_commands = {
            TunerBand.AM: "set_tuner_band_am",
            TunerBand.FM: "set_tuner_band_fm",
        }
        await self.send_command(tuner_commands[band])

    async def _calculate_am_frequency_step(self) -> None:
        """
        Automatically calculate the AM frequency step by stepping the frequency
        up and then down.
        """
        if self.params.get_param(PARAM_DEBUG_COMMAND_QUEUE):
            _LOGGER.debug(">> PioneerAVR._calculate_am_frequency_step() ")

        if self.params.get_param(PARAM_TUNER_AM_FREQ_STEP):
            return

        ## Check that tuner is active and band is set to AM
        if not (
            SOURCE_TUNER in self.properties.source.values()
            and self.properties.tuner.get("band") == "AM"
        ):
            raise RuntimeError(
                "cannot calculate AM frequency step: tuner is unavailable"
            )

        ## Try sending the query_tuner_am_step command first.
        await self.send_command(command="query_tuner_am_step", ignore_error=True)
        if self.params.get_param(PARAM_TUNER_AM_FREQ_STEP):
            return

        ## Step frequency once and calculate difference
        current_freq = self.properties.tuner.get("frequency")
        new_freq = current_freq
        count = 3
        while new_freq == current_freq and count > 0:
            await self.send_command("increase_tuner_frequency", ignore_error=True)
            new_freq = self.properties.tuner.get("frequency")
            count -= 1
        if new_freq == current_freq and count == 0:
            _LOGGER.error(
                "cannot calculate tuner AM frequency step: unable to step frequency"
            )
            return

        self.params.set_system_param(PARAM_TUNER_AM_FREQ_STEP, new_freq - current_freq)
        await self.send_command("decrease_tuner_frequency", ignore_error=True)

    async def _step_tuner_frequency(self, band: str, frequency: float) -> None:
        """Step the tuner frequency until requested frequency is reached."""
        zone = Zones.Z1
        current_freq = self.properties.tuner.get("frequency")
        if band == "AM":
            if (freq_step := self.params.get_param(PARAM_TUNER_AM_FREQ_STEP)) is None:
                raise ValueError(
                    "unknown AM tuner frequency step, param 'am_frequency_step' required"
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
        rc = True
        count = 100  ## Stop stepping after maximum steps
        if target_freq > current_freq:
            while current_freq < target_freq and count > 0 and rc:
                rc = await self.send_command(
                    "increase_tuner_frequency", zone, ignore_error=False
                )
                if rc is None:  ## ignore timeouts
                    rc = True
                current_freq = self.properties.tuner.get("frequency")
                count -= 1
        elif target_freq < current_freq:
            while current_freq > target_freq and count > 0 and rc:
                rc = await self.send_command(
                    "decrease_tuner_frequency", zone, ignore_error=False
                )
                if rc is None:  ## ignore timeouts
                    rc = True
                current_freq = self.properties.tuner.get("frequency")
                count -= 1

        if count == 0:
            raise RuntimeError("maximum frequency step count exceeded")

    async def set_tuner_frequency(self, band: TunerBand, frequency: float) -> None:
        """Set the tuner frequency and band."""
        if not isinstance(frequency, float):
            raise ValueError(f"invalid frequency {frequency}")
        elif (band == TunerBand.AM and not 530 <= frequency <= 1700) or (
            band == TunerBand.FM and not 87.5 <= frequency <= 108.0
        ):
            raise ValueError(f"frequency {frequency} out of range for band {band}")

        await self.select_tuner_band(band)
        await self._command_queue_wait()  ## wait for AM step to be calculated

        if await self.send_command("operation_direct_access", ignore_error=True):
            ## Set tuner frequency directly if command is supported
            freq_str = str(int(frequency * (100 if band == TunerBand.FM else 1)))
            for digit in freq_str:
                if not await self.send_command(
                    "operation_tuner_digit", prefix=digit, ignore_error=False
                ):
                    raise RuntimeError(f"AVR rejected frequency set to {frequency}")
        else:
            await self._step_tuner_frequency(band, frequency)

    async def select_tuner_preset(self, tuner_class: str, preset: int) -> None:
        """Select the tuner preset."""
        await self.send_command(
            "select_tuner_preset",
            prefix=str(tuner_class).upper() + str(preset).upper().zfill(2),
        )

    async def tuner_previous_preset(self) -> None:
        """Select the previous tuner preset."""
        await self.send_command("decrease_tuner_preset")

    async def tuner_next_preset(self) -> None:
        """Select the next tuner preset."""
        await self.send_command("increase_tuner_preset")

    async def set_channel_levels(
        self, channel: str, level: float, zone: Zones = Zones.Z1
    ) -> None:
        """Set the level (gain) for amplifier channel in zone."""
        zone = self._check_zone(zone)
        if self.properties.channel_levels.get(zone.value) is None:
            raise ValueError(f"channel levels not supported for zone {zone}")

        ## Check the channel exists
        if self.properties.channel_levels[zone.value].get(channel.upper()) is None:
            raise ValueError(f"invalid channel {channel} for zone {zone}")

        prefix = channel.ljust(3, "_") + str(int((level * 2) + 50))
        await self.send_command("set_channel_levels", zone, prefix=prefix)

    async def set_video_settings(self, **arguments) -> None:
        """Set video settings for a given zone."""
        zone = self._check_zone(arguments.get("zone"))

        # This function is only valid for zone 1, no video settings are
        # available for zone 2, 3, 4 and HDZone
        if zone is not Zones.Z1:
            raise ValueError(f"video settings not supporte for zone {zone}")

        # This is a complex function and supports handles requests to update any
        # video related parameters
        ## TODO: refactor to use match and possibly subfunctions
        for arg in arguments:
            if arg != "zone":
                if arguments.get(arg) is not None:
                    if self.properties.video.get(arg) is not arguments.get(arg):
                        if isinstance(arguments.get(arg), str):
                            # Functions to do a lookup here
                            if arg == "resolution":
                                arguments[arg] = self._get_parameter_key_from_value(
                                    arguments.get(arg), VIDEO_RESOLUTION_MODES
                                )
                                if arguments[arg] not in self.params.get_param(
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
                            prefix=str(arguments.get(arg)),
                            ignore_error=False,
                        )

    async def set_dsp_settings(self, **arguments) -> None:
        """Set the DSP settings for the amplifier."""
        zone = self._check_zone(arguments.get("zone"))
        if zone is not Zones.Z1:
            raise ValueError(f"DSP settings not supported for zone {zone}")

        ## TODO: refactor to use match and possibly subfunctions
        for arg in arguments:
            if arg != "zone":
                if arguments.get(arg) is not None:
                    if self.properties.dsp.get(arg) is not arguments.get(arg):
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
                            prefix=str(arguments.get(arg)),
                            ignore_error=False,
                        )

    async def media_control(self, action: str, zone: Zones = Zones.Z1) -> None:
        """
        Perform media control activities such as play, pause, stop, fast forward
        or rewind.
        """
        zone = self._check_zone(zone)
        media_commands = self.properties.media_control_mode.get(zone)
        if media_commands is not None:
            command = MEDIA_CONTROL_COMMANDS.get(media_commands, {}).get(action)
            if command is not None:
                # These commands are ALWAYS sent to zone 1 because each zone
                # does not have unique commands
                await self.send_command(command, Zones.Z1, ignore_error=False)
            else:
                raise NotImplementedError(
                    f"Current source ({self.properties.source.get(zone.value)} does not support "
                    "action {action}"
                )
        else:
            raise NotImplementedError(
                f"Current source ({self.properties.source.get(zone.value)}) does not support "
                "media_control activities"
            )

    async def set_source_name(
        self, source_id: str, source_name: str = "", default: bool = False
    ) -> None:
        """Renames a given input, set the default parameter to true to reset to default."""
        if default:
            await self.send_command(
                "set_default_source_name", Zones.Z1, suffix=source_id
            )
            return

        if len(source_name) > 14:
            raise ValueError(
                f"new source name {source_name} is longer than 14 characters"
            )
        if self.properties.source_id_to_name.get(source_id) == source_name:
            return

        await self.send_command(
            "set_source_name", Zones.Z1, prefix=source_name, suffix=source_id
        )
