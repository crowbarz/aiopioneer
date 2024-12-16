"""aiopioneer response parsers for core system responses."""

import re

from ..const import (
    SOURCE_TUNER,
    MEDIA_CONTROL_SOURCES,
    SPEAKER_MODES,
    HDMI_AUDIO_MODES,
    HDMI_OUT_MODES,
    PQLS_MODES,
    AMP_MODES,
    PANEL_LOCK,
    DIMMER_MODES,
    Zones,
)
from ..param import (
    PioneerAVRParams,
    PARAM_QUERY_SOURCES,
    PARAM_MHL_SOURCE,
    PARAM_SPEAKER_SYSTEM_MODES,
)
from .response import Response


class SystemParsers:
    """Core system parsers."""

    @staticmethod
    def power(
        raw: str, _params: PioneerAVRParams, zone=Zones.Z1, command="PWR"
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
                    zone=Zones.ALL,
                    value=power_state,
                    queue_commands=None,
                ),
            ]
        )
        return parsed

    @staticmethod
    def input_source(
        raw: str, params: PioneerAVRParams, zone=Zones.Z1, command="FN"
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
                    base_property="source",
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
                    zone=Zones.ALL,
                    value=(raw == "0"),
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
    def volume(
        raw: str, _params: PioneerAVRParams, zone=Zones.Z1, command="VOL"
    ) -> list[Response]:
        """Response parser for zone volume setting."""
        raw = "".join(filter(str.isnumeric, raw))  # select only numeric values from raw
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="volume",
                property_name=None,
                zone=zone,
                value=int(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def mute(
        raw: str, _params: PioneerAVRParams, zone=Zones.Z1, command="MUT"
    ) -> list[Response]:
        """Response parser for zone mute status."""
        raw = "".join(filter(str.isnumeric, raw))  # select only numeric values from raw
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="mute",
                property_name=None,
                zone=zone,
                value=(raw == "0"),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def speaker_modes(
        raw: str, _params: PioneerAVRParams, zone=None, command="SPK"
    ) -> list[Response]:
        """Response parser for speaker mode. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="speakers",
                zone=zone,
                value=SPEAKER_MODES.get(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def hdmi_out(
        raw: str, _params: PioneerAVRParams, zone=None, command="HO"
    ) -> list[Response]:
        """Response parser for HDMI out setting. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="hdmi_out",
                zone=zone,
                value=HDMI_OUT_MODES.get(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def hdmi_audio(
        raw: str, _params: PioneerAVRParams, zone=None, command="HA"
    ) -> list[Response]:
        """Response parser for HDMI audio mode. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="hdmi_audio",
                zone=zone,
                value=HDMI_AUDIO_MODES.get(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def pqls(
        raw: str, _params: PioneerAVRParams, zone=None, command="PQ"
    ) -> list[Response]:
        """Response parser for PQLS mode. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="pqls",
                zone=zone,
                value=PQLS_MODES.get(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def dimmer(
        raw: str, _params: PioneerAVRParams, zone=None, command="SAA"
    ) -> list[Response]:
        """Response parser for display dimmer. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="dimmer",
                zone=zone,
                value=DIMMER_MODES.get(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def sleep(
        raw: str, _params: PioneerAVRParams, zone=None, command="SAB"
    ) -> list[Response]:
        """Response parser for sleep timer. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="sleep",
                zone=zone,
                value=int(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def amp_status(
        raw: str, _params: PioneerAVRParams, zone=None, command="SAC"
    ) -> list[Response]:
        """Response parser for AMP status. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="status",
                zone=zone,
                value=AMP_MODES.get(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def panel_lock(
        raw: str, _params: PioneerAVRParams, zone=None, command="PKL"
    ) -> list[Response]:
        """Response parser for panel lock. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="panel_lock",
                zone=zone,
                value=PANEL_LOCK.get(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def remote_lock(
        raw: str, _params: PioneerAVRParams, zone=None, command="RML"
    ) -> list[Response]:
        """Response parser for remote lock. (Zone 1 only)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="remote_lock",
                zone=zone,
                value=raw,
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
