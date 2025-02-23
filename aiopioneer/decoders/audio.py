"""aiopioneer response decoders for audio parameters."""

from ..params import PioneerAVRParams
from .code_map import CodeDictStrMap, CodeDictListMap, CodeIntMap, CodeFloatMap
from .response import Response


class ChannelLevel(CodeFloatMap):
    """Channel level. (1step=0.5dB)"""

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
        params: PioneerAVRParams,
    ) -> list[Response]:
        """Response decoder for channel level."""
        code = response.code[3:]
        speaker = response.code[:3].strip("_").upper()
        response.update(code=code, property_name=speaker)
        return super().decode_response(response, params)


class ListeningMode(CodeDictListMap):
    """Listening mode."""

    ## code_map updated in _execute_local_command

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: PioneerAVRParams,
    ) -> list[Response]:
        """Response decoder for listening mode."""
        super().decode_response(response, params)
        return [
            response,
            response.clone(base_property="listening_mode_raw", value=response.code),
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
