"""aiopioneer response decoders for video parameters."""

from ..const import Zone
from ..exceptions import AVRCommandUnavailableError
from ..params import AVRParams, PARAM_VIDEO_RESOLUTION_MODES
from ..properties import AVRProperties
from .code_map import CodeBoolMap, CodeIntMap, CodeDictStrMap


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
    property_name = "black setup"


class VideoAspect(CodeDictStrMap):
    """Video aspect."""

    code_map = {"0": "passthrough", "1": "normal"}


class VideoSuperResolution(CodeIntMap):
    """Video super resolution."""

    value_min = 0
    value_max = 3
    code_zfill = 1


RESPONSE_DATA_VIDEO = [
    ["VTC", VideoResolution, Zone.Z1, "video", "resolution"],
    ["VTB", VideoConverter, Zone.Z1, "video", "converter"],
    ["VTD", VideoPureCinema, Zone.Z1, "video", "pure_cinema"],
    ["VTE", VideoProgMotion, Zone.Z1, "video", "prog_motion"],
    ["VTF", VideoStreamSmoother, Zone.Z1, "video", "stream_smoother"],
    ["VTG", AdvancedVideoAdjust, Zone.Z1, "video", "advanced_video_adjust"],
    ["VTH", VideoYnr, Zone.Z1, "video", "ynr"],
    ["VTI", VideoCnr, Zone.Z1, "video", "cnr"],
    ["VTJ", VideoBnr, Zone.Z1, "video", "bnr"],
    ["VTK", VideoMnr, Zone.Z1, "video", "mnr"],
    ["VTL", VideoDetail, Zone.Z1, "video", "detail"],
    ["VTM", VideoSharpness, Zone.Z1, "video", "sharpness"],
    ["VTN", VideoBrightness, Zone.Z1, "video", "brightness"],
    ["VTO", VideoContrast, Zone.Z1, "video", "contrast"],
    ["VTP", VideoHue, Zone.Z1, "video", "hue"],
    ["VTQ", VideoChroma, Zone.Z1, "video", "chroma"],
    ["VTR", VideoBlackSetup, Zone.Z1, "video", "black_setup"],
    ["VTS", VideoAspect, Zone.Z1, "video", "aspect"],
    ["VTT", VideoSuperResolution, Zone.Z1, "video", "super_resolution"],
]
