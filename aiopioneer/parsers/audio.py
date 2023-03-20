"""Pioneer AVR response parsers for audio parameters."""

from aiopioneer.const import LISTENING_MODES, TONE_MODES, TONE_DB_VALUES
from .const import Response

def listening_mode(raw: str, _param: dict) -> list:
    """Defines a listening mode response parser for Zone 1 returning string values"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="sr",
                         base_property="listening_mode",
                         property_name=None,
                         zone="1",
                         value=LISTENING_MODES.get(raw)[0],
                         queue_commands=None))
    return parsed

def tone(raw: str, _param: dict, zone = "1", command = "TO") -> list:
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

def tone_bass(raw: str, _param: dict, zone = "1", command = "BA") -> list:
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

def tone_treble(raw: str, _param: dict, zone = "1", command = "TO") -> list:
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

def channel_levels(raw: str, _param: dict, zone = "1", command = "CLV") -> list:
    """Defines a channel levels resposne object for Zone 1 returning float values"""
    value = float(int(raw[6:]) - 50) / 2
    speaker = str(raw[3:6]).strip("_").upper()

    parsed = []
    parsed.append(Response(raw=raw,
                         response_command=command,
                         base_property="channel_levels",
                         property_name=speaker,
                         zone=zone,
                         value=value,
                         queue_commands=None))
    return parsed
