"""Pioneer AVR response parsers for tuner parameters."""

from aiopioneer.param import PARAM_TUNER_AM_FREQ_STEP
from aiopioneer.const import Zones
from .response import Response

class TunerParsers():
    """Tuner related parsers"""

    @staticmethod
    def frequency_fm(raw: str, _param: dict, zone = Zones.Z1, command = "FR") -> list:
        """Defines a FM Tuner Frequency response parser."""
        freq = float(raw) / 100
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="tuner",
                            property_name="band",
                            zone=zone,
                            value="FM",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="tuner",
                            property_name="frequency",
                            zone=zone,
                            value=freq,
                            queue_commands=None))

        return parsed

    @staticmethod
    def frequency_am(raw: str, _param: dict, zone = Zones.Z1, command = "FR") -> list:
        """Defines a AM Tuner Frequency response parser."""
        freq = float(raw)
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="tuner",
                            property_name="band",
                            zone=zone,
                            value="AM",
                            queue_commands=None))

        if _param.get(PARAM_TUNER_AM_FREQ_STEP) is None:
            parsed[0].queue_commands=["_calculate_am_frequency_step"]

        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="tuner",
                            property_name="frequency",
                            zone=zone,
                            value=freq,
                            queue_commands=None))

        return parsed

    @staticmethod
    def preset(raw: str, _param: dict, zone = Zones.Z1, command = "PR") -> list:
        """Defines a tuner preset response."""
        t_class = raw[:1]
        t_preset = int(raw[1:])

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="tuner",
                            property_name="class",
                            zone=zone,
                            value=t_class,
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="tuner",
                            property_name="preset",
                            zone=zone,
                            value=t_preset,
                            queue_commands=None))

        return parsed

    @staticmethod
    def am_frequency_step(raw: str, _param: dict, zone = None, command = "SUQ") -> list:
        """Response parser for frequency step.
        NOTE: This is supported on very few AVRs"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="_params",
                            property_name=PARAM_TUNER_AM_FREQ_STEP,
                            zone=zone,
                            value=9 if raw == "0" else 10,
                            queue_commands=None))

        return parsed
