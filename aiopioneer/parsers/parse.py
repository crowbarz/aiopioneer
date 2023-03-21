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
    ["SPK", SystemParsers.speaker_modes, None],
    ["HO", SystemParsers.hdmi_out, None],
    ["HA", SystemParsers.hdmi_audio, None],
    ["PQ", SystemParsers.pqls, None],
    ["SAA", SystemParsers.dimmer, None],
    ["SAB", SystemParsers.sleep, None],
    ["SAC", SystemParsers.amp_status, None],
    ["PKL", SystemParsers.panel_lock, None],
    ["RML", SystemParsers.remote_lock, None],
    ["SSF", SystemParsers.speaker_system, None],

    ["AUA", SystemParsers.audio_parameter_prohibitation, Zones.Z1],
    ["AUB", SystemParsers.audio_parameter_working, Zones.Z1],

    ["CLV", AudioParsers.channel_levels, Zones.Z1],
    ["ZGE", AudioParsers.channel_levels, Zones.Z2],
    ["ZHE", AudioParsers.channel_levels, Zones.Z3],
    ["SR", AudioParsers.listening_mode, None],
    ["TO", AudioParsers.tone, Zones.Z1],
    ["BA", AudioParsers.tone_bass, Zones.Z1],
    ["TR", AudioParsers.tone_treble, Zones.Z1],
    ["ZGA", AudioParsers.tone, Zones.Z2],
    ["ZGB", AudioParsers.tone_bass, Zones.Z2],
    ["ZGC", AudioParsers.tone_treble, Zones.Z2],

    ["FRF", TunerParsers.frequency_fm, None],
    ["FRA", TunerParsers.frequency_am, None],
    ["PR", TunerParsers.preset, None],

    ["MC", DspParsers.mcacc_setting, None],
    ["IS", DspParsers.phasecontrol, None],
    ["VSP", DspParsers.virtual_speakers, None],
    ["VSB", DspParsers.virtual_soundback, None],
    ["VHT", DspParsers.virtual_height, None],
    ["SDA", DspParsers.signal_select, None],
    ["SDB", DspParsers.input_att, None],
    ["ATA", DspParsers.sound_retriever, None],
    ["ATC", DspParsers.equalizer, None],
    ["ATD", DspParsers.standing_wave, None],
    ["ATE", DspParsers.phase_control_plus, None],
    ["ATF", DspParsers.sound_delay, None],
    ["ATG", DspParsers.digital_noise_reduction, None],
    ["ATH", DspParsers.dialog_enhancement, None],
    ["ATI", DspParsers.hi_bit, None],
    ["ATJ", DspParsers.dual_mono, None],
    ["ATK", DspParsers.fixed_pcm, None],
    ["ATL", DspParsers.dynamic_range_control, None],
    ["ATM", DspParsers.lfe_attenuator, None],
    ["ATN", DspParsers.sacd_gain, None],
    ["ATO", DspParsers.auto_delay, None],
    ["ATP", DspParsers.center_width, None],
    ["ATQ", DspParsers.panorama, None],
    ["ATR", DspParsers.dimension, None],
    ["ATS", DspParsers.center_image, None],
    ["ATT", DspParsers.effect, None],
    ["ATU", DspParsers.height_gain, None],
    ["ATV", DspParsers.digital_filter, None],
    ["ATW", DspParsers.loudness_management, None],
    ["ATY", DspParsers.audio_scaler, None],
    ["ATZ", DspParsers.up_sampling, None],
    ["ARA", DspParsers.center_spread, None],
    ["VDP", DspParsers.virtual_depth, None],
    ["VWD", DspParsers.virtual_wide, None],
    ["ARB", DspParsers.rendering_mode, None],

    ["AST", InformationParsers.audio_information, None],
    ["VST", InformationParsers.video_information, None],
    ["FL", InformationParsers.device_display_information, None],

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
