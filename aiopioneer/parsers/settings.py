"""AVR Settings related parsers"""

from aiopioneer.const import (
    MCACC_MEASUREMENT_STATUS,
    MCACC_MEASUREMENT_ERROR,
    STANDING_WAVE_FREQUENCIES,
    XOVER_SETTING
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
        """Current standing wave status"""
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

    @staticmethod
    def standing_wave_sw_trim(raw: str, _param: dict, zone = None, command = "SUV") -> list:
        """Current standing wave SW trim status"""

        mcacc_memory = raw[:2]
        value = (int(raw[2:4])-50)/2

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name=f"standing_wave_sw_trim.{mcacc_memory}",
                            zone=zone,
                            value=value,
                            queue_commands=None))
        return parsed

    @staticmethod
    def surround_position(raw: str, _param: dict, zone = None, command = "SSP") -> list:
        """Current surround position setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="surround_position",
                            zone=zone,
                            value="side" if (raw == "0") else "rear",
                            queue_commands=None))
        return parsed

    @staticmethod
    def x_over(raw: str, _param: dict, zone = None, command = "SSQ") -> list:
        """Current X.OVER setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="x_over",
                            zone=zone,
                            value=XOVER_SETTING.get(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def x_curve(raw: str, _param: dict, zone = None, command = "SST") -> list:
        """Current X-Curve setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="x_over",
                            zone=zone,
                            value=-(int(raw)/2),
                            queue_commands=None))
        return parsed

    @staticmethod
    def loudness_plus(raw: str, _param: dict, zone = None, command = "SSU") -> list:
        """Current Loudness Plus setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="loudness_plus",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def sbch_processing(raw: str, _param: dict, zone = None, command = "SSV") -> list:
        """Current SBch Processing (THX Audio) setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="sbch_processing",
                            zone=zone,
                            value="auto" if raw == "0" else "manual",
                            queue_commands=None))
        return parsed
