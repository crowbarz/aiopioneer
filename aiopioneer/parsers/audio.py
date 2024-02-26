"""Pioneer AVR response parsers for audio parameters."""

from aiopioneer.const import Zones, TONE_MODES, TONE_DB_VALUES
from aiopioneer.param import PARAM_LISTENING_MODES
from .response import Response


class AudioParsers:
    """Audio related parsers."""

    @staticmethod
    def listening_mode(raw: str, params: dict, zone=Zones.Z1, command="SR") -> list:
        """Defines a listening mode response parser for Zone 1 returning string values"""
        listening_mode = params.get(PARAM_LISTENING_MODES, {}).get(raw)
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
    def tone(raw: str, _param: dict, zone = Zones.Z1, command = "TO") -> list:
        """Defines a tone mode response parser for Zone 1 returning string values"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="tone",
                            property_name="status",
                            zone=zone,
                            value=TONE_MODES.get(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def tone_bass(raw: str, _param: dict, zone = Zones.Z1, command = "BA") -> list:
        """Defines a tone bass response parser for Zone 1 returning string values"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="tone",
                            property_name="bass",
                            zone=zone,
                            value=TONE_DB_VALUES.get(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def tone_treble(raw: str, _param: dict, zone = Zones.Z1, command = "TO") -> list:
        """Defines a tone treble response parser for Zone 1 returning string values"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="tone",
                            property_name="treble",
                            zone=zone,
                            value=TONE_DB_VALUES.get(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def channel_levels(raw: str, _param: dict, zone = Zones.Z1, command = "CLV") -> list:
        """Defines a channel levels resposne object for Zone 1 returning float values"""
        value = float(int(raw[3:]) - 50) / 2
        speaker = str(raw[:3]).strip("_").upper()

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="channel_levels",
                            property_name=speaker,
                            zone=zone,
                            value=value,
                            queue_commands=None))
        return parsed
