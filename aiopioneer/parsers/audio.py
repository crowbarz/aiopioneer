"""aiopioneer response parsers for audio parameters."""

from ..params import PioneerAVRParams
from ..properties import PioneerAVRProperties
from .code_map import CodeDictStrMap, CodeDictListMap, CodeIntMap, CodeFloatMap
from .response import Response


class ChannelLevel(CodeFloatMap):
    """Channel level."""

    value_min = -12
    value_max = 12
    value_divider = 0.5
    value_offset = 25
    code_zfill = 2

    @classmethod
    def parse_response(
        cls,
        response: Response,
        params: PioneerAVRParams,
        properties: PioneerAVRProperties,
    ) -> list[Response]:
        """Response parser for channel level."""
        code = response.raw[3:]
        speaker = response.raw[:3].strip("_").upper()
        response.update(raw=code, property_name=speaker)
        super().parse_response(response, params, properties)
        return [response]


class ListeningMode(CodeDictListMap):
    """Listening mode."""

    ## code_map updated in _execute_local_command

    @classmethod
    def parse_response(
        cls,
        response: Response,
        params: PioneerAVRParams,
        properties: PioneerAVRProperties,
    ) -> list[Response]:
        """Response parser for listening mode."""
        super().parse_response(response, params, properties)
        return [
            response,
            response.clone(base_property="listening_mode_raw", value=response.raw),
        ]


class AvailableListeningMode(CodeDictStrMap):
    """Available listening mode."""

    ## code_map updated in PioneerAVR.update_listening_modes


class ToneMode(CodeDictStrMap):
    """Tone mode."""

    code_map = {"0": "bypass", "1": "on"}


class ToneDb(CodeIntMap):
    """Tone dB."""

    value_min = -6
    value_max = 6
    value_divider = -1
    value_offset = -6
    code_zfill = 2
