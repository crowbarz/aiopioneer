"""Pioneer AVR API (async)."""

# pylint: disable=relative-beyond-top-level disable=too-many-lines

import asyncio
import logging
import time

from collections.abc import Callable
from typing import Any

from .commands import PIONEER_COMMANDS
from .connection import AVRConnection
from .const import (
    Zone,
    TunerBand,
    VERSION,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    MIN_RESCAN_INTERVAL,
    SOURCE_TUNER,
    MEDIA_CONTROL_COMMANDS,
    CHANNELS_ALL,
)
from .exceptions import (
    AVRError,
    AVRUnavailableError,
    AVRResponseTimeoutError,
    AVRCommandError,
    AVRUnknownCommandError,
    AVRUnknownLocalCommandError,
    AVRTunerUnavailableError,
    AVRConnectProtocolError,
    AVRLocalCommandError,
)
from .params import (
    AVRParams,
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
    PARAM_ENABLED_FUNCTIONS,
    PARAM_INITIAL_REFRESH_FUNCTIONS,
    PARAM_DISABLE_AUTO_QUERY,
)
from .decoders.audio import (
    ChannelLevel,
    ListeningMode,
    AvailableListeningMode,
    ToneDb,
    ToneMode,
)
from .decoders.code_map import CodeMapBase
from .decoders.decode import process_raw_response
from .decoders.tuner import FrequencyAM, FrequencyFM, Preset
from .properties import AVRProperties
from .util import cancel_task

_LOGGER = logging.getLogger(__name__)


class PioneerAVR(AVRConnection):
    """Pioneer AVR interface."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
        scan_interval: float = DEFAULT_SCAN_INTERVAL,
        params: dict[str, str] = None,
    ):
        """Initialise the Pioneer AVR interface."""
        _LOGGER.info("Starting aiopioneer %s", VERSION)
        self.params = AVRParams(params)
        self.properties = AVRProperties(self.params)
        super().__init__(
            params=self.params,
            host=host,
            port=port,
            timeout=timeout,
            scan_interval=scan_interval,
        )

        ## Internal state
        self._update_lock = asyncio.Lock()
        self._updater_task = None
        self._command_queue_task = None
        self._command_queue_excs: list[Exception] = []
        self._command_queue: list = []  # queue of commands to execute
        self._zone_callback = {}

        # Register params update callbacks
        self.params.register_update_callback(self.update_listening_modes)

    ## Connection/disconnection
    async def on_connect(self) -> None:
        """Start AVR tasks on connection."""
        await super().on_connect()
        if await self.query_device_model() is None:
            raise AVRConnectProtocolError
        self.update_listening_modes()
        await self._updater_schedule()
        await asyncio.sleep(0)  # yield to updater task

    async def on_reconnect(self) -> None:
        """Update AVR on reconnection."""
        await super().on_reconnect()
        await self.update(wait=False)

    async def on_disconnect(self) -> None:
        """Stop AVR tasks on disconnection."""
        self.properties.reset()
        self._call_zone_callbacks()
        await self._command_queue_cancel(ignore_exception=True)
        await self._updater_cancel(ignore_exception=True)
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
        ignored_zones = [Zone(z) for z in self.params.get_param(PARAM_IGNORED_ZONES)]
        ignore_volume_check = self.params.get_param(PARAM_IGNORE_VOLUME_CHECK)
        # Defer updates to after query_zones has completed

        async def query_zone(zone: Zone, max_volume: int) -> bool | None:
            if await self.send_command("query_power", zone, ignore_error=True) and (
                ignore_volume_check
                or await self.send_command("query_volume", zone, ignore_error=True)
            ):
                if zone not in ignored_zones:
                    _LOGGER.info("%s discovered", zone.full_name)
                    if zone not in self.properties.zones:
                        self.properties.zones.add(zone)
                        self.properties.max_volume[zone.value] = max_volume
                    return True
                return False
            return None

        async with self._update_lock:
            if not await query_zone(Zone.Z1, self.params.get_param(PARAM_MAX_VOLUME)):
                _LOGGER.warning("%s not discovered on AVR", Zone.Z1.full_name)
            for zone in [Zone.Z2, Zone.Z3, Zone.HDZ]:
                await query_zone(zone, self.params.get_param(PARAM_MAX_VOLUME_ZONEX))

    async def build_source_dict(self) -> None:
        """Generate source id<->name translation tables."""
        timeouts = 0
        self.properties.query_sources = True
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

    async def query_device_model(self) -> bool | None:
        """Query device model from Pioneer AVR."""
        if (device_model := self.properties.amp.get("model")) is not None:
            return device_model
        _LOGGER.info("querying device model")
        if res := await self.send_command("query_model", ignore_error=True):
            ## Update default params for this model
            self.params.set_default_params_model(self.properties.amp.get("model"))
            return True
        elif res is False:
            _LOGGER.warning("AVR device model unavailable, no model parameters set")
        return res

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
        self, zone: Zone, callback: Callable[..., None] | None = None
    ) -> None:
        """Register a callback for a zone."""
        if zone in self.properties.zones or zone is Zone.ALL:
            if callback:
                self._zone_callback[zone] = callback
            else:
                self._zone_callback.pop(zone)

    def clear_zone_callbacks(self) -> None:
        """Clear callbacks for all zones."""
        self._zone_callback = {}

    def _call_zone_callbacks(self, zones: set[Zone] = None) -> None:
        """Call callbacks to signal updated zone(s)."""
        if zones is None:
            zones = self.properties.zones.copy()
            zones.add(Zone.ALL)
        for zone in zones:
            if zone in self._zone_callback:
                callback = self._zone_callback[zone]
                if callback:
                    callback()

    ## Response handling callbacks
    def decode_response(self, response_raw: str) -> None:
        """Decode response and commit to properties."""
        updated_zones, command_queue = process_raw_response(
            response_raw, self.params, self.properties
        )
        if command_queue:  ## Add any requested extra commands to run
            for command in command_queue:
                if isinstance(command, list):
                    cmd = command[0]
                    if cmd == "_oob":
                        if not self._update_lock.locked():
                            self.queue_command(command[1:])
                        continue
                self.queue_command(command)
        if updated_zones:  ## Call zone callbacks for updated zones
            self._call_zone_callbacks(updated_zones)

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

    async def _updater_cancel(self, ignore_exception=False) -> None:
        """Cancel the updater task."""
        debug_updater = self.params.get_param(PARAM_DEBUG_UPDATER)
        await cancel_task(
            self._updater_task,
            debug=debug_updater,
            ignore_exception=ignore_exception,
        )
        self._updater_task = None

    async def _refresh_zone(self, zone: Zone) -> None:
        """Perform full refresh an AVR zone."""
        ## Refresh only if zone is powered on
        await self.send_command("query_power", zone)
        if not bool(self.properties.power.get(zone)):
            return

        ## Check for timeouts, but ignore errors (eg. ?V will
        # return E02 immediately after power on)
        for command in ["query_volume", "query_mute", "query_source_id"]:
            if await self.send_command(command, zone, ignore_error=True) is None:
                raise AVRResponseTimeoutError(command=command)

        ## Zone-specific updates, if enabled
        if self.params.get_param(PARAM_DISABLE_AUTO_QUERY):
            return

        ## Loop through PIONEER_COMMANDS to allow us to add query commands
        ## without needing to add it here
        for comm, supported_zones in PIONEER_COMMANDS.items():
            if zone in supported_zones:
                comm_parts = comm.split("_")
                enabled_functions = set(self.params.get_param(PARAM_ENABLED_FUNCTIONS))
                if zone in self.properties.zones_initial_refresh:
                    enabled_functions -= set(
                        self.params.get_param(PARAM_INITIAL_REFRESH_FUNCTIONS)
                    )
                if comm_parts[0] == "query" and comm_parts[1] in enabled_functions:
                    await self.send_command(
                        comm, zone, ignore_error=True, rate_limit=False
                    )
                elif (
                    comm == "set_channel_levels"
                    and "channels" in enabled_functions
                    and self.properties.power.get(Zone.Z1)
                ):
                    ## Channel level updates are handled differently as it
                    ## requires more complex logic to send the commands we use
                    ## the set_channel_levels command and prefix the query to it
                    for channel in CHANNELS_ALL:
                        await self.send_command(
                            comm,
                            zone,
                            prefix="?" + channel.ljust(3, "_"),
                            ignore_error=True,
                            rate_limit=False,
                        )

    async def _refresh_zones(self, zones: set[Zone]) -> None:
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
        for zone in zones:
            await self._refresh_zone(zone)
            zones_initial_refresh = self.properties.zones_initial_refresh
            if self.properties.power[zone] and zone not in zones_initial_refresh:
                if zone is Zone.Z1:
                    await self.query_device_info()
                _LOGGER.info("completed initial refresh for %s", zone.full_name)
                self.properties.zones_initial_refresh.add(zone)
                self._call_zone_callbacks(zones=set([zone]))

        ## Trigger callbacks to all zones on refresh
        self._call_zone_callbacks(zones=set([Zone.ALL]))

        _LOGGER.debug(">> refresh completed")

    async def update(self, zones: list[Zone] = None, wait: bool = True) -> None:
        """Update AVR cached status."""
        if not zones or Zone.ALL in zones:
            self.queue_command("_full_refresh")
        else:
            for zone in zones:
                self.queue_command(["_refresh_zone", zone])
        if wait:
            await self._command_queue_wait()

    ## Command queue
    async def _execute_local_command(self, command: str, args: list) -> None:
        """Execute local command."""

        def check_args(command: str, args: list, num_args: int) -> None:
            """Check expected number of arguments have been provided."""
            if num_args != len(args):
                args_desc = "argument" if num_args == 1 else "arguments"
                raise ValueError(f"{command} requires {num_args} {args_desc}")

        match command:
            case "_power_on":
                check_args(command, args, 1)
                zone = Zone(args[0])
                if zone not in self.properties.zones_initial_refresh:
                    _LOGGER.info("scheduling initial refresh")
                    self.queue_command(["_sleep", 2], insert_at=1)
                    self.queue_command(["_refresh_zone", zone], insert_at=2)
                else:
                    self.queue_command(["_delayed_query_basic", 4], insert_at=1)
                if zone is Zone.Z1 and self.params.get_param(
                    PARAM_POWER_ON_VOLUME_BOUNCE
                ):
                    ## NOTE: volume workaround scheduled ahead of initial refresh
                    _LOGGER.info("scheduling Zone 1 volume workaround")
                    self.queue_command("volume_up", skip_if_queued=False, insert_at=1)
                    self.queue_command("volume_down", skip_if_queued=False, insert_at=2)
            case "_full_refresh":
                await self._refresh_zones(zones=self.properties.zones)
            case "_refresh_zone":
                check_args(command, args, 1)
                await self._refresh_zones(zones=[Zone(args[0])])
            case "_delayed_query_basic":
                check_args(command, args, 1)
                if not self.params.get_param(PARAM_DISABLE_AUTO_QUERY):
                    self.queue_command(["_sleep", args[0]], insert_at=1)
                    self.queue_command("_query_basic", insert_at=2)
            case "_query_basic":
                if any(self.properties.power.values()) and not self.params.get_param(
                    PARAM_DISABLE_AUTO_QUERY
                ):
                    for cmd in [
                        "query_listening_mode",
                        "query_basic_audio_information",
                        "query_basic_video_information",
                    ]:
                        await self.send_command(cmd, ignore_error=True)
            case "_update_listening_modes":
                self.update_listening_modes()
            case "_calculate_am_frequency_step":
                await self._calculate_am_frequency_step()
            case "_sleep":
                check_args(command, args, 1)
                await asyncio.sleep(args[0])
            case _:
                raise AVRUnknownLocalCommandError(command=command)

    async def _execute_command_queue(self) -> None:
        """Execute commands from a queue."""
        _LOGGER.debug(">> command queue started")
        async with self._update_lock:
            while len(self._command_queue) > 0:
                ## Keep command in queue until it has finished executing
                command: str | list = self._command_queue[0]
                _LOGGER.debug("command queue executing %s", command)
                try:
                    args = []
                    if isinstance(command, list):
                        args = command[1:]
                        command = command[0]
                    elif not isinstance(command, str):
                        raise AVRUnknownLocalCommandError(command=command)
                    if command.startswith("_"):
                        await self._execute_local_command(command, args)
                    else:
                        await self.send_command(command, ignore_error=False)
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
                    self._command_queue_excs.append(exc)

                self._command_queue.pop(0)

        _LOGGER.debug(">> command queue completed")

    async def _command_queue_wait(self) -> None:
        """Wait for command queue to be flushed."""
        await asyncio.sleep(0)  # yield to command queue task
        debug_command_queue = self.params.get_param(PARAM_DEBUG_COMMAND_QUEUE)
        if self._command_queue_task is None:
            return

        if debug_command_queue:
            _LOGGER.debug("waiting for command queue to be flushed")
        await asyncio.wait([self._command_queue_task])
        if self._command_queue_task is None:
            raise AVRUnavailableError
        if exc := self._command_queue_task.exception():
            _LOGGER.error("command queue task exception: %s", repr(exc))
            return

        self._command_queue_task = None
        if excs := self._command_queue_excs:
            if debug_command_queue:
                _LOGGER.debug("command queue exceptions: %s", repr(excs))
            if len(excs) == 1:
                raise excs[0]
            raise ExceptionGroup("command queue exceptions", excs)

    async def _command_queue_cancel(self, ignore_exception: bool = False) -> None:
        """Cancel any pending commands and the task itself."""
        debug_command_queue = self.params.get_param(PARAM_DEBUG_COMMAND_QUEUE)
        await cancel_task(
            self._command_queue_task,
            debug=debug_command_queue,
            ignore_exception=ignore_exception,
        )
        self._command_queue_task = None
        self._command_queue = []

    def _command_queue_schedule(self) -> None:
        """Schedule commands to queue."""
        if len(self._command_queue) == 0:
            return

        ## NOTE: does not create new task if one already exists
        if self._command_queue_task:
            if self._command_queue_task.done():
                if exc := self._command_queue_task.exception():
                    _LOGGER.error("command queue task exception: %s", repr(exc))
                self._command_queue_task = None
        if self._command_queue_task is None:
            if self.params.get_param(PARAM_DEBUG_COMMAND_QUEUE):
                _LOGGER.debug("creating command queue task")
            self._command_queue_task = asyncio.create_task(
                self._execute_command_queue(), name="avr_command_queue"
            )
            self._command_queue_excs = []

    def queue_command(
        self, command: str | list, skip_if_queued: bool = True, insert_at: int = -1
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
        self._command_queue_schedule()

    ## AVR methods
    def _check_zone(self, zone: Zone) -> Zone:
        """Check that specified zone is valid."""
        if not isinstance(zone, Zone):
            raise ValueError(f"{zone} is not a zone identifier")
        if zone not in self.properties.zones:
            raise ValueError(f"{zone.full_name} does not exist on AVR")
        return zone

    async def turn_on(self, zone: Zone = Zone.Z1) -> None:
        """Turn on the Pioneer AVR zone."""
        zone = self._check_zone(zone)
        await self.send_command("turn_on", zone)

    async def turn_off(self, zone: Zone = Zone.Z1) -> None:
        """Turn off the Pioneer AVR zone."""
        zone = self._check_zone(zone)
        await self.send_command("turn_off", zone)

    async def select_source(
        self, source: str = None, source_id: str = None, zone: Zone = Zone.Z1
    ) -> None:
        """Select input source."""
        zone = self._check_zone(zone)
        if source_id is None:
            source_id = self.properties.source_name_to_id.get(source)
        if source_id is None:
            raise ValueError(f"invalid source {source} for {zone.full_name}")

        await self.send_command("select_source", zone, prefix=source_id)

    async def volume_up(self, zone: Zone = Zone.Z1) -> None:
        """Volume up media player."""
        zone = self._check_zone(zone)
        await self.send_command("volume_up", zone)

    async def volume_down(self, zone: Zone = Zone.Z1) -> None:
        """Volume down media player."""
        zone = self._check_zone(zone)
        await self.send_command("volume_down", zone)

    async def set_volume_level(self, target_volume: int, zone: Zone = Zone.Z1) -> None:
        """Set volume level (0..185 for Zone 1, 0..81 for other Zones)."""
        zone = self._check_zone(zone)
        current_volume = self.properties.volume.get(zone.value)
        max_volume = self.properties.max_volume[zone.value]
        if target_volume < 0 or target_volume > max_volume:
            raise ValueError(
                f"volume {target_volume} out of range for {zone.full_name}"
            )
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
                        raise AVRCommandError(
                            command="set_volume_level",
                            err="AVR volume_up failed",
                            zone=zone,
                        )
                    if volume_step_count > (target_volume - start_volume):
                        raise AVRCommandError(
                            command="set_volume_level",
                            err="Exceeded max volume steps",
                            zone=zone,
                        )
                    current_volume = new_volume
            elif target_volume < start_volume:  # step down
                while current_volume > target_volume:
                    _LOGGER.debug("current volume: %d", current_volume)
                    await self.volume_down(zone)
                    volume_step_count += 1
                    new_volume = self.properties.volume.get(zone.value)
                    if new_volume >= current_volume:  # going wrong way
                        raise AVRCommandError(
                            command="set_volume_level",
                            err="AVR volume_down failed",
                            zone=zone,
                        )
                    if volume_step_count > (start_volume - target_volume):
                        raise AVRCommandError(
                            command="set_volume_level",
                            err="Exceeded max volume steps",
                            zone=zone,
                        )
                    current_volume = self.properties.volume.get(zone.value)
        else:
            vol_len = 3 if Zone(zone) is Zone.Z1 else 2
            vol_prefix = str(target_volume).zfill(vol_len)
            await self.send_command("set_volume_level", zone, prefix=vol_prefix)

    async def mute_on(self, zone: Zone = Zone.Z1) -> None:
        """Mute AVR."""
        zone = self._check_zone(zone)
        await self.send_command("mute_on", zone)

    async def mute_off(self, zone: Zone = Zone.Z1) -> None:
        """Unmute AVR."""
        zone = self._check_zone(zone)
        await self.send_command("mute_off", zone)

    def update_listening_modes(self) -> None:
        """Update list of valid listening modes for current input source."""
        self.properties.update_listening_modes()
        ListeningMode.code_map = self.properties.listening_modes_all
        AvailableListeningMode.code_map = self.properties.available_listening_modes

    def get_listening_modes(self) -> dict[str, str] | None:
        """Return dict of valid listening modes and names for Zone 1."""
        return AvailableListeningMode.values()

    async def select_listening_mode(
        self, mode_name: str = None, mode_id: str = None
    ) -> None:
        """Set the listening mode using the predefined list of options in params."""

        if mode_name and mode_id is None:
            mode_id = AvailableListeningMode(mode_name)
        if mode_id not in self.properties.available_listening_modes:
            raise ValueError(f"listening mode {mode_id} is not available")
        await self.send_command("set_listening_mode", prefix=mode_id)

    async def set_tone_settings(
        self,
        tone: str = None,
        treble: int = None,
        bass: int = None,
        zone: Zone = Zone.Z1,
    ) -> None:
        """Set the tone settings for a given zone."""
        ## Check the zone supports tone settings and that inputs are within range
        zone = self._check_zone(zone)
        if self.properties.tone.get(zone) is None:
            raise AVRLocalCommandError(
                command="set_tone_settings", err_key="tone_unavailable", zone=zone
            )

        if tone is not None:
            await self.send_command("set_tone_mode", zone=zone, prefix=ToneMode(tone))

        ## Set treble and bass only if zone tone status is set to "On"
        if self.properties.tone[zone].get("status") == "on":
            if treble is not None:
                await self.send_command(
                    "set_tone_treble", zone=zone, prefix=ToneDb(treble)
                )
            if bass is not None:
                await self.send_command("set_tone_bass", zone=zone, prefix=ToneDb(bass))

    async def set_amp_settings(self, **kwargs) -> None:
        """Set amplifier settings."""
        zone = Zone.Z1

        async def set_amp_setting(
            command: str, arg: str, value: Any, arg_code_map: CodeMapBase
        ) -> None:
            if arg in (
                ["speaker_mode", "hdmi_out", "hdmi3_out", "hdmi_audio", "pqls", "mode"]
            ):
                if self.properties.amp.get(arg) is None:
                    raise AVRLocalCommandError(
                        command=command, err_key=f"{arg}_unavailable"
                    )
            await self.send_command(command, zone, prefix=arg_code_map(value))

        for arg, value in kwargs.items():
            if self.properties.amp.get(arg) == value:
                continue
            if (command := "set_amp_" + arg) not in PIONEER_COMMANDS:
                raise AVRUnknownCommandError(command=command, zone=zone)
            arg_format = PIONEER_COMMANDS[command].get("args")
            if not isinstance(arg_format, list):
                raise RuntimeError(f"No arguments defined for amp setting {arg}")
            if not issubclass(arg_code_map := arg_format[0], CodeMapBase):
                raise RuntimeError(
                    f"Invalid code map {arg_code_map} for amp setting {arg}"
                )
            try:
                await set_amp_setting(command, arg, value, arg_code_map)
            except AVRError:
                raise
            except Exception as exc:  # pylint: disable=broad-except
                raise AVRLocalCommandError(command=command, exc=exc) from exc

    async def select_tuner_band(self, band: TunerBand = TunerBand.FM) -> None:
        """Set the tuner band."""
        if not isinstance(band, TunerBand):
            raise ValueError(f"invalid TunerBand specified: {band}")
        if (
            self.properties.tuner.get("band") is None
            or SOURCE_TUNER not in self.properties.source_id.values()
        ):
            raise AVRTunerUnavailableError(command="select_tuner_band")

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

        ## Skip if step was provided in params or has already been calculated
        if self.properties.tuner.get("am_frequency_step"):
            return

        ## Try sending the query_tuner_am_step command first
        if await self.send_command(command="query_tuner_am_step", ignore_error=True):
            return

        ## Step frequency once and check whether difference was calculated
        if await self.send_command("increase_tuner_frequency", ignore_error=True):
            await self.send_command("decrease_tuner_frequency")
            if self.properties.tuner.get("am_frequency_step"):
                return

        raise AVRLocalCommandError(
            command="calculate_am_frequency_step", err_key="freq_step_error"
        )

    async def _step_tuner_frequency(self, band: str, frequency: float) -> None:
        """Step the tuner frequency until requested frequency is reached."""
        zone = Zone.Z1
        current_freq = self.properties.tuner.get("frequency")
        if band == "AM":
            if not (
                am_frequency_step := self.properties.tuner.get("am_frequency_step")
            ):
                raise AVRLocalCommandError(
                    command="step_tuner_frequency", err_key="freq_step_unknown"
                )
            target_freq = frequency // am_frequency_step * am_frequency_step
            count = abs(frequency - current_freq) // am_frequency_step + 1
        else:
            target_freq = frequency * 1000 // 50 * 50 / 1000
            count = abs(int(frequency * 1000) - int(current_freq * 1000)) // 50 + 1

        ## Continue adjusting until frequency is set
        rc = True
        if target_freq > current_freq:
            while current_freq < target_freq and count > 0 and rc:
                rc = await self.send_command(
                    "increase_tuner_frequency",
                    zone,
                    ignore_error=False,
                    rate_limit=False,
                )
                if rc is None:  ## ignore timeouts
                    rc = True
                current_freq = self.properties.tuner.get("frequency")
                count -= 1
        elif target_freq < current_freq:
            while current_freq > target_freq and count > 0 and rc:
                rc = await self.send_command(
                    "decrease_tuner_frequency",
                    zone,
                    ignore_error=False,
                    rate_limit=False,
                )
                if rc is None:  ## ignore timeouts
                    rc = True
                current_freq = self.properties.tuner.get("frequency")
                count -= 1

        if count == 0:
            raise AVRLocalCommandError(
                command="step_tuner_frequency", err_key="freq_step_max_exceeded"
            )

    async def set_tuner_frequency(
        self, band: TunerBand, frequency: float | int
    ) -> None:
        """Set the tuner frequency and band."""
        await self.select_tuner_band(band)
        if band is TunerBand.AM and not self.properties.tuner.get("am_frequency_step"):
            await self._command_queue_wait()  ## wait for AM step to be calculated

        code = (
            FrequencyAM(frequency) if band is TunerBand.AM else FrequencyFM(frequency)
        )

        if await self.send_command("operation_direct_access", ignore_error=True):
            ## Set tuner frequency directly if command is supported
            try:
                for digit in code:
                    await self.send_command(
                        "operation_tuner_digit", prefix=digit, rate_limit=False
                    )
            except AVRCommandError as exc:
                raise AVRLocalCommandError(
                    command="set_tuner_frequency", err_key="freq_set_failed", exc=exc
                ) from exc
        else:
            await self._step_tuner_frequency(band=band, frequency=frequency)

    async def select_tuner_preset(self, tuner_class: str, tuner_preset: int) -> None:
        """Select the tuner preset."""
        await self.send_command(
            "select_tuner_preset", prefix=Preset((tuner_class, tuner_preset))
        )

    async def tuner_previous_preset(self) -> None:
        """Select the previous tuner preset."""
        await self.send_command("decrease_tuner_preset")

    async def tuner_next_preset(self) -> None:
        """Select the next tuner preset."""
        await self.send_command("increase_tuner_preset")

    async def set_channel_levels(
        self, channel: str, level: float, zone: Zone = Zone.Z1
    ) -> None:
        """Set the level (gain) for amplifier channel in zone."""
        zone = self._check_zone(zone)
        if channel_levels := self.properties.channel_levels.get(zone) is None:
            raise AVRLocalCommandError(
                command="set_channel_levels",
                err_key="channel_levels_unavailable",
                zone=zone,
            )
        if channel_levels.get(channel) is None:
            raise AVRLocalCommandError(
                command="set_channel_levels",
                err_key="channel_unavailable",
                zone=zone,
                channel=channel,
            )
        prefix = channel.ljust(3, "_") + ChannelLevel(level)
        await self.send_command("set_channel_levels", zone=zone, prefix=prefix)

    async def set_video_settings(self, zone: Zone, **arguments) -> None:
        """Set video settings for a given zone."""
        zone = self._check_zone(zone)

        # This function is only valid for zone 1, no video settings are
        # available for zone 2, 3, 4 and HDZone
        if zone is not Zone.Z1:
            raise AVRLocalCommandError(
                command="set_video_settings",
                err_key="video_settings_unavailable",
                zone=zone,
            )

        async def set_video_setting(
            command: str, arg: str, value: Any, arg_code_map: CodeMapBase
        ) -> None:
            code = arg_code_map(value)
            if arg == "resolution":
                resolution_modes = self.params.get_param(PARAM_VIDEO_RESOLUTION_MODES)
                if not resolution_modes or code not in resolution_modes:
                    raise AVRLocalCommandError(
                        command=command,
                        err_key="resolution_unavailable",
                        resolution=value,
                    )
            await self.send_command(command, zone, prefix=code)

        for arg, value in arguments.items():
            if self.properties.video.get(arg) == value:
                continue
            if (command := "set_video_" + arg) not in PIONEER_COMMANDS:
                raise AVRUnknownCommandError(command=command, zone=zone)
            arg_format = PIONEER_COMMANDS[command].get("args")
            if not isinstance(arg_format, list):
                raise RuntimeError(f"No arguments defined for command {command}")
            if not issubclass(arg_code_map := arg_format[0], CodeMapBase):
                raise RuntimeError(
                    f"Invalid code map {arg_code_map} for command {command}"
                )
            try:
                await set_video_setting(command, arg, value, arg_code_map)
            except AVRError:
                raise
            except Exception as exc:  # pylint: disable=broad-except
                raise AVRLocalCommandError(command=command, exc=exc) from exc

    async def set_dsp_settings(self, zone: Zone, **arguments) -> None:
        """Set the DSP settings for the amplifier."""
        zone = self._check_zone(zone)
        if zone is not Zone.Z1:
            raise AVRLocalCommandError(
                command="set_dsp_settings",
                err_key="dsp_settings_unavailable",
                zone=zone,
            )

        async def set_dsp_setting(
            command: str, _arg: str, value: Any, arg_code_map: CodeMapBase
        ) -> None:
            await self.send_command(command, zone, prefix=arg_code_map(value))

        for arg, value in arguments.items():
            if self.properties.dsp.get(arg) == value:
                continue
            if (command := "set_dsp_" + arg) not in PIONEER_COMMANDS:
                raise AVRUnknownCommandError(command=command, zone=zone)
            arg_format = PIONEER_COMMANDS[command].get("args")
            if not isinstance(arg_format, list):
                raise RuntimeError(f"No arguments defined for DSP setting {arg}")
            if not issubclass(arg_code_map := arg_format[0], CodeMapBase):
                raise RuntimeError(
                    f"Invalid code map {arg_code_map} for DSP setting {arg}"
                )
            try:
                await set_dsp_setting(command, arg, value, arg_code_map)
            except AVRError:
                raise
            except Exception as exc:  # pylint: disable=broad-except
                raise AVRLocalCommandError(command=command, exc=exc) from exc

    async def media_control(self, action: str, zone: Zone = Zone.Z1) -> None:
        """
        Perform media control activities such as play, pause, stop, fast forward
        or rewind.
        """
        zone = self._check_zone(zone)
        control_mode = self.properties.media_control_mode.get(zone)
        if control_mode is None:
            raise AVRLocalCommandError(
                command="media_control",
                err_key="media_controls_not_supported",
                source=self.properties.source_name.get(zone.value),
            )

        command = MEDIA_CONTROL_COMMANDS.get(control_mode, {}).get(action)
        if command is None:
            raise AVRLocalCommandError(
                command="media_control",
                err_key="media_action_not_supported",
                source=self.properties.source_name.get(zone.value),
                action=action,
            )

        # These commands are ALWAYS sent to zone 1 because each zone
        # does not have unique commands
        await self.send_command(command, Zone.Z1)

    async def set_source_name(
        self, source_id: str, source_name: str = "", default: bool = False
    ) -> None:
        """Renames a given input, set the default parameter to true to reset to default."""
        if default:
            await self.send_command(
                "set_default_source_name", Zone.Z1, suffix=source_id
            )
            return

        if len(source_name) > 14:
            raise ValueError(
                f"new source name {source_name} is longer than 14 characters"
            )
        if self.properties.source_id_to_name.get(source_id) == source_name:
            return

        await self.send_command(
            "set_source_name", Zone.Z1, prefix=source_name, suffix=source_id
        )
