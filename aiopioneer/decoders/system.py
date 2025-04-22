"""aiopioneer response decoders for AVR system responses."""

from ..const import Zone
from ..params import AVRParams, PARAM_SPEAKER_SYSTEM_MODES
from ..properties import AVRProperties
from .code_map import (
    CodeDefault,
    CodeMapSequence,
    CodeMapBlank,
    CodeBoolMap,
    CodeStrMap,
    CodeDynamicDictStrMap,
    CodeDictMap,
    CodeDictStrMap,
    CodeIntMap,
    CodeFloatMap,
)
from .response import Response


class SpeakerSystemIndex(CodeIntMap):
    """Listening mode index."""

    friendly_name = "speaker system"

    value_min = 0
    value_max = 99
    code_zfill = 2


class SpeakerSystem(CodeDynamicDictStrMap):
    """Speaker system."""

    friendly_name = "speaker system"
    base_property = "system"
    property_name = "speaker_system"

    index_map_class = SpeakerSystemIndex

    @classmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
    ) -> str:
        if isinstance(args[0], int):
            return SpeakerSystemIndex.value_to_code(args[0])
        return cls.parse_args_dynamic(
            command=command,
            args=args,
            zone=zone,
            params=params,
            properties=properties,
            code_map=params.get_param(PARAM_SPEAKER_SYSTEM_MODES, {}),
        )

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for speaker system."""
        cls.decode_response_dynamic(
            response=response,
            params=params,
            code_map=params.get_param(PARAM_SPEAKER_SYSTEM_MODES, {}),
        )
        return [
            response,
            response.clone(
                property_name="speaker_system_raw",
                value=SpeakerSystemIndex.code_to_value(response.code),
            ),
        ]


class HomeMenuStatus(CodeBoolMap):
    """Home menu status."""

    friendly_name = "home menu status"
    base_property = "system"
    property_name = "home_menu_status"


class McaccDiagnosticCurrentMeasurement(CodeIntMap):
    """MCACC diagnostic current measurement."""

    friendly_name = "MCACC diagnostic current measurement"
    base_property = "system"
    property_name = "mcacc_diagnostic_current_measurement"

    code_zfill = 2


class McaccDiagnosticTotalMeasurement(CodeIntMap):
    """MCACC diagnostic total measurement."""

    friendly_name = "MCACC diagnostic total measurement"
    base_property = "system"
    property_name = "mcacc_diagnostic_total_measurement"

    code_zfill = 2


class McaccDiagnosticMeasuring(CodeDictStrMap):
    """MCACC diagnostic measuring."""

    friendly_name = "MCACC diagnostic measuring"
    base_property = "system"
    property_name = "mcacc_diagnostic_measuring"

    code_map = {"0": "inactive", "1": "measuring"}


class McaccDiagnosticError(CodeDictStrMap):
    """MCACC measurement error."""

    friendly_name = "MCACC diagnostic error"
    base_property = "system"
    property_name = "mcacc_diagnostic_error"

    code_map = {
        "0": "no error",
        "1": "no microphone",
        "2": "ambient noise",
        "3": "microphone",
        "4": "unsupported connection",
        "5": "reverse phase",
        "6": "subwoofer level",
    }


class McaccDiagnosticStatus(CodeMapSequence):
    """MCACC diagnostic status."""

    friendly_name = "MCACC diagnostic status"
    base_property = "system"
    property_name = "mcacc_diagnostic_status"

    code_map_sequence = [
        McaccDiagnosticCurrentMeasurement,  # [:2]
        McaccDiagnosticTotalMeasurement,  # [2:4]
        CodeMapBlank(1),
        McaccDiagnosticMeasuring,  # [5]
        CodeMapBlank(-1),
        McaccDiagnosticError,  # [-1]
    ]


class StandingWaveMemory(CodeStrMap):
    """Standing wave memory."""

    friendly_name = "standing wave memory"
    base_property = "system"
    property_name = "standing_wave_memory"

    code_len = 2


class StandingWaveFilterChannel(CodeStrMap):
    """Standing wave filter channel."""

    friendly_name = "standing wave filter channel"
    base_property = "system"
    property_name = "standing_wave_filter_channel"

    code_len = 1


class StandingWaveFilterNumber(CodeStrMap):
    """Standing wave filter number."""

    friendly_name = "standing wave filter number"
    base_property = "system"
    property_name = "standing_wave_filter_number"

    code_len = 1


class StandingWaveFrequency(CodeDictStrMap):
    """Standing wave frequency."""

    friendly_name = "standing wave frequency"
    base_property = "system"
    property_name = "standing_wave_frequency"

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

    friendly_name = "standing wave Q"
    base_property = "system"
    property_name = "standing_wave_q"

    code_zfill = 2
    value_offset = -2
    value_divider = 0.2
    value_step = 0.2


class StandingWaveAttenuator(CodeFloatMap):
    """Standing wave attenuator."""

    friendly_name = "standing wave attenuator"
    base_property = "system"
    property_name = "standing_wave_attenuator"

    code_zfill = 2
    value_divider = 0.5
    value_step = 0.5


class StandingWaveStatus(CodeMapSequence):
    """Standing wave status."""

    friendly_name = "standing wave status"
    base_property = "system"
    property_name = "standing_wave_status"  # unused

    code_map_sequence = [
        StandingWaveMemory,  # [:2]
        StandingWaveFilterChannel,  # [2]
        StandingWaveFilterNumber,  # [3]
        StandingWaveFrequency,  # [4:6]
        StandingWaveQ,  # [6:8]
        StandingWaveAttenuator,  # [8:10] NOTE: assumed
    ]


class StandingWaveSwTrim(CodeFloatMap):
    """Standing wave SW trim."""

    friendly_name = "standing wave SW trim"
    base_property = "system"
    property_name = "standing_wave_sw_trim"  # unused

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

    friendly_name = "surround position"
    base_property = "system"
    property_name = "surround_position"

    code_map = {"0": "side", "1": "rear"}


class XOver(CodeDictStrMap):
    """X over."""

    friendly_name = "X over"
    base_property = "system"
    property_name = "x_over"

    code_map = {"0": "50Hz", "1": "80Hz", "2": "100Hz", "3": "150Hz", "4": "200Hz"}


class XCurve(CodeFloatMap):
    """X curve (1step=0.5)"""

    friendly_name = "X curve"
    base_property = "system"
    property_name = "x_curve"

    code_zfill = 2
    value_min = -49.5
    value_max = 0
    value_step = 0.5
    value_divider = -0.5


class LoudnessPlus(CodeBoolMap):
    """Loudness plus."""

    friendly_name = "loudness plus"
    base_property = "system"
    property_name = "loudness_plus"


class SbchProcessing(CodeDictStrMap):
    """SBch processing (THX Audio)."""

    friendly_name = "SBch processing"
    base_property = "system"
    property_name = "sbch_processing"

    code_map = {"0": "auto", "1": "manual"}


class SpeakerSettings(CodeDictMap):
    """Speaker setting."""

    friendly_name = "speaker setting"
    base_property = "system"
    property_name = "speaker_setting"  # unused

    code_len = 3
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

    friendly_name = "MCACC channel level"
    base_property = "system"
    property_name = "mcacc_channel_level"  # unused

    code_zfill = 7
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

    friendly_name = "MCACC speaker distance"
    base_property = "system"
    property_name = "mcacc_speaker_distance"  # unused

    code_zfill = 12
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
            return super().code_to_value(code=code[1:])
        value_ft = int(code[1:3])
        value_in = int(code[3:5])
        value_half_in = " 1/2" if code[5:7] == "12" else ""
        return f"{value_ft}'.{value_in}{value_half_in}\""


class InputLevel(CodeFloatMap):
    """Input level."""

    friendly_name = "input level"
    base_property = "system"
    property_name = "input_level"  # unused

    code_zfill = 2
    code_offset = -50
    value_min = -12
    value_max = 12
    value_divider = 0.5

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for input level."""
        source = response.code[0:2]
        response.code = response.code[2:4]
        response.property_name = f"input_level.{source}"
        return super().decode_response(response=response, params=params)

    ## NOTE: value_to_code unimplemented


class ThxUltraselect2(CodeBoolMap):
    """thx ultra/select2."""

    friendly_name = "THX ultra/select2"
    base_property = "system"
    property_name = "thx_ultraselect2"


class BoundaryGainCompression(CodeBoolMap):
    """boundary gain compression."""

    friendly_name = "boundary gain"
    base_property = "system"
    property_name = "boundary_gain_compression"


class ReEqualization(CodeBoolMap):
    """re-equalization."""

    friendly_name = "re-equalization"
    base_property = "system"
    property_name = "re_equalization"


class OsdLanguage(CodeDictStrMap):
    """OSD language."""

    friendly_name = "OSD language"
    base_property = "system"
    property_name = "osd_language"

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


class NetworkDhcp(CodeBoolMap):
    """Network DHCP."""

    friendly_name = "network dhcp"
    base_property = "system"
    property_name = "network_dhcp"


class NetworkProxyActive(CodeBoolMap):
    """Network proxy active."""

    friendly_name = "network proxy active"
    base_property = "system"
    property_name = "network_proxy_active"


class NetworkStandby(CodeBoolMap):
    """Network standby."""

    friendly_name = "network standby"
    base_property = "system"
    property_name = "network_standby"


class FriendlyName(CodeStrMap):
    """Friendly name."""

    friendly_name = "friendly name"
    base_property = "system"
    property_name = "friendly_name"


class ParentalLock(CodeBoolMap):
    """Parental lock."""

    friendly_name = "parental lock"
    base_property = "system"
    property_name = "parental_lock"


class ParentalLockPassword(CodeStrMap):
    """Parental lock password."""

    friendly_name = "parental lock password"
    base_property = "system"
    property_name = "parental_lock_password"


class IpControlPorts(CodeStrMap):
    """Enabled IP control ports."""

    friendly_name = "enabled IP control ports"
    base_property = "system"
    property_name = "ip_control_port"  # unused

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for enabled IP control ports."""
        cls.set_response_properties(response)
        ports = [response.code[i : i + 5] for i in range(0, len(response.code), 5)]

        def port_response(index: int) -> Response:
            port = int(port_str := ports[index])
            return response.clone(
                code=port_str,
                property_name=f"ip_control_port_{index}",
                value="disabled" if port == 99999 else port,
            )

        return [port_response(i) for i in range(len(ports))]

    ## NOTE: value_to_code unimplemented


class HdmiControl(CodeBoolMap):
    """HDMI control."""

    friendly_name = "HDMI control"
    base_property = "system"
    property_name = "hdmi_control"


class HdmiControlMode(CodeBoolMap):
    """HDMI control mode."""

    friendly_name = "HDMI control mode"
    base_property = "system"
    property_name = "hdmi_control_mode"


class HdmiArc(CodeBoolMap):
    """HDMI arc."""

    friendly_name = "HDMI arc"
    base_property = "system"
    property_name = "hdmi_arc"


class PqlsForBackup(CodeBoolMap):
    """PQLS for backup."""

    friendly_name = "PQLS for backup"
    base_property = "system"
    property_name = "pqls_for_backup"


class StandbyPassthrough(CodeDictStrMap):
    """Standby passthrough."""

    friendly_name = "standby passthrough"
    base_property = "system"
    property_name = "standby_passthrough"

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

    friendly_name = "external HDMI trigger"
    base_property = "system"
    property_name = "external_hdmi_trigger"

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


class ExternalHdmiTrigger1(ExternalHdmiTrigger):
    """External HDMI trigger 1."""

    property_name = "external_hdmi_trigger_1"


class ExternalHdmiTrigger2(ExternalHdmiTrigger):
    """External HDMI trigger 2."""

    property_name = "external_hdmi_trigger_2"


class SpeakerBLink(CodeBoolMap):
    """Speaker B link."""

    friendly_name = "speaker B link"
    base_property = "system"
    property_name = "speaker_b_link"


class OsdOverlay(CodeBoolMap):
    """OSD overlay."""

    friendly_name = "OSD overlay"
    base_property = "system"
    property_name = "osd_overlay"


class AdditionalService(CodeBoolMap):
    """Additional service."""

    friendly_name = "additional service"
    base_property = "system"
    property_name = "additional_service"


class UserLock(CodeBoolMap):
    """User lock."""

    friendly_name = "user lock"
    base_property = "system"
    property_name = "user_lock"


COMMANDS_SYSTEM = {
    "query_system_speaker_system": {Zone.Z1: ["?SSF", "SSF"]},
    "set_system_speaker_system": {
        Zone.Z1: ["SSF", "SSF"],
        "args": [SpeakerSystem],
        "retry_on_fail": True,
    },
    "query_system_home_menu_status": {Zone.Z1: ["?SSL", "SSL"]},
    "query_system_mcacc_diagnostic_status": {Zone.Z1: ["?SSJ", "SSJ"]},
    "query_system_standing_wave_status": {Zone.Z1: ["?SUU", "SUU"]},
    "query_system_standing_wave_sw_trim": {Zone.Z1: ["?SUV", "SUV"]},
    "query_system_surround_position": {Zone.Z1: ["?SSP", "SSP"]},
    "query_system_x_over": {Zone.Z1: ["?SSQ", "SSQ"]},
    "query_system_x_curve": {Zone.Z1: ["?SST", "SST"]},
    "query_system_loudness_plus": {Zone.Z1: ["?SSU", "SSU"]},
    "query_system_sbch_processing": {Zone.Z1: ["?SSV", "SSV"]},
    "query_system_speaker_setting": {Zone.Z1: ["?SSG", "SSG"]},
    "query_system_mcacc_channel_level": {Zone.Z1: ["?SSR", "SSR"]},
    "query_system_mcacc_speaker_distance": {Zone.Z1: ["?SSS", "SSS"]},
    "query_system_input_level": {Zone.Z1: ["?ILA", "ILA"]},
    "query_system_thx_ultraselect2": {Zone.Z1: ["?SSW", "SSW"]},
    "query_system_boundary_gain_compression": {Zone.Z1: ["?SSX", "SSX"]},
    "query_system_re_equalization": {Zone.Z1: ["?SSB", "SSB"]},
    "query_system_osd_language": {Zone.Z1: ["?SSE", "SSE"]},
    "query_system_network_dhcp": {Zone.Z1: ["?STA", "STA"]},
    "query_system_network_proxy_active": {Zone.Z1: ["?STG", "STG"]},
    "query_system_network_standby": {Zone.Z1: ["?STJ", "STJ"]},
    "query_system_friendly_name": {Zone.Z1: ["?SSO", "SSO"]},
    "query_system_parental_lock": {Zone.Z1: ["?STK", "STK"]},
    "query_system_parental_lock_password": {Zone.Z1: ["?STL", "STL"]},
    "query_system_ip_control_port": {Zone.Z1: ["?SUM", "SUM"]},
    "query_system_hdmi_control": {Zone.Z1: ["?STQ", "STQ"]},
    "query_system_hdmi_control_mode": {Zone.Z1: ["?STR", "STR"]},
    "query_system_hdmi_arc": {Zone.Z1: ["?STT", "STT"]},
    "query_system_pqls_for_backup": {Zone.Z1: ["?SVL", "SVL"]},
    "query_system_standby_passthrough": {Zone.Z1: ["?STU", "STU"]},
    "query_system_external_hdmi_trigger_1": {Zone.Z1: ["?STV", "STV"]},
    "query_system_external_hdmi_trigger_2": {Zone.Z2: ["?STW", "STW"]},
    "query_system_speaker_b_link": {Zone.Z1: ["?STX", "STX"]},
    "query_system_osd_overlay": {Zone.Z1: ["?SVA", "SVA"]},
    "query_system_additional_service": {Zone.Z1: ["?ADS", "ADS"]},
    "query_system_user_lock": {Zone.Z1: ["?SUT", "SUT"]},
}

RESPONSE_DATA_SYSTEM = [
    ("SSF", SpeakerSystem, Zone.ALL),  # system.speaker_system
    ("SSL", HomeMenuStatus, Zone.ALL),  # system.home_menu_status
    ("SSJ", McaccDiagnosticStatus, Zone.ALL),  # system.mcacc_diagnostic_status
    ("SUU", StandingWaveStatus, Zone.ALL),  # system
    ("SUV", StandingWaveSwTrim, Zone.ALL),  # system
    ("SSP", SurroundPosition, Zone.ALL),  # system.surround_position
    ("SSQ", XOver, Zone.ALL),  # system.x_over
    ("SST", XCurve, Zone.ALL),  # system.x_curve
    ("SSU", LoudnessPlus, Zone.ALL),  # system.loudness_plus
    ("SSV", SbchProcessing, Zone.ALL),  # system.sbch_processing
    ("SSG", SpeakerSettings, Zone.ALL),  # system.speaker_setting
    ("SSR", McaccChannelLevel, Zone.ALL),  # system.mcacc_channel_level
    ("SSS", McaccSpeakerDistance, Zone.ALL),  # system.mcacc_speaker_distance
    ("ILA", InputLevel, Zone.ALL),  # system.input_level
    ("SSW", ThxUltraselect2, Zone.ALL),  # system.thx_ultraselect2
    ("SSX", BoundaryGainCompression, Zone.ALL),  # system.boundary_gain_compression
    ("SSB", ReEqualization, Zone.ALL),  # system.re_equalization
    ("SSE", OsdLanguage, Zone.ALL),  # system.osd_language
    ("STA", NetworkDhcp, Zone.ALL),  # system.network_dhcp
    ("STG", NetworkProxyActive, Zone.ALL),  # system.network_proxy_active
    ("STJ", NetworkStandby, Zone.ALL),  # system.network_standby
    ("SSO", FriendlyName, Zone.ALL),  # system.friendly_name
    ("STK", ParentalLock, Zone.ALL),  # system.parental_lock
    ("STL", ParentalLockPassword, Zone.ALL),  # system.parental_lock_password
    ("SUM", IpControlPorts, Zone.ALL),  # system.ip_control_port
    ("STQ", HdmiControl, Zone.ALL),  # system.hdmi_control
    ("STR", HdmiControlMode, Zone.ALL),  # system.hdmi_control_mode
    ("STT", HdmiArc, Zone.ALL),  # system.hdmi_arc
    ("SVL", PqlsForBackup, Zone.ALL),  # system.pqls_for_backup
    ("STU", StandbyPassthrough, Zone.ALL),  # system.standby_passthrough
    ("STV", ExternalHdmiTrigger1, Zone.Z1),  # system.external_hdmi_trigger_1
    ("STW", ExternalHdmiTrigger2, Zone.Z2),  # system.external_hdmi_trigger_2
    ("STX", SpeakerBLink, Zone.ALL),  # system.speaker_b_link
    ("SVA", OsdOverlay, Zone.ALL),  # system.osd_overlay
    ("ADS", AdditionalService, Zone.ALL),  # system.additional_service
    ("SUT", UserLock, Zone.ALL),  # system.user_lock
]
