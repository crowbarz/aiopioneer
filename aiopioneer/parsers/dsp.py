"""aiopioneer response parsers for DSP functions. Most responses are only valid for Zone 1."""

from aiopioneer.const import AVRCodeStrMap
from .code_map import AVRCodeMapBase, AVRCodeIntMap, AVRCodeInt50Map, AVRCodeFloatMap


class DSPFloat10Map(AVRCodeFloatMap):
    """DSP float map * 10."""

    @classmethod
    def value_to_code(cls, value: float) -> str:
        return str(int(value * 10))

    @classmethod
    def code_to_value(cls, code: str) -> float:
        return float(code) / 10


class DspMcaccMemorySet(AVRCodeIntMap):
    """DSP MCACC memory set."""

    value_min = 1
    value_max = 6


class DSPPhaseControl(AVRCodeStrMap):
    """DSP phase control."""

    code_map = {"0": "off", "1": "on", "2": "full band on"}


class DSPSignalSelect(AVRCodeStrMap):
    """DSP signal select."""

    code_map = {"0": "AUTO", "1": "ANALOG", "2": "DIGITAL", "3": "HDMI"}


class DSPPhaseControlPlus(AVRCodeIntMap):
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


class DSPSoundDelay(DSPFloat10Map):
    """DSP sound delay. (1step=0.1frame)"""

    value_min = 0
    value_max = 800
    code_zfill = 3


class DSPAudioScaler(AVRCodeStrMap):
    """DSP audio scaler."""

    code_map = {"0": "AUTO", "1": "MANUAL"}


class DSPDialogEnhancement(AVRCodeStrMap):
    """DSP dialog enhancement."""

    code_map = {"0": "off", "1": "flat", "2": "+1", "3": "+2", "4": "+3", "5": "+4"}


class DSPDualMono(AVRCodeStrMap):
    """DSP dual mono."""

    code_map = {"0": "CH1+CH2", "1": "CH1", "2": "CH2"}


class DSPDynamicRange(AVRCodeStrMap):
    """DSP dyanmic range."""

    code_map = {"0": "off", "1": "auto", "2": "mid", "3": "max"}


class DSPLfeAttenuator(AVRCodeIntMap):
    """DSP LFE attenuator."""

    value_min = -20
    value_max = 0
    code_zfill = 2

    def __new__(cls, value: int | bool) -> str:
        if value is False:
            return "50"
        return super().__new__(cls, abs(value))

    @classmethod
    def code_to_value(cls, code: str) -> int | bool:
        if code == "50":
            return False
        return -super().code_to_value(code)


class DSPSacdGain(AVRCodeMapBase):
    """DSP SACD gain."""

    @classmethod
    def value_to_code(cls, value: int) -> str:
        if value not in [0, 6]:
            raise ValueError(f"Value {value} not in [1, 6] for {cls.__name__}")
        return str(int(bool(value)))

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return 6 if code else 0


class DSPCenterWidth(AVRCodeIntMap):
    """DSP center width."""

    value_min = 0
    value_max = 7


class DSPDimension(AVRCodeInt50Map):
    """DSP dimension."""

    value_min = -3
    value_max = 3


class DSPCenterImage(DSPFloat10Map):
    """DSP center image. (1step=0.1)"""

    value_min = 0
    value_max = 10
    code_zfill = 2


class DSPEffect(AVRCodeIntMap):
    """DSP effect. (1step=10)"""

    value_min = 10
    value_max = 90
    code_zfill = 2

    @classmethod
    def value_to_code(cls, value: int) -> str:
        if value % 10:
            raise ValueError(f"Value {value} is not divisible by 10 for {cls.__name__}")
        return str(int(value / 10))

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return int(code) * 10


class DSPHeightGain(AVRCodeStrMap):
    """DSP height gain."""

    code_map = {"0": "low", "1": "mid", "2": "high"}


class DSPDigitalFilter(AVRCodeStrMap):
    """DSP digital filter."""

    code_map = {"0": "slow", "1": "sharp", "2": "short"}


class DSPUpSampling(AVRCodeStrMap):
    """DSP up sampling."""

    code_map = {"0": "off", "1": "2 times", "2": "4 times"}


class DSPVirtualDepth(AVRCodeStrMap):
    """DSP virtual depth."""

    code_map = {"0": "off", "1": "min", "2": "mid", "3": "max"}


class DSPRenderingMode(AVRCodeStrMap):
    """DSP rendering mode."""

    code_map = {"0": "object base", "1": "channel base"}
