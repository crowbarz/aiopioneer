"""aiopioneer response decoders for DSP functions. Most responses are only valid for Zone 1."""

from ..const import Zone
from .code_map import (
    CodeBoolMap,
    CodeIntMap,
    CodeFloatMap,
    CodeDictStrMap,
)


class McaccMemorySet(CodeIntMap):
    """DSP MCACC memory set."""

    friendly_name = "MCACC memory set"
    base_property = "dsp"
    property_name = "mcacc_memory_set"

    value_min = 1
    value_max = 6
    code_zfill = 1


class PhaseControl(CodeDictStrMap):
    """Phase control."""

    friendly_name = "phase control"
    base_property = "dsp"
    property_name = "phase_control"

    code_map = {"0": "off", "1": "on", "2": "full band on"}


class PhaseControlPlus(CodeIntMap):
    """Phase control plus. (1step = 1ms)"""

    friendly_name = "phase control plus"
    base_property = "dsp"
    property_name = "phase_control_plus"

    value_min = 0
    value_max = 16
    code_zfill = 2

    @classmethod
    def value_to_code(cls, value: int | str) -> str:
        if value == "auto":
            return "97"
        return super().value_to_code(value=value)

    @classmethod
    def code_to_value(cls, code: str) -> int:
        if code in ["97", "98", "99"]:
            return "auto"
        return super().code_to_value(code=code)


class VirtualSpeakers(CodeDictStrMap):
    """Virtual speakers."""

    friendly_name = "virtual speakers"
    base_property = "dsp"
    property_name = "virtual_speakers"

    code_map = {"0": "auto", "1": "manual"}


class VirtualSoundback(CodeBoolMap):
    """Virtual soundback."""

    friendly_name = "virtual soundback"
    base_property = "dsp"
    property_name = "virtual_sb"  # NOTE: inconsistent


class VirtualHeight(CodeBoolMap):
    """virtual height."""

    friendly_name = "virtual height"
    base_property = "dsp"
    property_name = "virtual_height"


class VirtualWide(CodeBoolMap):
    """virtual wide."""

    friendly_name = "virtual wide"
    base_property = "dsp"
    property_name = "virtual_wide"


class VirtualDepth(CodeDictStrMap):
    """Virtual depth."""

    friendly_name = "virtual depth"
    base_property = "dsp"
    property_name = "virtual_depth"

    code_map = {"0": "off", "1": "min", "2": "mid", "3": "max"}


class SoundRetriever(CodeBoolMap):
    """Sound retriever."""

    friendly_name = "sound retriever"
    base_property = "dsp"
    property_name = "sound_retriever"


class SignalSelect(CodeDictStrMap):
    """Signal select."""

    friendly_name = "signal select"
    base_property = "dsp"
    property_name = "mcacc_memory_set"

    code_map = {"0": "auto", "1": "analog", "2": "digital", "3": "HDMI"}


class InputAttenuator(CodeBoolMap):
    """input attenuator."""

    friendly_name = "input attenuator"
    base_property = "dsp"
    property_name = "input_attenuator"


class Equalizer(CodeBoolMap):
    """Equalizer."""

    friendly_name = "equalizer"
    base_property = "dsp"
    property_name = "eq"


class StandingWave(CodeBoolMap):
    """Standing wave."""

    friendly_name = "standing wave"
    base_property = "dsp"
    property_name = "standing_wave"


class SoundDelay(CodeIntMap):
    """Sound delay. (1step=5ms)"""

    friendly_name = "sound delay"
    base_property = "dsp"
    property_name = "placeholder"

    value_min = 0
    value_max = 800
    value_step = 5
    value_divider = 5
    code_zfill = 3


class DigitalNoiseReduction(CodeBoolMap):
    """Digital noise reduction."""

    friendly_name = "digital noise reduction"
    base_property = "dsp"
    property_name = "digital_noise_reduction"


class DialogEnhancement(CodeDictStrMap):
    """Dialog enhancement."""

    friendly_name = "dialog enhancement"
    base_property = "dsp"
    property_name = "dialog_enchancement"

    code_map = {"0": "off", "1": "flat", "2": "+1", "3": "+2", "4": "+3", "5": "+4"}


class AudioScaler(CodeDictStrMap):
    """Audio scaler."""

    friendly_name = "audio scaler"
    base_property = "dsp"
    property_name = "audio_scaler"

    code_map = {"0": "auto", "1": "manual"}


class HiBit(CodeBoolMap):
    """Hi-bit."""

    friendly_name = "hi-bit"
    base_property = "dsp"
    property_name = "hi_bit"


class UpSampling(CodeDictStrMap):
    """Up sampling."""

    friendly_name = "up sampling"
    base_property = "dsp"
    property_name = "up_sampling"

    code_map = {"0": "off", "1": "2 times", "2": "4 times"}


class DigitalFilter(CodeDictStrMap):
    """Digital filter."""

    friendly_name = "digital filter"
    base_property = "dsp"
    property_name = "digital_filter"

    code_map = {"0": "slow", "1": "sharp", "2": "short"}


class DualMono(CodeDictStrMap):
    """Dual mono."""

    friendly_name = "dual mono"
    base_property = "dsp"
    property_name = "dual_mono"

    code_map = {"0": "CH1+CH2", "1": "CH1", "2": "CH2"}


class FixedPcm(CodeBoolMap):
    """Fixed PCM."""

    friendly_name = "fixed PCM"
    base_property = "dsp"
    property_name = "fixed_pcm"


class DynamicRange(CodeDictStrMap):
    """Dynamic range."""

    friendly_name = "dynamic range"
    base_property = "dsp"
    property_name = "dynamic_range"

    code_map = {"0": "off", "1": "auto", "2": "mid", "3": "max"}


class LfeAttenuator(CodeIntMap):
    """LFE attenuator."""

    friendly_name = "LFE attenuator"
    base_property = "dsp"
    property_name = "lfe_attenuator"

    value_min = -20
    value_max = 0
    code_zfill = 2
    value_divider = -1

    @classmethod
    def value_to_code(cls, value: int | str) -> str:
        if value == "off":
            return "50"
        return super().value_to_code(value=value)

    @classmethod
    def code_to_value(cls, code: str) -> int | str:
        if code == "50":
            return "off"
        return super().code_to_value(code=code)


class SacdGain(CodeIntMap):
    """SACD gain."""

    friendly_name = "SACD gain"
    base_property = "dsp"
    property_name = "sacd_gain"

    code_zfill = 1

    @classmethod
    def value_to_code(cls, value: int) -> str:
        if value not in [0, 6]:
            raise ValueError(f"Value {value} not in [0, 6] for {cls.__name__}")
        return "1" if value == 6 else "0"

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return 6 if code == "1" else 0


class AutoDelay(CodeBoolMap):
    """auto delay."""

    friendly_name = "auto delay"
    base_property = "dsp"
    property_name = "auto_delay"


class CenterWidth(CodeIntMap):
    """Center width."""

    friendly_name = "center width"
    base_property = "dsp"
    property_name = "center_width"

    value_min = 0
    value_max = 7
    code_zfill = 1


class Panorama(CodeBoolMap):
    """Panorama."""

    friendly_name = "panorama"
    base_property = "dsp"
    property_name = "panorama"


class Dimension(CodeIntMap):
    """Dimension."""

    friendly_name = "dimension"
    base_property = "dsp"
    property_name = "dimension"

    value_min = -3
    value_max = 3
    value_offset = 50
    code_zfill = 2


class CenterImage(CodeFloatMap):
    """Center image. (1step=0.1)"""

    friendly_name = "center image"
    base_property = "dsp"
    property_name = "center_image"

    value_min = 0
    value_max = 1
    value_step = 0.1
    value_divider = 0.1
    code_zfill = 2


class Effect(CodeIntMap):
    """Effect. (1step=10)"""

    friendly_name = "effect"
    base_property = "dsp"
    property_name = "effect"

    value_min = 10
    value_max = 90
    value_step = 10
    value_divider = 10
    code_zfill = 2


class HeightGain(CodeDictStrMap):
    """Height gain."""

    friendly_name = "height gain"
    base_property = "dsp"
    property_name = "height_gain"

    code_map = {"0": "low", "1": "mid", "2": "high"}


class LoudnessManagement(CodeBoolMap):
    """Loudness management."""

    friendly_name = "loudness management"
    base_property = "dsp"
    property_name = "loudness_management"


class CenterSpread(CodeBoolMap):
    """Center spread."""

    friendly_name = "center spread"
    base_property = "dsp"
    property_name = "center_spread"


class RenderingMode(CodeDictStrMap):
    """Rendering mode."""

    friendly_name = "rendering mode"
    base_property = "dsp"
    property_name = "rendering_mode"

    code_map = {"0": "object base", "1": "channel base"}


COMMANDS_DSP = {
    "query_dsp_mcacc_memory_query": {Zone.Z1: ["?MC", "MC"]},
    "set_dsp_mcacc_memory_set": {
        Zone.Z1: ["MC", "MC"],
        "args": [McaccMemorySet],
        "retry_on_fail": True,
    },
    "query_dsp_phase_control": {Zone.Z1: ["?IS", "IS"]},
    "set_dsp_phase_control": {
        Zone.Z1: ["IS", "IS"],
        "args": [PhaseControl],
        "retry_on_fail": True,
    },
    "query_dsp_phase_control_plus": {Zone.Z1: ["?ATE", "ATE"]},
    "set_dsp_phase_control_plus": {
        Zone.Z1: ["ATE", "ATE"],
        "args": [PhaseControlPlus],
        "retry_on_fail": True,
    },
    "query_dsp_virtual_speakers": {Zone.Z1: ["?VSP", "VSP"]},
    "set_dsp_virtual_speakers": {
        Zone.Z1: ["VSP", "VSP"],
        "args": [VirtualSpeakers],
        "retry_on_fail": True,
    },
    "query_dsp_virtual_sb": {Zone.Z1: ["?VSB", "VSB"]},
    "set_dsp_virtual_sb": {
        Zone.Z1: ["VSB", "VSB"],
        "args": [VirtualSoundback],
        "retry_on_fail": True,
    },
    "query_dsp_virtual_height": {Zone.Z1: ["?VHT", "VHT"]},
    "set_dsp_virtual_height": {
        Zone.Z1: ["VHT", "VHT"],
        "args": [VirtualHeight],
        "retry_on_fail": True,
    },
    "query_dsp_virtual_wide": {Zone.Z1: ["?VWD", "VWD"]},
    "set_dsp_virtual_wide": {
        Zone.Z1: ["VWD", "VWD"],
        "args": [VirtualWide],
        "retry_on_fail": True,
    },
    "query_dsp_virtual_depth": {Zone.Z1: ["?VDP", "VDP"]},
    "set_dsp_virtual_depth": {
        Zone.Z1: ["VDP", "VDP"],
        "args": [VirtualDepth],
        "retry_on_fail": True,
    },
    "query_dsp_sound_retriever": {Zone.Z1: ["?ATA", "ATA"]},
    "set_dsp_sound_retriever": {
        Zone.Z1: ["ATA", "ATA"],
        "args": [SoundRetriever],
        "retry_on_fail": True,
    },
    "query_dsp_signal_select": {Zone.Z1: ["?SDA", "SDA"]},
    "set_dsp_signal_select": {
        Zone.Z1: ["SDA", "SDA"],
        "args": [SignalSelect],
        "retry_on_fail": True,
    },
    "query_dsp_input_attenuator": {Zone.Z1: ["?SDB", "SDB"]},
    "set_dsp_input_attenuator": {
        Zone.Z1: ["SDB", "SDB"],
        "args": [InputAttenuator],
        "retry_on_fail": True,
    },
    "query_dsp_eq": {Zone.Z1: ["?ATC", "ATC"]},
    "set_dsp_eq": {Zone.Z1: ["ATC", "ATC"], "args": [Equalizer], "retry_on_fail": True},
    "query_dsp_standing_wave": {Zone.Z1: ["?ATD", "ATD"]},
    "set_dsp_standing_wave": {
        Zone.Z1: ["ATD", "ATD"],
        "args": [StandingWave],
        "retry_on_fail": True,
    },
    "query_dsp_sound_delay": {Zone.Z1: ["?ATF", "ATF"]},
    "set_dsp_sound_delay": {
        Zone.Z1: ["ATF", "ATF"],
        "args": [SoundDelay],
        "retry_on_fail": True,
    },
    "query_dsp_digital_noise_reduction": {Zone.Z1: ["?ATG", "ATG"]},
    "set_dsp_digital_noise_reduction": {
        Zone.Z1: ["ATG", "ATG"],
        "args": [DigitalNoiseReduction],
        "retry_on_fail": True,
    },
    "query_dsp_dialog_enhancement": {Zone.Z1: ["?ATH", "ATH"]},
    "set_dsp_dialog_enhancement": {
        Zone.Z1: ["ATH", "ATH"],
        "args": [DialogEnhancement],
        "retry_on_fail": True,
    },
    "query_dsp_audio_scaler": {Zone.Z1: ["?ATY", "ATY"]},
    "set_dsp_audio_scaler": {
        Zone.Z1: ["ATY", "ATY"],
        "args": [AudioScaler],
        "retry_on_fail": True,
    },
    "query_dsp_hi_bit": {Zone.Z1: ["?ATI", "ATI"]},
    "set_dsp_hi_bit": {Zone.Z1: ["ATI", "ATI"], "args": [HiBit], "retry_on_fail": True},
    "query_dsp_up_sampling": {Zone.Z1: ["?ATZ", "ATZ"]},
    "set_dsp_up_sampling": {
        Zone.Z1: ["ATZ", "ATZ"],
        "args": [UpSampling],
        "retry_on_fail": True,
    },
    "query_dsp_digital_filter": {Zone.Z1: ["?ATV", "ATV"]},
    "set_dsp_digital_filter": {
        Zone.Z1: ["ATV", "ATV"],
        "args": [DigitalFilter],
        "retry_on_fail": True,
    },
    "query_dsp_dual_mono": {Zone.Z1: ["?ATJ", "ATJ"]},
    "set_dsp_dual_mono": {
        Zone.Z1: ["ATJ", "ATJ"],
        "args": [DualMono],
        "retry_on_fail": True,
    },
    "query_dsp_fixed_pcm": {Zone.Z1: ["?ATK", "ATK"]},
    "set_dsp_fixed_pcm": {
        Zone.Z1: ["ATK", "ATK"],
        "args": [FixedPcm],
        "retry_on_fail": True,
    },
    "query_dsp_dynamic_range": {Zone.Z1: ["?ATL", "ATL"]},
    "set_dsp_dynamic_range": {
        Zone.Z1: ["ATL", "ATL"],
        "args": [DynamicRange],
        "retry_on_fail": True,
    },
    "query_dsp_lfe_attenuator": {Zone.Z1: ["?ATM", "ATM"]},
    "set_dsp_lfe_attenuator": {
        Zone.Z1: ["ATM", "ATM"],
        "args": [LfeAttenuator],
        "retry_on_fail": True,
    },
    "query_dsp_sacd_gain": {Zone.Z1: ["?ATN", "ATN"]},
    "set_dsp_sacd_gain": {
        Zone.Z1: ["ATN", "ATN"],
        "args": [SacdGain],
        "retry_on_fail": True,
    },
    "query_dsp_auto_delay": {Zone.Z1: ["?ATO", "ATO"]},
    "set_dsp_auto_delay": {
        Zone.Z1: ["ATO", "ATO"],
        "args": [AutoDelay],
        "retry_on_fail": True,
    },
    "query_dsp_center_width": {Zone.Z1: ["?ATP", "ATP"]},
    "set_dsp_center_width": {
        Zone.Z1: ["ATP", "ATP"],
        "args": [CenterWidth],
        "retry_on_fail": True,
    },
    "query_dsp_panorama": {Zone.Z1: ["?ATQ", "ATQ"]},
    "set_dsp_panorama": {
        Zone.Z1: ["ATQ", "ATQ"],
        "args": [Panorama],
        "retry_on_fail": True,
    },
    "query_dsp_dimension": {Zone.Z1: ["?ATR", "ATR"]},
    "set_dsp_dimension": {
        Zone.Z1: ["ATR", "ATR"],
        "args": [Dimension],
        "retry_on_fail": True,
    },
    "query_dsp_center_image": {Zone.Z1: ["?ATS", "ATS"]},
    "set_dsp_center_image": {
        Zone.Z1: ["ATS", "ATS"],
        "args": [CenterImage],
        "retry_on_fail": True,
    },
    "query_dsp_effect": {Zone.Z1: ["?ATT", "ATT"]},
    "set_dsp_effect": {
        Zone.Z1: ["ATT", "ATT"],
        "args": [Effect],
        "retry_on_fail": True,
    },
    "query_dsp_height_gain": {Zone.Z1: ["?ATU", "ATU"]},
    "set_dsp_height_gain": {
        Zone.Z1: ["ATU", "ATU"],
        "args": [HeightGain],
        "retry_on_fail": True,
    },
    "query_dsp_loudness_management": {Zone.Z1: ["?ATW", "ATW"]},
    "set_dsp_loudness_management": {
        Zone.Z1: ["ATW", "ATW"],
        "args": [LoudnessManagement],
        "retry_on_fail": True,
    },
    "query_center_spread": {Zone.Z1: ["?ARA", "ARA"]},
    "set_dsp_center_spread": {
        Zone.Z1: ["ARA", "ARA"],
        "args": [CenterSpread],
        "retry_on_fail": True,
    },
    "query_rendering_mode": {Zone.Z1: ["?ARB", "ARB"]},
    "set_dsp_rendering_mode": {
        Zone.Z1: ["ARB", "ARB"],
        "args": [RenderingMode],
        "retry_on_fail": True,
    },
}

RESPONSE_DATA_DSP = [
    ("MC", McaccMemorySet, Zone.ALL),  # dsp.mcacc_memory_set
    ("IS", PhaseControl, Zone.ALL),  # dsp.phase_control
    ("ATE", PhaseControlPlus, Zone.ALL),  # dsp.phase_control_plus
    ("VSP", VirtualSpeakers, Zone.ALL),  # dsp.virtual_speakers
    ("VSB", VirtualSoundback, Zone.ALL),  # dsp.virtual_sb
    ("VHT", VirtualHeight, Zone.ALL),  # dsp.virtual_height
    ("VWD", VirtualWide, Zone.ALL),  # dsp.virtual_wide
    ("VDP", VirtualDepth, Zone.ALL),  # dsp.virtual_depth
    ("ATA", SoundRetriever, Zone.ALL),  # dsp.sound_retriever
    ("SDA", SignalSelect, Zone.ALL),  # dsp.signal_select
    ("SDB", InputAttenuator, Zone.ALL),  # dsp.input_attenuator
    ("ATC", Equalizer, Zone.ALL),  # dsp.eq
    ("ATD", StandingWave, Zone.ALL),  # dsp.standing_wave
    ("ATF", SoundDelay, Zone.ALL),  # dsp.sound_delay
    ("ATG", DigitalNoiseReduction, Zone.ALL),  # dsp.digital_noise_reduction
    ("ATH", DialogEnhancement, Zone.ALL),  # dsp.dialog_enchancement
    ("ATY", AudioScaler, Zone.ALL),  # dsp.audio_scaler
    ("ATI", HiBit, Zone.ALL),  # dsp.hi_bit
    ("ATZ", UpSampling, Zone.ALL),  # dsp.up_sampling
    ("ATV", DigitalFilter, Zone.ALL),  # dsp.digital_filter
    ("ATJ", DualMono, Zone.ALL),  # dsp.dual_mono
    ("ATK", FixedPcm, Zone.ALL),  # dsp.fixed_pcm
    ("ATL", DynamicRange, Zone.ALL),  # dsp.dynamic_range
    ("ATM", LfeAttenuator, Zone.ALL),  # dsp.lfe_attenuator
    ("ATN", SacdGain, Zone.ALL),  # dsp.sacd_gain
    ("ATO", AutoDelay, Zone.ALL),  # dsp.auto_delay
    ("ATP", CenterWidth, Zone.ALL),  # dsp.center_width
    ("ATQ", Panorama, Zone.ALL),  # dsp.panorama
    ("ATR", Dimension, Zone.ALL),  # dsp.dimension
    ("ATS", CenterImage, Zone.ALL),  # dsp.center_image
    ("ATT", Effect, Zone.ALL),  # dsp.effect
    ("ATU", HeightGain, Zone.ALL),  # dsp.height_gain
    ("ATW", LoudnessManagement, Zone.ALL),  # dsp.loudness_management
    ("ARA", CenterSpread, Zone.ALL),  # dsp.center_spread
    ("ARB", RenderingMode, Zone.ALL),  # dsp.rendering_mode
]
