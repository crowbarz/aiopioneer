"""aiopioneer parsing classes and functions."""

from types import FunctionType
import logging

from ..const import Zone, AVRCodeMapBase, AVRCodeIntMap
from ..exceptions import AVRResponseParseError
from ..params import PioneerAVRParams
from ..properties import PioneerAVRProperties
from .response import Response
from .system import (
    SystemParsers,
    SpeakerModes,
    HDMIOutModes,
    HDMIAudioModes,
    PQLSModes,
    DimmerModes,
    AMPModes,
    PanelLock,
)
from .audio import AudioParsers
from .tuner import TunerParsers
from .dsp import DspParsers
from .information import InformationParsers
from .video import VideoParsers
from .settings import SettingsParsers

_LOGGER = logging.getLogger(__name__)

RESPONSE_DATA = [
    ["PWR", SystemParsers.power, Zone.Z1],
    ["APR", SystemParsers.power, Zone.Z2],
    ["BPR", SystemParsers.power, Zone.Z3],
    ["ZEP", SystemParsers.power, Zone.HDZ],
    ["FN", SystemParsers.input_source, Zone.Z1],
    ["Z2F", SystemParsers.input_source, Zone.Z2],
    ["Z3F", SystemParsers.input_source, Zone.Z3],
    ["ZEA", SystemParsers.input_source, Zone.HDZ],
    ["VOL", AVRCodeIntMap, Zone.Z1, "volume"],
    ["ZV", AVRCodeIntMap, Zone.Z2, "volume"],
    ["YV", AVRCodeIntMap, Zone.Z3, "volume"],
    ["XV", AVRCodeIntMap, Zone.HDZ, "volume"],
    ["MUT", SystemParsers.mute, Zone.Z1],
    ["Z2MUT", SystemParsers.mute, Zone.Z2],
    ["Z3MUT", SystemParsers.mute, Zone.Z3],
    ["HZMUT", SystemParsers.mute, Zone.HDZ],
    ["SPK", SpeakerModes, Zone.ALL, "amp", "speakers"],
    ["HO", HDMIOutModes, Zone.ALL, "amp", "hdmi_out"],
    ["HA", HDMIAudioModes, Zone.ALL, "amp", "hdmi_audio"],
    ["PQ", PQLSModes, Zone.ALL, "amp", "pqls"],
    ["SAA", DimmerModes, Zone.ALL, "amp", "dimmer"],
    ["SAB", AVRCodeIntMap, Zone.ALL, "amp", "sleep"],
    ["SAC", AMPModes, Zone.ALL, "amp", "status"],
    ["PKL", PanelLock, Zone.ALL, "amp", "panel_lock"],
    ["RML", AVRCodeMapBase, Zone.ALL, "amp", "remote_lock"],  ## TODO: add code map
    ["SSF", SystemParsers.speaker_system, Zone.ALL],
    ["RGB", SystemParsers.input_name, Zone.ALL],
    ["SVB", SystemParsers.mac_address, Zone.ALL],
    ["RGD", SystemParsers.avr_model, Zone.ALL],
    ["SSI", SystemParsers.software_version, Zone.ALL],
    ["AUA", SystemParsers.audio_parameter_prohibitation, Zone.Z1],
    ["AUB", SystemParsers.audio_parameter_working, Zone.Z1],
    ##
    ["SSL", SettingsParsers.home_menu_status, Zone.ALL],
    ["SSJ", SettingsParsers.mcacc_diagnostic_status, Zone.ALL],
    ["SUU", SettingsParsers.standing_wave_setting, Zone.ALL],
    ["SUV", SettingsParsers.standing_wave_sw_trim, Zone.ALL],
    ["SSP", SettingsParsers.surround_position, Zone.ALL],
    ["SSQ", SettingsParsers.x_over, Zone.ALL],
    ["SST", SettingsParsers.x_curve, Zone.ALL],
    ["SSU", SettingsParsers.loudness_plus, Zone.ALL],
    ["SSV", SettingsParsers.sbch_processing, Zone.ALL],
    ["SSG", SettingsParsers.speaker_setting, Zone.ALL],
    ["ILA", SettingsParsers.input_level_adjust, Zone.ALL],
    ["SSS", SettingsParsers.speaker_distance_mcacc, Zone.ALL],
    ["SSW", SettingsParsers.thx_ultraselect2_sw, Zone.ALL],
    ["SSX", SettingsParsers.boundary_gain_compression, Zone.ALL],
    ["SSB", SettingsParsers.re_equalization, Zone.ALL],
    ["SSE", SettingsParsers.osd_language, Zone.ALL],
    ["STA", SettingsParsers.dhcp, Zone.ALL],
    ["STG", SettingsParsers.proxy_enabled, Zone.ALL],
    ["STJ", SettingsParsers.network_standby, Zone.ALL],
    ["SSO", SettingsParsers.friendly_name, Zone.ALL],
    ["STK", SettingsParsers.parental_lock, Zone.ALL],
    ["STL", SettingsParsers.parental_lock_password, Zone.ALL],
    ["SUM", SettingsParsers.port_numbers, Zone.ALL],
    ["STQ", SettingsParsers.hdmi_control, Zone.ALL],
    ["STR", SettingsParsers.hdmi_control_mode, Zone.ALL],
    ["STT", SettingsParsers.hdmi_arc, Zone.ALL],
    ["SVL", SettingsParsers.pqls_for_backup, Zone.ALL],
    ["STU", SettingsParsers.standby_passthrough, Zone.ALL],
    ["STV", SettingsParsers.external_hdmi_trigger, Zone.ALL],
    ["STW", SettingsParsers.external_hdmi_trigger, Zone.ALL],
    ["STX", SettingsParsers.speaker_b_link, Zone.ALL],
    ["SVA", SettingsParsers.osd_overlay, Zone.ALL],
    ["ADS", SettingsParsers.additional_service, Zone.ALL],
    ["SUT", SettingsParsers.user_lock, Zone.ALL],
    ##
    ["CLV", AudioParsers.channel_levels, Zone.Z1],
    ["ZGE", AudioParsers.channel_levels, Zone.Z2],
    ["ZHE", AudioParsers.channel_levels, Zone.Z3],
    ["SR", AudioParsers.listening_mode, Zone.ALL],
    ["TO", AudioParsers.tone, Zone.Z1],
    ["BA", AudioParsers.tone_bass, Zone.Z1],
    ["TR", AudioParsers.tone_treble, Zone.Z1],
    ["ZGA", AudioParsers.tone, Zone.Z2],
    ["ZGB", AudioParsers.tone_bass, Zone.Z2],
    ["ZGC", AudioParsers.tone_treble, Zone.Z2],
    ##
    ["FRF", TunerParsers.frequency_fm, Zone.ALL],
    ["FRA", TunerParsers.frequency_am, Zone.ALL],
    ["PR", TunerParsers.preset, Zone.ALL],
    ["SUQ", TunerParsers.am_frequency_step, Zone.ALL],
    ##
    ["MC", DspParsers.mcacc_setting, Zone.ALL],
    ["IS", DspParsers.phasecontrol, Zone.ALL],
    ["VSP", DspParsers.virtual_speakers, Zone.ALL],
    ["VSB", DspParsers.virtual_soundback, Zone.ALL],
    ["VHT", DspParsers.virtual_height, Zone.ALL],
    ["SDA", DspParsers.signal_select, Zone.ALL],
    ["SDB", DspParsers.input_att, Zone.ALL],
    ["ATA", DspParsers.sound_retriever, Zone.ALL],
    ["ATC", DspParsers.equalizer, Zone.ALL],
    ["ATD", DspParsers.standing_wave, Zone.ALL],
    ["ATE", DspParsers.phase_control_plus, Zone.ALL],
    ["ATF", DspParsers.sound_delay, Zone.ALL],
    ["ATG", DspParsers.digital_noise_reduction, Zone.ALL],
    ["ATH", DspParsers.dialog_enhancement, Zone.ALL],
    ["ATI", DspParsers.hi_bit, Zone.ALL],
    ["ATJ", DspParsers.dual_mono, Zone.ALL],
    ["ATK", DspParsers.fixed_pcm, Zone.ALL],
    ["ATL", DspParsers.dynamic_range_control, Zone.ALL],
    ["ATM", DspParsers.lfe_attenuator, Zone.ALL],
    ["ATN", DspParsers.sacd_gain, Zone.ALL],
    ["ATO", DspParsers.auto_delay, Zone.ALL],
    ["ATP", DspParsers.center_width, Zone.ALL],
    ["ATQ", DspParsers.panorama, Zone.ALL],
    ["ATR", DspParsers.dimension, Zone.ALL],
    ["ATS", DspParsers.center_image, Zone.ALL],
    ["ATT", DspParsers.effect, Zone.ALL],
    ["ATU", DspParsers.height_gain, Zone.ALL],
    ["ATV", DspParsers.digital_filter, Zone.ALL],
    ["ATW", DspParsers.loudness_management, Zone.ALL],
    ["ATY", DspParsers.audio_scaler, Zone.ALL],
    ["ATZ", DspParsers.up_sampling, Zone.ALL],
    ["ARA", DspParsers.center_spread, Zone.ALL],
    ["VDP", DspParsers.virtual_depth, Zone.ALL],
    ["VWD", DspParsers.virtual_wide, Zone.ALL],
    ["ARB", DspParsers.rendering_mode, Zone.ALL],
    ##
    ["AST", InformationParsers.audio_information, Zone.ALL],
    ["VST", InformationParsers.video_information, Zone.ALL],
    ["FL", InformationParsers.device_display_information, Zone.ALL],
    ##
    ["VTB", VideoParsers.video_converter, Zone.Z1],
    ["VTC", VideoParsers.video_resolution, Zone.Z1],
    ["VTD", VideoParsers.pure_cinema, Zone.Z1],
    ["VTE", VideoParsers.prog_motion, Zone.Z1],
    ["VTF", VideoParsers.stream_smoother, Zone.Z1],
    ["VTG", VideoParsers.advanced_video_adjust, Zone.Z1],
    ["VTH", VideoParsers.output_ynr, Zone.Z1],
    ["VTI", VideoParsers.output_cnr, Zone.Z1],
    ["VTJ", VideoParsers.output_bnr, Zone.Z1],
    ["VTK", VideoParsers.output_mnr, Zone.Z1],
    ["VTL", VideoParsers.output_detail, Zone.Z1],
    ["VTM", VideoParsers.output_sharpness, Zone.Z1],
    ["VTN", VideoParsers.output_brightness, Zone.Z1],
    ["VTO", VideoParsers.output_contrast, Zone.Z1],
    ["VTP", VideoParsers.output_hue, Zone.Z1],
    ["VTQ", VideoParsers.output_chroma, Zone.Z1],
    ["VTR", VideoParsers.black_setup, Zone.Z1],
    ["VTS", VideoParsers.aspect, Zone.Z1],
    ["VTT", VideoParsers.super_resolution, Zone.Z1],
]


def _process_response(properties: PioneerAVRProperties, response: Response) -> None:
    """Process a parsed response."""
    current_base = current_value = None

    if response.base_property is None:
        return

    if response.base_property.startswith("_"):
        match response.base_property:
            case "_clear_source_id":
                properties.clear_source_id(response.value)
                return
            case "_get_source_name":
                response.base_property = "source_name"
                response.value = properties.get_source_name(response.value)

    current_base = current_value = getattr(properties, response.base_property)
    is_global = response.zone in [Zone.ALL, None]
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
) -> tuple[set[Zone], list[str]]:
    """Processes a raw response and looks up required functions from RESPONSE_DATA."""
    try:
        match_resp = next((r for r in RESPONSE_DATA if raw_resp.startswith(r[0])), None)
        if not match_resp:
            ## No error handling as not all responses have been captured by aiopioneer.
            if not raw_resp.startswith("E"):
                _LOGGER.debug("unparsed raw response: %s", raw_resp)
            return [], []

        parse_cmd: str = match_resp[0]
        parse_func = match_resp[1]
        parse_zone: Zone = match_resp[2]
        raw = raw_resp[len(parse_cmd) :]
        responses: list[Response] = []
        if isinstance(parse_func, FunctionType):
            responses = parse_func(raw, params, zone=parse_zone, command=parse_cmd)
        elif issubclass(parse_func, AVRCodeMapBase):
            responses = [
                Response(
                    raw=raw,
                    response_command=parse_cmd,
                    base_property=match_resp[3],
                    property_name=match_resp[4] if len(match_resp) >= 5 else None,
                    zone=parse_zone,
                    value=parse_func[raw],
                    queue_commands=None,
                )
            ]
        else:
            raise RuntimeError(f"Invalid parser {parse_func} for response: {raw}")
    except Exception as exc:  # pylint: disable=broad-except
        raise AVRResponseParseError(response=raw_resp, exc=exc) from exc

    ## Parse responses and update properties
    updated_zones: set[Zone] = set()
    command_queue: list[str] = []
    for response in responses:
        _process_response(properties, response)
        if response.zone is not None:
            updated_zones.add(response.zone)
        if response.command_queue:
            command_queue.extend(response.command_queue)

    return updated_zones, command_queue
