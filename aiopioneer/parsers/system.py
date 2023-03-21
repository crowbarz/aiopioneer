"""Core system related parsers for Pioneer AVRs."""

import re

from aiopioneer.param import PARAM_TUNER_AM_FREQ_STEP, PARAM_MHL_SOURCE, PARAM_SPEAKER_SYSTEM_MODES
from aiopioneer.const import (
    MEDIA_CONTROL_SOURCES,
    SPEAKER_MODES,
    HDMI_AUDIO_MODES,
    HDMI_OUT_MODES,
    PQLS_MODES,
    AMP_MODES,
    PANEL_LOCK,
    DIMMER_MODES,
    Zones
)
from .response import Response

class SystemParsers():
    """System related parsers."""

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def speaker_modes(raw: str, _param: dict, zone = Zones.Z1, command = "SPK") -> list:
        """Defines a speaker mode response. This response is only vaid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="speakers",
                            zone=zone,
                            value=SPEAKER_MODES.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def hdmi_out(raw: str, _param: dict, zone = Zones.Z1, command = "HO") -> list:
        """Defines a HDMI out mode response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="hdmi_out",
                            zone=zone,
                            value=HDMI_OUT_MODES.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def hdmi_audio(raw: str, _param: dict, zone = Zones.Z1, command = "HA") -> list:
        """Defines a HDMI audio mode response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="hdmi_audio",
                            zone=zone,
                            value=HDMI_AUDIO_MODES.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def pqls(raw: str, _param: dict, zone = Zones.Z1, command = "PQ") -> list:
        """Defines a PQLS mode response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="pqls",
                            zone=zone,
                            value=PQLS_MODES.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def dimmer(raw: str, _param: dict, zone = Zones.Z1, command = "SAA") -> list:
        """Defines a display dimmer response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="dimmer",
                            zone=zone,
                            value=DIMMER_MODES.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def sleep(raw: str, _param: dict, zone = Zones.Z1, command = "SAB") -> list:
        """Defines a sleep timer response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="sleep",
                            zone=zone,
                            value=int(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def amp_status(raw: str, _param: dict, zone = Zones.Z1, command = "SAC") -> list:
        """Defines a AMP status response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="status",
                            zone=zone,
                            value=AMP_MODES.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def panel_lock(raw: str, _param: dict, zone = Zones.Z1, command = "PKL") -> list:
        """Defines a panel lock response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="panel_lock",
                            zone=zone,
                            value=PANEL_LOCK.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def remote_lock(raw: str, _param: dict, zone = Zones.Z1, command = "RML") -> list:
        """Defines a remote lock response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="remote_lock",
                            zone=zone,
                            value=raw,
                            queue_commands=None))

        return parsed

    @staticmethod
    def speaker_system(raw: str, _param: dict, zone = Zones.Z1, command = "SSF") -> list:
        """Defines a speaker system mode response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="amp",
                            property_name="speaker_system",
                            zone=zone,
                            value=_param.get(PARAM_SPEAKER_SYSTEM_MODES).get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def mac_address(raw: str, _param: dict, zone = None, command = "SVB") -> list:
        """Defines a MAC response. This response is system wide."""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="mac_addr",
                            property_name=None,
                            zone=zone,
                            value=":".join([raw[i:i+2] for i in range(0, len(raw), 2)]),
                            queue_commands=None))

        return parsed

    @staticmethod
    def software_version(raw: str, _param: dict, zone = None, command = "SSI") -> list:
        """Defines a software version response. This response is system wide."""
        parsed = []
        matches = re.search(r'"([^)]*)"', raw)
        if matches:
            parsed.append(Response(raw=raw,
                                response_command=command,
                                base_property="software_version",
                                property_name=None,
                                zone=zone,
                                value=matches.group(1),
                                queue_commands=None))
        else:
            parsed.append(Response(raw=raw,
                                response_command=command,
                                base_property="software_version",
                                property_name=None,
                                zone=zone,
                                value="unknown",
                                queue_commands=None))

        return parsed

    @staticmethod
    def avr_model(raw: str, _param: dict, zone = None, command = "RGD") -> list:
        """Defines a model response. This response is system wide."""
        parsed = []
        matches = re.search(r"<([^>/]{5,})(/.[^>]*)?>", raw)
        if matches:
            parsed.append(Response(raw=raw,
                                response_command=command,
                                base_property="model",
                                property_name=None,
                                zone=zone,
                                value=matches.group(1),
                                queue_commands=None))
        else:
            parsed.append(Response(raw=raw,
                                response_command=command,
                                base_property="model",
                                property_name=None,
                                zone=zone,
                                value="unknown",
                                queue_commands=None))

        return parsed

    # The below responses are yet to be decoded properly due to little Pioneer documentation
    @staticmethod
    def audio_parameter_prohibitation(raw: str, _param: dict, zone = None, command = "AUA") -> list:
        """Defines a audio param prohibitaion response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property=None,
                            property_name=None,
                            zone=zone,
                            value=None,
                            queue_commands=None))

        return parsed

    @staticmethod
    def audio_parameter_working(raw: str, _param: dict, zone = None, command = "AUB") -> list:
        """Defines a audio param working response. This response is only valid for Zone 1"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property=None,
                            property_name=None,
                            zone=zone,
                            value=None,
                            queue_commands=None))

        return parsed
