"""aiopioneer parse response."""

from types import FunctionType
import logging

from ..const import Zone
from ..exceptions import AVRResponseParseError
from ..params import PioneerAVRParams
from ..properties import PioneerAVRProperties
from .audio import AudioParsers, ToneModes, ToneDb
from .code_map import (
    CodeMapBase,
    CodeBoolMap,
    CodeIntMap,
    CodeInverseBoolMap,
)
from .dsp import (
    DspMcaccMemorySet,
    DspPhaseControl,
    DspSignalSelect,
    DspPhaseControlPlus,
    DspSoundDelay,
    DspAutoManual,
    DspDialogEnhancement,
    DspDualMono,
    DspDynamicRange,
    DspLfeAttenuator,
    DspSacdGain,
    DspCenterWidth,
    DspDimension,
    DspCenterImage,
    DspEffect,
    DspHeightGain,
    DspDigitalFilter,
    DspUpSampling,
    DspVirtualDepth,
    DspRenderingMode,
)
from .information import InformationParsers, DisplayText
from .response import Response
from .settings import (
    SettingsParsers,
    SurroundPosition,
    XOver,
    XCurve,
    SbchProcessing,
    OsdLanguages,
    StandbyPassthrough,
)
from .system import (
    SystemParsers,
    SpeakerModes,
    HdmiOutModes,
    HdmiAudioModes,
    PqlsModes,
    DimmerModes,
    AmpModes,
    PanelLock,
)
from .tuner import TunerParsers
from .video import (
    VideoInt08Map,
    VideoProgMotion,
    VideoInt66Map,
    VideoResolutionModes,
    VideoPureCinemaModes,
    VideoStreamSmootherModes,
    AdvancedVideoAdjustModes,
    VideoAspectModes,
    VideoSuperResolution,
)

_LOGGER = logging.getLogger(__name__)

RESPONSE_DATA = [
    ## system
    ["PWR", SystemParsers.power, Zone.Z1],
    ["APR", SystemParsers.power, Zone.Z2],
    ["BPR", SystemParsers.power, Zone.Z3],
    ["ZEP", SystemParsers.power, Zone.HDZ],
    ["FN", SystemParsers.input_source, Zone.Z1],
    ["Z2F", SystemParsers.input_source, Zone.Z2],
    ["Z3F", SystemParsers.input_source, Zone.Z3],
    ["ZEA", SystemParsers.input_source, Zone.HDZ],
    ["VOL", CodeIntMap, Zone.Z1, "volume"],
    ["ZV", CodeIntMap, Zone.Z2, "volume"],
    ["YV", CodeIntMap, Zone.Z3, "volume"],
    ["XV", CodeIntMap, Zone.HDZ, "volume"],
    ["MUT", CodeInverseBoolMap, Zone.Z1, "mute"],
    ["Z2MUT", CodeInverseBoolMap, Zone.Z2, "mute"],
    ["Z3MUT", CodeInverseBoolMap, Zone.Z3, "mute"],
    ["HZMUT", CodeInverseBoolMap, Zone.HDZ, "mute"],
    ["SPK", SpeakerModes, Zone.ALL, "amp", "speakers"],
    ["HO", HdmiOutModes, Zone.ALL, "amp", "hdmi_out"],
    ["HA", HdmiAudioModes, Zone.ALL, "amp", "hdmi_audio"],
    ["PQ", PqlsModes, Zone.ALL, "amp", "pqls"],
    ["SAA", DimmerModes, Zone.ALL, "amp", "dimmer"],
    ["SAB", CodeIntMap, Zone.ALL, "amp", "sleep"],
    ["SAC", AmpModes, Zone.ALL, "amp", "status"],
    ["PKL", PanelLock, Zone.ALL, "amp", "panel_lock"],
    ["RML", CodeBoolMap, Zone.ALL, "amp", "remote_lock"],
    ["SSF", SystemParsers.speaker_system, Zone.ALL],
    ["RGB", SystemParsers.input_name, Zone.ALL],
    ["SVB", SystemParsers.mac_address, Zone.ALL],
    ["RGD", SystemParsers.avr_model, Zone.ALL],
    ["SSI", SystemParsers.software_version, Zone.ALL],
    ["AUA", SystemParsers.audio_parameter_prohibitation, Zone.Z1],
    ["AUB", SystemParsers.audio_parameter_working, Zone.Z1],
    ## settings
    ["SSL", CodeBoolMap, Zone.ALL, "system", "home_menu_status"],
    ["SSJ", SettingsParsers.mcacc_diagnostic_status, Zone.ALL],
    ["SUU", SettingsParsers.standing_wave_setting, Zone.ALL],
    ["SUV", SettingsParsers.standing_wave_sw_trim, Zone.ALL],
    ["SSP", SurroundPosition, Zone.ALL, "system", "surround_position"],
    ["SSQ", XOver, Zone.ALL, "system", "x_over"],
    ["SST", XCurve, Zone.ALL, "system", "x_curve"],
    ["SSU", CodeBoolMap, Zone.ALL, "system", "loudness_plus"],
    ["SSV", SbchProcessing, Zone.ALL, "system", "sbch_processing"],
    ["SSG", SettingsParsers.speaker_setting, Zone.ALL],
    ["ILA", SettingsParsers.input_level_adjust, Zone.ALL],
    ["SSS", SettingsParsers.speaker_distance_mcacc, Zone.ALL],
    ["SSW", CodeBoolMap, Zone.ALL, "system", "thx_ultraselect2"],
    ["SSX", CodeBoolMap, Zone.ALL, "system", "boundary_gain_compression"],
    ["SSB", CodeBoolMap, Zone.ALL, "system", "re_equalization"],
    ["SSE", OsdLanguages, Zone.ALL, "system", "osd_language"],
    ["STA", CodeBoolMap, Zone.ALL, "system", "network_dhcp"],
    ["STG", CodeBoolMap, Zone.ALL, "system", "network_proxy_active"],
    ["STJ", CodeBoolMap, Zone.ALL, "system", "network_standby"],
    ["SSO", CodeMapBase, Zone.ALL, "system", "friendly_name"],
    ["STK", CodeBoolMap, Zone.ALL, "system", "parental_lock"],
    ["STL", CodeMapBase, Zone.ALL, "system", "parental_lock_password"],
    ["SUM", SettingsParsers.port_numbers, Zone.ALL],
    ["STQ", CodeBoolMap, Zone.ALL, "system", "hdmi_control"],
    ["STR", CodeBoolMap, Zone.ALL, "system", "hdmi_control_mode"],
    ["STT", CodeBoolMap, Zone.ALL, "system", "hdmi_arc"],
    ["SVL", CodeBoolMap, Zone.ALL, "system", "pqls_for_backup"],
    ["STU", StandbyPassthrough, Zone.ALL, "system", "standby_passthrough"],
    ["STV", SettingsParsers.external_hdmi_trigger, Zone.ALL],
    ["STW", SettingsParsers.external_hdmi_trigger, Zone.ALL],
    ["STX", CodeBoolMap, Zone.ALL, "system", "speaker_b_link"],
    ["SVA", CodeBoolMap, Zone.ALL, "system", "osd_overlay"],
    ["ADS", CodeBoolMap, Zone.ALL, "system", "additional_service"],
    ["SUT", CodeBoolMap, Zone.ALL, "system", "user_lock"],
    ## audio
    ["CLV", AudioParsers.channel_levels, Zone.Z1],
    ["ZGE", AudioParsers.channel_levels, Zone.Z2],
    ["ZHE", AudioParsers.channel_levels, Zone.Z3],
    ["SR", AudioParsers.listening_mode, Zone.ALL],
    ["TO", ToneModes, Zone.Z1, "tone", "status"],
    ["BA", ToneDb, Zone.Z1, "tone", "bass"],
    ["TR", ToneDb, Zone.Z1, "tone", "treble"],
    ["ZGA", ToneModes, Zone.Z2, "tone", "status"],
    ["ZGB", ToneDb, Zone.Z2, "tone", "bass"],
    ["ZGC", ToneDb, Zone.Z2, "tone", "treble"],
    ## tuner
    ["FRF", TunerParsers.frequency_fm, Zone.ALL],
    ["FRA", TunerParsers.frequency_am, Zone.ALL],
    ["PR", TunerParsers.preset, Zone.ALL],
    ["SUQ", TunerParsers.am_frequency_step, Zone.ALL],
    ## dsp
    ["MC", DspMcaccMemorySet, Zone.ALL, "dsp", "mcacc_memory_set"],
    ["IS", DspPhaseControl, Zone.ALL, "dsp", "phase_control"],
    ["VSP", DspAutoManual, Zone.ALL, "dsp", "virtual_speakers"],
    ["VSB", CodeBoolMap, Zone.ALL, "dsp", "virtual_sb"],  # virtual_soundback
    ["VHT", CodeBoolMap, Zone.ALL, "dsp", "virtual_height"],
    ["SDA", DspSignalSelect, Zone.ALL, "dsp", "signal_select"],
    ["SDB", CodeBoolMap, Zone.ALL, "dsp", "input_att"],
    ["ATA", CodeBoolMap, Zone.ALL, "dsp", "sound_retriever"],
    ["ATC", CodeBoolMap, Zone.ALL, "dsp", "eq"],
    ["ATD", CodeBoolMap, Zone.ALL, "dsp", "standing_wave"],
    ["ATE", DspPhaseControlPlus, Zone.ALL, "dsp", "phase_control_plus"],
    ["ATF", DspSoundDelay, Zone.ALL, "dsp", "sound_delay"],
    ["ATG", CodeBoolMap, Zone.ALL, "dsp", "digital_noise_reduction"],
    ["ATH", DspDialogEnhancement, Zone.ALL, "dsp", "dialog_enchancement"],
    ["ATI", CodeBoolMap, Zone.ALL, "dsp", "hi_bit"],
    ["ATJ", DspDualMono, Zone.ALL, "dsp", "dual_mono"],
    ["ATK", CodeBoolMap, Zone.ALL, "dsp", "fixed_pcm"],
    ["ATL", DspDynamicRange, Zone.ALL, "dsp", "dynamic_range_control"],
    ["ATM", DspLfeAttenuator, Zone.ALL, "dsp", "lfe_attenuator"],
    ["ATN", DspSacdGain, Zone.ALL, "dsp", "sacd_gain"],
    ["ATO", CodeBoolMap, Zone.ALL, "dsp", "auto_delay"],
    ["ATP", DspCenterWidth, Zone.ALL, "dsp", "center_width"],
    ["ATQ", CodeBoolMap, Zone.ALL, "dsp", "panorama"],
    ["ATR", DspDimension, Zone.ALL, "dsp", "dimension"],
    ["ATS", DspCenterImage, Zone.ALL, "dsp", "center_image"],
    ["ATT", DspEffect, Zone.ALL, "dsp", "effect"],
    ["ATU", DspHeightGain, Zone.ALL, "dsp", "height_gain"],
    ["ATV", DspDigitalFilter, Zone.ALL, "dsp", "digital_filter"],
    ["ATW", CodeBoolMap, Zone.ALL, "dsp", "loudness_management"],
    ["ATY", DspAutoManual, Zone.ALL, "dsp", "audio_scaler"],
    ["ATZ", DspUpSampling, Zone.ALL, "dsp", "up_sampling"],
    ["ARA", CodeBoolMap, Zone.ALL, "dsp", "center_spread"],
    ["VDP", DspVirtualDepth, Zone.ALL, "dsp", "virtual_depth"],
    ["VWD", CodeBoolMap, Zone.ALL, "dsp", "virtual_wide"],
    ["ARB", DspRenderingMode, Zone.ALL, "dsp", "rendering_mode"],
    ## information
    ["AST", InformationParsers.audio_information, Zone.ALL],
    ["VST", InformationParsers.video_information, Zone.ALL],
    ["FL", DisplayText, Zone.ALL, "amp", "display"],
    ## video
    ["VTB", CodeBoolMap, Zone.Z1, "video", "converter"],
    ["VTC", VideoResolutionModes, Zone.Z1, "video", "resolution"],
    ["VTD", VideoPureCinemaModes, Zone.Z1, "video", "pure_cinema"],
    ["VTE", VideoProgMotion, Zone.Z1, "video", "prog_motion"],
    ["VTF", VideoStreamSmootherModes, Zone.Z1, "video", "stream_smoother"],
    ["VTG", AdvancedVideoAdjustModes, Zone.Z1, "video", "advanced_video_adjust"],
    ["VTH", VideoInt08Map, Zone.Z1, "video", "ynr"],
    ["VTI", VideoInt08Map, Zone.Z1, "video", "cnr"],
    ["VTJ", VideoInt08Map, Zone.Z1, "video", "bnr"],
    ["VTK", VideoInt08Map, Zone.Z1, "video", "mnr"],
    ["VTL", VideoInt08Map, Zone.Z1, "video", "detail"],
    ["VTM", VideoInt08Map, Zone.Z1, "video", "sharpness"],
    ["VTN", VideoInt66Map, Zone.Z1, "video", "brightness"],
    ["VTO", VideoInt66Map, Zone.Z1, "video", "contrast"],
    ["VTP", VideoInt66Map, Zone.Z1, "video", "hue"],
    ["VTQ", VideoInt66Map, Zone.Z1, "video", "chroma"],
    ["VTR", CodeBoolMap, Zone.Z1, "video", "black_setup"],
    ["VTS", VideoAspectModes, Zone.Z1, "video", "aspect"],
    ["VTT", VideoSuperResolution, Zone.Z1, "video", "super_resolution"],
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
        elif issubclass(parse_func, CodeMapBase):
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
