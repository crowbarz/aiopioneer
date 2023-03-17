"""Pioneer AVR response parsers for audio parameters."""

from aiopioneer.const import LISTENING_MODES, TONE_MODES, TONE_DB_VALUES, CHANNEL_LEVELS_OBJ
from .const import Response

def sr(raw: str, _param: dict) -> list:
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

def to(raw: str, _param: dict) -> list:
    """Defines a tone mode response parser for Zone 1 returning string values"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="to",
                         base_property="tone",
                         property_name="status",
                         zone="1",
                         value=TONE_MODES.get(raw),
                         queue_commands=None))
    return parsed

def ba(raw: str, _param: dict) -> list:
    """Defines a tone bass response parser for Zone 1 returning string values"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ba",
                         base_property="tone",
                         property_name="bass",
                         zone="1",
                         value=TONE_DB_VALUES.get(raw),
                         queue_commands=None))
    return parsed

def tr(raw: str, _param: dict) -> list:
    """Defines a tone treble response parser for Zone 1 returning string values"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="tr",
                         base_property="tone",
                         property_name="treble",
                         zone="1",
                         value=TONE_DB_VALUES.get(raw),
                         queue_commands=None))
    return parsed

def zga(raw: str, _param: dict) -> list:
    """Defines a tone mode response parser for Zone 2 returning string values"""
    # Reuse the response parser from Zone 1 but override the zone before returning
    parsed = to(raw, _param)
    parsed[0].zone="2"
    return parsed

def zgb(raw: str, _param: dict) -> list:
    """Defines a tone bass response parser for Zone 2 returning string values"""
    # Reuse the response parser from Zone 1 but override the zone before returning
    parsed = ba(raw, _param)
    parsed[0].zone="2"
    return parsed

def zgc(raw: str, _param: dict) -> list:
    """Defines a tone treble response parser for Zone 2 returning string values"""
    # Reuse the response parser from Zone 1 but override the zone before returning
    parsed = tr(raw, _param)
    parsed[0].zone="2"
    return parsed

def clv(raw: str, _param: dict) -> list:
    value = float(int(raw[6:]) - 50) / 2
    speaker = str(raw[3:6]).strip("_").upper()

    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="clv",
                         base_property="channel_levels",
                         property_name=speaker,
                         zone="1",
                         value=value,
                         queue_commands=None))
    return parsed

def zge(raw: str, _param: dict) -> list:
    parsed = clv(raw, _param)
    parsed[0].zone = "2"
    parsed[0].response_command = "zge"
    return parsed

def zhe(raw: str, _param: dict) -> list:
    parsed = clv(raw, _param)
    parsed[0].zone = "3"
    parsed[0].response_command = "zhe"
    return parsed
