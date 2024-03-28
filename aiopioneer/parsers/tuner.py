"""aiopioneer response parsers for tuner parameters."""

from aiopioneer.param import PARAM_TUNER_AM_FREQ_STEP
from aiopioneer.const import Zones
from .response import Response


class TunerParsers:
    """Tuner response parsers."""

    @staticmethod
    def frequency_fm(raw: str, _params: dict, zone=Zones.Z1, command="FR") -> list:
        """Response parser for FM tuner frequency."""
        freq = float(raw) / 100
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="tuner",
                property_name="band",
                zone=zone,
                value="FM",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="tuner",
                property_name="frequency",
                zone=zone,
                value=freq,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def frequency_am(raw: str, params: dict, zone=Zones.Z1, command="FR") -> list:
        """Response parser AM tuner frequency."""
        freq = float(raw)
        parsed = []
        queue_commands = None
        if params.get(PARAM_TUNER_AM_FREQ_STEP) is None:
            queue_commands = ["_calculate_am_frequency_step"]

        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="tuner",
                property_name="band",
                zone=zone,
                value="AM",
                queue_commands=queue_commands,
            )
        )

        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="tuner",
                property_name="frequency",
                zone=zone,
                value=freq,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def preset(raw: str, _params: dict, zone=Zones.Z1, command="PR") -> list:
        """Response parser for tuner preset."""
        t_class = raw[:1]
        t_preset = int(raw[1:])

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="tuner",
                property_name="class",
                zone=zone,
                value=t_class,
                queue_commands=None,  # AVR automatically sends frequency response
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="tuner",
                property_name="preset",
                zone=zone,
                value=t_preset,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def am_frequency_step(raw: str, _params: dict, zone=None, command="SUQ") -> list:
        """Response parser for AM frequency step. (Supported on very few AVRs)"""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="_system_params",
                property_name=PARAM_TUNER_AM_FREQ_STEP,
                zone=zone,
                value=9 if raw == "0" else 10,
                queue_commands=None,
            )
        )
        return parsed
