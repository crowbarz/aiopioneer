"""AVR Settings related parsers"""

from aiopioneer.const import (
    MCACC_MEASUREMENT_STATUS,
    MCACC_MEASUREMENT_ERROR,
    STANDING_WAVE_FREQUENCIES,
    XOVER_SETTING,
    OSD_LANGUAGES
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

    @staticmethod
    def speaker_setting(raw: str, _param: dict, zone = None, command = "SSG") -> list:
        """Current speaker setting"""

        value = raw[2]
        speaker = raw[:2]

        if speaker == "05":
            if value == "0":
                value = "small*2"
            elif value == "1":
                value = "large*1"
            elif value == "2":
                value = "large*2"
            elif value == "3":
                value = "no"
            elif value == "4":
                value = "small*1"
        elif speaker == "06":
            if value == "0":
                value = "yes"
            elif value == "1":
                value = "plus"
            elif value == "2":
                value = "no"
        else:
            if value == "0":
                value = "small"
            elif value == "1":
                value = "large"
            elif value == "2":
                value = "off"

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name=f"speaker_setting.{speaker}",
                            zone=zone,
                            value=value,
                            queue_commands=None))
        return parsed

    @staticmethod
    def input_level_adjust(raw: str, _param: dict, zone = None, command = "ILA") -> list:
        """Current Loudness Plus setting"""

        source = raw[0:2]
        value = (int(raw[2:4])-50)/2

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name=f"input_level.{source}",
                            zone=zone,
                            value=value,
                            queue_commands=None))
        return parsed

    @staticmethod
    def channel_level_mcacc(raw: str, _param: dict, zone = None, command = "SSR") -> list:
        """Current channel level for MCACC MEMORY setting"""

        memory = raw[0:2]
        speaker = raw[2:5].replace("_", "")
        value = (int(raw[5:7])-50)/2

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name=f"mcacc_channel_level.{memory}.{speaker}",
                            zone=zone,
                            value=value,
                            queue_commands=None))
        return parsed

    @staticmethod
    def speaker_distance_mcacc(raw: str, _param: dict, zone = None, command = "SSS") -> list:
        """Current speaker distance for MCACC MEMORY setting"""

        memory = raw[0:2]
        speaker = raw[2:5].replace("_", "")
        unit = "m" if raw[5] == "1" else "ft"
        value = float(raw[6:len(raw)])
        if unit == "m":
            value = value/100
        else:
            is_half = raw[10:12]=="12"
            value = raw[6:8] + "’." + raw[8:10] + "\"" + (" 1/2" if is_half else "")

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name=f"mcacc_speaker_distance.{memory}.{speaker}",
                            zone=zone,
                            value=value,
                            queue_commands=None))
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name=f"mcacc_speaker_distance.{memory}.{unit}",
                            zone=zone,
                            value=unit,
                            queue_commands=None))
        return parsed

    @staticmethod
    def thx_ultraselect2_sw(raw: str, _param: dict, zone = None, command = "SSW") -> list:
        """Current THX Ultra2/Select2 SW (THX Audio) setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="thx_ultraselect2",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def boundary_gain_compression(raw: str, _param: dict, zone = None, command = "SSX") -> list:
        """Current BGC (THX Audio) setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="boundary_gain_compression",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def re_equalization(raw: str, _param: dict, zone = None, command = "SSB") -> list:
        """Current Re-EQ (THX Audio) setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="re_equalization",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def osd_language(raw: str, _param: dict, zone = None, command = "SSE") -> list:
        """Current OSD language setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="osd_language",
                            zone=zone,
                            value=OSD_LANGUAGES.get(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def dhcp(raw: str, _param: dict, zone = None, command = "STA") -> list:
        """Current DHCP setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="network_dhcp",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def proxy_enabled(raw: str, _param: dict, zone = None, command = "STG") -> list:
        """Current proxy server setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="network_proxy_active",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def network_standby(raw: str, _param: dict, zone = None, command = "STJ") -> list:
        """Current network standby setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="network_standby",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def friendly_name(raw: str, _param: dict, zone = None, command = "SSO") -> list:
        """Current friendly name setting"""

        value = raw.split('"')[1]

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="friendly_name",
                            zone=zone,
                            value=value,
                            queue_commands=None))
        return parsed

    @staticmethod
    def parental_lock(raw: str, _param: dict, zone = None, command = "STK") -> list:
        """Current parental lock setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="parental_lock",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def parental_lock_password(raw: str, _param: dict, zone = None, command = "STL") -> list:
        """Current parental lock password setting"""

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="system",
                            property_name="parental_lock_password",
                            zone=zone,
                            value=raw,
                            queue_commands=None))
        return parsed
