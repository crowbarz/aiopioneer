"""Pioneer AVR response parsers for video parameters."""

from aiopioneer.const import VIDEO_RESOLUTION_MODES, ADVANCED_VIDEO_ADJUST_MODES, Zones
from .parse import Response

def vtb(raw: str, _param: dict) -> list:
    value = int(raw)
    if value == 1:
        value = "on"
    else:
        value = "off"

    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vtb",
                         base_property="video",
                         property_name="converter",
                         zone="1",
                         value=value,
                         queue_commands=None))
    return parsed

def vtc(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vtc",
                         base_property="video",
                         property_name="resolution",
                         zone="1",
                         value=VIDEO_RESOLUTION_MODES.get(raw),
                         queue_commands=None))
    return parsed

def vtd(raw: str, _param: dict) -> list:
    value = int(raw)
    if value == 0:
        value = "auto"
    elif value == 2:
        value = "on"
    else:
        value = "off"

    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vtd",
                         base_property="video",
                         property_name="pure_cinema",
                         zone="1",
                         value=value,
                         queue_commands=None))
    return parsed

def vte(raw: str, _param: dict) -> list:
    value = int(raw)
    if value < 55:
        value = value - 50

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="vte",
                            base_property="video",
                            property_name="prog_motion",
                            zone="1",
                            value=value,
                            queue_commands=None))
        return parsed

def vtf(raw: str, _param: dict) -> list:
    value = int(raw)
    if value == 0:
        value = "off"
    elif value == "1":
        value = "on"
    else:
        value = "auto"

    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vtf",
                         base_property="video",
                         property_name="stream_smoother",
                         zone="1",
                         value=value,
                         queue_commands=None))
    return parsed

def vtg(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vtg",
                         base_property="video",
                         property_name="advanced_video_adjust",
                         zone="1",
                         value=ADVANCED_VIDEO_ADJUST_MODES.get(raw),
                         queue_commands=None))
    return parsed

def vth(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vth",
                         base_property="video",
                         property_name="ynr",
                         zone="1",
                         value=int(raw) - 50,
                         queue_commands=None))
    return parsed

def vti(raw: str, _param: dict) -> list:
    parsed = vth(raw, _param)
    parsed[0].property_name = "cnr"
    parsed[0].response_command = "vti"
    return parsed

def vtj(raw: str, _param: dict) -> list:
    parsed = vth(raw, _param)
    parsed[0].property_name = "bnr"
    parsed[0].response_command = "vtj"
    return parsed

def vtk(raw: str, _param: dict) -> list:
    parsed = vth(raw, _param)
    parsed[0].property_name = "mnr"
    parsed[0].response_command = "vtk"
    return parsed

def vtl(raw: str, _param: dict) -> list:
    parsed = vth(raw, _param)
    parsed[0].property_name = "detail"
    parsed[0].response_command = "vtl"
    return parsed

def vtm(raw: str, _param: dict) -> list:
    parsed = vth(raw, _param)
    parsed[0].property_name = "sharpness"
    parsed[0].response_command = "vtm"
    return parsed

def vtn(raw: str, _param: dict) -> list:
    parsed = vth(raw, _param)
    parsed[0].property_name = "brightness"
    parsed[0].response_command = "vtn"
    return parsed

def vto(raw: str, _param: dict) -> list:
    parsed = vth(raw, _param)
    parsed[0].property_name = "contrast"
    parsed[0].response_command = "vto"
    return parsed

def vtp(raw: str, _param: dict) -> list:
    parsed = vth(raw, _param)
    parsed[0].property_name = "hue"
    parsed[0].response_command = "vtp"
    return parsed

def vtq(raw: str, _param: dict) -> list:
    parsed = vth(raw, _param)
    parsed[0].property_name = "chroma"
    parsed[0].response_command = "vtq"
    return parsed

def vtr(raw: str, _param: dict) -> list:
    value = int(raw)
    if value == 0:
        value = 0
    elif value == 1:
        value = 7.5

    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vtr",
                         base_property="video",
                         property_name="black_setup",
                         zone="1",
                         value=value,
                         queue_commands=None))
    return parsed

def vts(raw: str, _param: dict) -> list:
    value = int(raw)
    if value == 0:
        value = "passthrough"
    elif value == 1:
        value = "normal"

    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vts",
                         base_property="video",
                         property_name="aspect",
                         zone="1",
                         value=value,
                         queue_commands=None))
    return parsed
