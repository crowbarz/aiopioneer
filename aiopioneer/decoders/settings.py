"""aiopioneer response decoders for AVR settings."""

from ..const import Zone
from ..params import AVRParams
from .code_map import (
    CodeDefault,
    CodeMapBase,
    CodeStrMap,
    CodeDictMap,
    CodeDictStrMap,
    CodeIntMap,
    CodeFloatMap,
)
from .response import Response


class McaccDiagnosticStatus(CodeMapBase):
    """MCACC diagnostic status."""

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for MCACC diagnostic status."""

        def decode_child_response(
            property_name: str, code: str, code_map: CodeMapBase
        ) -> list[Response]:
            """Decode a child response."""
            child_response = response.clone(property_name=property_name, code=code)
            return code_map.decode_response(child_response, params)

        return [
            *decode_child_response(
                property_name="mcacc_diagnostic_current_measurement",
                code=response.code[:2],
                code_map=McaccDiagnosticCurrentMeasurement,
            ),
            *decode_child_response(
                property_name="mcacc_diagnostic_total_measurement",
                code=response.code[2:4],
                code_map=McaccDiagnosticTotalMeasurement,
            ),
            *decode_child_response(
                property_name="mcacc_diagnostic_status",
                code=response.code[5],
                code_map=McaccMeasurementStatus,
            ),
            *decode_child_response(
                property_name="mcacc_diagnostic_error",
                code=response.code[-1],
                code_map=McaccMeasurementError,
            ),
        ]


class McaccDiagnosticCurrentMeasurement(CodeIntMap):
    """MCACC diagnostic current measurement."""

    code_zfill = 2


class McaccDiagnosticTotalMeasurement(CodeIntMap):
    """MCACC diagnostic total measurement."""

    code_zfill = 2


class McaccMeasurementStatus(CodeDictStrMap):
    """MCACC measurement status."""

    code_map = {"0": "inactive", "1": "measuring"}


class McaccMeasurementError(CodeDictStrMap):
    """MCACC measurement error."""

    code_map = {
        "0": "no error",
        "1": "no microphone",
        "2": "ambient noise",
        "3": "microphone",
        "4": "unsupported connection",
        "5": "reverse phase",
        "6": "subwoofer level",
    }


class StandingWaveStatus(CodeMapBase):
    """Standing wave status."""

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for standing wave status."""

        def decode_child_response(
            property_name: str, code: str, code_map: CodeMapBase
        ) -> list[Response]:
            """Decode a child response."""
            child_response = response.clone(property_name=property_name, code=code)
            return code_map.decode_response(child_response, params)

        return [
            *decode_child_response(
                property_name="standing_wave_memory",
                code=response.code[:2],
                code_map=StandingWaveMemory,
            ),
            *decode_child_response(
                property_name="standing_wave_filter_channel",
                code=response.code[2],
                code_map=StandingWaveFilterChannel,
            ),
            *decode_child_response(
                property_name="standing_wave_filter_number",
                code=response.code[3],
                code_map=StandingWaveFilterNumber,
            ),
            *decode_child_response(
                property_name="standing_wave_frequency",
                code=response.code[4:6],
                code_map=StandingWaveFrequency,
            ),
            *decode_child_response(
                property_name="standing_wave_q",
                code=response.code[6:8],
                code_map=StandingWaveQ,
            ),
            *decode_child_response(
                property_name="standing_wave_attenuator",
                code=response.code[8:10],  ## NOTE: assumed
                code_map=StandingWaveAttenuator,
            ),
        ]


class StandingWaveMemory(CodeStrMap):
    """Standing wave memory."""

    code_len = 2


class StandingWaveFilterChannel(CodeStrMap):
    """Standing wave filter channel."""

    code_len = 1


class StandingWaveFilterNumber(CodeStrMap):
    """Standing wave filter number."""

    code_len = 1


class StandingWaveFrequency(CodeDictStrMap):
    """Standing wave frequency."""

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


class StandingWaveQ(CodeFloatMap):
    """Standing wave Q."""

    code_zfill = 2
    value_offset = -2
    value_divider = 0.2
    value_step = 0.2


class StandingWaveAttenuator(CodeFloatMap):
    """Standing wave attenuator."""

    code_zfill = 2
    value_divider = 0.5
    value_step = 0.5


class StandingWaveSwTrim(CodeFloatMap):
    """Standing wave SW trim."""

    code_zfill = 2
    code_offset = -50
    value_divider = 0.5

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for Standing wave SW trim."""
        mcacc_memory = response.code[:2]
        response.code = response.code[2:4]
        response.property_name = f"standing_wave_sw_trim.{mcacc_memory}"
        return super().decode_response(response=response, params=params)

    ## NOTE: value_to_code not implemented


class SurroundPosition(CodeDictStrMap):
    """Surround position."""

    code_map = {"0": "side", "1": "rear"}


class XOver(CodeDictStrMap):
    """X over."""

    code_map = {"0": "50Hz", "1": "80Hz", "2": "100Hz", "3": "150Hz", "4": "200Hz"}


class XCurve(CodeFloatMap):
    """X curve (1step=0.5)"""

    code_zfill = 2
    value_min = -49.5
    value_max = 0
    value_step = 0.5
    value_divider = -0.5


class SbchProcessing(CodeDictStrMap):
    """SBch processing (THX Audio)."""

    code_map = {"0": "auto", "1": "manual"}


class SpeakerSettings(CodeDictMap):
    """Speaker setting."""

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

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for speaker setting."""
        speaker = response.code[:2]
        response.code = speaker_sub = response.code[2]
        response.property_name = f"speaker_setting.{speaker}"
        super().decode_response(response=response, params=params)
        response.value = response.value.get(speaker_sub, speaker_sub)
        return [response]

    ## NOTE: value_to_code unimplemented


class McaccChannelLevel(CodeFloatMap):
    """MCACC channel level."""

    code_offset = -50
    value_divider = 0.5

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for MCACC channel level."""
        memory = response.code[0:2]
        speaker = response.code[2:5].replace("_", "")
        response.code = response.code[5:7]
        response.property_name = f"mcacc_channel_level.{memory}.{speaker}"
        return super().decode_response(response=response, params=params)

    ## NOTE: value_to_code unimplemented


class McaccSpeakerDistance(CodeFloatMap):
    """MCACC speaker distance."""

    value_divider = 0.01

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for MCACC speaker distance."""
        memory = response.code[0:2]
        speaker = response.code[2:5].replace("_", "")
        response.code = response.code[5:]
        response.property_name = f"mcacc_speaker_distance.{memory}.{speaker}"
        super().decode_response(response=response, params=params)
        unit = "m" if isinstance(response.value, float) else "ft"
        return [
            response,
            response.clone(property_name=response.property_name + ".unit", value=unit),
        ]

    ## NOTE: value_to_code unimplemented

    @classmethod
    def code_to_value(cls, code: str) -> str | float:
        unit_metric = code[0] == "1"
        if unit_metric:
            return super().code_to_value(code[1:])
        value_ft = int(code[1:3])
        value_in = int(code[3:5])
        value_half_in = " 1/2" if code[5:7] == "12" else ""
        return f"{value_ft}'.{value_in}{value_half_in}\""


class InputLevelAdjust(CodeFloatMap):
    """Input level adjust."""

    code_offset = -50
    value_divider = 0.5

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for input level adjust."""
        source = response.code[0:2]
        response.code = response.code[2:4]
        response.property_name = f"input_level.{source}"
        return super().decode_response(response=response, params=params)

    ## NOTE: value_to_code unimplemented


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


class PortNumbers(CodeMapBase):
    """Enabled TCP port numbers."""

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for enabled TCP port numbers."""

        ports = [int(response.code[i : i + 5]) for i in range(0, len(response.code), 5)]

        def port_response(index: int) -> Response:
            port = ports[index]
            return response.clone(
                property_name=f"ip_control_port_{index}",
                value="disabled" if port == 99999 else port,
            )

        return [port_response(i) for i in range(len(ports))]

    ## NOTE: value_to_code unimplemented


class StandbyPassthrough(CodeDictStrMap):
    """Standby Passthrough."""

    code_map = {
        "00": "off",
        "01": "last",
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


class ExternalHdmiTrigger(CodeDictStrMap):
    """External HDMI trigger."""

    code_map = {
        "0": "off",
        "1": "HDMI OUT 1",
        "2": "HDMI OUT 2",
        "3": "HDMI OUT 3",
        "4": "HDMI OUT 4/HDBaseT",
    }

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for 12V Trigger 1 (HDMI Setup)."""

        response.update_zones = {Zone.ALL}
        return super().decode_response(response=response, params=params)
