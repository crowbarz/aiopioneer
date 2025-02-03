"""Pioneer AVR response parsers for video parameters."""

from .code_map import AVRCodeInt50Map, AVRCodeIntMap, AVRCodeStrDictMap


class VideoInt08Map(AVRCodeInt50Map):
    """Video map for integer values between 0 and +8."""

    value_min = 0
    value_max = 8


class VideoInt66Map(AVRCodeInt50Map):
    """Video map for integer values between -6 and +6."""

    value_min = -6
    value_max = 6


class VideoResolutionModes(AVRCodeStrDictMap):
    """Video resolution modes."""

    code_map = {
        "0": "AUTO",
        "1": "PURE",
        "3": "480/576p",
        "4": "720p",
        "5": "1080i",
        "6": "1080p",
        "7": "1080/24p",
        "8": "4K",
        "9": "4K/24p",
    }


class VideoPureCinemaModes(AVRCodeStrDictMap):
    """Video pure cinema modes."""

    code_map = {"0": "AUTO", "1": "ON", "2": "OFF"}


class VideoProgMotion(AVRCodeInt50Map):
    """Video prog motion."""

    value_min = -4
    value_max = 4


class VideoStreamSmootherModes(AVRCodeStrDictMap):
    """Video stream smoother modes."""

    code_map = {"0": "OFF", "1": "ON", "2": "AUTO"}


class AdvancedVideoAdjustModes(AVRCodeStrDictMap):
    """Advanced video adjust modes."""

    code_map = {"0": "PDP", "1": "LCD", "2": "FPJ", "3": "Professional", "4": "Memory"}


class VideoAspectModes(AVRCodeStrDictMap):
    """Video aspect modes."""

    code_map = {"0": "PASSTHROUGH", "1": "NORMAL"}


class VideoSuperResolution(AVRCodeIntMap):
    """Video super resolution."""

    value_min = 0
    value_max = 3
