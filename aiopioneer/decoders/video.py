"""aiopioneer response decoders for video parameters."""

from ..const import Zone
from ..exceptions import AVRCommandUnavailableError
from ..params import AVRParams, PARAM_VIDEO_RESOLUTION_MODES
from ..properties import AVRProperties
from ..property_entry import gen_set_property, gen_query_property
from .code_map import (
    CodeDefault,
    CodeMapBlank,
    CodeMapSequence,
    CodeBoolMap,
    CodeIntMap,
    CodeDictStrMap,
)
from .response import Response


class VideoSignalInputTerminal(CodeDictStrMap):
    """Video signal input terminal."""

    friendly_name = "video signal input terminal"
    base_property = "video"
    property_name = "signal_input_terminal"

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "VIDEO",
        "2": "S-VIDEO",
        "3": "COMPONENT",
        "4": "HDMI",
        "5": "Self OSD/JPEG",
    }


class VideoSignalFormat(CodeDictStrMap):
    """Video signal format."""

    friendly_name = "video signal format"
    base_property = "video"
    property_name = "signal_format"  # unused

    code_map = {
        CodeDefault(): None,
        # "00": "---",
        "01": "480/60i",
        "02": "576/50i",
        "03": "480/60p",
        "04": "576/50p",
        "05": "720/60p",
        "06": "720/50p",
        "07": "1080/60i",
        "08": "1080/50i",
        "09": "1080/60p",
        "10": "1080/50p",
        "11": "1080/24p",
        "12": "4Kx2K/24Hz",
        "13": "4Kx2K/25Hz",
        "14": "4Kx2K/30Hz",
        "15": "4Kx2K/24Hz(SMPTE)",
        "16": "4Kx2K/50Hz",
        "17": "4Kx2K/60Hz",
    }


class VideoSignalInputResolution(VideoSignalFormat):
    """Video signal input resolution."""

    friendly_name = "video signal input resolution"
    base_property = "video"
    property_name = "signal_input_resolution"


class VideoSignalOutputResolution(VideoSignalFormat):
    """Video signal output resolution."""

    friendly_name = "video signal output resolution"
    base_property = "video"
    property_name = "signal_output_resolution"


class VideoSignalHDMI1RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI1 recommended resolution."""

    friendly_name = "video signal HDMI1 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi1_recommended_resolution"


class VideoSignalHDMI2RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI2 recommended resolution."""

    friendly_name = "video signal HDMI2 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi2_recommended_resolution"


class VideoSignalHDMI3RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI3 recommended resolution."""

    friendly_name = "video signal HDMI3 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi3_recommended_resolution"


class VideoSignalHDMI4RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI4 recommended resolution."""

    friendly_name = "video signal HDMI4 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi4_recommended_resolution"


class VideoSignalAspect(CodeDictStrMap):
    """Video signal aspect."""

    friendly_name = "video signal aspect"
    base_property = "video"
    property_name = "signal_aspect"  # unused

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "4:3",
        "2": "16:9",
        "3": "14:9",
    }


class VideoSignalInputAspect(VideoSignalAspect):
    """Video signal input aspect."""

    friendly_name = "video signal input aspect"
    base_property = "video"
    property_name = "signal_input_aspect"


class VideoSignalOutputAspect(VideoSignalAspect):
    """Video signal output aspect."""

    friendly_name = "video signal output aspect"
    base_property = "video"
    property_name = "signal_output_aspect"


class VideoSignalColorspace(CodeDictStrMap):
    """Video signal colorspace."""

    friendly_name = "video signal colorspace"
    base_property = "video"
    property_name = "signal_colorspace"  # unused

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "RGB Limit",
        "2": "RGB Full",
        "3": "YcbCr444",
        "4": "YcbCr422",
        "5": "YcbCr420",
    }


class VideoSignalInputColorspace(VideoSignalColorspace):
    """Video signal input colorspace."""

    friendly_name = "video signal input colorspace"
    base_property = "video"
    property_name = "signal_input_color_format"  # NOTE: inconsistent


class VideoSignalOutputColorspace(VideoSignalColorspace):
    """Video signal output colorspace."""

    friendly_name = "video signal output colorspace"
    base_property = "video"
    property_name = "signal_output_color_format"  # NOTE: inconsistent


class VideoSignalBits(CodeDictStrMap):
    """Video signal bits."""

    friendly_name = "video signal bits"
    base_property = "video"
    property_name = "signal_bits"  # unused

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "24bit (8bit*3)",
        "2": "30bit (10bit*3)",
        "3": "36bit (12bit*3)",
        "4": "48bit (16bit*3)",
    }


class VideoSignalInputBits(VideoSignalBits):
    """Video signal input bits."""

    friendly_name = "video signal input bits"
    base_property = "video"
    property_name = "signal_input_bit"  # NOTE: inconsistent


class VideoSignalOutputBits(VideoSignalBits):
    """Video signal output bits."""

    friendly_name = "video signal output bits"
    base_property = "video"
    property_name = "signal_output_bit"  # NOTE: inconsistent


class VideoSignalHDMI1Deepcolor(VideoSignalBits):
    """Video signal HDMI1 deepcolor."""

    friendly_name = "video signal HDMI1 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi1_deepcolor"  # NOTE: inconsistent


class VideoSignalHDMI2Deepcolor(VideoSignalBits):
    """Video signal HDMI2 deepcolor."""

    friendly_name = "video signal HDMI2 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi2_deepcolor"  # NOTE: inconsistent


class VideoSignalHDMI3Deepcolor(VideoSignalBits):
    """Video signal HDMI3 deepcolor."""

    friendly_name = "video signal HDMI3 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi3_deepcolor"  # NOTE: inconsistent


class VideoSignalHDMI4Deepcolor(VideoSignalBits):
    """Video signal HDMI4 deepcolor."""

    friendly_name = "video signal HDMI4 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi4_deepcolor"  # NOTE: inconsistent


class VideoSignalExtendedColorspace(CodeDictStrMap):
    """Video signal ext colorspace."""

    friendly_name = "video signal ext colorspace"
    base_property = "video"
    property_name = "signal_ext_colorspace"  # unused

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "Standard",
        "2": "xvYCC601",
        "3": "xvYCC709",
        "4": "sYCC",
        "5": "AdobeYCC601",
        "6": "AdobeRGB",
    }


class VideoSignalInputExtendedColorspace(VideoSignalExtendedColorspace):
    """Video signal input extended colorspace."""

    friendly_name = "video signal input extended colorspace"
    base_property = "video"
    property_name = "signal_input_extended_colorspace"


class VideoSignalOutputExtendedColorspace(VideoSignalExtendedColorspace):
    """Video signal output extended colorspace."""

    friendly_name = "video signal output extended colorspace"
    base_property = "video"
    property_name = "signal_output_extended_colorspace"


class VideoSignal3DFormat(CodeDictStrMap):
    """Video signal 3D mode."""

    friendly_name = "video signal 3D mode"
    base_property = "video"
    property_name = "signal_3d_format"  # unused

    code_map = {
        CodeDefault(): None,
        # "00": "---",
        "01": "Frame packing",
        "02": "Field alternative",
        "03": "Line alternative",
        "04": "Side-by-Side(Full)",
        "05": "L + depth",
        "06": "L + depth + graphics",
        "07": "Top-and-Bottom",
        "08": "Side-by-Side(Half)",
    }


class VideoSignalInput3DFormat(VideoSignal3DFormat):
    """Video signal input 3D format."""

    friendly_name = "video signal input 3D format"
    base_property = "video"
    property_name = "input_3d_format"


class VideoSignalOutput3DFormat(VideoSignal3DFormat):
    """Video signal output 3D format."""

    friendly_name = "video signal output 3D format"
    base_property = "video"
    property_name = "output_3d_format"


class VideoInformation(CodeMapSequence):
    """Video information."""

    friendly_name = "video information"
    base_property = "video"
    property_name = "information"  # unused

    code_map_sequence = [
        VideoSignalInputTerminal,  # [0] signal_input_terminal
        VideoSignalInputResolution,  # [1:3] signal_input_resolution
        VideoSignalInputAspect,  # [3] signal_input_aspect
        VideoSignalInputColorspace,  # [4] signal_input_color_format
        VideoSignalInputBits,  # [5] signal_input_bit
        VideoSignalInputExtendedColorspace,  # [6] signal_input_extended_colorspace
        VideoSignalOutputResolution,  # [7:9] signal_output_resolution
        VideoSignalOutputAspect,  # [9] signal_output_aspect
        VideoSignalOutputColorspace,  # [10] signal_output_color_format
        VideoSignalOutputBits,  # [11] signal_output_bit
        VideoSignalOutputExtendedColorspace,  # [12] signal_output_extended_colorspace
        VideoSignalHDMI1RecommendedResolution,  # [13:15] signal_hdmi1_recommended_resolution
        VideoSignalHDMI1Deepcolor,  # [15] signal_hdmi1_deepcolor
        CodeMapBlank(5),
        VideoSignalHDMI2RecommendedResolution,  # [21:23] signal_hdmi2_recommended_resolution
        VideoSignalHDMI2Deepcolor,  # [23] signal_hdmi2_deepcolor
    ]

    code_map_sequence_extra = [
        *code_map_sequence,
        CodeMapBlank(5),
        VideoSignalHDMI3RecommendedResolution,  # [29:31] signal_hdmi3_recommended_resolution
        VideoSignalHDMI3Deepcolor,  # [31] signal_hdmi3_deepcolor
        CodeMapBlank(5),
        VideoSignalInput3DFormat,  # [37:39] input_3d_format
        VideoSignalOutput3DFormat,  # [39:41] output_3d_format
        VideoSignalHDMI4RecommendedResolution,  # [41:43] signal_hdmi4_recommended_resolution
        VideoSignalHDMI4Deepcolor,  # [44] signal_hdmi4_deepcolor
    ]

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for video information."""
        code_map_sequence = cls.code_map_sequence

        ## FY11 AVRs only return 25 data values
        if len(response.code) > 40:
            code_map_sequence = cls.code_map_sequence_extra

        return cls.decode_response_sequence(
            response=response, params=params, code_map_sequence=code_map_sequence
        )


class VideoResolution(CodeDictStrMap):
    """Video resolution."""

    friendly_name = "video resolution"
    base_property = "video"
    property_name = "resolution"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-screenshot"

    code_map = {
        "00": "auto",
        "01": "pure",
        "03": "480/576p",
        "04": "720p",
        "05": "1080i",
        "06": "1080p",
        "07": "1080/24p",
        "08": "4K",
        "09": "4K/24p",
    }

    @classmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,  # pylint: disable=unused-argument
        params: AVRParams,
        properties: AVRProperties,  # pylint: disable=unused-argument
    ) -> str:
        code = cls.value_to_code(args[0])
        resolution_modes = params.get_param(PARAM_VIDEO_RESOLUTION_MODES)
        if not resolution_modes or code not in resolution_modes:
            raise AVRCommandUnavailableError(
                command=command,
                err_key="resolution_unavailable",
                resolution=args[0],
            )
        return code


class VideoConverter(CodeBoolMap):
    """Video converter."""

    friendly_name = "video converter"
    base_property = "video"
    property_name = "converter"
    supported_zones = {Zone.Z1}
    icon = "mdi:mdi:monitor-shimmer"


class VideoPureCinema(CodeDictStrMap):
    """Video pure cinema."""

    friendly_name = "video pure cinema"
    base_property = "video"
    property_name = "pure_cinema"
    supported_zones = {Zone.Z1}
    icon = "mdi:mdi:monitor-shimmer"

    code_map = {"0": "auto", "1": "on", "2": "off"}


class VideoProgressiveMotion(CodeIntMap):
    """Video progressive motion."""

    friendly_name = "video progressive motion"
    base_property = "video"
    property_name = "prog_motion"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"

    value_min = -4
    value_max = 4
    value_offset = 50
    code_zfill = 2


class VideoStreamSmoother(CodeDictStrMap):
    """Video stream smoother."""

    friendly_name = "video stream smoother"
    base_property = "video"
    property_name = "stream_smoother"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"

    code_map = {"0": "off", "1": "on", "2": "auto"}


class AdvancedVideoAdjust(CodeDictStrMap):
    """Advanced video adjust."""

    friendly_name = "advanced video adjust"
    base_property = "video"
    property_name = "advanced_video_adjust"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"

    code_map = {"0": "PDP", "1": "LCD", "2": "FPJ", "3": "professional", "4": "memory"}


class VideoInt08Map(CodeIntMap):
    """Video map for integer values between 0 and +8."""

    friendly_name = "video 0 to +8"
    base_property = "video"

    value_min = 0
    value_max = 8
    value_offset = 50
    code_zfill = 2


class VideoInt66Map(CodeIntMap):
    """Video map for integer values between -6 and +6."""

    friendly_name = "video -6 to +6"
    base_property = "video"

    value_min = -6
    value_max = 6
    value_offset = 50
    code_zfill = 2


class VideoYNR(VideoInt08Map):
    """Video YNR (brightness noise reduction)."""

    friendly_name = "video YNR"
    base_property = "video"
    property_name = "ynr"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoCNR(VideoInt08Map):
    """Video CNR (colour noise reduction)."""

    friendly_name = "video CNR"
    base_property = "video"
    property_name = "cnr"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoBNR(VideoInt08Map):
    """Video BNR (block noise reduction)."""

    friendly_name = "video BNR"
    base_property = "video"
    property_name = "bnr"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoMNR(VideoInt08Map):
    """Video MNR (mosquito noise reduction)."""

    friendly_name = "video MNR"
    base_property = "video"
    property_name = "mnr"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoDetail(VideoInt08Map):
    """Video detail."""

    friendly_name = "video detail"
    base_property = "video"
    property_name = "detail"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoSharpness(VideoInt08Map):
    """Video sharpness."""

    friendly_name = "video sharpness"
    base_property = "video"
    property_name = "sharpness"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoBrightness(VideoInt66Map):
    """Video brightness."""

    friendly_name = "video brightness"
    base_property = "video"
    property_name = "brightness"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoContrast(VideoInt66Map):
    """Video contrast."""

    friendly_name = "video contrast"
    base_property = "video"
    property_name = "contrast"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoHue(VideoInt66Map):
    """Video hue."""

    friendly_name = "video hue"
    base_property = "video"
    property_name = "hue"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoChroma(VideoInt66Map):
    """Video chroma."""

    friendly_name = "video chroma"
    base_property = "video"
    property_name = "chroma"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"


class VideoBlackSetup(CodeBoolMap):
    """Video black setup."""

    friendly_name = "video black setup"
    base_property = "video"
    property_name = "black_setup"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"


class VideoAspect(CodeDictStrMap):
    """Video aspect."""

    friendly_name = "video aspect"
    base_property = "video"
    property_name = "aspect"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-screenshot"

    code_map = {"0": "passthrough", "1": "normal"}


class VideoSuperResolution(CodeIntMap):
    """Video super resolution."""

    friendly_name = "video super resolution"
    base_property = "video"
    property_name = "super_resolution"
    supported_zones = {Zone.Z1}
    icon = "mdi:monitor-shimmer"
    ha_number_mode = "slider"

    value_min = 0
    value_max = 3
    code_zfill = 1


PROPERTIES_VIDEO = [
    gen_query_property(VideoInformation, {Zone.ALL: "VST"}, query_group="basic"),
    gen_set_property(VideoResolution, {Zone.Z1: "VTC"}),
    gen_set_property(VideoConverter, {Zone.Z1: "VTB"}),
    gen_set_property(VideoPureCinema, {Zone.Z1: "VTD"}),
    gen_set_property(VideoProgressiveMotion, {Zone.Z1: "VTE"}),
    gen_set_property(VideoStreamSmoother, {Zone.Z1: "VTF"}),
    gen_set_property(AdvancedVideoAdjust, {Zone.Z1: "VTG"}),
    gen_set_property(VideoYNR, {Zone.Z1: "VTH"}),
    gen_set_property(VideoCNR, {Zone.Z1: "VTI"}),
    gen_set_property(VideoBNR, {Zone.Z1: "VTJ"}),
    gen_set_property(VideoMNR, {Zone.Z1: "VTK"}),
    gen_set_property(VideoDetail, {Zone.Z1: "VTL"}),
    gen_set_property(VideoSharpness, {Zone.Z1: "VTM"}),
    gen_set_property(VideoBrightness, {Zone.Z1: "VTN"}),
    gen_set_property(VideoContrast, {Zone.Z1: "VTO"}),
    gen_set_property(VideoHue, {Zone.Z1: "VTP"}),
    gen_set_property(VideoChroma, {Zone.Z1: "VTQ"}),
    gen_set_property(VideoBlackSetup, {Zone.Z1: "VTR"}),
    gen_set_property(VideoAspect, {Zone.Z1: "VTS"}),
    gen_set_property(VideoSuperResolution, {Zone.Z1: "VTT"}),
]
