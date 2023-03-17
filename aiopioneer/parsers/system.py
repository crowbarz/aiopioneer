"""Core system related parsers for Pioneer AVRs."""

from aiopioneer.param import PARAM_TUNER_AM_FREQ_STEP, PARAM_MHL_SOURCE, PARAM_SPEAKER_SYSTEM_MODES
from aiopioneer.const import (
    MEDIA_CONTROL_SOURCES,
    SPEAKER_MODES,
    HDMI_AUDIO_MODES,
    HDMI_OUT_MODES,
    PQLS_MODES,
    AMP_MODES,
    PANEL_LOCK
)
from .const import Response


def pwr(raw: str, _param: dict) -> list:
    """Defines a power response parser for Zone 1 returning values of True or False"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="pwr",
                         base_property="power",
                         property_name=None,
                         zone="1",
                         value=(raw == "0"),
                         queue_commands=None))
    return parsed

def apr(raw: str, _param: dict) -> list:
    """Defines a power response parser for Zone 2 returning values of True or False"""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = pwr(raw, _param)
    parsed[0].zone="2"
    parsed[0].response_command="apr"
    return parsed

def bpr(raw: str, _param: dict) -> list:
    """Defines a power response parser for Zone 3 returning values of True or False"""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = pwr(raw, _param)
    parsed[0].zone="3"
    parsed[0].response_command="bpr"
    return parsed

def zep(raw: str, _param: dict) -> list:
    """Defines a power response parser for HDZone (Z) returning values of True or False"""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = pwr(raw, _param)
    parsed[0].zone="Z"
    parsed[0].response_command="zep"
    return parsed

def fn(raw: str, _param: dict) -> list:
    """Defines a source input response parser for Zone 1 returning string values."""
    raw = "".join(filter(str.isnumeric, raw)) # Select only numeric values from raw
    parsed = []
    command_queue = []
    if raw == "02":
        command_queue.append("query_tuner_frequency")
        command_queue.append("query_tuner_preset")
        if _param.get(PARAM_TUNER_AM_FREQ_STEP) is None:
            command_queue.append("_calculate_am_frequency_step")

    parsed.append(Response(raw=raw,
                         response_command="fn",
                         base_property="source",
                         property_name=None,
                         zone="1",
                         value=raw,
                         queue_commands=command_queue))

    # Add a response for media_control_mode
    if raw in MEDIA_CONTROL_SOURCES:
        parsed.append(Response(raw=raw,
                         response_command="fn",
                         base_property="media_control_mode",
                         property_name=None,
                         zone="1",
                         value=MEDIA_CONTROL_SOURCES.get(raw),
                         queue_commands=command_queue))

    elif raw is _param.get(PARAM_MHL_SOURCE):
        # This source is a MHL source
        parsed.append(Response(raw=raw,
                         response_command="fn",
                         base_property="media_control_mode",
                         property_name=None,
                         zone="1",
                         value="MHL",
                         queue_commands=command_queue))
    else:
        # This source is a MHL source
        parsed.append(Response(raw=raw,
                         response_command="fn",
                         base_property="media_control_mode",
                         property_name=None,
                         zone="1",
                         value=None,
                         queue_commands=command_queue))

    return parsed

def z2f(raw: str, _param: dict) -> list:
    """Defines a source input response parser for Zone 2 returning string values."""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = fn(raw, _param)

    parsed[0].zone="2"
    parsed[0].response_command="z2f"
    parsed[1].zone="2"
    parsed[1].response_command="z2f"

    return parsed

def z3f(raw: str, _param: dict) -> list:
    """Defines a source input response parser for Zone 3 returning string values."""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = fn(raw, _param)

    parsed[0].zone="3"
    parsed[0].response_command="z3f"
    parsed[1].zone="3"
    parsed[1].response_command="z3f"

    return parsed

def zea(raw: str, _param: dict) -> list:
    """Defines a source input response parser for HDZone (Z) returning string values."""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = fn(raw, _param)

    parsed[0].zone="Z"
    parsed[0].response_command="zea"
    parsed[1].zone="Z"
    parsed[1].response_command="zea"

    return parsed

def vol(raw: str, _param: dict) -> list:
    """Defines a volume response parser for Zone 1 returning integer values"""
    raw = "".join(filter(str.isnumeric, raw)) # Select only numeric values from raw
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vol",
                         base_property="volume",
                         property_name=None,
                         zone="1",
                         value=int(raw),
                         queue_commands=None))

    return parsed

def zv(raw: str, _param: dict) -> list:
    """Defines a volume response parser for Zone 2 returning integer values"""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = vol(raw, _param)
    parsed[0].zone="2"
    parsed[0].response_command="zv"
    return parsed

def yv(raw: str, _param: dict) -> list:
    """Defines a volume response parser for Zone 3 returning integer values"""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = vol(raw, _param)
    parsed[0].zone="3"
    parsed[0].response_command="yv"
    return parsed

def xv(raw: str, _param: dict) -> list:
    """Defines a volume response parser for HDZone (Z) returning integer values"""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = vol(raw, _param)
    parsed[0].zone="Z"
    parsed[0].response_command="xv"
    return parsed

def mut(raw: str, _param: dict) -> list:
    """Defines a mute status response parser for Zone 1 returning values of True or False"""
    raw = "".join(filter(str.isnumeric, raw)) # Select only numeric values from raw
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="mut",
                         base_property="mute",
                         property_name=None,
                         zone="1",
                         value=(raw == "0"),
                         queue_commands=None))

    return parsed

def z2mut(raw: str, _param: dict) -> list:
    """Defines a mute status response parser for Zone 2 returning values of True or False"""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = mut(raw, _param)
    parsed[0].zone="2"
    parsed[0].response_command="z2mut"
    return parsed

def z3mut(raw: str, _param: dict) -> list:
    """Defines a mute status response parser for Zone 3 returning values of True or False"""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = mut(raw, _param)
    parsed[0].zone="3"
    parsed[0].response_command="z3mut"
    return parsed

def hzmut(raw: str, _param: dict) -> list:
    """Defines a mute status response parser for HDZone (Z) returning values of True or False"""
    # Reuse Zone 1 parser and override zone and response_command parameter
    parsed = mut(raw, _param)
    parsed[0].zone="Z"
    parsed[0].response_command="hzmut"
    return parsed

# AMP FUNCTIONS
def spk(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="spk",
                         base_property="amp",
                         property_name="speakers",
                         zone="1",
                         value=SPEAKER_MODES.get(raw),
                         queue_commands=None))

    return parsed

def ho(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ho",
                         base_property="amp",
                         property_name="hdmi_out",
                         zone="1",
                         value=HDMI_OUT_MODES.get(raw),
                         queue_commands=None))

    return parsed
    
def ha(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ho",
                         base_property="amp",
                         property_name="hdmi_audio",
                         zone="1",
                         value=HDMI_AUDIO_MODES.get(raw),
                         queue_commands=None))

    return parsed

def pq(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="pq",
                         base_property="amp",
                         property_name="pqls",
                         zone="1",
                         value=PQLS_MODES.get(raw),
                         queue_commands=None))

    return parsed

def saa(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="saa",
                         base_property="amp",
                         property_name="dimmer",
                         zone="1",
                         value=raw,
                         queue_commands=None))

    return parsed

def sab(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="sab",
                         base_property="amp",
                         property_name="dimmer",
                         zone="1",
                         value=int(raw),
                         queue_commands=None))

    return parsed

def sac(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="sac",
                         base_property="amp",
                         property_name="status",
                         zone="1",
                         value=AMP_MODES.get(raw),
                         queue_commands=None))

    return parsed

def pkl(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="pkl",
                         base_property="amp",
                         property_name="panel_lock",
                         zone="1",
                         value=PANEL_LOCK.get(raw),
                         queue_commands=None))

    return parsed

def rml(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="pkl",
                         base_property="amp",
                         property_name="remote_lock",
                         zone="1",
                         value=raw,
                         queue_commands=None))

    return parsed

def ssf(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ssf",
                         base_property="amp",
                         property_name="remote_lock",
                         zone="1",
                         value=_param.get(PARAM_SPEAKER_SYSTEM_MODES).get(raw),
                         queue_commands=None))
    
    return parsed

def aua(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="aua",
                         base_property=None,
                         property_name=None,
                         zone=None,
                         value=None,
                         queue_commands=None))

    return parsed

def aub(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="aub",
                         base_property=None,
                         property_name=None,
                         zone=None,
                         value=None,
                         queue_commands=None))

    return parsed
