"""Pioneer AVR API (async)."""

# pylint: disable=relative-beyond-top-level disable=too-many-lines

import asyncio
import logging
import time
import traceback

from collections.abc import Callable

from .command_queue import CommandItem
from .connection import AVRConnection
from .const import (
    Zone,
    TunerBand,
    VERSION,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    MIN_RESCAN_INTERVAL,
    MEDIA_CONTROL_COMMANDS,
    CHANNELS_ALL,
)
from .decode import process_raw_response
from .decoders.amp import Volume
from .decoders.tuner import FrequencyAM, FrequencyFM
from .exceptions import (
    AVRError,
    AVRResponseTimeoutError,
    AVRCommandError,
    AVRUnknownLocalCommandError,
    AVRTunerUnavailableError,
    AVRConnectProtocolError,
    AVRLocalCommandError,
    AVRCommandUnavailableError,
    AVRUnavailableError,
)
from .params import (
    AVRParams,
    PARAM_IGNORED_ZONES,
    PARAM_MAX_SOURCE_ID,
    PARAM_MAX_VOLUME,
    PARAM_MAX_VOLUME_ZONEX,
    PARAM_VOLUME_STEP_ONLY,
    PARAM_IGNORE_VOLUME_CHECK,
    PARAM_RETRY_COUNT,
    PARAM_DEBUG_UPDATER,
    PARAM_DEBUG_COMMAND,
    PARAM_DEBUG_COMMAND_QUEUE,
    PARAM_ENABLED_FUNCTIONS,
    PARAM_INITIAL_REFRESH_FUNCTIONS,
    PARAM_DISABLE_AUTO_QUERY,
)
from .properties import AVRProperties
from .property_registry import PROPERTY_REGISTRY
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
        self.properties.command_queue.register_execute_callback(self._execute_command)
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
        self._zone_callback: dict[Zone, Callable[[None], None]] = {}

    ## Connection/disconnection
    async def on_connect(self) -> None:
        """Start AVR tasks on connection."""
        await super().on_connect()
        async with self.properties.command_queue.startup_lock:
            if await self.query_device_model() is None:
                raise AVRConnectProtocolError
            self.properties.update_listening_modes()
            await self._updater_schedule()
            await asyncio.sleep(0)  # yield to updater task

    async def on_reconnect(self) -> None:
        """Update AVR on reconnection."""
        await super().on_reconnect()
        await self.refresh(wait=False)

    async def on_disconnect(self) -> None:
        """Stop AVR tasks on disconnection."""
        self.properties.reset()
        self._call_zone_callbacks()
        await self.properties.command_queue.cancel(ignore_exceptions=True)
        await self._updater_cancel(ignore_exception=True)
        await asyncio.sleep(0)  # yield to command queue and updater tasks
        await super().on_disconnect()

    async def set_scan_interval(self, scan_interval: int) -> None:
        """Set scan interval and restart updater."""
        _LOGGER.debug(">> set_scan_interval(%d)", scan_interval)
        if not (isinstance(scan_interval, (int, float)) and scan_interval >= 0):
            raise ValueError(
                f"scan_interval {scan_interval} is not a non-negative number"
            )
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

        async def query_zone(zone: Zone, max_volume: int) -> bool | None:
            if await self.send_command(
                "query_power", zone=zone, ignore_error=True
            ) and (
                ignore_volume_check
                or await self.send_command("query_volume", zone=zone, ignore_error=True)
            ):
                if zone not in ignored_zones:
                    _LOGGER.info("%s discovered", zone.full_name)
                    if zone not in self.properties.zones:
                        self.properties.zones.add(zone)
                        self.properties.max_volume[zone] = max_volume
                    return True
                return False
            return None

        command_queue = self.properties.command_queue
        await command_queue.wait()  ## wait for command queue to complete
        async with command_queue, command_queue.startup_lock:
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

        command_queue = self.properties.command_queue
        await command_queue.wait()  ## wait for command queue to complete
        _LOGGER.info("querying AVR source names")
        async with command_queue, command_queue.startup_lock:
            for src_id in range(self.params.get_param(PARAM_MAX_SOURCE_ID) + 1):
                try:
                    response = await self.send_command(
                        "query_source_name", src_id, rate_limit=False
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

    async def query_device_model(self) -> str | bool:
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
        for command in PROPERTY_REGISTRY.get_commands("system_query_"):
            await self.send_command(command.name, ignore_error=True)

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
        self, zone: Zone, callback: Callable[[None], None] | None = None
    ) -> None:
        """Register a callback for a zone."""
        if zone in self.properties.zones or zone is Zone.ALL:
            if callback is not None:
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
                if callback := self._zone_callback[zone]:
                    callback()

    ## Response handling callbacks
    def decode_response(self, response_raw: str) -> None:
        """Decode response and commit to properties."""
        updated_zones = process_raw_response(response_raw, self.params, self.properties)
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
                    self.properties.command_queue.enqueue(
                        CommandItem("_full_refresh", queue_id=2)
                    )
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
            ignore_exceptions=ignore_exception,
        )
        self._updater_task = None

    async def _refresh_zone(self, zone: Zone) -> None:
        """Refresh an AVR zone."""
        if not self.available:
            _LOGGER.debug("AVR not connected, skipping refresh")
        if zone not in self.properties.zones:
            _LOGGER.debug("zone %s not discovered, skipping refresh", zone.full_name)

        _LOGGER.info("refreshing %s", zone.full_name)

        ## Refresh only if zone is powered on
        await self.send_command("query_power", zone=zone)
        if not bool(self.properties.power.get(zone)):
            return

        ## Check for timeouts, but ignore errors (eg. ?V will
        ## return E02 immediately after power on)
        for command in ["query_volume", "query_mute", "query_source"]:
            if await self.send_command(command, zone=zone, ignore_error=True) is None:
                raise AVRResponseTimeoutError(command=command)

        ## Zone-specific updates, if enabled
        if not self.params.get_param(PARAM_DISABLE_AUTO_QUERY):
            enabled_functions = set(self.params.get_param(PARAM_ENABLED_FUNCTIONS))
            if zone in self.properties.zones_initial_refresh:
                enabled_functions -= set(
                    self.params.get_param(PARAM_INITIAL_REFRESH_FUNCTIONS)
                )

            ## Loop through PIONEER_COMMANDS to allow us to add query commands
            ## without needing to add it here
            for func in enabled_functions:
                for command in PROPERTY_REGISTRY.get_commands(
                    prefix=f"query_{func}", zone=zone
                ):
                    if command.name == "query_channel_levels":
                        for channel in CHANNELS_ALL:
                            await self.send_command(
                                command.name,
                                channel,
                                zone=zone,
                                ignore_error=True,
                                rate_limit=False,
                            )
                    else:
                        await self.send_command(
                            command.name, zone=zone, ignore_error=True, rate_limit=False
                        )

        ## Mark zone as completed initial refresh
        zones_initial_refresh = self.properties.zones_initial_refresh
        if zone not in zones_initial_refresh:
            if zone is Zone.Z1:
                await self.query_device_info()
            _LOGGER.info("completed initial refresh for %s", zone.full_name)
            self.properties.zones_initial_refresh.add(zone)

        self._call_zone_callbacks(zones=set([zone]))
        _LOGGER.debug(">> refresh zone %s completed", zone.full_name)

    async def _refresh_all_zones(self) -> None:
        """Refresh all AVR zones."""
        if not self.properties.zones:
            _LOGGER.debug("zones not discovered yet, skipping refresh")

        now = time.time()
        last_updated_str = "never"
        if self.last_updated:
            last_updated_str = f"{(now - self.last_updated):.3f}s ago"
        _LOGGER.info("refreshing all zones (last updated %s)", last_updated_str)
        self.last_updated = time.time()
        self.properties.zones_initial_refresh = set()

        for zone in Zone:  ## refresh zones in enum order
            if zone in self.properties.zones:
                await self._refresh_zone(zone)

        self._call_zone_callbacks(zones=set([Zone.ALL]))
        _LOGGER.debug(">> full refresh completed")

    async def refresh(
        self, zones: list[Zone] | set[Zone] | Zone = None, wait: bool = True
    ) -> None:
        """Refresh AVR cached properties."""
        if isinstance(zones, Zone):
            zones = {zones}
        if isinstance(zones, list):
            zones = set(zones)
        command_queue = self.properties.command_queue
        if not zones or Zone.ALL in zones:
            command_queue.enqueue(CommandItem("_full_refresh"), queue_id=2)
        else:
            for zone in zones:
                command_queue.enqueue(CommandItem("_refresh_zone", zone), queue_id=2)
        if wait:
            await command_queue.wait()

    ## Command execution
    async def send_command(
        self,
        command: str,
        *command_args,
        zone: Zone = Zone.Z1,
        prefix: str = None,
        suffix: str = None,
        ignore_error: bool | None = None,
        rate_limit: bool = True,
        retry_on_fail: bool = None,
    ) -> str | bool | None:
        """Send a command or request to the device."""
        # pylint: disable=unidiomatic-typecheck disable=logging-not-lazy
        debug_command = self.params.get_param(PARAM_DEBUG_COMMAND)
        if debug_command:
            _LOGGER.debug(
                ">> send_command(%s, %s, zone=%s, prefix=%s, "
                "suffix=%s, ignore_error=%s, rate_limit=%s)",
                repr(command),
                repr(command_args),
                zone,
                repr(prefix),
                repr(suffix),
                repr(ignore_error),
                repr(rate_limit),
            )

        try:
            command_item = PROPERTY_REGISTRY.get_command(command, zone)
            command = command_item.get_avr_command(zone)
            arg_code_maps = command_item.avr_args
            if arg_code_maps and prefix is None and suffix is None:
                ## Convert command_args to prefix and suffix
                prefix_map = arg_code_maps[0]
                prefix_args = list(command_args)
                if len(arg_code_maps) > 1:
                    ## Parse suffix code map (requires prefix code map)
                    prefix_nargs = prefix_map.get_nargs()
                    suffix_map = arg_code_maps[1]
                    suffix_args = prefix_args[prefix_nargs:]
                    del prefix_args[prefix_nargs:]
                    suffix = suffix_map.parse_args(
                        command=command,
                        args=suffix_args,
                        zone=zone,
                        params=self.params,
                        properties=self.properties,
                    )
                ## Parse prefix code map
                prefix = prefix_map.parse_args(
                    command=command,
                    args=prefix_args,
                    zone=zone,
                    params=self.params,
                    properties=self.properties,
                )

            if (response := command_item.get_avr_response(zone)) is None:
                ## Send raw command only
                await self.send_raw_command(
                    command=(prefix or "") + command + (suffix or ""),
                    rate_limit=rate_limit,
                )
                return True

            retry_count = 0
            if retry_on_fail or (retry_on_fail is None and command_item.retry_on_fail):
                retry_count = self.params.get_param(PARAM_RETRY_COUNT)

            ## Send raw command, then wait for response
            response = await self.send_raw_request(
                command=(prefix or "") + command + (suffix or ""),
                response_prefix=command_item.get_avr_response(zone),
                rate_limit=rate_limit,
                retry_count=retry_count,
            )
            if debug_command:
                _LOGGER.debug(
                    "send_command %s received response: %s", command, response
                )
            return response

        except AVRUnavailableError:  ## always raise even if ignoring errors
            raise
        except AVRError as exc:
            if ignore_error is None:
                _LOGGER.debug("send_command raised exception: %s", str(exc))
                raise exc
            if ignore_error:
                _LOGGER.debug(str(exc))
            else:
                _LOGGER.error(str(exc))
            return False if isinstance(exc, AVRCommandError) else None
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.error("send_command exception: %s: %s", command, repr(exc))
            _LOGGER.error(traceback.format_exc())

    async def _execute_local_command(self, command: str, args: list) -> None:
        """Execute local command."""

        def check_args(command: str, args: list, num_args: int) -> None:
            """Check expected number of arguments have been provided."""
            if num_args != len(args):
                args_desc = "argument" if num_args == 1 else "arguments"
                raise ValueError(f"{command} requires {num_args} {args_desc}")

        match command:
            case "_full_refresh":
                await self._refresh_all_zones()
            case "_refresh_zone":
                check_args(command, args, 1)
                await self._refresh_zone(zone=Zone(args[0]))
            case "_delayed_refresh_zone":
                await asyncio.sleep(2.5)  ## TODO: parameterise
                await self._refresh_zone(zone=Zone(args[0]))
            case "_delayed_query_basic":
                check_args(command, args, 1)
                if self.params.get_param(PARAM_DISABLE_AUTO_QUERY):
                    return
                await asyncio.sleep(args[0])  ## TODO: parameterise
                for cmd in [
                    "query_listening_mode",
                    "query_basic_audio_information",
                    "query_basic_video_information",
                ]:
                    await self.send_command(cmd, ignore_error=True)
            case "_update_listening_modes":
                self.properties.update_listening_modes()
            case "_calculate_am_frequency_step":
                await asyncio.sleep(2.5)  ## TODO: parameterise
                await self._calculate_am_frequency_step()
            case "_sleep":
                check_args(command, args, 1)
                await asyncio.sleep(args[0])
            case _:
                raise AVRUnknownLocalCommandError(command=command)

    async def _execute_command(self, command_item: CommandItem) -> None:
        """Execute a command from the command queue."""
        command = command_item.command
        args = command_item.args
        if command.startswith("_"):
            await self._execute_local_command(command=command, args=args)
        else:
            await self.send_command(command=command, *args, ignore_error=False)

    ## AVR methods
    def _check_zone(self, zone: Zone) -> Zone:
        """Check that specified zone is valid."""
        if not isinstance(zone, Zone):
            raise ValueError(f"{zone} is not a zone identifier")
        if zone not in self.properties.zones:
            raise ValueError(f"{zone.full_name} is not available on AVR")
        return zone

    async def power_on(self, zone: Zone = Zone.Z1) -> None:
        """Power on the Pioneer AVR zone."""
        await self.send_command("power_on", zone=self._check_zone(zone))

    async def power_off(self, zone: Zone = Zone.Z1) -> None:
        """Power off the Pioneer AVR zone."""
        await self.send_command("power_off", zone=self._check_zone(zone))

    async def select_source(self, source: str | int, zone: Zone = Zone.Z1) -> None:
        """Select input source."""
        await self.send_command("select_source", source, zone=self._check_zone(zone))

    async def volume_up(self, zone: Zone = Zone.Z1) -> None:
        """Volume up media player."""
        await self.send_command("volume_up", zone=self._check_zone(zone))

    async def volume_down(self, zone: Zone = Zone.Z1) -> None:
        """Volume down media player."""
        await self.send_command("volume_down", zone=self._check_zone(zone))

    async def set_volume_level(self, target_volume: int, zone: Zone = Zone.Z1) -> None:
        """Set volume level (0..185 for Zone 1, 0..81 for other Zones)."""
        zone = self._check_zone(zone)

        if not self.params.get_param(PARAM_VOLUME_STEP_ONLY):
            await self.send_command("set_volume_level", target_volume, zone=zone)
            return

        ## Step volume to reach target volume
        Volume.value_to_code(target_volume, zone=zone, properties=self.properties)
        start_volume = self.properties.volume.get(zone)
        current_volume = start_volume
        volume_step_count = 0
        command = "set_volume_level"
        if target_volume > start_volume:  # step up
            while current_volume < target_volume:
                await self.volume_up(zone)
                volume_step_count += 1
                new_volume = self.properties.volume.get(zone)
                if new_volume <= current_volume:  # going wrong way
                    raise AVRCommandError(
                        command=command, err="AVR volume_up failed", zone=zone
                    )
                if volume_step_count > (target_volume - start_volume):
                    raise AVRCommandError(
                        command=command, err="maximum volume steps exceeded", zone=zone
                    )
                current_volume = new_volume
        elif target_volume < start_volume:  # step down
            while current_volume > target_volume:
                _LOGGER.debug("current volume: %d", current_volume)
                await self.volume_down(zone)
                volume_step_count += 1
                new_volume = self.properties.volume.get(zone)
                if new_volume >= current_volume:  # going wrong way
                    raise AVRCommandError(
                        command=command, err="AVR volume_down failed", zone=zone
                    )
                if volume_step_count > (start_volume - target_volume):
                    raise AVRCommandError(
                        command=command, err="maximum volume steps exceeded", zone=zone
                    )
                current_volume = self.properties.volume.get(zone)

    async def mute_on(self, zone: Zone = Zone.Z1) -> None:
        """Mute AVR."""
        await self.send_command("mute_on", zone=self._check_zone(zone))

    async def mute_off(self, zone: Zone = Zone.Z1) -> None:
        """Unmute AVR."""
        await self.send_command("mute_off", zone=self._check_zone(zone))

    def get_listening_modes(self) -> list[str] | None:
        """Return list of valid listening modes and names for Zone 1."""
        return list(self.properties.available_listening_modes.values())

    async def select_listening_mode(self, mode: str | int) -> None:
        """Set the listening mode using the predefined list of options in params."""
        await self.send_command("select_listening_mode", mode)

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
            raise AVRCommandUnavailableError(
                command="set_tone_settings", err_key="tone", zone=zone
            )

        if tone is not None:
            await self.send_command("set_tone_mode", tone, zone=zone)
        if self.properties.tone[zone].get("status") == "on":
            if treble is not None:
                await self.send_command("set_tone_treble", treble, zone=zone)
            if bass is not None:
                await self.send_command("set_tone_bass", bass, zone=zone)

    async def set_amp_settings(self, **kwargs) -> None:
        """Set amplifier settings (always use Main Zone)."""
        for arg, value in kwargs.items():
            try:
                command = f"set_amp_{arg}"
                await self.send_command(command, value)
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
            or not self.properties.is_source_tuner()
        ):
            raise AVRTunerUnavailableError(command="select_tuner_band")

        ## Set the tuner band
        if band == self.properties.tuner.get("band"):
            return
        tuner_commands = {TunerBand.AM: "tuner_band_am", TunerBand.FM: "tuner_band_fm"}
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
        if await self.send_command("tuner_increase_frequency", ignore_error=True):
            await self.send_command("tuner_decrease_frequency")
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
                    command="set_tuner_frequency", err_key="freq_step_unknown"
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
                    "tuner_increase_frequency",
                    zone=zone,
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
                    "tuner_decrease_frequency",
                    zone=zone,
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
        command = "set_tuner_frequency"
        await self.select_tuner_band(band)
        if band is TunerBand.AM and not self.properties.tuner.get("am_frequency_step"):
            await self.properties.command_queue.wait()  ## for AM step calculation

        if band is TunerBand.AM:
            code = FrequencyAM.value_to_code(frequency, properties=self.properties)
        else:
            code = FrequencyFM.value_to_code(frequency)

        if await self.send_command("tuner_direct_access", ignore_error=True):
            ## Set tuner frequency directly if command is supported
            try:
                for digit in code.lstrip("0"):
                    await self.send_command("tuner_digit", prefix=digit)
            except AVRCommandError as exc:
                raise AVRLocalCommandError(
                    command=command, err_key="freq_set_failed", exc=exc
                ) from exc
        else:
            await self._step_tuner_frequency(band=band, frequency=frequency)

    async def select_tuner_preset(self, tuner_class: str, tuner_preset: int) -> None:
        """Select the tuner preset."""
        await self.send_command("select_tuner_preset", (tuner_class, tuner_preset))

    async def tuner_previous_preset(self) -> None:
        """Select the previous tuner preset."""
        await self.send_command("tuner_previous_preset")

    async def tuner_next_preset(self) -> None:
        """Select the next tuner preset."""
        await self.send_command("tuner_next_preset")

    async def set_channel_levels(
        self, channel: str, level: float, zone: Zone = Zone.Z1
    ) -> None:
        """Set the level (gain) for amplifier channel in zone."""
        zone = self._check_zone(zone)
        await self.send_command("set_channel_levels", channel, level, zone=zone)

    async def set_video_settings(self, zone: Zone, **arguments) -> None:
        """Set video settings for a given zone."""
        zone = self._check_zone(zone)
        command = "set_video_settings"

        if zone is not Zone.Z1:
            raise AVRCommandUnavailableError(
                command=command, err_key="video_settings", zone=zone
            )

        for arg, value in arguments.items():
            if self.properties.video.get(arg) == value:
                continue
            try:
                command = f"set_video_{arg}"
                await self.send_command(command, value, zone=zone)
            except AVRError:
                raise
            except Exception as exc:  # pylint: disable=broad-except
                raise AVRLocalCommandError(command=command, exc=exc) from exc

    async def set_dsp_settings(self, zone: Zone, **arguments) -> None:
        """Set the DSP settings for the amplifier."""
        zone = self._check_zone(zone)
        command = "set_dsp_settings"

        if zone is not Zone.Z1:
            raise AVRCommandUnavailableError(
                command=command, err_key="dsp_settings", zone=zone
            )

        for arg, value in arguments.items():
            if self.properties.dsp.get(arg) == value:
                continue
            try:
                command = f"set_dsp_{arg}"
                await self.send_command(command, value, zone=zone)
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
            raise AVRCommandUnavailableError(
                command="media_control",
                err_key="media_controls",
                source=self.properties.source_name.get(zone),
            )

        command = MEDIA_CONTROL_COMMANDS.get(control_mode, {}).get(action)
        if command is None:
            raise AVRCommandUnavailableError(
                command="media_control",
                err_key="media_action",
                source=self.properties.source_name.get(zone),
                action=action,
            )

        # These commands are ALWAYS sent to zone 1 because each zone
        # does not have unique commands
        await self.send_command(command)

    async def set_source_name(self, source_id: int, source_name: str = None) -> None:
        """Renames an input to source_name. Reset to default if source_name is None."""
        if source_name is None:
            await self.send_command("set_default_source_name", source_id)
            return
        if self.properties.source_id_to_name.get(source_id) == source_name:
            return
        await self.send_command("set_source_name", source_name, source_id)
