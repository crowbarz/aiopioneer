"""aiopioneer response parsers for DSP functions. Most responses are only valid for Zone 1."""

from .code_map import (
    CodeMapBase,
    CodeIntMap,
    CodeFloatMap,
    CodeDictStrMap,
)


class DspMcaccMemorySet(CodeIntMap):
    """DSP MCACC memory set."""

    value_min = 1
    value_max = 6


class DspPhaseControl(CodeDictStrMap):
    """DSP phase control."""

    code_map = {"0": "off", "1": "on", "2": "full band on"}


class DspSignalSelect(CodeDictStrMap):
    """DSP signal select."""

    code_map = {"0": "AUTO", "1": "ANALOG", "2": "DIGITAL", "3": "HDMI"}


class DspPhaseControlPlus(CodeIntMap):
    """DSP phase control plus."""

    value_min = 0
    value_max = 16
    code_zfill = 2

    def __new__(cls, value: int | str) -> str:
        if value == "auto":
            return "97"
        return super().__new__(cls, value)

    @classmethod
    def code_to_value(cls, code: str) -> int:
        if code == "97":
            return "auto"
        return super().code_to_value(code)


class DspVirtualSpeakers(CodeDictStrMap):
    """DSP virtual speakers."""

    code_map = {"0": "auto", "1": "manual"}


class DspSoundDelay(CodeIntMap):
    """DSP sound delay. (1step=5ms)"""

    value_min = 0
    value_max = 800
    value_step = 5
    value_divider = 5
    code_zfill = 3


class DspAudioScaler(CodeDictStrMap):
    """DSP audio scaler."""

    code_map = {"0": "auto", "1": "manual"}


class DspDialogEnhancement(CodeDictStrMap):
    """DSP dialog enhancement."""

    code_map = {"0": "off", "1": "flat", "2": "+1", "3": "+2", "4": "+3", "5": "+4"}


class DspDualMono(CodeDictStrMap):
    """DSP dual mono."""

    code_map = {"0": "CH1+CH2", "1": "CH1", "2": "CH2"}


class DspDynamicRange(CodeDictStrMap):
    """DSP dynamic range."""

    code_map = {"0": "off", "1": "auto", "2": "mid", "3": "max"}


class DspLfeAttenuator(CodeIntMap):
    """DSP LFE attenuator."""

    value_min = -20
    value_max = 0
    code_zfill = 2
    value_divider = -1

    def __new__(cls, value: int | str) -> str:
        if value == "off":
            return "50"
        return super().__new__(cls, value)

    @classmethod
    def code_to_value(cls, code: str) -> int | str:
        if code == "50":
            return "off"
        return super().code_to_value(code)


class DspSacdGain(CodeMapBase):
    """DSP SACD gain."""

    @classmethod
    def value_to_code(cls, value: int) -> str:
        if value not in [0, 6]:
            raise ValueError(f"Value {value} not in [0, 6] for {cls.__name__}")
        return "1" if value == 6 else "0"

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return 6 if code == "1" else 0


class DspCenterWidth(CodeIntMap):
    """DSP center width."""

    value_min = 0
    value_max = 7


class DspDimension(CodeIntMap):
    """DSP dimension."""

    value_min = -3
    value_max = 3
    value_offset = 50


class DspCenterImage(CodeFloatMap):
    """DSP center image. (1step=0.1)"""

    value_min = 0
    value_max = 1
    value_step = 0.1
    value_divider = 0.1
    code_zfill = 2


class DspEffect(CodeIntMap):
    """DSP effect. (1step=10)"""

    value_min = 10
    value_max = 90
    value_step = 10
    value_divider = 10
    code_zfill = 2


class DspHeightGain(CodeDictStrMap):
    """DSP height gain."""

    code_map = {"0": "low", "1": "mid", "2": "high"}


class DspDigitalFilter(CodeDictStrMap):
    """DSP digital filter."""

    code_map = {"0": "slow", "1": "sharp", "2": "short"}


class DspUpSampling(CodeDictStrMap):
    """DSP up sampling."""

    code_map = {"0": "off", "1": "2 times", "2": "4 times"}


class DspVirtualDepth(CodeDictStrMap):
    """DSP virtual depth."""

    code_map = {"0": "off", "1": "min", "2": "mid", "3": "max"}


class DspRenderingMode(CodeDictStrMap):
    """DSP rendering mode."""

    code_map = {"0": "object base", "1": "channel base"}
