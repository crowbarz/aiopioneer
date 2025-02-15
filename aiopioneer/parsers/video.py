"""Pioneer AVR response parsers for video parameters."""

from .code_map import CodeIntMap, CodeDictStrMap


class VideoInt08Map(CodeIntMap):
    """Video map for integer values between 0 and +8."""

    value_min = 0
    value_max = 8
    value_offset = 50


class VideoInt66Map(CodeIntMap):
    """Video map for integer values between -6 and +6."""

    value_min = -6
    value_max = 6
    value_offset = 50


class VideoResolution(CodeDictStrMap):
    """Video resolution."""

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


class VideoPureCinema(CodeDictStrMap):
    """Video pure cinema."""

    code_map = {"0": "auto", "1": "on", "2": "off"}


class VideoProgMotion(CodeIntMap):
    """Video prog motion."""

    value_min = -4
    value_max = 4
    value_offset = 50


class VideoStreamSmoother(CodeDictStrMap):
    """Video stream smoother."""

    code_map = {"0": "off", "1": "on", "2": "auto"}


class AdvancedVideoAdjust(CodeDictStrMap):
    """Advanced video adjust."""

    code_map = {"0": "PDP", "1": "LCD", "2": "FPJ", "3": "professional", "4": "memory"}


class VideoAspect(CodeDictStrMap):
    """Video aspect."""

    code_map = {"0": "passthrough", "1": "normal"}


class VideoSuperResolution(CodeIntMap):
    """Video super resolution."""

    value_min = 0
    value_max = 3
