"""Main aiopioneer parsing classes and functions"""

from aiopioneer.const import Zones
from .system import SystemParsers
from .audio import AudioParsers
from .tuner import TunerParsers
from .dsp import DspParsers
from .information import InformationParsers
from .video import VideoParsers

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
    ["SPK", SystemParsers.speaker_modes, Zones.Z1],
    ["HO", SystemParsers.hdmi_out, Zones.Z1],
    ["HA", SystemParsers.hdmi_audio, Zones.Z1],
    ["PQ", SystemParsers.pqls, Zones.Z1],
    ["SAA", SystemParsers.dimmer, Zones.Z1],
    ["SAB", SystemParsers.sleep, Zones.Z1],
    ["SAC", SystemParsers.amp_status, Zones.Z1],
    ["PKL", SystemParsers.panel_lock, Zones.Z1],
    ["RML", SystemParsers.remote_lock, Zones.Z1],
    ["SSF", SystemParsers.speaker_system, Zones.Z1],
    ["AUA", SystemParsers.audio_parameter_prohibitation, Zones.Z1],
    ["AUB", SystemParsers.audio_parameter_working, Zones.Z1],

    ["CLV", AudioParsers.channel_levels, Zones.Z1],
    ["ZGE", AudioParsers.channel_levels, Zones.Z2],
    ["ZHE", AudioParsers.channel_levels, Zones.Z3],
    ["SR", AudioParsers.listening_mode, Zones.Z1],
    ["TO", AudioParsers.tone, Zones.Z1],
    ["BA", AudioParsers.tone_bass, Zones.Z1],
    ["TR", AudioParsers.tone_treble, Zones.Z1],
    ["ZGA", AudioParsers.tone, Zones.Z2],
    ["ZGB", AudioParsers.tone_bass, Zones.Z2],
    ["ZGC", AudioParsers.tone_treble, Zones.Z2],

    ["FRF", TunerParsers.frequency_fm, Zones.Z1],
    ["FRA", TunerParsers.frequency_am, Zones.Z1],
    ["PR", TunerParsers.preset, Zones.Z1],

    ["MC", DspParsers.mcacc_setting, Zones.Z1],
    ["IS", DspParsers.phasecontrol, Zones.Z1],
    ["VSP", DspParsers.virtual_speakers, Zones.Z1],
    ["VSB", DspParsers.virtual_soundback, Zones.Z1],
    ["VHT", DspParsers.virtual_height, Zones.Z1],
    ["SDA", DspParsers.signal_select, Zones.Z1],
    ["SDB", DspParsers.input_att, Zones.Z1],
    ["ATA", DspParsers.sound_retriever, Zones.Z1],
    ["ATC", DspParsers.equalizer, Zones.Z1],
    ["ATD", DspParsers.standing_wave, Zones.Z1],
    ["ATE", DspParsers.phase_control_plus, Zones.Z1],
    ["ATF", DspParsers.sound_delay, Zones.Z1],
    ["ATG", DspParsers.digital_noise_reduction, Zones.Z1],
    ["ATH", DspParsers.dialog_enhancement, Zones.Z1],
    ["ATI", DspParsers.hi_bit, Zones.Z1],
    ["ATJ", DspParsers.dual_mono, Zones.Z1],
    ["ATK", DspParsers.fixed_pcm, Zones.Z1],
    ["ATL", DspParsers.dynamic_range_control, Zones.Z1],
    ["ATM", DspParsers.lfe_attenuator, Zones.Z1],
    ["ATN", DspParsers.sacd_gain, Zones.Z1],
    ["ATO", DspParsers.auto_delay, Zones.Z1],
    ["ATP", DspParsers.center_width, Zones.Z1],
    ["ATQ", DspParsers.panorama, Zones.Z1],
    ["ATR", DspParsers.dimension, Zones.Z1],
    ["ATS", DspParsers.center_image, Zones.Z1],
    ["ATT", DspParsers.effect, Zones.Z1],
    ["ATU", DspParsers.height_gain, Zones.Z1],
    ["ATV", DspParsers.digital_filter, Zones.Z1],
    ["ATW", DspParsers.loudness_management, Zones.Z1],
    ["ATY", DspParsers.audio_scaler, Zones.Z1],
    ["ATZ", DspParsers.up_sampling, Zones.Z1],
    ["ARA", DspParsers.center_spread, Zones.Z1],
    ["VDP", DspParsers.virtual_depth, Zones.Z1],
    ["VWD", DspParsers.virtual_wide, Zones.Z1],
    ["ARB", DspParsers.rendering_mode, Zones.Z1],

    ["AST", InformationParsers.audio_information, Zones.Z1],
    ["VST", InformationParsers.video_information, Zones.Z1],

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

def process_raw_response(raw_resp: str, _param: dict) -> list:
    """Processes a raw response and looks up required functions from RESPONSE_DATA."""
    match_resp = next((r for r in RESPONSE_DATA if raw_resp.startswith(r[0])), None)
    if match_resp:
        parse_cmd = match_resp[0]
        parse_func = match_resp[1]
        parse_zone = match_resp[2]
        return parse_func(
            raw=raw_resp[len(parse_cmd):],
            _param=_param,
            zone=parse_zone,
            command=parse_cmd
        )
    else:
        pass ## No error handling as not all responses have been captured by aiopioneer.

class Response():
    """Model defining a parsed response for dynamic parsing into aiopioneer properties."""

    def __init__(
            self,
            raw: str,
            response_command: str,
            base_property: str,
            property_name: str,
            zone: str,
            value,
            queue_commands: list
        ):
        self.raw = raw
        self.response_command =  response_command
        self.base_property = base_property
        self.property_name = property_name
        self.zone = zone
        self.value = value
        self.command_queue = queue_commands
