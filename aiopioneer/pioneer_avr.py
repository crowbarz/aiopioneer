"""Pioneer AVR API (async)."""
# pylint: disable=relative-beyond-top-level disable=too-many-lines

import asyncio
import time
import logging
import re
import math
from .util import (
    merge,
    sock_set_keepalive,
    get_backoff_delay,
    cancel_task,
    safe_wait_for,
)
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
    PARAM_LISTENING_MODES,
    PARAM_TONE_MODES,
    PARAM_TONE_DB_VALUES,
    PARAM_SPEAKER_MODES,
    PARAM_HDMI_OUT_MODES,
    PARAM_HDMI_AUDIO_MODES,
    PARAM_PQLS_MODES,
    PARAM_PANEL_LOCK,
    PARAM_AMP_MODES,
    PARAM_VIDEO_RESOLUTION_MODES,
    PARAM_ADVANCED_VIDEO_ADJUST_MODES,
    PARAM_VIDEO_PURE_CINEMA_MODES,
    PARAM_VIDEO_STREAM_SMOOTHER_MODES,
    PARAM_VIDEO_ASPECT_MODES,
    PARAM_CHANNEL_LEVELS_OBJ,
    PARAM_DSP_OBJ,
    PARAM_DSP_PHASE_CONTROL,
    PARAM_DSP_SIGNAL_SELECT,
    PARAM_DSP_DIGITAL_DIALOG_ENHANCEMENT,
    PARAM_DSP_DUAL_MONO,
    PARAM_DSP_DRC,
    PARAM_DSP_HEIGHT_GAIN,
    PARAM_DSP_VIRTUAL_DEPTH,
    PARAM_DSP_DIGITAL_FILTER,
    PARAM_VIDEO_OBJ,
    PARAM_MULTI_CH_SOURCES,
)

_LOGGER = logging.getLogger(__name__)

VERSION = "0.3.4"

PIONEER_COMMANDS = {
    "system_query_mac_addr": {"1": ["?SVB", "SVB"]},
    "system_query_software_version": {"1": ["?SSI", "SSI"]},
    "system_query_model": {"1": ["?RGD", "RGD"]},
    "turn_on": {
        "1": ["PO", "PWR"],
        "2": ["APO", "APR"],
        "3": ["BPO", "BPR"],
        "Z": ["ZEO", "ZEP"],
    },
    "turn_off": {
        "1": ["PF", "PWR"],
        "2": ["APF", "APR"],
        "3": ["BPF", "BPR"],
        "Z": ["ZEF", "ZEP"],
    },
    "select_source": {
        "1": ["FN", "FN"],
        "2": ["ZS", "Z2F"],
        "3": ["ZT", "Z3F"],
        "Z": ["ZEA", "ZEA"],
    },
    "volume_up": {
        "1": ["VU", "VOL"],
        "2": ["ZU", "ZV"],
        "3": ["YU", "YV"],
        "Z": ["HZU", "XV"],
    },
    "volume_down": {
        "1": ["VD", "VOL"],
        "2": ["ZD", "ZV"],
        "3": ["YD", "YV"],
        "Z": ["HZD", "XV"],
    },
    "set_volume_level": {
        "1": ["VL", "VOL"],
        "2": ["ZV", "ZV"],
        "3": ["YV", "YV"],
        "Z": ["HZV", "XV"],
    },
    "mute_on": {
        "1": ["MO", "MUT"],
        "2": ["Z2MO", "Z2MUT"],
        "3": ["Z3MO", "Z3MUT"],
        "Z": ["HZMO", "HZMUT"],
    },
    "mute_off": {
        "1": ["MF", "MUT"],
        "2": ["Z2MF", "Z2MUT"],
        "3": ["Z3MF", "Z3MUT"],
        "Z": ["HZMF", "HZMUT"],
    },
    "query_power": {
        "1": ["?P", "PWR"],
        "2": ["?AP", "APR"],
        "3": ["?BP", "BPR"],
        "Z": ["?ZEP", "ZEP"],
    },
    "query_volume": {
        "1": ["?V", "VOL"],
        "2": ["?ZV", "ZV"],
        "3": ["?YV", "YV"],
        "Z": ["?HZV", "XV"],
    },
    "query_mute": {
        "1": ["?M", "MUT"],
        "2": ["?Z2M", "Z2MUT"],
        "3": ["?Z3M", "Z3MUT"],
        "Z": ["?HZM", "HZMUT"],
    },
    "query_source_id": {
        "1": ["?F", "FN"],
        "2": ["?ZS", "Z2F"],
        "3": ["?ZT", "Z3F"],
        "Z": ["?ZEA", "ZEA"],
    },
    "query_listening_mode": {
        "1": ["?S", "SR"]
    },
    "set_listening_mode": {
        "1": ["SR", "SR"]
    },
    "query_tone_mode": {
        "1": ["?TO", "TO"],
        "2": ["?ZGA", "ZGA"]
    },
    "query_bass_status": {
        "1": ["?BA", "BA"],
        "2": ["?ZGB", "ZGB"]
    },
    "query_treble_status": {
        "1": ["?TR", "TR"],
        "2": ["?ZGC", "ZGC"]
    },
    "set_tone_mode": {
        "1": ["TO", "TO"],
        "2": ["ZGA", "ZGA"],
    },
    "set_tone_bass": {
        "1": ["BA", "BA"],
        "2": ["ZGB", "ZGB"],
    },
    "set_tone_treble": {
        "1": ["TR", "TR"],
        "2": ["ZGC", "ZGC"],
    },
    "query_speaker_status": {
        "1": ["?SPK", "SPK"]
    },
    "set_speaker_status": {
        "1": ["SPK", "SPK"]
    },
    "query_hdmi_out_status": {
        "1": ["?HO", "HO"]
    },
    "set_hdmi_out_status": {
        "1": ["HO", "HO"]
    },
    "query_hdmi_audio_status": {
        "1": ["?HA", "HA"]
    },
    "set_hdmi_audio_status": {
        "1": ["HA", "HA"]
    },
    "query_pqls_status": {
        "1": ["?PQ", "PQ"]
    },
    "set_pqls_status": {
        "1": ["PQ", "PQ"]
    },
    "set_dimmer": {
        "1": ["SAA", "SAA"]
    },
    "query_sleep_remain_time": {
        "1": ["?SAB", "SAB"]
    },
    "set_sleep_remain_time": {
        "1": ["SAB", "SAB"]
    },
    "query_tuner_frequency": {
        "1": ["?FR", "FR"]
    },
    "set_tuner_band_am": {
        "1": ["01TN", "FR"]
    },
    "set_tuner_band_fm": {
        "1": ["00TN", "FR"]
    },
    "increase_tuner_frequency": {
        "1": ["TFI", "FR"]
    },
    "decrease_tuner_frequency": {
        "1": ["TFD", "FR"]
    },
    "query_panel_lock": {
        "1": ["?PKL", "PKL"]
    },
    "query_remote_lock": {
        "1": ["?RML", "RML"]
    },
    "set_panel_lock": {
        "1": ["PKL", "PKL"]
    },
    "set_remote_lock": {
        "1": ["RML", "RML"]
    },
    "query_tuner_preset": {
        "1": ["?PR", "PR"]
    },
    "query_video_resolution": {
        "1": ["?VTC", "VTC"]
    },
    "set_video_resolution": {
        "1": ["VTC", "VTC"]
    },
    "query_video_converter": {
        "1": ["?VTB", "VTB"]
    },
    "set_video_converter": {
        "1": ["VTB", "VTB"]
    },
    "query_pure_cinema_status": {
        "1": ["?VTD", "VTD"]
    },
    "set_pure_cinema_status": {
        "1": ["VTD", "VTD"]
    },
    "query_prog_motion_status": {
        "1": ["?VTE", "VTE"]
    }, 
    "set_prog_motion_status": {
        "1": ["VTE", "VTE"]
    },
    "query_stream_smoother": {
        "1": ["?VTF", "VTF"]
    },
    "set_stream_smoother": {
        "1": ["VTF", "VTF"]
    },
    "query_advanced_video_adjust": {
        "1": ["?VTG", "VTG"]
    },
    "set_advanced_video_adjust": {
        "1": ["VTG", "VTG"]
    },
    "query_ynr": {
        "1": ["?VTH", "VTH"]
    },
    "set_ynr": {
        "1": ["VTH", "VTH"]
    },
    "query_cnr": {
        "1": ["?VTI", "VTI"]
    },
    "set_cnr": {
        "1": ["VTI", "VTI"]
    },
    "query_bnr": {
        "1": ["?VTJ", "VTJ"]
    },
    "set_bnr": {
        "1": ["VTJ", "VTJ"]
    },
    "query_mnr": {
        "1": ["?VTK", "VTK"]
    },
    "set_mnr": {
        "1": ["VTK", "VTK"]
    },
    "query_detail": {
        "1": ["?VTL", "VTL"]
    },
    "set_detail": {
        "1": ["VTL", "VTL"]
    },
    "query_sharpness": {
        "1": ["?VTM", "VTM"]
    },
    "set_sharpness": {
        "1": ["VTM", "VTM"]
    },
    "query_brightness": {
        "1": ["?VTN", "VTN"]
    },
    "set_brightness": {
        "1": ["VTN", "VTN"]
    },
    "query_contrast": {
        "1": ["?VTO", "VTO"]
    },
    "set_contrast": {
        "1": ["VTO", "VTO"]
    },
    "query_hue": {
        "1": ["?VTP", "VTP"]
    },
    "set_hue": {
        "1": ["VTP", "VTP"]
    },
    "query_chroma": {
        "1": ["?VTQ", "VTQ"]
    },
    "set_chroma": {
        "1": ["VTQ", "VTQ"]
    },
    "query_black_setup": {
        "1": ["?VTR", "VTR"]
    },
    "set_black_setup": {
        "1": ["VTR", "VTR"]
    },
    "query_aspect": {
        "1": ["?VTS", "VTS"]
    },
    "set_aspect": {
        "1": ["VTS", "VTS"]
    },
    "set_channel_levels": {
        "1": ["CLV", "CLV"],
        "2": ["ZGE", "ZGE"],
        "3": ["ZHE", "ZHE"]
    },
    "set_mcacc_memory_set": {
        "1": ["MC", "MC"]
    },
    "set_phase_control": {
        "1": ["IS", "IS"]
    },
    "set_virtual_sb": {
        "1": ["VSB", "VSB"]
    },
    "set_virtual_height": {
        "1": ["VHT", "VHT"]
    },
    "set_sound_retriever": {
        "1": ["ATA", "ATA"]
    },
    "set_signal_select": {
        "1": ["SDA", "SDA"]
    },
    "set_analog_input_att": {
        "1": ["SDB", "SDB"]
    },
    "set_eq": {
        "1": ["ATC", "ATC"]
    },
    "set_standing_wave": {
        "1": ["ATD", "ATD"]
    },
    "set_phase_control_plus": {
        "1": ["ATE", "ATE"]
    },
    "set_sound_delay": {
        "1": ["ATF", "ATF"]
    },
    "set_digital_noise_reduction": {
        "1": ["ATG", "ATG"]
    },
    "set_digital_dialog_enhancement": {
        "1": ["ATH", "ATH"]
    },
    "set_hi_bit": {
        "1": ["ATI", "ATI"]
    },
    "set_dual_mono": {
        "1": ["ATJ", "ATJ"]
    },
    "set_fixed_pcm": {
        "1": ["ATK", "ATK"]
    },
    "set_drc": {
        "1": ["ATL", "ATL"]
    },
    "set_lfe_att": {
        "1": ["ATM", "ATM"]
    },
    "set_sacd_gain": {
        "1": ["ATN", "ATN"]
    },
    "set_auto_delay": {
        "1": ["ATO", "ATO"]
    },
    "set_center_width": {
        "1": ["ATP", "ATP"]
    },
    "set_panorama": {
        "1": ["ATQ", "ATQ"]
    },
    "set_dimension": {
        "1": ["ATR", "ATR"]
    },
    "set_center_image": {
        "1": ["ATS", "ATS"]
    },
    "set_effect": {
        "1": ["ATT", "ATT"]
    },
    "set_height_gain": {
        "1": ["ATU", "ATU"]
    },
    "set_virtual_depth": {
        "1": ["VDP", "VDP"]
    },
    "set_digital_filter": {
        "1": ["ATV", "ATV"]
    },
    "set_loudness_management": {
        "1": ["ATW", "ATW"]
    },
    "set_virtual_wide": {
        "1": ["VWD", "VWD"]
    },
    "query_mcacc_memory_query": {
        "1": ["?MC", "MC"]
    },
    "query_phase_control": {
        "1": ["?IS", "IS"]
    },
    "query_virtual_sb": {
        "1": ["?VSB", "VSB"]
    },
    "query_virtual_height": {
        "1": ["?VHT", "VHT"]
    },
    "query_sound_retriever": {
        "1": ["?ATA", "ATA"]
    },
    "query_signal_select": {
        "1": ["?SDA", "SDA"]
    },
    "query_analog_input_att": {
        "1": ["?SDB", "SDB"]
    },
    "query_eq": {
        "1": ["?ATC", "ATC"]
    },
    "query_standing_wave": {
        "1": ["?ATD", "ATD"]
    },
    "query_phase_control_plus": {
        "1": ["?ATE", "ATE"]
    },
    "query_sound_delay": {
        "1": ["?ATF", "ATF"]
    },
    "query_digital_noise_reduction": {
        "1": ["?ATG", "ATG"]
    },
    "query_digital_dialog_enhancement": {
        "1": ["?ATH", "ATH"]
    },
    "query_hi_bit": {
        "1": ["?ATI", "ATI"]
    },
    "query_dual_mono": {
        "1": ["?ATJ", "ATJ"]
    },
    "query_fixed_pcm": {
        "1": ["?ATK", "ATK"]
    },
    "query_drc": {
        "1": ["?ATL", "ATL"]
    },
    "query_lfe_att": {
        "1": ["?ATM", "ATM"]
    },
    "query_sacd_gain": {
        "1": ["?ATN", "ATN"]
    },
    "query_auto_delay": {
        "1": ["?ATO", "ATO"]
    },
    "query_center_width": {
        "1": ["?ATP", "ATP"]
    },
    "query_panorama": {
        "1": ["?ATQ", "ATQ"]
    },
    "query_dimension": {
        "1": ["?ATR", "ATR"]
    },
    "query_center_image": {
        "1": ["?ATS", "ATS"]
    },
    "query_effect": {
        "1": ["?ATT", "ATT"]
    },
    "query_height_gain": {
        "1": ["?ATU", "ATU"]
    },
    "query_virtual_depth": {
        "1": ["?VDP", "VDP"]
    },
    "query_digital_filter": {
        "1": ["?ATV", "ATV"]
    },
    "query_loudness_management": {
        "1": ["?ATW", "ATW"]
    },
    "query_virtual_wide": {
        "1": ["?VWD", "VWD"]
    }
}

class PioneerAVR:
    """Pioneer AVR interface."""

    def __init__(
        self,
        host,
        port=8102,
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

        ## Public properties
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

        ## FUNC: TONE
        self.tone = {}
        self.tone_bass = {}
        self.tone_treble = {}

        ## FUNC: AMP
        self.speakers = {}
        self.hdmi_out = {}
        self.hdmi_audio = {}
        self.pqls = {}
        self.sleep_remain = {}
        self.dimmer = {}
        self.amp = {}
        self.panel_lock = {}
        self.remote_lock = {}

        ## FUNC: TUNER
        self.tuner_frequency = {}
        self.tuner_band = {}
        self.tuner_preset = {}

        ## Complex object that holds multiple different props for the CHANNEL/DSP functions
        self.channel_levels = {}
        self.dsp = {}
        self.video = {}

        ## Parameters
        self._default_params = PARAM_DEFAULTS
        self._user_params = None
        self._params = None
        self.set_user_params(params)

        ## Internal state
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
        self._bouncer_task = None
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

    ## Parameter management functions
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
                    merge(self._default_params, model_params)
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

    ## Connection/disconnection
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

            ## Open new connection
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
            await self._bouncer_cancel()

            writer = self._writer
            if writer:
                ## Close AVR connection
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
                    ## 20201212 removed as connect already schedules full update
                    # _LOGGER.debug("Scheduling full AVR status update")
                    # self._full_update = True
                    # await self.update()
                    if self.available:
                        break
                except asyncio.CancelledError:  # pylint: disable=try-except-raise
                    ## pass through to outer except
                    raise
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.debug(
                        "could not reconnect to AVR: %s: %s", type(exc).__name__, exc
                    )
                    ## fall through to reconnect outside try block

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
                await asyncio.sleep(0)  ## yield to reconnect task if running
                if reconnect_task.done():
                    reconnect_task = None  ## trigger new task creation
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
                    ## Connection closed or exception, exit task
                    break

                ## Check for empty response
                debug_listener = self._params[PARAM_DEBUG_LISTENER]
                self._last_updated = time.time()  ## include empty responses
                if not response:
                    ## Skip processing empty responses (keepalives)
                    if debug_listener:
                        _LOGGER.debug("ignoring empty response")
                    continue
                if debug_listener:
                    _LOGGER.debug("AVR listener received response: %s", response)

                ## Parse response, update cached properties
                updated_zones = self._parse_response(response)

                ## Detect Main Zone power on for volume workaround
                power_on_volume_bounce = self._params[PARAM_POWER_ON_VOLUME_BOUNCE]
                if power_on_volume_bounce and self._power_zone_1 is not None:
                    if not self._power_zone_1 and self.power.get("1"):
                        ## Main zone powered on, schedule bounce task
                        _LOGGER.info("scheduling main zone volume workaround")
                        await self._bouncer_schedule()
                self._power_zone_1 = self.power.get("1")  ## cache value

                ## NOTE: to avoid deadlocks, do not run any operations that
                ## depend on further responses (returned by the listener) within
                ## the listener loop.

                if updated_zones:
                    ## Call zone callbacks for updated zones
                    self._call_zone_callbacks(updated_zones)
                    ## NOTE: updating zone 1 does not reset its scan interval -
                    ##       scan interval is set to a regular timer

            except asyncio.CancelledError:
                _LOGGER.debug(">> PioneerAVR._connection_listener() cancelled")
                running = False
                break
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.error(
                    ">> PioneerAVR._connection_listener() exception: %s", str(exc)
                )
                # continue listening on exception

        if running and self.available:
            ## Trigger disconnection if not already disconnected
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

    ## Reader co-routine
    async def _reader_readuntil(self):
        """Read from reader with cancel detection."""
        try:
            return await self._reader.readuntil(b"\n")
        except asyncio.CancelledError:
            _LOGGER.debug("reader: readuntil() was cancelled")
            return None

    ## Read responses from AVR
    async def _read_response(self, timeout=None):
        """Wait for a response from AVR and return to all readers."""
        debug_responder = self._params[PARAM_DEBUG_RESPONDER]

        if debug_responder:
            _LOGGER.debug(">> PioneerAVR._read_response(timeout=%s)", timeout)

        ## Schedule responder task if not already created
        responder_task = self._responder_task
        if responder_task:
            if responder_task.done():
                responder_task = None  ## trigger new task creation
        if responder_task is None:
            responder_task = asyncio.create_task(self._reader_readuntil())
            # responder_task = asyncio.create_task(self._reader.readuntil(b"\n"))
            self._responder_task = responder_task
            if debug_responder:
                _LOGGER.debug("created responder task %s", responder_task)
        else:
            ## Wait on existing responder task
            if debug_responder:
                _LOGGER.debug("using existing responder task %s", responder_task)

        ## Wait for result and process
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
            ## Connection closed
            _LOGGER.debug("%s: connection closed", task_name)
            return None
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.error("%s: exception: %s", task_name, str(exc))
            return None
        if raw_response is None:  ## task cancelled
            return None
        response = raw_response.decode().strip()
        if debug_responder:
            _LOGGER.debug("%s: received response: %s", task_name, response)
        return response

    async def _responder_cancel(self):
        """Cancel any active responder task."""
        await cancel_task(self._responder_task, "responder")
        self._responder_task = None

    ## Send commands and requests to AVR
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
            ## Rate limit commands
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

                ## Check response
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
                    ## Handle command as request
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

    ## Initialisation functions
    async def query_zones(self, force_update=False):
        """Query zones on Pioneer AVR by querying power status."""
        _LOGGER.info("querying available zones on AVR")
        ignored_zones = self._params[PARAM_IGNORED_ZONES]
        ignore_volume_check = self._params[PARAM_IGNORE_VOLUME_CHECK]
        added_zones = False
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

    async def update_zones(self):
        """Update zones from ignored_zones and re-query zones."""
        removed_zones = False
        for zone in self._params[PARAM_IGNORED_ZONES]:
            if zone in self.zones:
                zone_name = "HDZone" if zone == "Z" else zone
                _LOGGER.info("Removing zone %s", zone_name)
                self.zones.remove(zone)
                self._call_zone_callbacks([zone])  ## update availability
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

    def get_source_list(self):
        """Return list of available input sources."""
        return list(self._source_name_to_id.keys())

    def get_sound_modes(self, zone):
        """Return list of valid sound modes."""
        ## Check if the zone is the main zone or not, listening modes aren't supported on other zones
        if (zone == "1"):
            ## Now check if the current input is multi channel or not
            if (self.source.get(zone) not in self._params.get(PARAM_MULTI_CH_SOURCES)):
                return list([v for k, v in PARAM_LISTENING_MODES.items() if "MULTI CH" not in v.upper()])
            else:
                return list([v for k, v in PARAM_LISTENING_MODES.items() if "MULTI CH" in v.upper() or "DIRECT" in v.upper()])
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

        ## Query model via command
        data = await self.send_command("system_query_model", ignore_error=True)
        if data:
            matches = re.search(r"<([^>/]{5,})(/.[^>]*)?>", data)
            if matches:
                model = matches.group(1)

        ## Query MAC address via command
        data = await self.send_command("system_query_mac_addr", ignore_error=True)
        if data:
            mac_addr = data[0:2] + ":" + data[2:4] + ":" + data[4:6]
            mac_addr += ":" + data[6:8] + ":" + data[8:10] + ":" + data[10:12]

        ## Query software version via command
        data = await self.send_command("system_query_software_version", ignore_error=True)
        if data:
            matches = re.search(r'SSI"([^)]*)"', data)
            if matches:
                software_version = matches.group(1)

        self.model = "unknown"
        if model:
            self.model = model

        ## Update default params for this model
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

    ## Callback functions
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

    ## Update functions
    def _parse_response(self, response):
        """Parse response and update cached parameters."""
        updated_zones = set()

        ## Set DSP if not already set
        if self.dsp.get("1") is None:
                self.dsp["1"] = PARAM_DSP_OBJ

        ## Set VIDEO if not already set
        if self.video.get("1") is None:
            self.video["1"] = PARAM_VIDEO_OBJ

        ## POWER STATUS
        if response.startswith("PWR"):
            value = response == "PWR0"
            if self.power.get("1") != value:
                self.power["1"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Power: %s", value)
        elif response.startswith("APR"):
            value = response == "APR0"
            if self.power.get("2") != value:
                self.power["2"] = value
                updated_zones.add("2")
                _LOGGER.info("Zone 2: Power: %s", value)
        elif response.startswith("BPR"):
            value = response == "BPR0"
            if self.power.get("3") != value:
                self.power["3"] = value
                updated_zones.add("3")
                _LOGGER.info("Zone 3: Power: %s", value)
        elif response.startswith("ZEP"):
            value = response == "ZEP0"
            if self.power.get("Z") != value:
                self.power["Z"] = value
                updated_zones.add("Z")
                _LOGGER.info("HDZone: Power: %s", value)

        ## VOLUME STATUS
        elif response.startswith("VOL"):
            value = int(response[3:])
            if self.volume.get("1") != value:
                self.volume["1"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Volume: %s", value)
        elif response.startswith("ZV"):
            value = int(response[2:])
            if self.volume.get("2") != value:
                self.volume["2"] = value
                updated_zones.add("2")
                _LOGGER.info("Zone 2: Volume: %s", value)
        elif response.startswith("YV"):
            value = int(response[2:])
            if self.volume.get("3") != value:
                self.volume["3"] = value
                updated_zones.add("3")
                _LOGGER.info("Zone 3: Volume: %s", value)
        elif response.startswith("XV"):
            value = int(response[2:])
            if self.volume.get("Z") != value:
                self.volume["Z"] = value
                updated_zones.add("Z")
                _LOGGER.info("HDZone: Volume: %s", value)

        ## MUTE STATUS
        elif response.startswith("MUT"):
            value = response == "MUT0"
            if self.mute.get("1") != value:
                self.mute["1"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Mute: %s", value)
        elif response.startswith("Z2MUT"):
            value = response == "Z2MUT0"
            if self.mute.get("2") != value:
                self.mute["2"] = value
                updated_zones.add("2")
                _LOGGER.info("Zone 2: Mute: %s", value)
        elif response.startswith("Z3MUT"):
            value = response == "Z3MUT0"
            if self.mute.get("3") != value:
                self.mute["3"] = value
                updated_zones.add("3")
                _LOGGER.info("Zone 3: Mute: %s", value)
        elif response.startswith("HZMUT"):
            value = response == "HZMUT0"
            if self.mute.get("Z") != value:
                self.mute["Z"] = value
                updated_zones.add("Z")
                _LOGGER.info("HDZone: Mute: %s", value)

        ## INPUTS
        elif response.startswith("FN"):
            zid = response[2:]
            if self.source.get("1") != zid:
                self.source["1"] = zid
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Source: %s (%s)", zid, self.get_source_name(zid))
        elif response.startswith("Z2F"):
            zid = response[3:]
            if self.source.get("2") != zid:
                self.source["2"] = zid
                updated_zones.add("2")
                _LOGGER.info("Zone 2: Source: %s (%s)", zid, self.get_source_name(zid))
        elif response.startswith("Z3F"):
            zid = response[3:]
            if self.source.get("3") != zid:
                self.source["3"] = zid
                updated_zones.add("3")
                _LOGGER.info("Zone 3: Source: %s (%s)", zid, self.get_source_name(zid))
        elif response.startswith("ZEA"):
            zid = response[3:]
            if self.source.get("Z") != zid:
                self.source["Z"] = zid
                updated_zones.add("Z")
                _LOGGER.info("HDZone: Source: %s (%s)", zid, self.get_source_name(zid))
        
        ## LISTENING MODES
        elif response.startswith("SR"):
            value = response[2:]
            if self.listening_mode.get("1") != value:
                self.listening_mode["1"] = PARAM_LISTENING_MODES.get(value)
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Listening Mode: %s (%s)", self.listening_mode.get("1"), value)

        ## TONE CONTROL
        elif response.startswith("TO"):
            value = response[2:]
            if self.tone.get("1") != value:
                self.tone["1"] = PARAM_TONE_MODES.get(value)
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Tone: %s (%s)", self.tone.get("1"), value)
        elif response.startswith("BA"):
            value = response[2:]
            if self.tone_bass.get("1") != value:
                self.tone_bass["1"] = PARAM_TONE_DB_VALUES.get(value)
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Bass Level: %s (%s)", self.tone_bass.get("1"), value)
        elif response.startswith("TR"):
            value = response[2:]
            if self.tone_treble.get("1") != value:
                self.tone_treble["1"] = PARAM_TONE_DB_VALUES.get(value)
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Treble Level: %s (%s)", self.tone_treble.get("1"), value)

        elif response.startswith("ZGA"):
            value = response[3:]
            if self.tone.get("2") != value:
                self.tone["2"] = PARAM_TONE_MODES.get(value)
                updated_zones.add("2")
                _LOGGER.info("Zone 2: Tone: %s (%s)", self.tone.get("2"), value)
        elif response.startswith("ZGB"):
            value = int(response[3:])-50
            if self.tone_bass.get("2") != value:
                self.tone_bass["2"] = value
                updated_zones.add("2")
                _LOGGER.info("Zone 2: Bass Level: %s (%s)", self.tone_bass.get("2"), value)
        elif response.startswith("ZGC"):
            value = int(response[3:])-50
            if self.tone_treble.get("2") != value:
                self.tone_treble["2"] = value
                updated_zones.add("2")
                _LOGGER.info("Zone 2: Treble Level: %s (%s)", self.tone_treble.get("2"), value)

        ## AMP FUNCTIONS
        elif response.startswith("SPK"):
            value = response[3:]
            if self.speakers.get("1") != value:
                self.speakers["1"] = PARAM_SPEAKER_MODES.get(value)
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Speakers: %s (%s)", self.speakers.get("1"), value)
        elif response.startswith("HO"):
            value = response[2:]
            if self.hdmi_out.get("1") != value:
                self.hdmi_out["1"] = PARAM_HDMI_OUT_MODES.get(value)
                updated_zones.add("1")
                _LOGGER.info("Zone 1: HDMI OUT: %s (%s)", self.hdmi_out.get("1"), value)
        elif response.startswith("HA"):
            value = response[2:]
            if self.hdmi_audio.get("1") != value:
                self.hdmi_audio["1"] = PARAM_HDMI_AUDIO_MODES.get(value)
                updated_zones.add("1")
                _LOGGER.info("Zone 1: HDMI AUDIO: %s (%s)", self.hdmi_audio.get("1"), value)
        elif response.startswith("PQ"):
            value = response[2:]
            if self.pqls.get("1") != value:
                self.pqls["1"] = PARAM_PQLS_MODES.get(value)
                updated_zones.add("1")
                _LOGGER.info("Zone 1: PQLS: %s (%s)", self.pqls.get("1"), value)
        elif response.startswith("SAA"):
            value = int(response[3:])
            if self.dimmer.get("1") != value:
                self.dimmer["1"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Dimmer: %s", self.dimmer.get("1"))
        elif response.startswith("SAB"):
            sleep_remaining = int(response[3:])
            if (sleep_remaining == 0):
                sleep_remaining = None

            if self.sleep_remain.get("1") != sleep_remaining:
                self.sleep_remain["1"] = sleep_remaining
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Sleep Remaining: %sm", str(sleep_remaining))
        elif response.startswith("SAC"):
            value = int(response[3:])
            value = PARAM_AMP_MODES.get(str(value))
            if self.amp.get("1") != value:
                self.amp["1"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: AMP Status: %s (%s)", value, response[3:])
        
        ## KEY LOCK
        elif response.startswith("PKL"):
            value = response[3:]
            if self.panel_lock.get("1") != value:
                self.panel_lock["1"] = PARAM_PANEL_LOCK.get(value)
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Panel Lock: %s (%s)", self.panel_lock.get("1"), value)
        elif response.startswith("RML"):
            value = (int(response[3:]))
            if self.remote_lock.get("1") != value:
                self.remote_lock["1"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Remote Lock: %s", self.remote_lock.get("1"))

        ## TUNER
        elif response.startswith("FR"):
            value = response[2:]
            ## Split the value up here, first char is band
            band = value[:1]
            if band == "F":
                freq = float(value[1:]) / 100
            else:
                freq = float(value[1:])

            if (self.tuner_band.get("1") != band) or (self.tuner_frequency.get("1") != freq):
                self.tuner_band["1"] = band
                self.tuner_frequency["1"] = freq
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Tuner Frequency: %s, Band: %s (%s)", str(freq), str(band), value)

        elif response.startswith("PR"):
            value = response[2:]
            t_class = value[:1]
            t_preset = int(value[1:])
            value = t_class+str(t_preset)
            if (self.tuner_preset.get("1") != value):
                self.tuner_preset["1"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Tuner Preset: %s (%s)", value, response[2:])

        ## VIDEO FUNCTIONS
        elif response.startswith("VTB"):
            value = int(response[3:])
            if value == 1:
                value = "on"
            else:
                value = "off"
            if self.video.get("1").get("converter") != value:
                self.video["1"]["converter"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Converter: %s (%s)", value, response[3:])

        elif response.startswith("VTC"):
            value = int(response[3:])
            if self.video.get("1").get("resolution") != PARAM_VIDEO_RESOLUTION_MODES.get(str(value)):
                self.video["1"]["resolution"] = PARAM_VIDEO_RESOLUTION_MODES.get(str(value))
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Resolution: %s (%s)", self.video_resolution.get("1"), str(value))

        elif response.startswith("VTD"):
            value = int(response[3:])
            ## Override value to auto, on or off
            if value == 0:
                value = "auto"
            elif value == 2:
                value = "on"
            else:
                value = "off"
            if self.video.get("1").get("pure_cinema") != value:
                self.video["1"]["pure_cinema"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Pure Cinema: %s (%s)", value, response[3:])

        elif response.startswith("VTE"):
            value = int(response[3:])
            if value < 55:
                value = value - 50
                if (self.video.get("1").get("prog_motion") != value):
                    self.video["1"]["prog_motion"] = value
                    updated_zones.add("1")
                    _LOGGER.info("Zone 1: Video Prog. Motion: %s", str(value))

        elif response.startswith("VTF"):
            value = int(response[3:])
            if value == 0:
                value = "off"
            elif value =="1":
                value = "on"
            else:
                value = "auto"
            if (self.video.get("1").get("stream_smoother") != value):
                self.video["1"]["stream_smoother"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Stream Smoother: %s", value)

        elif response.startswith("VTG"):
            value = int(response[3:])
            if (self.video.get("1").get("advanced_video_adjust") != PARAM_ADVANCED_VIDEO_ADJUST_MODES.get(str(value))):
                self.video["1"]["advanced_video_adjust"] = PARAM_ADVANCED_VIDEO_ADJUST_MODES.get(str(value))
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Advanced Video Adjust: %s (%s)", PARAM_ADVANCED_VIDEO_ADJUST_MODES.get(str(value)), value)

        elif response.startswith("VTH"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("ynr") != value):
                self.video["1"]["ynr"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video YNR: %s", str(value))

        elif response.startswith("VTI"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("cnr") != value):
                self.video["1"]["cnr"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video CNR: %s", str(value))

        elif response.startswith("VTJ"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("bnr") != value):
                self.video["1"]["bnr"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video BNR: %s", str(value))

        elif response.startswith("VTK"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("mnr") != value):
                self.video["1"]["mnr"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video MNR: %s", str(value))

        elif response.startswith("VTL"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("detail") != value):
                self.video["1"]["detail"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Detail: %s", str(value))

        elif response.startswith("VTM"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("sharpness") != value):
                self.video["1"]["sharpness"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Sharpness: %s", str(value))

        elif response.startswith("VTN"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("brightness") != value):
                self.video["1"]["brightness"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Brightness: %s", str(value))

        elif response.startswith("VTO"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("contrast") != value):
                self.video["1"]["contrast"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Contrast: %s", str(value))

        elif response.startswith("VTP"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("hue") != value):
                self.video["1"]["hue"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Hue: %s", str(value))

        elif response.startswith("VTQ"):
            value = int(response[3:])
            value = value - 50
            if (self.video.get("1").get("chroma") != value):
                self.video["1"]["chroma"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Chroma: %s", str(value))

        elif response.startswith("VTR"):
            value = int(response[3:])
            if value == 0:
                value = 0
            elif value == 1:
                value = 7.5

            if (self.video.get("1").get("black_setup") != value):
                self.video["1"]["black_setup"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Black Setup: %s", str(value))

        elif response.startswith("VTS"):
            value = int(response[3:])
            if value == 0:
                value = "passthrough"
            elif value == 1:
                value = "normal"

            if (self.video.get("1").get("aspect") != value):
                self.video["1"]["aspect"] = value
                updated_zones.add("1")
                _LOGGER.info("Zone 1: Video Aspect: %s", str(value))

        ## CHANNEL FUNCTIONS
        elif response.startswith("CLV"):
            value = float((int(response[6:])-50)/2)
            speaker = str(response[3:6]).strip("_").upper()
            if (self.channel_levels.get("1") is None):
                ## Define a new channel_levels object for zone 1
                self.channel_levels["1"] = PARAM_CHANNEL_LEVELS_OBJ

            if (self.channel_levels.get("1").get(speaker) is not value):
                _LOGGER.info("Zone 1: Speaker %s Channel Level %s", str(speaker), str(value))
                self.channel_levels["1"][speaker] = value

            updated_zones.add("1")

        elif response.startswith("ZGE"):
            value = float((int(response[6:])-50)/2)
            speaker = str(response[3:6]).strip("_").upper()
            if self.channel_levels.get("2") is None:
                ## Define a new channel_levels object for zone 2
                self.channel_levels["2"] = PARAM_CHANNEL_LEVELS_OBJ

            if self.channel_levels.get("2").get(speaker) is not value:
                _LOGGER.info("Zone 2: Speaker %s Channel Level %s", str(speaker), str(value))
                self.channel_levels["2"][speaker] = value

            updated_zones.add("2")

        elif response.startswith("ZHE"):
            value = float((int(response[6:])-50)/2)
            speaker = str(response[3:6]).strip("_").upper()
            if self.channel_levels.get("3") is None:
                ## Define a new channel_levels object for zone 2
                self.channel_levels["3"] = PARAM_CHANNEL_LEVELS_OBJ

            if self.channel_levels.get("3").get(speaker) is not value:
                _LOGGER.info("Zone 3: Speaker %s Channel Level %s", str(speaker), str(value))
                self.channel_levels["3"][speaker] = value

            updated_zones.add("3")

        ## FUNC: DSP
        elif response.startswith("MC"):
            value = int(response[2:])
            if self.dsp.get("1").get("mcacc_memory_set") is not value:
                _LOGGER.info("Zone 1: MCACC MEMORY SET %s", str(value))
                self.dsp["1"]["mcacc_memory_set"] = value
            
            updated_zones.add("1")
        
        elif response.startswith("IS"):
            value = response[2:]
            if self.dsp.get("1").get("phase_control") is not PARAM_DSP_PHASE_CONTROL.get(value):
                _LOGGER.info("Zone 1: PHASE CONTROL %s", str(value))
                self.dsp["1"]["phase_control"] = PARAM_DSP_PHASE_CONTROL.get(value)

            updated_zones.add("1")

        elif response.startswith("VSB"):
            value = bool(response[3:])
            if self.dsp.get("1").get("virtual_sb") is not value:
                _LOGGER.info("Zone 1: VIRTUAL SB %s", str(value))
                self.dsp["1"]["virtual_sb"] = value

            updated_zones.add("1")

        elif response.startswith("VHT"):
            value = bool(response[3:])
            if self.dsp.get("1").get("virtual_height") is not value:
                _LOGGER.info("Zone 1: VIRTUAL HEIGHT %s", str(value))
                self.dsp["1"]["virtual_height"] = value

            updated_zones.add("1")
        
        elif response.startswith("ATA"):
            value = bool(response[3:])
            if self.dsp.get("1").get("sound_retriever") is not value:
                _LOGGER.info("Zone 1: SOUND RETRIEVER %s", str(value))
                self.dsp["1"]["sound_retriever"] = value

            updated_zones.add("1")
        
        elif response.startswith("SDA"):
            value = response[3:]
            value = PARAM_DSP_SIGNAL_SELECT.get(value)
            if self.dsp.get("1").get("signal_select") is not value:
                _LOGGER.info("Zone 1: SIGNAL SELECT %s", str(value))
                self.dsp["1"]["signal_select"] = value

            updated_zones.add("1")

        elif response.startswith("SDB"):
            value = bool(response[3:])
            if self.dsp.get("1").get("analog_input_att") is not value:
                _LOGGER.info("Zone 1: ANALOG INPUT ATT %s", str(value))
                self.dsp["1"]["analog_input_att"] = value

            updated_zones.add("1")
        
        elif response.startswith("ATC"):
            value = bool(response[3:])
            if self.dsp.get("1").get("eq") is not value:
                _LOGGER.info("Zone 1: EQ %s", str(value))
                self.dsp["1"]["eq"] = value

            updated_zones.add("1")

        elif response.startswith("ATD"):
            value = bool(response[3:])
            if self.dsp.get("1").get("standing_wave") is not value:
                _LOGGER.info("Zone 1: STANDING WAVE %s", str(value))
                self.dsp["1"]["standing_wave"] = value

            updated_zones.add("1")

        elif response.startswith("ATE"):
            value = int(response[3:])
            if value == 97:
                value = "AUTO"
            
            if self.dsp.get("1").get("phase_control_plus") is not value:
                _LOGGER.info("Zone 1: PHASE CONTROL PLUS %s", str(value))
                self.dsp["1"]["phase_control_plus"] = value

            updated_zones.add("1")

        elif response.startswith("ATF"):
            value = float(response[3:])/10
            if self.dsp.get("1").get("sound_delay") is not value:
                _LOGGER.info("Zone 1: SOUND DELAY %s", str(value))
                self.dsp["1"]["sound_delay"] = value

            updated_zones.add("1")

        elif response.startswith("ATG"):
            value = bool(response[3:])
            if self.dsp.get("1").get("digital_noise_reduction") is not value:
                _LOGGER.info("Zone 1: DIGITAL NOISE REDUCTION %s", str(value))
                self.dsp["1"]["digital_noise_reduction"] = value

            updated_zones.add("1")

        elif response.startswith("ATH"):
            value = response[3:]
            value = PARAM_DSP_DIGITAL_DIALOG_ENHANCEMENT.get(value)
            if self.dsp.get("1").get("digital_dialog_enhancement") is not value:
                _LOGGER.info("Zone 1: DIGITAL DIALOG ENHANCEMENT %s", str(value))
                self.dsp["1"]["digital_dialog_enhancement"] = value

            updated_zones.add("1")

        elif response.startswith("ATI"):
            value = bool(response[3:])
            if self.dsp.get("1").get("hi_bit") is not value:
                _LOGGER.info("Zone 1: HI-BIT %s", str(value))
                self.dsp["1"]["hi_bit"] = value

            updated_zones.add("1")

        elif response.startswith("ATJ"):
            value = PARAM_DSP_DUAL_MONO.get(response[3:])
            if self.dsp.get("1").get("dual_mono") is not value:
                _LOGGER.info("Zone 1: DUAL MONO %s", str(value))
                self.dsp["1"]["dual_mono"] = value

            updated_zones.add("1")

        elif response.startswith("ATK"):
            value = bool(response[3:])
            if self.dsp.get("1").get("fixed_pcm") is not value:
                _LOGGER.info("Zone 1: FIXED PCM %s", str(value))
                self.dsp["1"]["fixed_pcm"] = value

            updated_zones.add("1")

        elif response.startswith("ATL"):
            value = PARAM_DSP_DRC.get(response[3:])
            if self.dsp.get("1").get("drc") is not value:
                _LOGGER.info("Zone 1: DRC %s", str(value))
                self.dsp["1"]["drc"] = value

            updated_zones.add("1")

        elif response.startswith("ATM"):
            value = int(response[3:])*-5
            if value < -20:
                value = "off"
            if self.dsp.get("1").get("lfe_att") is not value:
                _LOGGER.info("Zone 1: LFE ATT %s", str(value))
                self.dsp["1"]["lfe_att"] = value

            updated_zones.add("1")

        elif response.startswith("ATN"):
            value = 6 if bool(response[3:]) == True else 0
            if self.dsp.get("1").get("sacd_gain") is not value:
                _LOGGER.info("Zone 1: SACD GAIN %s", str(value))
                self.dsp["1"]["sacd_gain"] = value

            updated_zones.add("1")

        elif response.startswith("ATO"):
            value = bool(response[3:])
            if self.dsp.get("1").get("auto_delay") is not value:
                _LOGGER.info("Zone 1: AUTO DELAY %s", str(value))
                self.dsp["1"]["auto_delay"] = value

            updated_zones.add("1")

        elif response.startswith("ATP"):
            value = int(response[3:])
            if self.dsp.get("1").get("center_width") is not value:
                _LOGGER.info("Zone 1: CENTER WIDTH %s", str(value))
                self.dsp["1"]["center_width"] = value

            updated_zones.add("1")
        
        elif response.startswith("ATQ"):
            value = bool(response[3:])
            if self.dsp.get("1").get("panorama") is not value:
                _LOGGER.info("Zone 1: PANORAMA %s", str(value))
                self.dsp["1"]["panorama"] = value

            updated_zones.add("1")

        elif response.startswith("ATR"):
            value = int(response[3:])-50
            if self.dsp.get("1").get("dimension") is not value:
                _LOGGER.info("Zone 1: DIMENSION %s", str(value))
                self.dsp["1"]["dimension"] = value

            updated_zones.add("1")

        elif response.startswith("ATS"):
            value = float(response[3:])/10
            if self.dsp.get("1").get("center_image") is not value:
                _LOGGER.info("Zone 1: CENTER IMAGE %s", str(value))
                self.dsp["1"]["center_image"] = value

            updated_zones.add("1")

        elif response.startswith("ATT"):
            value = int(response[3:])*10
            if self.dsp.get("1").get("effect") is not value:
                _LOGGER.info("Zone 1: EFFECT %s", str(value))
                self.dsp["1"]["effect"] = value

            updated_zones.add("1")

        elif response.startswith("ATU"):
            value = PARAM_DSP_HEIGHT_GAIN.get(response[3:])
            if self.dsp.get("1").get("height_gain") is not value:
                _LOGGER.info("Zone 1: HEIGHT GAIN %s", str(value))
                self.dsp["1"]["height_gain"] = value

            updated_zones.add("1")

        elif response.startswith("VDP"):
            value = PARAM_DSP_VIRTUAL_DEPTH.get(response[3:])
            if self.dsp.get("1").get("virtual_depth") is not value:
                _LOGGER.info("Zone 1: VIRTUAL DEPTH %s", str(value))
                self.dsp["1"]["virtual_depth"] = value

            updated_zones.add("1")

        elif response.startswith("ATV"):
            value = PARAM_DSP_DIGITAL_FILTER.get(response[3:])
            if self.dsp.get("1").get("digital_filter") is not value:
                _LOGGER.info("Zone 1: DIGITAL FILTER %s", str(value))
                self.dsp["1"]["digital_filter"] = value

            updated_zones.add("1")

        elif response.startswith("ATW"):
            value = bool(response[3:])
            if self.dsp.get("1").get("loudness_management") is not value:
                _LOGGER.info("Zone 1: LOUDNESS MANAGEMENT %s", str(value))
                self.dsp["1"]["loudness_management"] = value

            updated_zones.add("1")

        elif response.startswith("VWD"):
            value = bool(response[3:])
            if self.dsp.get("1").get("virtual_wide") is not value:
                _LOGGER.info("Zone 1: VIRTUAL WIDE %s", str(value))
                self.dsp["1"]["virtual_wide"] = value

            updated_zones.add("1")

        return updated_zones

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
            except asyncio.TimeoutError:  ## update timer expired
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
            self._full_update = True  ## always perform full update on schedule
            self._updater_task = asyncio.create_task(self._updater())

    async def _updater_cancel(self):
        """Cancel the updater task."""
        await cancel_task(self._updater_task, "updater")
        self._updater_task = None

    async def _update_zone(self, zone):
        """Update an AVR zone."""
        ## Check for timeouts, but ignore errors (eg. ?V will
        ## return E02 immediately after power on)
        query_commands = [k for k in PIONEER_COMMANDS.keys() if k.startswith("query")]

        ## All zone updates
        if (
            await self.send_command("query_power", zone, ignore_error=True) is None
            or await self.send_command("query_volume", zone, ignore_error=True) is None
            or await self.send_command("query_mute", zone, ignore_error=True) is None
            or await self.send_command("query_source_id", zone, ignore_error=True) is None
        ):
            ## Timeout occurred, indicates AVR disconnected
            raise TimeoutError("Timeout waiting for data")

        ## Zone 1 updates only, we loop through this to allow us to add commands to read without 
        ## needing to add it here, also only do this if the zone is powered on
        if (zone == "1" and self.power.get("1") == True):
            for comm in query_commands:
                if len(PIONEER_COMMANDS.get(comm)) == 1:
                    await self.send_command(comm, zone, ignore_error=True)

        ## Zone 1 or 2 updates only, only availble if zone 1 is on
        if ((zone == "1") or (zone == "2")) and self.power.get("1") == True:
            for comm in query_commands:
                if (len(PIONEER_COMMANDS.get(comm)) == 2):
                    await self.send_command(comm, zone, ignore_error=True)

        ## CHANNEL updates are handled differently as it requires more complex logic to send the commands
        ## we use the set_channel_levels command and prefix the query to it
        ## Only run this if the main zone is on
        ## HDZone does not have any channels
        if (self.power.get("1") == True) and zone != "Z":
            for k in PARAM_CHANNEL_LEVELS_OBJ.keys():
                if len(k) == 1:
                    ## Add two underscores
                    k = k + "__"
                elif len(k) == 2:
                    ## Add one underscore
                    k = k + "_"
                await self.send_command("set_channel_levels", zone, "?" + str(k), ignore_error=True)

    async def _updater_update(self):
        """Update AVR cached status."""
        debug_updater = self._params[PARAM_DEBUG_UPDATER]
        if debug_updater:
            _LOGGER.debug(">> PioneerAVR._updater_update() started")
        if self._update_lock.locked():
            _LOGGER.warning("AVR update already running, skipping")
            return False
        if not self.available:
            _LOGGER.debug("AVR not connected, skipping update")
            return False

        _rc = True
        async with self._update_lock:
            ## Update only if scan_interval has passed
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
                        ## Trigger updates to all zones on full update
                        self._call_zone_callbacks()
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.error(
                        "could not update AVR status: %s: %s",
                        type(exc).__name__,
                        str(exc),
                    )
                    _rc = False
            else:
                ## NOTE: any response from the AVR received within
                ## scan_interval, including keepalives and responses triggered
                ## via the remote and by other clients, will cause the next
                ## update to be skipped if that update is scheduled to occur
                ## within scan_interval of the response.
                ##
                ## Keepalives may be sent by the AVR (every 30 seconds on the
                ## VSX-930) when connected to port 8102, but are not sent when
                ## connected to port 23.
                _rc = None
                if debug_updater:
                    _LOGGER.debug(
                        "skipping update: last updated %.3f s ago", since_updated
                    )
        if _rc is False:
            ## Disconnect on error
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
            ## scan_interval not set, execute update synchronously
            await self._updater_update()

    ## State change functions

    def _get_parameter_key_from_value(self, val: str, parameters: dict, looseMatch: bool=False):
        items = None
        if looseMatch:
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
        ## Now schedule a full update of all zones if listening_mode is None (this means that the library connected to the AVR while the AVR was off)
        if (zone == "1" and self.listening_mode.get("1") is None):
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
            result = await self.send_command(
                "select_source", zone, prefix=source_id, ignore_error=False
            )
            ## Refresh listening mode information for zone 1 as this some AVRs can remember different states for different sources
            if zone == "1":
                await self.send_command("query_listening_mode", zone, ignore_error=True)
            
            return result
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

    async def bounce_volume(self):
        """
        Send volume up/down to work around Main Zone reporting bug where
        an initial volume is set. This initial volume is not reported until
        the volume is changed.
        """
        if await self.volume_up():
            return await self.volume_down()
        else:
            return False

    async def _bouncer_schedule(self):
        """Schedule volume bounce task. Run when zone 0 power on is detected."""
        _LOGGER.debug(">> PioneerAVR._bouncer_schedule()")
        await self._bouncer_cancel()
        self._bouncer_task = asyncio.create_task(self.bounce_volume())

    async def _bouncer_cancel(self):
        """Cancel volume bounce task."""
        await cancel_task(self._bouncer_task, "bouncer")
        self._bouncer_task = None

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
        """Sets the listening mode using the predefnined list of options in params."""
        self._check_zone(zone)
        return await self.send_command(
            "set_listening_mode", zone, prefix=self._get_parameter_key_from_value(listening_mode, PARAM_LISTENING_MODES), ignore_error=False
        )

    async def set_panel_lock(self, panel_lock: str, zone="1"):
        """Sets the panel lock."""
        self._check_zone(zone)
        return await self.send_command("set_panel_lock", zone, self._get_parameter_key_from_value(panel_lock, PARAM_PANEL_LOCK), ignore_error=False)

    async def set_remote_lock(self, remote_lock: bool, zone="1"):
        """Sets the remote lock."""
        self._check_zone(zone)
        return await self.send_command("set_remote_lock", zone, ignore_error=False, prefix=str(int(remote_lock)))

    async def set_dimmer(self, dimmer, zone="1"):
        """Set the display dimmer."""
        self._check_zone(zone)
        return await self.send_command("set_dimmer", zone, ignore_error=False, prefix=dimmer)

    async def set_tone_settings(self, tone: str=None, treble: int=None, bass: int=None, zone="1"):
        """Set the tone settings of a given zone."""
        ## Check the zone supports tone settings
        if (self.tone.get(zone) is not None):
            toneResponse, toneTreble, toneBass = True, True, True
            if (tone is not None):
                toneResponse = await self.send_command("set_tone_mode", zone, self._get_parameter_key_from_value(tone, PARAM_TONE_MODES), ignore_error=False)
            ## These actions only work if zone tone is set to "ON"
            if (self.tone.get(zone) == "ON"):
                if (treble is not None):
                    toneTreble = await self.send_command("set_tone_treble", zone, self._get_parameter_key_from_value(str(treble), PARAM_TONE_DB_VALUES, looseMatch=True), ignore_error=False)
                if (bass is not None):
                    toneBass = await self.send_command("set_tone_bass", zone, self._get_parameter_key_from_value(str(bass), PARAM_TONE_DB_VALUES, looseMatch=True), ignore_error=False)
            
            ## Only return true if all responses were true
            if toneResponse and toneBass and toneTreble:
                return True
            else:
                return False
    
    async def set_video_settings(self, video_converter: bool=None, resolution: str=None, pure_cinema: str=None, prog_motion: int=None, stream_smoother: str=None, advanced_video_adjust: str=None, ynr: int=None, cnr: int=None, bnr: int=None, mnr: int=None, detail: int=None, sharpness: int=None, brightness: int=None, contrast: int=None, hue: int=None, chroma: int=None, black: bool=None, aspect: str=None, zone="1"):
        """Set video settings for a given zone using provided parameters."""
        self._check_zone(zone)
        ## This is a complex function and supports handles requests to update any video related parameters

        ## FUNC: VIDEO CONVERTER - 0 = OFF, 1 = ON
        if (self.video.get(zone).get("converter") is not None and video_converter is not None):
            await self.send_command("set_video_converter", zone, str(int(video_converter)), ignore_error=False)

        ## FUNC: RESOLUTION (use PARAM_VIDEO_RESOLUTIONS)
        if (self.video.get(zone).get("resolution") is not None and resolution is not None):
            await self.send_command("set_video_resolution", zone, self._get_parameter_key_from_value(resolution, PARAM_VIDEO_RESOLUTION_MODES), ignore_error=False)

        ## FUNC: PURE CINEMA
        if (self.video.get(zone).get("pure_cinema") is not None and pure_cinema is not None):
            await self.send_command("set_pure_cinema_status", zone, self._get_parameter_key_from_value(pure_cinema, PARAM_VIDEO_PURE_CINEMA_MODES), ignore_error=False)

        ## FUNC: PROG. MOTION
        if (self.video.get(zone).get("prog_motion") is not None and prog_motion is not None):
            ## parameter 0 = 50, so add 50
            prog_motion += 50
            await self.send_command("set_prog_motion_status", zone, str(prog_motion), ignore_error=False)

        ## FUNC: STREAM SMOOTHER (use PARAM_VIDEO_STREAM_SMOOTHER_MODES)
        if (self.video.get(zone).get("stream_smoother") is not None and stream_smoother is not None):
            await self.send_command("set_stream_smoother", zone, self._get_parameter_key_from_value(stream_smoother, PARAM_VIDEO_STREAM_SMOOTHER_MODES), ignore_error=False)
        
        ## FUNC: ADVANCED VIDEO ADJUST (use PARAM_ADVANCED_VIDEO_ADJUST_MODES)
        if (self.video.get(zone).get("advanced_video_adjust") is not None and advanced_video_adjust is not None):
            await self.send_command("set_advanced_video_adjust", zone, self._get_parameter_key_from_value(advanced_video_adjust, PARAM_ADVANCED_VIDEO_ADJUST_MODES), ignore_error=False)

        ## FUNC: YNR
        if (self.video.get(zone).get("ynr") is not None and ynr is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_ynr", zone, str(ynr + 50), ignore_error=False)

        ## FUNC: CNR
        if (self.video.get(zone).get("cnr") is not None and cnr is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_cnr", zone, str(cnr + 50), ignore_error=False)

        ## FUNC: BNR
        if (self.video.get(zone).get("bnr") is not None and bnr is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_bnr", zone, str(bnr + 50), ignore_error=False)

        ## FUNC: MNR
        if (self.video.get(zone).get("mnr") is not None and mnr is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_mnr", zone, str(mnr + 50), ignore_error=False)

        ## FUNC: DETAIL
        if (self.video.get(zone).get("detail") is not None and detail is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_detail", zone, str(detail + 50), ignore_error=False)

        ## FUNC: SHARPNESS
        if (self.video.get(zone).get("sharpness") is not None and sharpness is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_sharpness", zone, str(sharpness + 50), ignore_error=False)

        ## FUNC: BRIGHTNESS
        if (self.video.get(zone).get("brightness") is not None and brightness is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_brightness", zone, str(brightness + 50), ignore_error=False)

        ## FUNC: CONTRAST
        if (self.video.get(zone).get("contrast") is not None and contrast is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_contrast", zone, str(contrast + 50), ignore_error=False)

        ## FUNC: HUE
        if (self.video.get(zone).get("hue") is not None and hue is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_hue", zone, str(hue + 50), ignore_error=False)

        ## FUNC: CHROMA
        if (self.video.get(zone).get("chroma") is not None and chroma is not None):
            ## parameter 0 = 50, so add 50
            await self.send_command("set_chroma", zone, str(chroma + 50), ignore_error=False)

        ## FUNC: BLACK SETUP (0 = 0, 1 = 7.5)
        if (self.video.get(zone).get("black_setup") is not None and black is not None):
            await self.send_command("set_chroma", zone, str(int(black)), ignore_error=False)

        ## FUNC: ASPECT (use PARAM_VIDEO_ASPECT_MODES)
        if (self.video.get(zone).get("aspect") is not None and aspect is not None):
            await self.send_command("set_aspect", zone, str(self._get_parameter_key_from_value(aspect, PARAM_VIDEO_ASPECT_MODES)), ignore_error=False)

        return True

    async def set_amp_settings(self, speaker_config: str=None, hdmi_out: str=None, hdmi_audio_output: bool=None, pqls: bool=None, amp: str=None, zone="1"):
        """Set AMP function settings for a given zone."""
        self._check_zone(zone)

        ## FUNC: SPEAKERS (use PARAM_SPEAKER_MODES)
        if (self.speakers.get(zone) is not None and speaker_config is not None):
            await self.send_command("set_speaker_status", zone, self._get_parameter_key_from_value(speaker_config, PARAM_SPEAKER_MODES), ignore_error=False)

        ## FUNC: HDMI OUTPUT SELECT (use PARAM_HDMI_OUT_MODES)
        if (self.hdmi_out.get(zone) is not None and hdmi_out is not None):
            await self.send_command("set_hdmi_out_status", zone, self._get_parameter_key_from_value(hdmi_out, PARAM_HDMI_OUT_MODES), ignore_error=False)

        ## FUNC: HDMI AUDIO (simple bool, True is on, otherwise audio only goes to amp)
        if (self.hdmi_audio.get(zone) is not None and hdmi_audio_output is not None):
            await self.send_command("set_hdmi_audio_status", zone, str(int(hdmi_audio_output)), ignore_error=False)

        ## FUNC: PQLS (simple bool, True is auto, False is off)
        if (self.pqls.get(zone) is not None and pqls is not None):
            await self.send_command("set_pqls_status", zone, str(int(pqls)), ignore_error=False)

        ## FUNC: AMP (use PARAM_AMP_MODES)
        if (self.amp.get(zone) is not None and amp is not None):
            await self.send_command("set_amp", zone, self._get_parameter_key_from_value(amp, PARAM_AMP_MODES), ignore_error=False)

    async def set_tuner_frequency(self, band: str, frequency: float, zone="1"):
        """Sets the tuner frequency and band."""

        if ((self.tuner_band.get(zone) is None) or (self.power.get(zone) == False)):
            raise SystemError(f"Tuner functions are currently not available. Ensure Main Zone is on and source is set to tuner.")
        
        if (band.upper() != "AM" and band.upper() != "FM"):
            raise ValueError(f"The provided band is invalid")

        if (band.upper() == "AM" and self.tuner_band.get(zone) == "F"):
            band = "A"
            ## Set the tuner band
            await self.send_command("set_tuner_band_am", zone, ignore_error=False)
        elif (band.upper() == "FM" and self.tuner_band.get(zone) == "A"):
            band = "F"
            ## Set the tuner band
            await self.send_command("set_tuner_band_fm", zone, ignore_error=False)

        ## Round the frequency to nearest 0.05 if band is FM, otherwise divide frequency by 9 using modf so that the remainder is split out, then select the whole number response and times by 9
        if (band.upper() == "FM"):
            frequency = round(0.05 * round(frequency/0.05), 2)
        elif (band.upper() == "AM"):
            frequency = (math.modf(frequency/9)[1])*9

        resp = True

        ## Continue adjusting until frequency is set
        while (True):
            to_freq = (str(frequency))
            current_freq = (str(self.tuner_frequency.get(zone)))

            if to_freq == current_freq:
                break

            ## Decrease frequency
            if (self.tuner_frequency.get(zone) > frequency):
                resp = await self.send_command("decrease_tuner_frequency", ignore_error=False)
            else:
                resp = await self.send_command("increase_tuner_frequency")

            if (resp == False):
                ## On error, exit loop
                break
        
        if resp:
            return True
        else:
            return False

    async def set_channel_levels(self, channel: str, level: float, zone="1"):
        """Sets the level(gain) of each amplifier channel."""
        self._check_zone(zone)

        if self.channel_levels.get(zone) is not None:
            ## Check the channel exists
            if self.channel_levels.get(zone).get(channel.upper()) is not None:
                ## Append underscores depending on length
                if len(channel) == 1:
                    channel = channel + "__"
                elif len(channel) == 2:
                    channel = channel + "_"

                ## convert the float to correct int
                level = int((level*2)+50)
                return await self.send_command("set_channel_levels", zone, channel + str(level), ignore_error=False)
            else:
                raise ValueError(f"The provided channel is invalid ({channel}, {str(level)} for zone {zone}")
        else:
            raise ValueError(f"Invalid zone {zone}")

    async def set_dsp_settings(self, **arguments):
        """Sets the DSP settings for the amplifier."""
        zone = arguments.get("zone")
        self._check_zone(zone)
        ## Get current DSP settings
        zone_dsp_settings: dict = self.dsp.get(zone)

        if zone_dsp_settings == None:
            raise ValueError(f"Invalid zone {zone}")

        for arg in arguments:
            if arg != "zone":
                if arguments.get(arg) is not None:
                    if zone_dsp_settings.get(arg) is not arguments.get(arg):
                        if type(arguments.get(arg)) == str:
                            ## Functions to do a lookup here
                            if arg == "phase_control":
                                arguments[arg] = self._get_parameter_key_from_value(arguments.get(arg), PARAM_DSP_PHASE_CONTROL)
                            elif arg == "signal_select":
                                arguments[arg] = self._get_parameter_key_from_value(arguments.get(arg), PARAM_DSP_SIGNAL_SELECT)
                            elif arg == "digital_dialog_enhancement":
                                arguments[arg] = self._get_parameter_key_from_value(arguments.get(arg), PARAM_DSP_DIGITAL_DIALOG_ENHANCEMENT)
                            elif arg == "dual_mono":
                                arguments[arg] = self._get_parameter_key_from_value(arguments.get(arg), PARAM_DSP_DUAL_MONO)
                            elif arg == "drc":
                                arguments[arg] = self._get_parameter_key_from_value(arguments.get(arg), PARAM_DSP_DRC)
                            elif arg == "height_gain":
                                arguments[arg] = self._get_parameter_key_from_value(arguments.get(arg), PARAM_DSP_HEIGHT_GAIN)
                            elif arg == "virtual_depth":
                                arguments[arg] = self._get_parameter_key_from_value(arguments.get(arg), PARAM_DSP_VIRTUAL_DEPTH)
                            elif arg == "digital_filter":
                                arguments[arg] = self._get_parameter_key_from_value(arguments.get(arg), PARAM_DSP_DIGITAL_FILTER)
                        elif type(arguments.get(arg)) == bool:
                            arguments[arg] = str(int(arguments.get(arg)))
                        elif type(arguments.get(arg)) == float:
                            if arg == "sound_delay":
                                arguments[arg] = str(int(float(arguments.get(arg)) * 10)).zfill(3)
                            elif arg == "center_image":
                                arguments[arg] = str(int(arguments.get(arg)) * 10).zfill(2)
                        elif type(arguments.get(arg) == int):
                            if arg == "lfe_att":
                                arguments[arg] = int((-20/5)*-1)
                            elif arg == "dimension": 
                                arguments[arg] = arguments.get(arg)+50
                            elif arg == "effect":
                                arguments[arg] = str(arguments.get(arg)/10).zfill(2)
                            elif arg == "phase_control_plus":
                                arguments[arg] = str(arguments.get(arg)).zfill(2)
                            elif arg == "center_width":
                                arguments[arg] = str(arguments.get(arg)).zfill(2)

                        await self.send_command("set_" + arg, zone, str(arguments.get(arg)), ignore_error=False)