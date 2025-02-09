"""aiopioneer response parsers for AVR settings."""

from typing import Tuple

from ..params import PioneerAVRParams
from .code_map import CodeDefault, CodeDictMap, CodeDictStrMap, CodeFloatMap
from .response import Response


class SurroundPosition(CodeDictStrMap):
    """Surround position."""

    code_map = {"0": "side", "1": "rear"}


class XOver(CodeDictStrMap):
    """X over."""

    code_map = {"0": "50Hz", "1": "80Hz", "2": "100Hz", "3": "150Hz", "4": "200Hz"}


class XCurve(CodeFloatMap):
    """X curve (1step=0.5)"""

    code_zfill = 2

    @classmethod
    def value_to_code(cls, value: float) -> str:
        if value % 0.5:
            raise ValueError(
                f"Value {value} is not a multiple of 0.5 for {cls.__name__}"
            )
        return str(abs(int(value * 2)))

    @classmethod
    def code_to_value(cls, code: str) -> float:
        return -(int(code) / 2)


class SbchProcessing(CodeDictStrMap):
    """SBch processing (THX Audio)."""

    code_map = {"0": "auto", "1": "manual"}


class OsdLanguage(CodeDictStrMap):
    """OSD language."""

    code_map = {
        "00": "English",
        "01": "French",
        "03": "German",
        "04": "Italian",
        "05": "Spanish",
        "06": "Dutch",
        "07": "Russian",
        "08": "Chinese (簡体)",
        "09": "Chinese (繁体)",
        "10": "Japanese",
    }


class StandbyPassthrough(CodeDictStrMap):
    """Standby Passthrough."""

    code_map = {
        "00": "OFF",
        "01": "LAST",
        "02": "BD",
        "03": "HDMI1",
        "04": "HDMI2",
        "05": "HDMI3",
        "06": "HDMI4",
        "07": "HDMI5",
        "08": "HDMI6",
        "09": "HDMI7",
        "10": "HDMI8",
    }


class SpeakerSettings(CodeDictMap):
    """Speaker settings."""

    code_map = {
        "05": {
            "0": "small*2",
            "1": "large*1",
            "2": "large*2",
            "3": "no",
            "4": "small*1",
        },
        "06": {"0": "yes", "1": "plus", "2": "no"},
        CodeDefault(): {"0": "small", "1": "large", "2": "off"},
    }

    ## NOTE: value_to_code unimplemented

    @classmethod
    def code_to_value(cls, code: str) -> Tuple[str, str]:
        """Convert code to value."""
        speaker = code[:2]
        speaker_type = code[2]
        value_map: dict[str, str] = super().code_to_value(speaker)
        return speaker, value_map.get(speaker_type, speaker_type)


class McaccMeasurementError(CodeDictStrMap):
    """MCACC measurement error."""

    code_map = {
        "0": "No error",
        "1": "No microphone",
        "2": "Ambient noise",
        "3": "Microphone",
        "4": "Unsupported connection",
        "5": "Reverse phase",
        "6": "Subwoofer level",
    }


class McaccMeasurementStatus(CodeDictStrMap):
    """MCACC measurement status."""

    code_map = {"0": "Inactive", "1": "Measuring"}


class StandingWaveFrequencies(CodeDictStrMap):
    """Standing Wave Frequencies."""

    code_map = {
        "00": "63Hz",
        "01": "65Hz",
        "02": "68Hz",
        "03": "71Hz",
        "04": "74Hz",
        "05": "78Hz",
        "06": "81Hz",
        "07": "85Hz",
        "08": "88Hz",
        "09": "92Hz",
        "10": "96Hz",
        "11": "101Hz",
        "12": "105Hz",
        "13": "110Hz",
        "14": "115Hz",
        "15": "120Hz",
        "16": "125Hz",
        "17": "131Hz",
        "18": "136Hz",
        "19": "142Hz",
        "20": "149Hz",
        "21": "155Hz",
        "22": "162Hz",
        "23": "169Hz",
        "24": "177Hz",
        "25": "185Hz",
        "26": "193Hz",
        "27": "201Hz",
        "28": "210Hz",
        "29": "220Hz",
        "30": "229Hz",
        "31": "239Hz",
        "32": "250Hz",
    }


class ExternalHdmiTriggerOptions(CodeDictStrMap):
    """External HDMI trigger options."""

    code_map = {
        "0": "OFF",
        "1": "HDMIOUT1",
        "2": "HDMIOUT2",
        "3": "HDMIOUT3",
        "4": "HDMIOUT4/HDBaseT",
    }


class SettingsParsers:
    """AVR Setting related parsers."""

    @staticmethod
    def mcacc_diagnostic_status(
        raw: str, _params: PioneerAVRParams, zone=None, command="SSJ"
    ) -> list[Response]:
        """Response parser for diagnostic information for MCACC."""
        parsed = []

        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="mcacc_diagnostic_current_measurement",
                zone=zone,
                value=int(raw[:2]),
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="mcacc_diagnostic_total_measurement",
                zone=zone,
                value=int(raw[2:4]),
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="mcacc_diagnostic_status",
                zone=zone,
                value=McaccMeasurementStatus[raw[5]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="mcacc_diagnostic_error",
                zone=zone,
                value=McaccMeasurementError[raw[len(raw) - 1]],
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def standing_wave_setting(
        raw: str, _params: PioneerAVRParams, zone=None, command="SUU"
    ) -> list[Response]:
        """Response parser for standing wave status."""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="standing_wave_memory",
                zone=zone,
                value=raw[:2],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="standing_wave_filter_channel",
                zone=zone,
                value=raw[2],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="standing_wave_filter_number",
                zone=zone,
                value=raw[3],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="standing_wave_frequency",
                zone=zone,
                value=StandingWaveFrequencies[raw[4:6]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="standing_wave_q",
                zone=zone,
                value=2.0 + (int(raw[6:8]) * 0.2),
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="standing_wave_att",
                zone=zone,
                value=int(raw[6:8]) / 2,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def standing_wave_sw_trim(
        raw: str, _params: PioneerAVRParams, zone=None, command="SUV"
    ) -> list[Response]:
        """Response parser for standing wave SW trim status."""
        mcacc_memory = raw[:2]
        value = (int(raw[2:4]) - 50) / 2

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name=f"standing_wave_sw_trim.{mcacc_memory}",
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def surround_position(
        raw: str, _params: PioneerAVRParams, zone=None, command="SSP"
    ) -> list[Response]:
        """Response parser for surround position setting."""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name="surround_position",
                zone=zone,
                value="side" if (raw == "0") else "rear",
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def speaker_setting(
        raw: str, _params: PioneerAVRParams, zone=None, command="SSG"
    ) -> list[Response]:
        """Response parser for speaker setting."""
        speaker, speaker_type = SpeakerSettings[raw]
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name=f"speaker_setting.{speaker}",
                zone=zone,
                value=speaker_type,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def input_level_adjust(
        raw: str, _params: PioneerAVRParams, zone=None, command="ILA"
    ) -> list[Response]:
        """Response parser for input level adjust setting."""
        source = raw[0:2]
        value = (int(raw[2:4]) - 50) / 2

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name=f"input_level.{source}",
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def channel_level_mcacc(
        raw: str, _params: PioneerAVRParams, zone=None, command="SSR"
    ) -> list[Response]:
        """Response parser for channel level for MCACC MEMORY setting."""
        memory = raw[0:2]
        speaker = raw[2:5].replace("_", "")
        value = (int(raw[5:7]) - 50) / 2

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name=f"mcacc_channel_level.{memory}.{speaker}",
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def speaker_distance_mcacc(
        raw: str, _params: PioneerAVRParams, zone=None, command="SSS"
    ) -> list[Response]:
        """Response parser for speaker distance for MCACC MEMORY setting."""
        memory = raw[0:2]
        speaker = raw[2:5].replace("_", "")
        unit = "m" if raw[5] == "1" else "ft"
        value = float(raw[6 : len(raw)])

        if unit == "m":
            value = value / 100
        else:
            is_half = raw[10:12] == "12"
            value = raw[6:8] + "’." + raw[8:10] + '"' + (" 1/2" if is_half else "")

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name=f"mcacc_speaker_distance.{memory}.{speaker}",
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name=f"mcacc_speaker_distance.{memory}.{unit}",
                zone=zone,
                value=unit,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def port_numbers(
        raw: str, _params: PioneerAVRParams, zone=None, command="SUM"
    ) -> list[Response]:
        """Response parser for TCP port numbers set for the AVR."""
        ports = [raw[i : i + 2] for i in range(0, len(raw), 2)]
        parsed = []
        index = 1

        for port in ports:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="system",
                    property_name=f"ip_control_port_{index}",
                    zone=zone,
                    value="disabled" if port == "99999" else port,
                    queue_commands=None,
                )
            )
            index += 1

        return parsed

    @staticmethod
    def external_hdmi_trigger(
        raw: str, _params: PioneerAVRParams, zone=None, command="STV"
    ) -> list[Response]:
        """Response parser for 12V Trigger 1 (HDMI Setup) setting."""
        trigger = "1" if command == "STV" else "2"

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="system",
                property_name=f"external_hdmi_trigger_{trigger}",
                zone=zone,
                value=ExternalHdmiTriggerOptions[raw],
                queue_commands=None,
            )
        )
        return parsed
