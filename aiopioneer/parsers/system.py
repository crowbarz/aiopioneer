"""aiopioneer response parsers for core system responses."""

import re

from ..const import (
    SOURCE_TUNER,
    MEDIA_CONTROL_SOURCES,
    Zone,
)
from ..params import (
    PioneerAVRParams,
    PARAM_QUERY_SOURCES,
    PARAM_MHL_SOURCE,
    PARAM_SPEAKER_SYSTEM_MODES,
)
from .code_map import CodeBoolMap, CodeDictStrMap, CodeIntMap
from .response import Response


class SpeakerMode(CodeDictStrMap):
    """Speaker mode."""

    code_map = {"0": "off", "1": "A", "2": "B", "3": "A+B"}


class HdmiOut(CodeDictStrMap):
    """HDMI out."""

    code_map = {"0": "all", "1": "HDMI 1", "2": "HDMI 2"}


class Hdmi3Out(CodeBoolMap):
    """HDMI3 out."""

    code_true = "1"
    code_false = "3"


class HdmiAudio(CodeDictStrMap):
    """HDMI audio."""

    code_map = {"0": "amp", "1": "passthrough"}


class Pqls(CodeDictStrMap):
    """PQLS."""

    code_map = {"0": "off", "1": "auto"}


class Dimmer(CodeDictStrMap):
    """Dimmer."""

    code_map = {
        "0": "brightest",
        "1": "bright",
        "2": "dark",
        "3": "off",
    }


class SleepTime(CodeIntMap):
    """Sleep time remaining."""

    value_min = 0
    value_max = 90
    value_step = 30
    code_zfill = 3


class AmpMode(CodeDictStrMap):
    """AMP status."""

    code_map = {
        "0": "amp on",
        "1": "amp front off",
        "2": "amp front & center off",
        "3": "amp off",
    }


class PanelLock(CodeDictStrMap):
    """Panel lock."""

    code_map = {"0": "off", "1": "panel only", "2": "panel + volume"}


class SystemParsers:
    """Core system parsers."""

    @staticmethod
    def power(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="PWR"
    ) -> list[Response]:
        """Response parser for zone power status."""
        parsed = []
        command_queue = []
        if power_state := raw == "0":
            command_queue.append(["_oob", "_power_on", zone])
        else:
            command_queue.append(["_oob", "_delayed_query_basic", 2])

        parsed.extend(
            [
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="power",
                    property_name=None,
                    zone=zone,
                    value=power_state,
                    queue_commands=command_queue,
                ),
                Response(  # also trigger global update
                    raw=raw,
                    response_command=command,
                    base_property=None,
                    property_name=None,
                    zone=Zone.ALL,
                    value=power_state,
                    queue_commands=None,
                ),
            ]
        )
        return parsed

    @staticmethod
    def input_source(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="FN"
    ) -> list[Response]:
        """Response parser for current zone source input."""
        raw = "".join(filter(str.isnumeric, raw))  # select only numeric values from raw
        parsed = []
        command_queue = []
        if raw == SOURCE_TUNER:
            command_queue.extend(["query_tuner_frequency", "query_tuner_preset"])
        command_queue.append(["_oob", "_delayed_query_basic", 2])

        parsed.extend(
            [
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="_get_source_name",
                    property_name=None,
                    zone=zone,
                    value=raw,
                    queue_commands=command_queue,
                ),
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="source_id",
                    property_name=None,
                    zone=zone,
                    value=raw,
                    queue_commands=command_queue,
                ),
                Response(  # also trigger global update
                    raw=raw,
                    response_command=command,
                    base_property=None,
                    property_name=None,
                    zone=Zone.ALL,
                    value=raw,
                    queue_commands=None,
                ),
            ]
        )

        ## Add a response for media_control_mode
        if raw in MEDIA_CONTROL_SOURCES:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="media_control_mode",
                    property_name=None,
                    zone=zone,
                    value=MEDIA_CONTROL_SOURCES.get(raw),
                    queue_commands=None,
                )
            )
        elif raw is params.get_param(PARAM_MHL_SOURCE):
            ## This source is a MHL source
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="media_control_mode",
                    property_name=None,
                    zone=zone,
                    value="MHL",
                    queue_commands=None,
                )
            )
        else:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="media_control_mode",
                    property_name=None,
                    zone=zone,
                    value=None,
                    queue_commands=None,
                )
            )
        return parsed

    @staticmethod
    def speaker_system(
        raw: str, params: PioneerAVRParams, zone=None, command="SSF"
    ) -> list[Response]:
        """Response parser for speaker system mode. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="speaker_system",
                zone=zone,
                value=params.get_param(PARAM_SPEAKER_SYSTEM_MODES).get(raw),
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="speaker_system_raw",
                zone=zone,
                value=raw,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def mac_address(
        raw: str, _params: PioneerAVRParams, zone=None, command="SVB"
    ) -> list[Response]:
        """Response parser for system MAC address."""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="mac_addr",
                property_name=None,
                zone=zone,
                value=":".join([raw[i : i + 2] for i in range(0, len(raw), 2)]),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def software_version(
        raw: str, _params: PioneerAVRParams, zone=None, command="SSI"
    ) -> list[Response]:
        """Response parser for system software version."""
        parsed = []
        matches = re.search(r'"([^)]*)"', raw)
        if matches:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="software_version",
                    property_name=None,
                    zone=zone,
                    value=matches.group(1),
                    queue_commands=None,
                )
            )
        else:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="software_version",
                    property_name=None,
                    zone=zone,
                    value="unknown",
                    queue_commands=None,
                )
            )
        return parsed

    @staticmethod
    def avr_model(
        raw: str, _params: PioneerAVRParams, zone=None, command="RGD"
    ) -> list[Response]:
        """Response parser for AVR model."""
        parsed = []
        matches = re.search(r"<([^>/]{5,})(/.[^>]*)?>", raw)
        if matches:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="model",
                    property_name=None,
                    zone=zone,
                    value=matches.group(1),
                    queue_commands=None,
                )
            )
        else:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="model",
                    property_name=None,
                    zone=zone,
                    value="unknown",
                    queue_commands=None,
                )
            )
        return parsed

    @staticmethod
    def input_name(
        raw: str, params: PioneerAVRParams, zone=None, command="RGB"
    ) -> list[Response]:
        """Response parser for input friendly names."""
        source_number = raw[:2]
        source_name = raw[3:]

        parsed = []
        if not params.get_param(PARAM_QUERY_SOURCES):
            ## Only update AVR source mappings if AVR sources are being queried
            return parsed
        ## Clear current source ID from source mappings via PioneerAVR.clear_source_id
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="_clear_source_id",
                property_name=None,
                zone=zone,
                value=source_number,
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="source_name_to_id",
                property_name=source_name,
                zone=zone,
                value=source_number,
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="source_id_to_name",
                property_name=source_number,
                zone=zone,
                value=source_name,
                queue_commands=None,
            )
        )
        return parsed

    ## The below responses are yet to be decoded properly due to little Pioneer documentation
    @staticmethod
    def audio_parameter_prohibitation(
        raw: str, _params: PioneerAVRParams, zone=None, command="AUA"
    ) -> list[Response]:
        """Response parser for audio param prohibitation. (Zone 1 only)"""
        parsed = []
        command_queue = [["_delayed_query_basic", 2]]
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property=None,
                property_name=None,
                zone=zone,
                value=None,
                queue_commands=command_queue,
            )
        )
        return parsed

    @staticmethod
    def audio_parameter_working(
        raw: str, _params: PioneerAVRParams, zone=None, command="AUB"
    ) -> list[Response]:
        """Response parser for audio param working. (Zone 1 only)"""
        parsed = []
        command_queue = [["_delayed_query_basic", 2]]
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property=None,
                property_name=None,
                zone=zone,
                value=None,
                queue_commands=command_queue,
            )
        )
        return parsed
