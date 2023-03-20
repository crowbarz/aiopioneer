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
from .const import Response, Zones


def power(raw: str, _param: dict, zone = Zones.Z1, command = "PWR") -> list:
    """Defines a power response parser for Zone 1 returning values of True or False"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command=command,
                         base_property="power",
                         property_name=None,
                         zone=zone,
                         value=(raw == "0"),
                         queue_commands=None))
    return parsed

def input_source(raw: str, _param: dict, zone = Zones.Z1, command = "FN") -> list:
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
                         response_command=command,
                         base_property="source",
                         property_name=None,
                         zone=zone,
                         value=raw,
                         queue_commands=command_queue))

    # Add a response for media_control_mode
    if raw in MEDIA_CONTROL_SOURCES:
        parsed.append(Response(raw=raw,
                         response_command=command,
                         base_property="media_control_mode",
                         property_name=None,
                         zone=zone,
                         value=MEDIA_CONTROL_SOURCES.get(raw),
                         queue_commands=command_queue))

    elif raw is _param.get(PARAM_MHL_SOURCE):
        # This source is a MHL source
        parsed.append(Response(raw=raw,
                         response_command=command,
                         base_property="media_control_mode",
                         property_name=None,
                         zone=zone,
                         value="MHL",
                         queue_commands=command_queue))
    else:
        # This source is a MHL source
        parsed.append(Response(raw=raw,
                         response_command=command,
                         base_property="media_control_mode",
                         property_name=None,
                         zone=zone,
                         value=None,
                         queue_commands=command_queue))

    return parsed

def volume(raw: str, _param: dict, zone = Zones.Z1, command = "VOL") -> list:
    """Defines a volume response parser for Zone 1 returning integer values"""
    raw = "".join(filter(str.isnumeric, raw)) # Select only numeric values from raw
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command=command,
                         base_property="volume",
                         property_name=None,
                         zone=zone,
                         value=int(raw),
                         queue_commands=None))

    return parsed

def mute(raw: str, _param: dict, zone = Zones.Z1, command = "MUT") -> list:
    """Defines a mute status response parser for Zone 1 returning values of True or False"""
    raw = "".join(filter(str.isnumeric, raw)) # Select only numeric values from raw
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command=command,
                         base_property="mute",
                         property_name=None,
                         zone=zone,
                         value=(raw == "0"),
                         queue_commands=None))

    return parsed

# AMP FUNCTIONS
def speaker_modes(raw: str, _param: dict) -> list:
    """Defines a speaker mode response. This response is only vaid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="SPK",
                         base_property="amp",
                         property_name="speakers",
                         zone=Zones.Z1,
                         value=SPEAKER_MODES.get(raw),
                         queue_commands=None))

    return parsed

def hdmi_out(raw: str, _param: dict) -> list:
    """Defines a HDMI out mode response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="HO",
                         base_property="amp",
                         property_name="hdmi_out",
                         zone=Zones.Z1,
                         value=HDMI_OUT_MODES.get(raw),
                         queue_commands=None))

    return parsed
    
def hdmi_audio(raw: str, _param: dict) -> list:
    """Defines a HDMI audio mode response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="HA",
                         base_property="amp",
                         property_name="hdmi_audio",
                         zone=Zones.Z1,
                         value=HDMI_AUDIO_MODES.get(raw),
                         queue_commands=None))

    return parsed

def pqls(raw: str, _param: dict) -> list:
    """Defines a PQLS mode response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="PQ",
                         base_property="amp",
                         property_name="pqls",
                         zone=Zones.Z1,
                         value=PQLS_MODES.get(raw),
                         queue_commands=None))

    return parsed

def dimmer(raw: str, _param: dict) -> list:
    """Defines a display dimmer response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="SAA",
                         base_property="amp",
                         property_name="dimmer",
                         zone=Zones.Z1,
                         value=raw,
                         queue_commands=None))

    return parsed

def sleep(raw: str, _param: dict) -> list:
    """Defines a sleep timer response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="SAB",
                         base_property="amp",
                         property_name="sleep",
                         zone=Zones.Z1,
                         value=int(raw),
                         queue_commands=None))

    return parsed

def amp_status(raw: str, _param: dict) -> list:
    """Defines a AMP status response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="SAC",
                         base_property="amp",
                         property_name="status",
                         zone=Zones.Z1,
                         value=AMP_MODES.get(raw),
                         queue_commands=None))

    return parsed

def panel_lock(raw: str, _param: dict) -> list:
    """Defines a panel lock response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="PKL",
                         base_property="amp",
                         property_name="panel_lock",
                         zone=Zones.Z1,
                         value=PANEL_LOCK.get(raw),
                         queue_commands=None))

    return parsed

def remote_lock(raw: str, _param: dict) -> list:
    """Defines a remote lock response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="RML",
                         base_property="amp",
                         property_name="remote_lock",
                         zone=Zones.Z1,
                         value=raw,
                         queue_commands=None))

    return parsed

def speaker_system(raw: str, _param: dict) -> list:
    """Defines a speaker system mode response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="SSF",
                         base_property="amp",
                         property_name="speaker_system",
                         zone=Zones.Z1,
                         value=_param.get(PARAM_SPEAKER_SYSTEM_MODES).get(raw),
                         queue_commands=None))
    
    return parsed

# The below responses are yet to be decoded properly due to little Pioneer documentation
def audio_parameter_prohibitation(raw: str, _param: dict) -> list:
    """Defines a audio param prohibitaion response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="AUA",
                         base_property=None,
                         property_name=None,
                         zone=None,
                         value=None,
                         queue_commands=None))

    return parsed

def audio_parameter_working(raw: str, _param: dict) -> list:
    """Defines a audio param working response. This response is only valid for Zone 1"""
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="AUB",
                         base_property=None,
                         property_name=None,
                         zone=None,
                         value=None,
                         queue_commands=None))

    return parsed
