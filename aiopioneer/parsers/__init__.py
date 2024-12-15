"""aiopioneer parsing classes and functions."""

from collections.abc import Callable
import logging

from ..const import Zones
from ..param import PioneerAVRParams
from ..properties import PioneerAVRProperties
from .response import Response
from .system import SystemParsers
from .audio import AudioParsers
from .tuner import TunerParsers
from .dsp import DspParsers
from .information import InformationParsers
from .video import VideoParsers
from .settings import SettingsParsers

_LOGGER = logging.getLogger(__name__)

RESPONSE_DATA = [
    ["PWR", SystemParsers.power, Zones.Z1],
    ["APR", SystemParsers.power, Zones.Z2],
    ["BPR", SystemParsers.power, Zones.Z3],
    ["ZEP", SystemParsers.power, Zones.HDZ],
    ["FN", SystemParsers.input_source, Zones.Z1],
    ["Z2F", SystemParsers.input_source, Zones.Z2],
    ["Z3F", SystemParsers.input_source, Zones.Z3],
    ["ZEA", SystemParsers.input_source, Zones.HDZ],
    ["VOL", SystemParsers.volume, Zones.Z1],
    ["ZV", SystemParsers.volume, Zones.Z2],
    ["YV", SystemParsers.volume, Zones.Z3],
    ["XV", SystemParsers.volume, Zones.HDZ],
    ["MUT", SystemParsers.mute, Zones.Z1],
    ["Z2MUT", SystemParsers.mute, Zones.Z2],
    ["Z3MUT", SystemParsers.mute, Zones.Z3],
    ["HZMUT", SystemParsers.mute, Zones.HDZ],
    ["SPK", SystemParsers.speaker_modes, Zones.ALL],
    ["HO", SystemParsers.hdmi_out, Zones.ALL],
    ["HA", SystemParsers.hdmi_audio, Zones.ALL],
    ["PQ", SystemParsers.pqls, Zones.ALL],
    ["SAA", SystemParsers.dimmer, Zones.ALL],
    ["SAB", SystemParsers.sleep, Zones.ALL],
    ["SAC", SystemParsers.amp_status, Zones.ALL],
    ["PKL", SystemParsers.panel_lock, Zones.ALL],
    ["RML", SystemParsers.remote_lock, Zones.ALL],
    ["SSF", SystemParsers.speaker_system, Zones.ALL],
    ["RGB", SystemParsers.input_name, Zones.ALL],
    ["SVB", SystemParsers.mac_address, Zones.ALL],
    ["RGD", SystemParsers.avr_model, Zones.ALL],
    ["SSI", SystemParsers.software_version, Zones.ALL],
    ##
    ["AUA", SystemParsers.audio_parameter_prohibitation, Zones.Z1],
    ["AUB", SystemParsers.audio_parameter_working, Zones.Z1],
    ##
    ["SSL", SettingsParsers.home_menu_status, Zones.ALL],
    ["SSJ", SettingsParsers.mcacc_diagnostic_status, Zones.ALL],
    ["SUU", SettingsParsers.standing_wave_setting, Zones.ALL],
    ["SUV", SettingsParsers.standing_wave_sw_trim, Zones.ALL],
    ["SSP", SettingsParsers.surround_position, Zones.ALL],
    ["SSQ", SettingsParsers.x_over, Zones.ALL],
    ["SST", SettingsParsers.x_curve, Zones.ALL],
    ["SSU", SettingsParsers.loudness_plus, Zones.ALL],
    ["SSV", SettingsParsers.sbch_processing, Zones.ALL],
    ["SSG", SettingsParsers.speaker_setting, Zones.ALL],
    ["ILA", SettingsParsers.input_level_adjust, Zones.ALL],
    ["SSS", SettingsParsers.speaker_distance_mcacc, Zones.ALL],
    ["SSW", SettingsParsers.thx_ultraselect2_sw, Zones.ALL],
    ["SSX", SettingsParsers.boundary_gain_compression, Zones.ALL],
    ["SSB", SettingsParsers.re_equalization, Zones.ALL],
    ["SSE", SettingsParsers.osd_language, Zones.ALL],
    ["STA", SettingsParsers.dhcp, Zones.ALL],
    ["STG", SettingsParsers.proxy_enabled, Zones.ALL],
    ["STJ", SettingsParsers.network_standby, Zones.ALL],
    ["SSO", SettingsParsers.friendly_name, Zones.ALL],
    ["STK", SettingsParsers.parental_lock, Zones.ALL],
    ["STL", SettingsParsers.parental_lock_password, Zones.ALL],
    ["SUM", SettingsParsers.port_numbers, Zones.ALL],
    ["STQ", SettingsParsers.hdmi_control, Zones.ALL],
    ["STR", SettingsParsers.hdmi_control_mode, Zones.ALL],
    ["STT", SettingsParsers.hdmi_arc, Zones.ALL],
    ["SVL", SettingsParsers.pqls_for_backup, Zones.ALL],
    ["STU", SettingsParsers.standby_passthrough, Zones.ALL],
    ["STV", SettingsParsers.external_hdmi_trigger, Zones.ALL],
    ["STW", SettingsParsers.external_hdmi_trigger, Zones.ALL],
    ["STX", SettingsParsers.speaker_b_link, Zones.ALL],
    ["SVA", SettingsParsers.osd_overlay, Zones.ALL],
    ["ADS", SettingsParsers.additional_service, Zones.ALL],
    ["SUT", SettingsParsers.user_lock, Zones.ALL],
    ##
    ["CLV", AudioParsers.channel_levels, Zones.Z1],
    ["ZGE", AudioParsers.channel_levels, Zones.Z2],
    ["ZHE", AudioParsers.channel_levels, Zones.Z3],
    ["SR", AudioParsers.listening_mode, Zones.ALL],
    ["TO", AudioParsers.tone, Zones.Z1],
    ["BA", AudioParsers.tone_bass, Zones.Z1],
    ["TR", AudioParsers.tone_treble, Zones.Z1],
    ["ZGA", AudioParsers.tone, Zones.Z2],
    ["ZGB", AudioParsers.tone_bass, Zones.Z2],
    ["ZGC", AudioParsers.tone_treble, Zones.Z2],
    ##
    ["FRF", TunerParsers.frequency_fm, Zones.ALL],
    ["FRA", TunerParsers.frequency_am, Zones.ALL],
    ["PR", TunerParsers.preset, Zones.ALL],
    ["SUQ", TunerParsers.am_frequency_step, Zones.ALL],
    ##
    ["MC", DspParsers.mcacc_setting, Zones.ALL],
    ["IS", DspParsers.phasecontrol, Zones.ALL],
    ["VSP", DspParsers.virtual_speakers, Zones.ALL],
    ["VSB", DspParsers.virtual_soundback, Zones.ALL],
    ["VHT", DspParsers.virtual_height, Zones.ALL],
    ["SDA", DspParsers.signal_select, Zones.ALL],
    ["SDB", DspParsers.input_att, Zones.ALL],
    ["ATA", DspParsers.sound_retriever, Zones.ALL],
    ["ATC", DspParsers.equalizer, Zones.ALL],
    ["ATD", DspParsers.standing_wave, Zones.ALL],
    ["ATE", DspParsers.phase_control_plus, Zones.ALL],
    ["ATF", DspParsers.sound_delay, Zones.ALL],
    ["ATG", DspParsers.digital_noise_reduction, Zones.ALL],
    ["ATH", DspParsers.dialog_enhancement, Zones.ALL],
    ["ATI", DspParsers.hi_bit, Zones.ALL],
    ["ATJ", DspParsers.dual_mono, Zones.ALL],
    ["ATK", DspParsers.fixed_pcm, Zones.ALL],
    ["ATL", DspParsers.dynamic_range_control, Zones.ALL],
    ["ATM", DspParsers.lfe_attenuator, Zones.ALL],
    ["ATN", DspParsers.sacd_gain, Zones.ALL],
    ["ATO", DspParsers.auto_delay, Zones.ALL],
    ["ATP", DspParsers.center_width, Zones.ALL],
    ["ATQ", DspParsers.panorama, Zones.ALL],
    ["ATR", DspParsers.dimension, Zones.ALL],
    ["ATS", DspParsers.center_image, Zones.ALL],
    ["ATT", DspParsers.effect, Zones.ALL],
    ["ATU", DspParsers.height_gain, Zones.ALL],
    ["ATV", DspParsers.digital_filter, Zones.ALL],
    ["ATW", DspParsers.loudness_management, Zones.ALL],
    ["ATY", DspParsers.audio_scaler, Zones.ALL],
    ["ATZ", DspParsers.up_sampling, Zones.ALL],
    ["ARA", DspParsers.center_spread, Zones.ALL],
    ["VDP", DspParsers.virtual_depth, Zones.ALL],
    ["VWD", DspParsers.virtual_wide, Zones.ALL],
    ["ARB", DspParsers.rendering_mode, Zones.ALL],
    ##
    ["AST", InformationParsers.audio_information, Zones.ALL],
    ["VST", InformationParsers.video_information, Zones.ALL],
    ["FL", InformationParsers.device_display_information, Zones.ALL],
    ##
    ["VTB", VideoParsers.video_converter, Zones.Z1],
    ["VTC", VideoParsers.video_resolution, Zones.Z1],
    ["VTD", VideoParsers.pure_cinema, Zones.Z1],
    ["VTE", VideoParsers.prog_motion, Zones.Z1],
    ["VTF", VideoParsers.stream_smoother, Zones.Z1],
    ["VTG", VideoParsers.advanced_video_adjust, Zones.Z1],
    ["VTH", VideoParsers.output_ynr, Zones.Z1],
    ["VTI", VideoParsers.output_cnr, Zones.Z1],
    ["VTJ", VideoParsers.output_bnr, Zones.Z1],
    ["VTK", VideoParsers.output_mnr, Zones.Z1],
    ["VTL", VideoParsers.output_detail, Zones.Z1],
    ["VTM", VideoParsers.output_sharpness, Zones.Z1],
    ["VTN", VideoParsers.output_brightness, Zones.Z1],
    ["VTO", VideoParsers.output_contrast, Zones.Z1],
    ["VTP", VideoParsers.output_hue, Zones.Z1],
    ["VTQ", VideoParsers.output_chroma, Zones.Z1],
    ["VTR", VideoParsers.black_setup, Zones.Z1],
    ["VTS", VideoParsers.aspect, Zones.Z1],
]


def _process_response(properties: PioneerAVRProperties, response: Response) -> None:
    """Process a parsed response."""
    current_base = current_value = None
    if response.base_property is not None:
        current_base = current_value = getattr(properties, response.base_property)
        is_global = response.zone in [Zones.ALL, None]
        if response.property_name is None and not is_global:
            current_value = current_base.get(response.zone)
            if current_value != response.value:
                current_base[response.zone] = response.value
                setattr(properties, response.base_property, current_base)
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
                current_base[response.zone][response.property_name] = response.value
                setattr(properties, response.base_property, current_base)
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
                setattr(properties, response.base_property, response.value)
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
                setattr(properties, response.base_property, current_base)
                _LOGGER.info(
                    "Global: %s.%s: %s -> %s (%s)",
                    response.base_property,
                    response.property_name,
                    current_value,
                    response.value,
                    response.raw,
                )


def process_raw_response(
    raw_resp: str, params: PioneerAVRParams, properties: PioneerAVRProperties
) -> tuple[set[Zones], list[str]]:
    """Processes a raw response and looks up required functions from RESPONSE_DATA."""
    match_resp = next((r for r in RESPONSE_DATA if raw_resp.startswith(r[0])), None)
    if not match_resp:
        ## No error handling as not all responses have been captured by aiopioneer.
        # _LOGGER.debug("unparsed raw response ignored: %s", raw_resp)
        return [], []

    parse_cmd: str = match_resp[0]
    parse_func: Callable[[str, PioneerAVRParams, Zones, str], Response] = match_resp[1]
    parse_zone: Zones = match_resp[2]
    responses: list[Response] = parse_func(
        raw_resp[len(parse_cmd) :], params, zone=parse_zone, command=parse_cmd
    )

    ## Parse responses and update properties
    updated_zones: set[Zones] = set()
    command_queue: list[str] = []
    for response in responses:
        _process_response(properties, response)
        if response.zone is not None:
            updated_zones.add(response.zone)
        if response.command_queue:
            command_queue.extend(response.command_queue)

    return updated_zones, command_queue
