"""aiopioneer response decoders for DSP functions. Most responses are only valid for Zone 1."""

from ..const import Zone
from ..property_entry import gen_set_property
from .code_map import (
    CodeBoolMap,
    CodeIntMap,
    CodeFloatMap,
    CodeDictStrMap,
)


class MCACCMemorySet(CodeIntMap):
    """DSP MCACC memory set."""

    friendly_name = "MCACC memory set"
    base_property = "dsp"
    property_name = "mcacc_memory_set"
    supported_zones = {Zone.ALL}
    icon = "mdi:book-cog-outline"

    value_min = 1
    value_max = 6
    code_zfill = 1


class PhaseControl(CodeDictStrMap):
    """Phase control."""

    friendly_name = "phase control"
    base_property = "dsp"
    property_name = "phase_control"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "off", "1": "on", "2": "full band on"}


class PhaseControlPlus(CodeIntMap):
    """Phase control plus (1step = 1ms)."""

    friendly_name = "phase control plus"
    base_property = "dsp"
    property_name = "phase_control_plus"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"
    unit_of_measurement = "ms"
    ha_auto_entity = False
    ha_device_class = "duration"
    ha_number_mode = "slider"

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
    supported_zones = {Zone.ALL}
    icon = "mdi:speaker-multiple"

    code_map = {"0": "auto", "1": "manual"}


class VirtualSoundback(CodeBoolMap):
    """Virtual soundback."""

    friendly_name = "virtual soundback"
    base_property = "dsp"
    property_name = "virtual_sb"  # NOTE: inconsistent
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class VirtualHeight(CodeBoolMap):
    """virtual height."""

    friendly_name = "virtual height"
    base_property = "dsp"
    property_name = "virtual_height"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class VirtualWide(CodeBoolMap):
    """virtual wide."""

    friendly_name = "virtual wide"
    base_property = "dsp"
    property_name = "virtual_wide"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class VirtualDepth(CodeDictStrMap):
    """Virtual depth."""

    friendly_name = "virtual depth"
    base_property = "dsp"
    property_name = "virtual_depth"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "off", "1": "min", "2": "mid", "3": "max"}


class SoundRetriever(CodeBoolMap):
    """Sound retriever."""

    friendly_name = "sound retriever"
    base_property = "dsp"
    property_name = "sound_retriever"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class SignalSelect(CodeDictStrMap):
    """Signal select."""

    friendly_name = "signal select"
    base_property = "dsp"
    property_name = "signal_select"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "auto", "1": "analog", "2": "digital", "3": "HDMI"}


class InputAttenuator(CodeBoolMap):
    """input attenuator."""

    friendly_name = "input attenuator"
    base_property = "dsp"
    property_name = "input_attenuator"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class Equalizer(CodeBoolMap):
    """Equalizer."""

    friendly_name = "equalizer"
    base_property = "dsp"
    property_name = "eq"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class StandingWave(CodeBoolMap):
    """Standing wave."""

    friendly_name = "standing wave"
    base_property = "dsp"
    property_name = "standing_wave"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class SoundDelay(CodeIntMap):
    """Sound delay (1step = 5ms)."""

    friendly_name = "sound delay"
    base_property = "dsp"
    property_name = "sound_delay"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"
    unit_of_measurement = "ms"
    ha_device_class = "duration"
    ha_number_mode = "slider"

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
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class DialogEnhancement(CodeDictStrMap):
    """Dialog enhancement."""

    friendly_name = "dialog enhancement"
    base_property = "dsp"
    property_name = "dialog_enhancement"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "off", "1": "flat", "2": "+1", "3": "+2", "4": "+3", "5": "+4"}


class AudioScaler(CodeDictStrMap):
    """Audio scaler."""

    friendly_name = "audio scaler"
    base_property = "dsp"
    property_name = "audio_scaler"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "auto", "1": "manual"}


class HiBit(CodeBoolMap):
    """Hi-bit."""

    friendly_name = "hi-bit"
    base_property = "dsp"
    property_name = "hi_bit"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class UpSampling(CodeDictStrMap):
    """Up sampling."""

    friendly_name = "up sampling"
    base_property = "dsp"
    property_name = "up_sampling"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "off", "1": "2 times", "2": "4 times"}


class DigitalFilter(CodeDictStrMap):
    """Digital filter."""

    friendly_name = "digital filter"
    base_property = "dsp"
    property_name = "digital_filter"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "slow", "1": "sharp", "2": "short"}


class DualMono(CodeDictStrMap):
    """Dual mono."""

    friendly_name = "dual mono"
    base_property = "dsp"
    property_name = "dual_mono"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "CH1+CH2", "1": "CH1", "2": "CH2"}


class FixedPCM(CodeBoolMap):
    """Fixed PCM."""

    friendly_name = "fixed PCM"
    base_property = "dsp"
    property_name = "fixed_pcm"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class DynamicRange(CodeDictStrMap):
    """Dynamic range."""

    friendly_name = "dynamic range"
    base_property = "dsp"
    property_name = "dynamic_range"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "off", "1": "auto", "2": "mid", "3": "max"}


class LFEAttenuator(CodeIntMap):
    """LFE attenuator."""

    friendly_name = "LFE attenuator"
    base_property = "dsp"
    property_name = "lfe_attenuator"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"
    unit_of_measurement = "dB"
    ha_device_class = "signal_strength"
    ha_number_mode = "slider"

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


class SACDGain(CodeIntMap):
    """SACD gain."""

    friendly_name = "SACD gain"
    base_property = "dsp"
    property_name = "sacd_gain"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"
    unit_of_measurement = "dB"
    ha_device_class = "signal_strength"
    ha_number_mode = "slider"

    value_min = 0
    value_max = 6
    value_step = 6
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
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class CenterWidth(CodeIntMap):
    """Center width."""

    friendly_name = "center width"
    base_property = "dsp"
    property_name = "center_width"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"
    ha_number_mode = "slider"

    value_min = 0
    value_max = 7
    code_zfill = 1


class Panorama(CodeBoolMap):
    """Panorama."""

    friendly_name = "panorama"
    base_property = "dsp"
    property_name = "panorama"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class Dimension(CodeIntMap):
    """Dimension."""

    friendly_name = "dimension"
    base_property = "dsp"
    property_name = "dimension"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"
    ha_number_mode = "slider"

    value_min = -3
    value_max = 3
    value_offset = 50
    code_zfill = 2


class CenterImage(CodeFloatMap):
    """Center image (1step = 0.1)."""

    friendly_name = "center image"
    base_property = "dsp"
    property_name = "center_image"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"
    ha_number_mode = "slider"

    value_min = 0
    value_max = 1
    value_step = 0.1
    value_divider = 0.1
    code_zfill = 2


class Effect(CodeIntMap):
    """Effect (1step = 10)."""

    friendly_name = "effect"
    base_property = "dsp"
    property_name = "effect"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"
    ha_number_mode = "slider"

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
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "low", "1": "mid", "2": "high"}


class LoudnessManagement(CodeBoolMap):
    """Loudness management."""

    friendly_name = "loudness management"
    base_property = "dsp"
    property_name = "loudness_management"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class CenterSpread(CodeBoolMap):
    """Center spread."""

    friendly_name = "center spread"
    base_property = "dsp"
    property_name = "center_spread"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"


class RenderingMode(CodeDictStrMap):
    """Rendering mode."""

    friendly_name = "rendering mode"
    base_property = "dsp"
    property_name = "rendering_mode"
    supported_zones = {Zone.ALL}
    icon = "mdi:equalizer"

    code_map = {"0": "object base", "1": "channel base"}


PROPERTIES_DSP = [
    gen_set_property(MCACCMemorySet, {Zone.ALL: "MC"}),
    gen_set_property(PhaseControl, {Zone.ALL: "IS"}),
    gen_set_property(PhaseControlPlus, {Zone.ALL: "ATE"}),
    gen_set_property(VirtualSpeakers, {Zone.ALL: "VSP"}),
    gen_set_property(VirtualSoundback, {Zone.ALL: "VSB"}),
    gen_set_property(VirtualHeight, {Zone.ALL: "VHT"}),
    gen_set_property(VirtualWide, {Zone.ALL: "VWD"}),
    gen_set_property(VirtualDepth, {Zone.ALL: "VDP"}),
    gen_set_property(SoundRetriever, {Zone.ALL: "ATA"}),
    gen_set_property(SignalSelect, {Zone.ALL: "SDA"}),
    gen_set_property(InputAttenuator, {Zone.ALL: "SDB"}),
    gen_set_property(Equalizer, {Zone.ALL: "ATC"}),
    gen_set_property(StandingWave, {Zone.ALL: "ATD"}),
    gen_set_property(SoundDelay, {Zone.ALL: "ATF"}),
    gen_set_property(DigitalNoiseReduction, {Zone.ALL: "ATG"}),
    gen_set_property(DialogEnhancement, {Zone.ALL: "ATH"}),
    gen_set_property(AudioScaler, {Zone.ALL: "ATY"}),
    gen_set_property(HiBit, {Zone.ALL: "ATI"}),
    gen_set_property(UpSampling, {Zone.ALL: "ATZ"}),
    gen_set_property(DigitalFilter, {Zone.ALL: "ATV"}),
    gen_set_property(DualMono, {Zone.ALL: "ATJ"}),
    gen_set_property(FixedPCM, {Zone.ALL: "ATK"}),
    gen_set_property(DynamicRange, {Zone.ALL: "ATL"}),
    gen_set_property(LFEAttenuator, {Zone.ALL: "ATM"}),
    gen_set_property(SACDGain, {Zone.ALL: "ATN"}),
    gen_set_property(AutoDelay, {Zone.ALL: "ATO"}),
    gen_set_property(CenterWidth, {Zone.ALL: "ATP"}),
    gen_set_property(Panorama, {Zone.ALL: "ATQ"}),
    gen_set_property(Dimension, {Zone.ALL: "ATR"}),
    gen_set_property(CenterImage, {Zone.ALL: "ATS"}),
    gen_set_property(Effect, {Zone.ALL: "ATT"}),
    gen_set_property(HeightGain, {Zone.ALL: "ATU"}),
    gen_set_property(LoudnessManagement, {Zone.ALL: "ATW"}),
    gen_set_property(CenterSpread, {Zone.ALL: "ARA"}),
    gen_set_property(RenderingMode, {Zone.ALL: "ARB"}),
]
