"""aiopioneer response decoders for audio responses."""

from ..const import Zone
from ..params import AVRParams
from ..properties import AVRProperties
from .code_map import (
    CodeDynamicDictStrMap,
    CodeDynamicDictListMap,
    CodeDictStrMap,
    CodeIntMap,
    CodeFloatMap,
)
from .response import Response


class ChannelLevel(CodeFloatMap):
    """Channel level. (1step=0.5dB)"""

    friendly_name = "channel level"
    base_property = "channel_levels"  # NOTE: inconsistency

    value_min = -12
    value_max = 12
    value_step = 0.5
    value_divider = 0.5
    value_offset = 25
    code_zfill = 2

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for channel level."""
        code = response.code[3:]
        speaker = response.code[:3].strip("_").upper()
        response.update(code=code, property_name=speaker)
        return super().decode_response(response=response, params=params)


class ListeningMode(CodeDynamicDictListMap):
    """Listening mode."""

    friendly_name = "listening mode"
    base_property = "listening_mode"

    @classmethod
    def value_to_code(cls, value: str, properties: AVRProperties = None) -> str:
        if not issubclass(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        return cls.value_to_code_dynamic(value, code_map=properties.listening_modes_all)

    @classmethod
    def code_to_value(cls, code: str, properties: AVRProperties = None) -> str:
        if not issubclass(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        return cls.code_to_value_dynamic(code, code_map=properties.listening_modes_all)

    @classmethod
    def parse_args(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,  # pylint: disable=unused-argument
        params: AVRParams,  # pylint: disable=unused-argument
        properties: AVRProperties,
    ) -> str:
        return cls.parse_args_dynamic(
            command=command,
            args=args,
            zone=zone,
            params=params,
            properties=properties,
            code_map=properties.listening_modes_all,
        )

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for listening mode."""
        cls.decode_response_dynamic(
            response=response,
            params=params,
            code_map=response.properties.listening_modes_all,
        )
        return [
            response,
            response.clone(base_property="listening_mode_raw", value=response.code),
        ]


# pylint: disable=abstract-method
class AvailableListeningMode(CodeDynamicDictStrMap):
    """Available listening mode."""

    @classmethod
    def value_to_code(cls, value: str, properties: AVRProperties = None) -> str:
        if not issubclass(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        return cls.value_to_code_dynamic(
            value, code_map=properties.available_listening_modes
        )

    ## NOTE: code_to_value unimplemented


class ToneMode(CodeDictStrMap):
    """Tone mode."""

    friendly_name = "channel level"
    base_property = "tone"
    property_name = "status"

    code_map = {"0": "bypass", "1": "on"}


class ToneDb(CodeIntMap):
    """Tone dB value."""

    value_min = -6
    value_max = 6
    value_divider = -1
    value_offset = -6
    code_zfill = 2


class ToneBass(ToneDb):
    """Tone bass."""

    friendly_name = "tone bass"
    base_property = "tone"
    property_name = "bass"


class ToneTreble(ToneDb):
    """Tone treble."""

    friendly_name = "tone treble"
    base_property = "tone"
    property_name = "treble"


RESPONSE_DATA_AUDIO = [
    ["CLV", ChannelLevel, Zone.Z1],  # channel_levels
    ["ZGE", ChannelLevel, Zone.Z2],  # channel_levels
    ["ZHE", ChannelLevel, Zone.Z3],  # channel_levels
    ["SR", ListeningMode, Zone.ALL],  # listening_mode
    ["TO", ToneMode, Zone.Z1],  # tone.status
    ["BA", ToneBass, Zone.Z1],  # tone.bass
    ["TR", ToneTreble, Zone.Z1],  # tone.treble
    ["ZGA", ToneMode, Zone.Z2],  # tone.status
    ["ZGB", ToneBass, Zone.Z2],  # tone.bass
    ["ZGC", ToneTreble, Zone.Z2],  # tone.treble
]
