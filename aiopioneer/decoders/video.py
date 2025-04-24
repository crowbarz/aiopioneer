"""aiopioneer response decoders for video parameters."""

from ..const import Zone
from ..exceptions import AVRCommandUnavailableError
from ..params import AVRParams, PARAM_VIDEO_RESOLUTION_MODES
from ..properties import AVRProperties
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


class VideoSignalHdmi1RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI1 recommended resolution."""

    friendly_name = "video signal HDMI1 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi1_recommended_resolution"


class VideoSignalHdmi2RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI2 recommended resolution."""

    friendly_name = "video signal HDMI2 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi2_recommended_resolution"


class VideoSignalHdmi3RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI3 recommended resolution."""

    friendly_name = "video signal HDMI3 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi3_recommended_resolution"


class VideoSignalHdmi4RecommendedResolution(VideoSignalFormat):
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


class VideoSignalHdmi1Deepcolor(VideoSignalBits):
    """Video signal HDMI1 deepcolor."""

    friendly_name = "video signal HDMI1 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi1_deepcolor"  # NOTE: inconsistent


class VideoSignalHdmi2Deepcolor(VideoSignalBits):
    """Video signal HDMI2 deepcolor."""

    friendly_name = "video signal HDMI2 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi2_deepcolor"  # NOTE: inconsistent


class VideoSignalHdmi3Deepcolor(VideoSignalBits):
    """Video signal HDMI3 deepcolor."""

    friendly_name = "video signal HDMI3 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi3_deepcolor"  # NOTE: inconsistent


class VideoSignalHdmi4Deepcolor(VideoSignalBits):
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
        VideoSignalHdmi1RecommendedResolution,  # [13:15] signal_hdmi1_recommended_resolution
        VideoSignalHdmi1Deepcolor,  # [15] signal_hdmi1_deepcolor
        CodeMapBlank(5),
        VideoSignalHdmi2RecommendedResolution,  # [21:23] signal_hdmi2_recommended_resolution
        VideoSignalHdmi2Deepcolor,  # [23] signal_hdmi2_deepcolor
    ]

    code_map_sequence_extra = [
        *code_map_sequence,
        CodeMapBlank(5),
        VideoSignalHdmi3RecommendedResolution,  # [29:31] signal_hdmi3_recommended_resolution
        VideoSignalHdmi3Deepcolor,  # [31] signal_hdmi3_deepcolor
        CodeMapBlank(5),
        VideoSignalInput3DFormat,  # [37:39] input_3d_format
        VideoSignalOutput3DFormat,  # [39:41] output_3d_format
        VideoSignalHdmi4RecommendedResolution,  # [41:43] signal_hdmi4_recommended_resolution
        VideoSignalHdmi4Deepcolor,  # [44] signal_hdmi4_deepcolor
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

    code_map = {
        "0": "auto",
        "1": "pure",
        "3": "480/576p",
        "4": "720p",
        "5": "1080i",
        "6": "1080p",
        "7": "1080/24p",
        "8": "4K",
        "9": "4K/24p",
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


class VideoPureCinema(CodeDictStrMap):
    """Video pure cinema."""

    friendly_name = "video pure cinema"
    base_property = "video"
    property_name = "pure_cinema"

    code_map = {"0": "auto", "1": "on", "2": "off"}


class VideoProgMotion(CodeIntMap):
    """Video prog motion."""

    friendly_name = "video prog motion"
    base_property = "video"
    property_name = "prog_motion"

    value_min = -4
    value_max = 4
    value_offset = 50
    code_zfill = 2


class VideoStreamSmoother(CodeDictStrMap):
    """Video stream smoother."""

    friendly_name = "video stream smoother"
    base_property = "video"
    property_name = "stream_smoother"

    code_map = {"0": "off", "1": "on", "2": "auto"}


class AdvancedVideoAdjust(CodeDictStrMap):
    """Advanced video adjust."""

    friendly_name = "advanced video adjust"
    base_property = "video"
    property_name = "advanced_video_adjust"

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


class VideoYnr(VideoInt08Map):
    """Video YNR."""

    friendly_name = "video YNR"
    base_property = "video"
    property_name = "ynr"


class VideoCnr(VideoInt08Map):
    """Video CNR."""

    friendly_name = "video CNR"
    base_property = "video"
    property_name = "cnr"


class VideoBnr(VideoInt08Map):
    """Video BNR."""

    friendly_name = "video BNR"
    base_property = "video"
    property_name = "bnr"


class VideoMnr(VideoInt08Map):
    """Video MNR."""

    friendly_name = "video MNR"
    base_property = "video"
    property_name = "mnr"


class VideoDetail(VideoInt08Map):
    """Video detail."""

    friendly_name = "video detail"
    base_property = "video"
    property_name = "detail"


class VideoSharpness(VideoInt08Map):
    """Video sharpness."""

    friendly_name = "video sharpness"
    base_property = "video"
    property_name = "sharpness"


class VideoBrightness(VideoInt66Map):
    """Video brightness."""

    friendly_name = "video brightness"
    base_property = "video"
    property_name = "brightness"


class VideoContrast(VideoInt66Map):
    """Video contrast."""

    friendly_name = "video contrast"
    base_property = "video"
    property_name = "contrast"


class VideoHue(VideoInt66Map):
    """Video hue."""

    friendly_name = "video hue"
    base_property = "video"
    property_name = "hue"


class VideoChroma(VideoInt66Map):
    """Video chroma."""

    friendly_name = "video chroma"
    base_property = "video"
    property_name = "chroma"


class VideoBlackSetup(CodeBoolMap):
    """Video black setup."""

    friendly_name = "video black setup"
    base_property = "video"
    property_name = "black_setup"


class VideoAspect(CodeDictStrMap):
    """Video aspect."""

    friendly_name = "video aspect"
    base_property = "video"
    property_name = "aspect"

    code_map = {"0": "passthrough", "1": "normal"}


class VideoSuperResolution(CodeIntMap):
    """Video super resolution."""

    friendly_name = "video super resolution"
    base_property = "video"
    property_name = "super_resolution"

    value_min = 0
    value_max = 3
    code_zfill = 1


COMMANDS_VIDEO = {
    "query_basic_video_information": {Zone.Z1: ["?VST", "VST"]},
    "query_video_resolution": {Zone.Z1: ["?VTC", "VTC"]},
    "set_video_resolution": {
        Zone.Z1: ["VTC", "VTC"],
        "args": [VideoResolution],
        "retry_on_fail": True,
    },
    "query_video_converter": {Zone.Z1: ["?VTB", "VTB"]},
    "set_video_converter": {
        Zone.Z1: ["VTB", "VTB"],
        "args": [VideoConverter],
        "retry_on_fail": True,
    },
    "query_video_pure_cinema": {Zone.Z1: ["?VTD", "VTD"]},
    "set_video_pure_cinema": {
        Zone.Z1: ["VTD", "VTD"],
        "args": [VideoPureCinema],
        "retry_on_fail": True,
    },
    "query_video_prog_motion": {Zone.Z1: ["?VTE", "VTE"]},
    "set_video_prog_motion": {
        Zone.Z1: ["VTE", "VTE"],
        "args": [VideoProgMotion],
        "retry_on_fail": True,
    },
    "query_video_stream_smoother": {Zone.Z1: ["?VTF", "VTF"]},
    "set_video_stream_smoother": {
        Zone.Z1: ["VTF", "VTF"],
        "args": [VideoStreamSmoother],
        "retry_on_fail": True,
    },
    "query_video_advanced_video_adjust": {Zone.Z1: ["?VTG", "VTG"]},
    "set_video_advanced_video_adjust": {
        Zone.Z1: ["VTG", "VTG"],
        "args": [AdvancedVideoAdjust],
        "retry_on_fail": True,
    },
    "query_video_ynr": {Zone.Z1: ["?VTH", "VTH"]},
    "set_video_ynr": {
        Zone.Z1: ["VTH", "VTH"],
        "args": [VideoYnr],
        "retry_on_fail": True,
    },
    "query_video_cnr": {Zone.Z1: ["?VTI", "VTI"]},
    "set_video_cnr": {
        Zone.Z1: ["VTI", "VTI"],
        "args": [VideoCnr],
        "retry_on_fail": True,
    },
    "query_video_bnr": {Zone.Z1: ["?VTJ", "VTJ"]},
    "set_video_bnr": {
        Zone.Z1: ["VTJ", "VTJ"],
        "args": [VideoBnr],
        "retry_on_fail": True,
    },
    "query_video_mnr": {Zone.Z1: ["?VTK", "VTK"]},
    "set_video_mnr": {
        Zone.Z1: ["VTK", "VTK"],
        "args": [VideoMnr],
        "retry_on_fail": True,
    },
    "query_video_detail": {Zone.Z1: ["?VTL", "VTL"]},
    "set_video_detail": {
        Zone.Z1: ["VTL", "VTL"],
        "args": [VideoDetail],
        "retry_on_fail": True,
    },
    "query_video_sharpness": {Zone.Z1: ["?VTM", "VTM"]},
    "set_video_sharpness": {
        Zone.Z1: ["VTM", "VTM"],
        "args": [VideoSharpness],
        "retry_on_fail": True,
    },
    "query_video_brightness": {Zone.Z1: ["?VTN", "VTN"]},
    "set_video_brightness": {
        Zone.Z1: ["VTN", "VTN"],
        "args": [VideoBrightness],
        "retry_on_fail": True,
    },
    "query_video_contrast": {Zone.Z1: ["?VTO", "VTO"]},
    "set_video_contrast": {
        Zone.Z1: ["VTO", "VTO"],
        "args": [VideoContrast],
        "retry_on_fail": True,
    },
    "query_video_hue": {Zone.Z1: ["?VTP", "VTP"]},
    "set_video_hue": {
        Zone.Z1: ["VTP", "VTP"],
        "args": [VideoHue],
        "retry_on_fail": True,
    },
    "query_video_chroma": {Zone.Z1: ["?VTQ", "VTQ"]},
    "set_video_chroma": {
        Zone.Z1: ["VTQ", "VTQ"],
        "args": [VideoChroma],
        "retry_on_fail": True,
    },
    "query_video_black_setup": {Zone.Z1: ["?VTR", "VTR"]},
    "set_video_black_setup": {
        Zone.Z1: ["VTR", "VTR"],
        "args": [VideoBlackSetup],
        "retry_on_fail": True,
    },
    "query_video_aspect": {Zone.Z1: ["?VTS", "VTS"]},
    "set_video_aspect": {
        Zone.Z1: ["VTS", "VTS"],
        "args": [VideoAspect],
        "retry_on_fail": True,
    },
    "query_video_super_resolution": {Zone.Z1: ["?VTT", "VTT"]},
    "set_video_super_resolution": {
        Zone.Z1: ["VTT", "VTT"],
        "args": [VideoSuperResolution],
        "retry_on_fail": True,
    },
}

RESPONSE_DATA_VIDEO = [
    ("VST", VideoInformation, Zone.ALL),  # video
    ("VTC", VideoResolution, Zone.Z1),  # video.resolution
    ("VTB", VideoConverter, Zone.Z1),  # video.converter
    ("VTD", VideoPureCinema, Zone.Z1),  # video.pure_cinema
    ("VTE", VideoProgMotion, Zone.Z1),  # video.prog_motion
    ("VTF", VideoStreamSmoother, Zone.Z1),  # video.stream_smoother
    ("VTG", AdvancedVideoAdjust, Zone.Z1),  # video.advanced_video_adjust
    ("VTH", VideoYnr, Zone.Z1),  # video.ynr
    ("VTI", VideoCnr, Zone.Z1),  # video.cnr
    ("VTJ", VideoBnr, Zone.Z1),  # video.bnr
    ("VTK", VideoMnr, Zone.Z1),  # video.mnr
    ("VTL", VideoDetail, Zone.Z1),  # video.detail
    ("VTM", VideoSharpness, Zone.Z1),  # video.sharpness
    ("VTN", VideoBrightness, Zone.Z1),  # video.brightness
    ("VTO", VideoContrast, Zone.Z1),  # video.contrast
    ("VTP", VideoHue, Zone.Z1),  # video.hue
    ("VTQ", VideoChroma, Zone.Z1),  # video.chroma
    ("VTR", VideoBlackSetup, Zone.Z1),  # video.black_setup
    ("VTS", VideoAspect, Zone.Z1),  # video.aspect
    ("VTT", VideoSuperResolution, Zone.Z1),  # video.super_resolution
]
