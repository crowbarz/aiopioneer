"""AVR Settings related parsers"""

from aiopioneer.const import (
    MCACC_MEASUREMENT_STATUS,
    MCACC_MEASUREMENT_ERROR,
    STANDING_WAVE_FREQUENCIES
)
from .response import Response

class SettingsParsers():
    """AVR Setting related parsers."""

    @staticmethod
    def home_menu_status(raw: str, _param: dict, zone = None, command = "SSL") -> list:
        """Current home menu status"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="home_menu_status",
                            zone=zone,
                            value=(raw == "1"),
                            queue_commands=None))
        return parsed

    @staticmethod
    def mcacc_diagnostic_status(raw: str, _param: dict, zone = None, command = "SSJ") -> list:
        """Current diagnostic information for MCACC"""
        parsed = []

        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="mcacc_diagnostic_current_measurement",
                            zone=zone,
                            value=int(raw[:2]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="mcacc_diagnostic_total_measurement",
                            zone=zone,
                            value=int(raw[2:4]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="mcacc_diagnostic_status",
                            zone=zone,
                            value=MCACC_MEASUREMENT_STATUS.get(raw[5]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="mcacc_diagnostic_error",
                            zone=zone,
                            value=MCACC_MEASUREMENT_ERROR.get(raw[len(raw)-1]),
                            queue_commands=None))

        return parsed

    @staticmethod
    def standing_wave_setting(raw: str, _param: dict, zone = None, command = "SUU") -> list:
        """Current home menu status"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="standing_wave_memory",
                            zone=zone,
                            value=raw[:2],
                            queue_commands=None))
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="standing_wave_filter_channel",
                            zone=zone,
                            value=raw[2],
                            queue_commands=None))
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="standing_wave_filter_number",
                            zone=zone,
                            value=raw[3],
                            queue_commands=None))
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="standing_wave_frequency",
                            zone=zone,
                            value=STANDING_WAVE_FREQUENCIES.get(raw[4:6]),
                            queue_commands=None))
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="standing_wave_q",
                            zone=zone,
                            value=2.0+(int(raw[6:8])*0.2),
                            queue_commands=None))
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="standing_wave_att",
                            zone=zone,
                            value=int(raw[6:8])/2,
                            queue_commands=None))

        return parsed
