"""Pioneer AVR response parsers for tuner parameters."""

from aiopioneer.param import PARAM_TUNER_AM_FREQ_STEP
from .const import Response, Zones

def frequency_fm(raw: str, _param: dict) -> list:
    """Defines a FM Tuner Frequency response parser."""
    freq = float(raw) / 100
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="FR",
                         base_property="tuner",
                         property_name="band",
                         zone=Zones.Z1,
                         value="FM",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="FR",
                         base_property="tuner",
                         property_name="frequency",
                         zone=Zones.Z1,
                         value=freq,
                         queue_commands=None))

    return parsed

def frequency_am(raw: str, _param: dict) -> list:
    """Defines a AM Tuner Frequency response parser."""
    freq = float(raw)
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="FR",
                         base_property="tuner",
                         property_name="band",
                         zone=Zones.Z1,
                         value="AM",
                         queue_commands=None))

    if _param.get(PARAM_TUNER_AM_FREQ_STEP) is None:
        parsed[0].queue_commands=["_calculate_am_frequency_step"]

    parsed.append(Response(raw=raw,
                         response_command="FR",
                         base_property="tuner",
                         property_name="frequency",
                         zone=Zones.Z1,
                         value=freq,
                         queue_commands=None))

    return parsed

def preset(raw: str, _param: dict) -> list:
    """Defines a tuner preset response."""
    t_class = raw[:1]
    t_preset = int(raw[1:])

    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="PR",
                         base_property="tuner",
                         property_name="class",
                         zone=Zones.Z1,
                         value=t_class,
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="PR",
                         base_property="tuner",
                         property_name="preset",
                         zone=Zones.Z1,
                         value=t_preset,
                         queue_commands=None))

    return parsed
