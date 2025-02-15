"""aiopioneer response parsers for audio parameters."""

from ..const import Zone
from ..params import PioneerAVRParams, PARAM_ALL_LISTENING_MODES
from .code_map import CodeDictStrMap, CodeIntMap
from .response import Response


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


class AudioParsers:
    """Audio response parsers."""

    @staticmethod
    def listening_mode(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="SR"
    ) -> list[Response]:
        """Response parser for listening_mode. (Zone 1 only)"""
        listening_mode = params.get_param(PARAM_ALL_LISTENING_MODES, {}).get(raw)
        mode_name = listening_mode[0] if isinstance(listening_mode, list) else raw

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="listening_mode",
                property_name=None,
                zone=zone,
                value=mode_name,
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="listening_mode_raw",
                property_name=None,
                zone=zone,
                value=raw,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def channel_levels(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="CLV"
    ) -> list[Response]:
        """Response parser for channel levels."""
        value = float(int(raw[3:]) - 50) / 2
        speaker = str(raw[:3]).strip("_").upper()

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="channel_levels",
                property_name=speaker,
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        return parsed
