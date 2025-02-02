"""Constants for aiopioneer."""

from enum import StrEnum
from typing import Any, Tuple

VERSION = "0.8.1"
DEFAULT_TIMEOUT = 2
DEFAULT_SCAN_INTERVAL = 60
MIN_RESCAN_INTERVAL = 10
DEFAULT_PORT = 8102


class Zone(StrEnum):
    """Valid aiopioneer zones."""

    ALL = "ALL"
    Z1 = "1"
    Z2 = "2"
    Z3 = "3"
    HDZ = "Z"

    @property
    def full_name(self) -> str:
        """Get zone full name."""
        return {
            Zone.ALL: "All Zones",
            Zone.Z1: "Main Zone",
            Zone.Z2: "Zone 2",
            Zone.Z3: "Zone 3",
            Zone.HDZ: "HDZone",
        }.get(self)


class TunerBand(StrEnum):
    """Valid frequency bands."""

    FM = "FM"
    AM = "AM"


SOURCE_TUNER = "02"


class AVRCodeMapBase(dict):
    """Map AVR codes to values."""

    def __new__(cls, value):
        return cls.value_to_code(value)

    def __class_getitem__(cls, code: str):
        return cls.code_to_value(code)

    @classmethod
    def value_to_code(cls, value) -> str:
        """Convert value to code."""
        return str(value)

    @classmethod
    def code_to_value(cls, code: str) -> Any:
        """Convert code to value."""
        return str(code)

    @classmethod
    def match(cls, v, value):
        """Default value match function."""
        return v == value


class AVRCodeBoolMap(AVRCodeMapBase):
    """Map AVR codes to bool values."""

    @classmethod
    def value_to_code(cls, value: bool) -> Any:
        if not isinstance(value, bool):
            raise ValueError(f"Value {value} expected for {cls.__name__}")
        return str(bool(value))

    @classmethod
    def code_to_value(cls, code: str) -> str:
        return bool(code)


class AVRCodeInverseBoolMap(AVRCodeBoolMap):
    """Map AVR codes to inverse bool values."""

    @classmethod
    def value_to_code(cls, value: bool) -> Any:
        if not isinstance(value, bool):
            raise ValueError(f"Value {value} expected for {cls.__name__}")
        return super().value_to_code(not value)

    @classmethod
    def code_to_value(cls, code: str) -> str:
        return not super().value_to_code(code)


class AVRCodeMap(AVRCodeMapBase):
    """Map AVR codes to generic map of values."""

    code_map: dict[str, Any] = {}

    @classmethod
    def value_to_code(cls, value: Any) -> Any:
        for k, v in cls.code_map.items():
            if cls.match(v, value):
                return k
        raise ValueError(f"Name {value} not found in {cls.__name__}")

    @classmethod
    def code_to_value(cls, code: str) -> str:
        if (value := cls.code_map.get(code)) is not None:
            return value
        raise ValueError(f"Key {code} not found in {cls.__name__}")


class AVRCodeStrMap(AVRCodeMap):
    """Map AVR codes to str values."""

    code_map: dict[str, str] = {}


class AVRCodeListMap(AVRCodeMap):
    """Map AVR codes to a list with value as first element."""

    code_map: dict[str, list] = {}

    @classmethod
    def match(cls, v: list, value: str):
        """Match value to first element of list."""
        return v[0] == value

    @classmethod
    def code_to_value(cls, code: str) -> Tuple[str, list]:
        value_list = cls.code_map[code]
        return value_list[0], value_list[1:]


class AVRCodeIntMap(AVRCodeMapBase):
    """Map AVR codes to integer values."""

    code_zfill: int = None
    value_min: int = 0
    value_max: int = 0

    def __new__(cls, value: int) -> str:
        if not cls.value_min >= value >= cls.value_max:
            raise ValueError(
                f"Value {value} outside of range {cls.value_min} -- {cls.value_max} "
                f"for {cls.__name__}"
            )
        if cls.code_zfill:
            return cls.value_to_code(value).zfill(cls.code_zfill)
        return cls.value_to_code(value)

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return int(code)


class AVRCodeInt50Map(AVRCodeIntMap):
    """Map AVR codes to integer values with +50 delta."""

    @classmethod
    def value_to_code(cls, value: int) -> str:
        return str(value + 50)

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return int(code) - 50


# Listening modes is a dict with a nested array for the following structure:
# key: [display_name, 2ch_source_bool, multichannel_source_bool]
LISTENING_MODES = {
    "0001": ["STEREO", True, True],
    "0003": ["Front Stage Surround Advance", True, True],
    "0004": ["Front Stage Surround Advance Wide", True, True],
    "0005": ["AUTO SURR/STREAM DIRECT", True, True],
    "0006": ["AUTO SURROUND", True, True],
    "0007": ["DIRECT", True, True],
    "0008": ["PURE DIRECT", True, True],
    "0009": ["STEREO (direct)", True, False],
    "0010": ["STANDARD", True, False],
    "0011": ["2ch", True, False],
    "0012": ["PRO LOGIC", True, False],
    "0013": ["PRO LOGIC2 MOVIE", True, False],
    "0014": ["PRO LOGIC2 MUSIC", True, False],
    "0015": ["PRO LOGIC2 GAME", True, False],
    "0016": ["Neo:6 CINEMA", True, False],
    "0017": ["Neo:6 MUSIC", True, False],
    "0018": ["PRO LOGIC2x MOVIE", True, False],
    "0019": ["PRO LOGIC2x MUSIC", True, False],
    "0020": ["PRO LOGIC2x GAME", True, False],
    "0021": ["Multi ch", False, True],
    "0022": ["DOLBY EX", False, True],
    "0023": ["PRO LOGIC2x MOVIE (2)", False, True],
    "0024": ["PRO LOGIC2x MUSIC (2)", False, True],
    "0025": ["DTS-ES Neo", False, True],
    "0026": ["DTS-ES matrix", False, True],
    "0027": ["DTS-ES discrete", False, True],
    "0028": ["XM HD SURROUND", True, True],
    "0029": ["NEURAL SURROUND", True, True],
    "0030": ["DTS-ES 8ch discrete", False, True],
    "0031": ["PRO LOGIC2z HEIGHT", True, True],
    "0032": ["WIDE SURROUND MOVIE", True, True],
    "0033": ["WIDE SURROUND MUSIC", True, True],
    "0034": ["PRO LOGIC2z HEIGHT (2)", False, True],
    "0035": ["WIDE SURROUND MOVIE (2)", False, True],
    "0036": ["WIDE SURROUND MUSIC (2)", False, True],
    "0037": ["Neo:X CINEMA", True, True],
    "0038": ["Neo:X MUSIC", True, True],
    "0039": ["Neo:X GAME", True, True],
    "0040": ["NEURAL SURROUND+Neo:X CINEMA", True, True],
    "0041": ["NEURAL SURROUND+Neo:X MUSIC", True, True],
    "0042": ["NEURAL SURROUND+Neo:X GAME", True, True],
    "0043": ["Neo:X CINEMA (2)", False, True],
    "0044": ["Neo:X MUSIC (2)", False, True],
    "0045": ["Neo:X GAME (2)", False, True],
    "0051": ["PROLOGIC + THX CINEMA", True, True],
    "0052": ["PL2 MOVIE + THX CINEMA", True, True],
    "0053": ["Neo:6 CINEMA + THX CINEMA", True, True],
    "0054": ["PL2x MOVIE + THX CINEMA", True, True],
    "0055": ["THX SELECT2 GAMES", True, True],
    "0056": ["THX CINEMA", False, True],
    "0057": ["THX SURROUND EX", False, True],
    "0058": ["PL2x MOVIE + THX CINEMA (2)", False, True],
    "0059": ["ES Neo:6 + THX CINEMA", False, True],
    "0060": ["ES MATRIX + THX CINEMA", False, True],
    "0061": ["ES DISCRETE + THX CINEMA", False, True],
    "0062": ["THX SELECT2 CINEMA", False, True],
    "0063": ["THX SELECT2 MUSIC", False, True],
    "0064": ["THX SELECT2 GAMES (2)", False, True],
    "0065": ["THX ULTRA2 CINEMA", False, True],
    "0066": ["THX ULTRA2 MUSIC", False, True],
    "0067": ["ES 8ch DISCRETE + THX CINEMA", False, True],
    "0068": ["THX CINEMA (2)", True, False],
    "0069": ["THX MUSIC (2)", True, False],
    "0070": ["THX GAMES (2)", True, False],
    "0071": ["PL2 MUSIC + THX MUSIC", True, True],
    "0072": ["PL2x MUSIC + THX MUSIC", True, True],
    "0073": ["Neo:6 MUSIC + THX MUSIC", True, True],
    "0074": ["PL2 GAME + THX GAMES", True, True],
    "0075": ["PL2x GAME + THX GAMES", True, True],
    "0076": ["THX ULTRA2 GAMES", True, True],
    "0077": ["PROLOGIC + THX MUSIC", True, True],
    "0078": ["PROLOGIC + THX GAMES", True, True],
    "0079": ["THX ULTRA2 GAMES (2)", False, True],
    "0080": ["THX MUSIC", False, True],
    "0081": ["THX GAMES", False, True],
    "0082": ["PL2x MUSIC + THX MUSIC (2)", False, True],
    "0083": ["EX + THX GAMES", False, True],
    "0084": ["Neo:6 + THX MUSIC", False, True],
    "0085": ["Neo:6 + THX GAMES", False, True],
    "0086": ["ES MATRIX + THX MUSIC", False, True],
    "0087": ["ES MATRIX + THX GAMES", False, True],
    "0088": ["ES DISCRETE + THX MUSIC", False, True],
    "0089": ["ES DISCRETE + THX GAMES", False, True],
    "0090": ["ES 8CH DISCRETE + THX MUSIC", False, True],
    "0091": ["ES 8CH DISCRETE + THX GAMES", False, True],
    "0092": ["PL2z HEIGHT + THX CINEMA", True, False],
    "0093": ["PL2z HEIGHT + THX MUSIC", True, False],
    "0094": ["PL2z HEIGHT + THX GAMES", True, False],
    "0095": ["PL2z HEIGHT + THX CINEMA (2)", False, True],
    "0096": ["PL2z HEIGHT + THX MUSIC (2)", False, True],
    "0097": ["PL2z HEIGHT + THX GAMES (2)", False, True],
    "0101": ["ACTION", True, True],
    "0102": ["SCI-FI", True, True],
    "0103": ["DRAMA", True, True],
    "0104": ["ENTERTAINMENT SHOW", True, True],
    "0105": ["MONO FILM", True, True],
    "0106": ["EXPANDED THEATER", True, True],
    "0107": ["CLASSICAL", True, True],
    "0109": ["UNPLUGGED", True, True],
    "0110": ["ROCK/POP", True, True],
    "0112": ["EXTENDED STEREO", True, True],
    "0113": ["PHONES SURROUND", True, True],
    "0116": ["TV SURROUND", True, True],
    "0117": ["SPORTS", True, True],
    "0118": ["ADVANCED GAME", True, True],
    "0151": ["Auto Level Control", True, True],
    "0152": ["OPTIMUM SURROUND", True, True],
    "0153": ["RETRIEVER AIR", True, True],
    "0200": ["ECO MODE", True, True],
    "0201": ["Neo:X CINEMA + THX CINEMA", True, False],
    "0202": ["Neo:X MUSIC + THX MUSIC", True, False],
    "0203": ["Neo:X GAME + THX GAMES", True, False],
    "0204": ["Neo:X CINEMA + THX CINEMA (2)", False, True],
    "0205": ["Neo:X MUSIC + THX MUSIC (2)", False, True],
    "0206": ["Neo:X GAME + THX GAMES (2)", False, True],
    "0212": ["ECO MODE 1", True, True],
    "0213": ["ECO MODE 2", True, True],
}

MEDIA_CONTROL_SOURCES = {
    "26": "NETWORK",
    "38": "NETWORK",
    "44": "NETWORK",
    "02": "TUNER",
    "13": "ADAPTERPORT",
    "41": "NETWORK",
    "53": "NETWORK",
    "17": "IPOD",
}

MEDIA_CONTROL_COMMANDS = {
    "NETWORK": {
        "play": "operation_network_play",
        "pause": "operation_network_pause",
        "stop": "operation_network_stop",
        "ff": "operation_network_fastforward",
        "rw": "operation_network_rewind",
        "next": "operation_network_next",
        "previous": "operation_network_previous",
        "repeat": "operation_network_repeat",
        "shuffle": "operation_network_random",
    },
    "IPOD": {
        "play": "operation_ipod_play",
        "pause": "operation_ipod_pause",
        "stop": "operation_ipod_stop",
        "ff": "operation_ipod_fastforward",
        "rw": "operation_ipod_rewind",
        "next": "operation_ipod_next",
        "previous": "operation_ipod_previous",
        "repeat": "operation_ipod_repeat",
        "shuffle": "operation_ipod_shuffle",
    },
    "TUNER": {
        "ff": "increase_tuner_frequency",
        "rw": "decrease_tuner_frequency",
        "next": "increase_tuner_preset",
        "previous": "decrease_tuner_preset",
    },
    "ADAPTERPORT": {
        "play": "operation_adapaterport_play",
        "pause": "operation_adapaterport_pause",
        "stop": "operation_adapaterport_stop",
        "previous": "operation_adapaterport_previous",
        "next": "operation_adapaterport_next",
        "rw": "operation_adapaterport_rewind",
        "ff": "operation_adapaterport_fastforward",
        "repeat": "operation_adapaterport_repeat",
        "shuffle": "operation_adapaterport_random",
    },
    "MHL": {
        "play": "operation_mhl_play",
        "pause": "operation_mhl_pause",
        "stop": "operation_mhl_stop",
        "record": "operation_mhl_record",
        "rw": "operation_mhl_rewind",
        "ff": "operation_mhl_fastforward",
        "eject": "operation_mhl_eject",
        "next": "operation_mhl_next",
        "previous": "operation_mhl_previous",
    },
}


class ToneModes(AVRCodeStrMap):
    """Tone modes."""

    code_map = {"0": "Bypass", "1": "On", "9": "(cycle)"}


class ToneDB(AVRCodeStrMap):
    """Tone dB values."""

    code_map = {
        "00": "6dB",
        "01": "5dB",
        "02": "4dB",
        "03": "3dB",
        "04": "2dB",
        "05": "1dB",
        "06": "0dB",
        "07": "-1dB",
        "08": "-2dB",
        "09": "-3dB",
        "10": "-4dB",
        "11": "-5dB",
        "12": "-6dB",
    }


class VideoInt08Map(AVRCodeInt50Map):
    """Video map for integer values between 0 and +8."""

    value_min = 0
    value_max = 8


class VideoInt66Map(AVRCodeInt50Map):
    """Video map for integer values between -6 and +6."""

    value_min = -6
    value_max = 6


class VideoInt44Map(AVRCodeInt50Map):
    """Video map for integer values between -6 and +6."""

    value_min = -4
    value_max = 4


class VideoPureCinemaModes(AVRCodeStrMap):
    """Video pure cinema modes."""

    code_map = {"0": "AUTO", "1": "ON", "2": "OFF"}


class VideoStreamSmootherModes(AVRCodeStrMap):
    """Video stream smoother modes."""

    code_map = {"0": "OFF", "1": "ON", "2": "AUTO"}


class VideoAspectModes(AVRCodeStrMap):
    """Video aspect modes."""

    code_map = {"0": "PASSTHROUGH", "1": "NORMAL"}


class AdvancedVideoAdjustModes(AVRCodeStrMap):
    """Advanced video adjust modes."""

    code_map = {"0": "PDP", "1": "LCD", "2": "FPJ", "3": "Professional", "4": "Memory"}


CHANNEL_LEVELS_OBJ = {
    "C": 0,
    "L": 0,
    "R": 0,
    "SL": 0,
    "SR": 0,
    "SBL": 0,
    "SBR": 0,
    "SW": 0,
    "LH": 0,
    "RH": 0,
    "LW": 0,
    "RW": 0,
}


class VideoSuperResolution(AVRCodeIntMap):
    """Video super resolution."""

    value_min = 0
    value_max = 3


class DSPAutoManual(AVRCodeStrMap):
    """DSP auto/manual."""

    code_map = {"0": "AUTO", "1": "MANUAL"}


class DSPPhaseControl(AVRCodeStrMap):
    """DSP phase control."""

    code_map = {"0": "off", "1": "on", "2": "full band on"}


class DSPSignalSelect(AVRCodeStrMap):
    """DSP signal select."""

    code_map = {"0": "AUTO", "1": "ANALOG", "2": "DIGITAL", "3": "HDMI"}


class DSPDialogEnhancement(AVRCodeStrMap):
    """DSP dialog enhancement."""

    code_map = {"0": "off", "1": "flat", "2": "+1", "3": "+2", "4": "+3", "5": "+4"}


class DSPDualMono(AVRCodeStrMap):
    """DSP dual mono."""

    code_map = {"0": "CH1+CH2", "1": "CH1", "2": "CH2"}


class DSPDynamicRange(AVRCodeStrMap):
    """DSP dyanmic range."""

    code_map = {"0": "off", "1": "auto", "2": "mid", "3": "max"}


class DSPHeightGain(AVRCodeStrMap):
    """DSP height gain."""

    code_map = {"0": "low", "1": "mid", "2": "high"}


class DSPVirtualDepth(AVRCodeStrMap):
    """DSP virtual depth."""

    code_map = {"0": "off", "1": "min", "2": "mid", "3": "max"}


class DSPDigitalFilter(AVRCodeStrMap):
    """DSP digital filter."""

    code_map = {"0": "slow", "1": "sharp", "2": "short"}


class DSPUpSampling(AVRCodeStrMap):
    """DSP up sampling."""

    code_map = {"0": "off", "1": "2 times", "2": "4 times"}


class DSPRenderingMode(AVRCodeStrMap):
    """DSP rendering mode."""

    code_map = {"0": "object base", "1": "channel base"}


AUDIO_SIGNAL_INPUT_INFO = {
    "00": "ANALOG",
    "01": "ANALOG",
    "02": "ANALOG",
    "03": "PCM",
    "04": "PCM",
    "05": "DOLBY DIGITAL",
    "06": "DTS",
    "07": "DTS-ES Matrix",
    "08": "DTS-ES Discrete",
    "09": "DTS 96/24",
    "10": "DTS 96/24 ES Matrix",
    "11": "DTS 96/24 ES Discrete",
    "12": "MPEG-2 AAC",
    "13": "WMA9 Pro",
    "14": "DSD (HDMI or File via DSP route)",
    "15": "HDMI THROUGH",
    "16": "DOLBY DIGITAL PLUS",
    "17": "DOLBY TrueHD",
    "18": "DTS EXPRESS",
    "19": "DTS-HD Master Audio",
    "20": "DTS-HD High Resolution",
    "21": "DTS-HD High Resolution",
    "22": "DTS-HD High Resolution",
    "23": "DTS-HD High Resolution",
    "24": "DTS-HD High Resolution",
    "25": "DTS-HD High Resolution",
    "26": "DTS-HD High Resolution",
    "27": "DTS-HD Master Audio",
    "28": "DSD (HDMI or File via DSD DIRECT route)",
    "29": "Dolby Atmos",
    "30": "Dolby Atmos over Dolby Digital Plus",
    "31": "Dolby Atmos over Dolby TrueHD",
    "64": "MP3",
    "65": "WAV",
    "66": "WMA",
    "67": "MPEG4-AAC",
    "68": "FLAC",
    "69": "ALAC(Apple Lossless)",
    "70": "AIFF",
    "71": "DSD (USB-DAC)",
    "72": "Spotify",
}

AUDIO_SIGNAL_INPUT_FREQ = {
    "00": "32kHz",
    "01": "44.1kHz",
    "02": "48kHz",
    "03": "88.2kHz",
    "04": "96kHz",
    "05": "176.4kHz",
    "06": "192kHz",
    # "07": "---",
    "32": "2.8MHz",
    "33": "5.6MHz",
}

AUDIO_WORKING_PQLS = {"0": "off", "1": "2h", "2": "Multi-channel", "3": "Bitstream"}

VIDEO_SIGNAL_INPUT_TERMINAL = {
    # "0": "---",
    "1": "VIDEO",
    "2": "S-VIDEO",
    "3": "COMPONENT",
    "4": "HDMI",
    "5": "Self OSD/JPEG",
}

VIDEO_SIGNAL_FORMATS = {
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

VIDEO_SIGNAL_ASPECTS = {
    # "0": "---",
    "1": "4:3",
    "2": "16:9",
    "3": "14:9",
}

VIDEO_SIGNAL_COLORSPACE = {
    # "0": "---",
    "1": "RGB Limit",
    "2": "RGB Full",
    "3": "YcbCr444",
    "4": "YcbCr422",
    "5": "YcbCr420",
}

VIDEO_SIGNAL_BITS = {
    # "0": "---",
    "1": "24bit (8bit*3)",
    "2": "30bit (10bit*3)",
    "3": "36bit (12bit*3)",
    "4": "48bit (16bit*3)",
}

VIDEO_SIGNAL_EXT_COLORSPACE = {
    # "0": "---",
    "1": "Standard",
    "2": "xvYCC601",
    "3": "xvYCC709",
    "4": "sYCC",
    "5": "AdobeYCC601",
    "6": "AdobeRGB",
}

VIDEO_SIGNAL_3D_MODES = {
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


class VideoResolutionModes(AVRCodeStrMap):
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


MCACC_MEASUREMENT_ERROR = {
    "0": "No error",
    "1": "No microphone",
    "2": "Ambient noise",
    "3": "Microphone",
    "4": "Unsupported connection",
    "5": "Reverse phase",
    "6": "Subwoofer level",
}

MCACC_MEASUREMENT_STATUS = {"0": "Inactive", "1": "Measuring"}

STANDING_WAVE_FREQUENCIES = {
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

XOVER_SETTING = {
    "0": "50Hz",
    "1": "80Hz",
    "2": "100Hz",
    "3": "150Hz",
    "4": "200Hz",
}

OSD_LANGUAGES = {
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

STANDBY_PASSTHROUGH_OPTIONS = {
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

EXTERNAL_HDMI_TRIGGER_OPTIONS = {
    "0": "OFF",
    "1": "HDMIOUT1",
    "2": "HDMIOUT2",
    "3": "HDMIOUT3",
    "4": "HDMIOUT4/HDBaseT",
}
