"""Constants for aiopioneer."""

DEFAULT_PORT = 8102
VERSION = "0.2.2"

# Listening modes is a dict with a nested dict for the following structure:
LISTENING_MODES = {
    "0001": "STEREO",
    "0003": "Front Stage Surround Advance",
    "0004": "Front Stage Surround Advance Wide",
    "0005": "AUTO SURR/STREAM DIRECT",
    "0006": "AUTO SURROUND",
    "0007": "DIRECT",
    "0008": "PURE DIRECT",
    "0009": "STEREO (direct)",
    "0010": "STANDARD",
    "0011": "2ch",
    "0012": "PRO LOGIC",
    "0013": "PRO LOGIC2 MOVIE",
    "0014": "PRO LOGIC2 MUSIC",
    "0015": "PRO LOGIC2 GAME",
    "0016": "Neo:6 CINEMA",
    "0017": "Neo:6 MUSIC",
    "0018": "PRO LOGIC2x MOVIE",
    "0019": "PRO LOGIC2x MUSIC",
    "0020": "PRO LOGIC2x GAME",
    "0021": "Multi ch",
    "0022": "Multi ch+DOLBY EX",
    "0023": "Multi ch+PRO LOGIC2x MOVIE",
    "0024": "Multi ch+PRO LOGIC2x MUSIC",
    "0025": "Multi ch+DTS-ES Neo",
    "0026": "Multi ch+DTS-ES matrix",
    "0027": "Multi ch+DTS-ES discrete",
    "0028": "XM HD SURROUND",
    "0029": "NEURAL SURROUND",
    "0030": "Multi ch+DTS-ES 8ch discrete",
    "0031": "PRO LOGIC2z HEIGHT",
    "0032": "WIDE SURROUND MOVIE",
    "0033": "WIDE SURROUND MUSIC",
    "0034": "Multi ch+PRO LOGIC2z HEIGHT",
    "0035": "Multi ch+WIDE SURROUND MOVIE",
    "0036": "Multi ch+WIDE SURROUND MUSIC",
    "0037": "Neo:X CINEMA",
    "0038": "Neo:X MUSIC",
    "0039": "Neo:X GAME",
    "0040": "NEURAL SURROUND+Neo:X CINEMA",
    "0041": "NEURAL SURROUND+Neo:X MUSIC",
    "0042": "NEURAL SURROUND+Neo:X GAME",
    "0043": "Multi ch+Neo:X CINEMA ",
    "0044": "Multi ch+Neo:X MUSIC",
    "0045": "Multi ch+Neo:X GAME",
    "0051": "PROLOGIC + THX CINEMA",
    "0052": "PL2 MOVIE + THX CINEMA",
    "0053": "Neo:6 CINEMA + THX CINEMA",
    "0054": "PL2x MOVIE + THX CINEMA",
    "0055": "THX SELECT2 GAMES",
    "0056": "THX CINEMA (for multi ch)",
    "0057": "THX SURROUND EX (for multi ch)",
    "0058": "PL2x MOVIE + THX CINEMA (for multi ch)",
    "0059": "ES Neo:6 + THX CINEMA (for multi ch)",
    "0060": "ES MATRIX + THX CINEMA (for multi ch)",
    "0061": "ES DISCRETE + THX CINEMA (for multi ch)",
    "0062": "THX SELECT2 CINEMA (for multi ch)",
    "0063": "THX SELECT2 MUSIC (for multi ch)",
    "0064": "THX SELECT2 GAMES (for multi ch)",
    "0065": "THX ULTRA2 CINEMA (for multi ch)",
    "0066": "THX ULTRA2 MUSIC (for multi ch)",
    "0067": "ES 8ch DISCRETE + THX CINEMA (for multi ch)",
    "0068": "THX CINEMA (for 2ch)",
    "0069": "THX MUSIC (for 2ch)",
    "0070": "THX GAMES (for 2ch)",
    "0071": "PL2 MUSIC + THX MUSIC",
    "0072": "PL2x MUSIC + THX MUSIC",
    "0073": "Neo:6 MUSIC + THX MUSIC",
    "0074": "PL2 GAME + THX GAMES",
    "0075": "PL2x GAME + THX GAMES",
    "0076": "THX ULTRA2 GAMES",
    "0077": "PROLOGIC + THX MUSIC",
    "0078": "PROLOGIC + THX GAMES",
    "0079": "THX ULTRA2 GAMES (for multi ch)",
    "0080": "THX MUSIC (for multi ch)",
    "0081": "THX GAMES (for multi ch)",
    "0082": "PL2x MUSIC + THX MUSIC (for multi ch)",
    "0083": "EX + THX GAMES (for multi ch)",
    "0084": "Neo:6 + THX MUSIC (for multi ch)",
    "0085": "Neo:6 + THX GAMES (for multi ch)",
    "0086": "ES MATRIX + THX MUSIC (for multi ch)",
    "0087": "ES MATRIX + THX GAMES (for multi ch)",
    "0088": "ES DISCRETE + THX MUSIC (for multi ch)",
    "0089": "ES DISCRETE + THX GAMES (for multi ch)",
    "0090": "ES 8CH DISCRETE + THX MUSIC (for multi ch)",
    "0091": "ES 8CH DISCRETE + THX GAMES (for multi ch)",
    "0092": "PL2z HEIGHT + THX CINEMA",
    "0093": "PL2z HEIGHT + THX MUSIC",
    "0094": "PL2z HEIGHT + THX GAMES",
    "0095": "PL2z HEIGHT + THX CINEMA (for multi ch)",
    "0096": "PL2z HEIGHT + THX MUSIC (for multi ch)",
    "0097": "PL2z HEIGHT + THX GAMES (for multi ch)",
    "0101": "ACTION",
    "0102": "SCI-FI",
    "0103": "DRAMA",
    "0104": "ENTERTAINMENT SHOW",
    "0105": "MONO FILM",
    "0106": "EXPANDED THEATER",
    "0107": "CLASSICAL",
    "0109": "UNPLUGGED",
    "0110": "ROCK/POP",
    "0112": "EXTENDED STEREO",
    "0113": "PHONES SURROUND",
    "0116": "TV SURROUND",
    "0117": "SPORTS",
    "0118": "ADVANCED GAME",
    "0151": "Auto Level Control",
    "0152": "OPTIMUM SURROUND",
    "0153": "RETRIEVER AIR",
    "0200": "ECO MODE",
    "0201": "Neo:X CINEMA + THX CINEMA",
    "0202": "Neo:X MUSIC + THX MUSIC",
    "0203": "Neo:X GAME + THX GAMES",
    "0204": "Neo:X CINEMA + THX CINEMA (for multi ch)",
    "0205": "Neo:X MUSIC + THX MUSIC (for multi ch)",
    "0206": "Neo:X GAME + THX GAMES (for multi ch)",
    "0212": "ECO MODE 1",
    "0213": "ECO MODE 2",
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
    }
}

TONE_MODES = {
    "0": "Bypass",
    "1": "ON",
    "9": "TONE (Cyclic)",
}

TONE_DB_VALUES = {
    "00": "6db",
    "01": "5db",
    "02": "4db",
    "03": "3db",
    "04": "2db",
    "05": "1db",
    "06": "0db",
    "07": "-1db",
    "08": "-2db",
    "09": "-3db",
    "10": "-4db",
    "11": "-5db",
    "12": "-6db",
}

SPEAKER_MODES = {
    "0": "OFF",
    "1": "A",
    "2": "B",
    "3": "A+B",
}

HDMI_OUT_MODES = {
    "0": "ALL",
    "1": "HDMI 1",
    "2": "HDMI 2",
    "3": "HDMI (cyclic)",
}

HDMI_AUDIO_MODES = {
    "0": "AMP",
    "1": "PASSTHROUGH",
}

PANEL_LOCK = {
    "0": "OFF",
    "1": "PANEL ONLY",
    "2": "PANEL + VOLUME",
}

PQLS_MODES = {
    "0": "OFF",
    "1": "AUTO",
}

AMP_MODES = {
    "0": "AMP ON",
    "1": "AMP Front OFF",
    "2": "AMP Front & Center OFF",
    "3": "AMP OFF",
}

VIDEO_PURE_CINEMA_MODES = {
    "0": "AUTO",
    "1": "ON",
    "2": "OFF",
}

VIDEO_STREAM_SMOOTHER_MODES = {
    "0": "OFF",
    "1": "ON",
    "2": "AUTO"
}

VIDEO_ASPECT_MODES = {
    "0": "PASSTHROUGH",
    "1": "NORMAL",
}

ADVANCED_VIDEO_ADJUST_MODES = {
    "0": "PDP",
    "1": "LCD",
    "2": "FPJ",
    "3": "Professional",
    "4": "Memory",
}

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

DSP_PHASE_CONTROL = {
    "0": "off",
    "1": "on",
    "2": "full band on"
}

DSP_SIGNAL_SELECT = {
    "0": "AUTO",
    "1": "ANALOG",
    "2": "DIGITAL",
    "3": "HDMI"
}

DSP_DIGITAL_DIALOG_ENHANCEMENT = {
    "0": "off",
    "1": "flat",
    "2": "+1",
    "3": "+2",
    "4": "+3",
    "5": "+4"
}

DSP_DUAL_MONO = {
    "0": "CH1+CH2",
    "1": "CH1",
    "2": "CH2"
}

DSP_DRC = {
    "0": "off",
    "1": "auto",
    "2": "mid",
    "3": "max"
}

DSP_HEIGHT_GAIN = {
    "0": "low",
    "1": "mid",
    "2": "high"
}

DSP_VIRTUAL_DEPTH = {
    "0": "off",
    "1": "min",
    "2": "mid",
    "3": "max"
}

DSP_DIGITAL_FILTER = {
    "0": "slow",
    "1": "sharp",
    "2": "short"
}

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
    "72": "Spotify"
}

AUDIO_SIGNAL_INPUT_FREQ = {
    "00": "32kHz",
    "01": "44.1kHz",
    "02": "48kHz",
    "03": "88.2kHz",
    "04": "96kHz",
    "05": "176.4kHz",
    "06": "192kHz",
    "07": "---",
    "32": "2.8MHz",
    "33": "5.6MHz"
}

AUDIO_WORKING_PQLS = {
    "0": "off",
    "1": "2h",
    "2": "Multi-channel",
    "3": "Bitstream"
}

VIDEO_SIGNAL_INPUT_TERMINAL = {
    "0": "---",
    "1": "VIDEO",
    "2": "S-VIDEO",
    "3": "COMPONENT",
    "4": "HDMI",
    "5": "Self OSD/JPEG",
}

VIDEO_SIGNAL_FORMATS = {
    "00": "---",
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
    "0": "---",
    "1": "4:3",
    "2": "16:9",
    "3": "14:9",
}

VIDEO_SIGNAL_COLORSPACE = {
    "0": "---",
    "1": "RGB Limit",
    "2": "RGB Full",
    "3": "YcbCr444",
    "4": "YcbCr422",
    "5": "YcbCr420",
}

VIDEO_SIGNAL_BITS = {
    "0": "---",
    "1": "24bit (8bit*3)",
    "2": "30bit (10bit*3)",
    "3": "36bit (12bit*3)",
    "4": "48bit (16bit*3)",
}

VIDEO_SIGNAL_EXT_COLORSPACE = {
    "0": "---",
    "1": "Standard",
    "2": "xvYCC601",
    "3": "xvYCC709",
    "4": "sYCC",
    "5": "AdobeYCC601",
    "6": "AdobeRGB",
}

VIDEO_SIGNAL_3D_MODES = {
    "00": "---",
    "01": "Frame packing",
    "02": "Field alternative",
    "03": "Line alternative",
    "04": "Side-by-Side(Full)",
    "05": "L + depth",
    "06": "L + depth + graphics",
    "07": "Top-and-Bottom",
    "08": "Side-by-Side(Half)",
}

VIDEO_RESOLUTION_MODES = {
    "0": "AUTO",
    "1": "PURE",
    "3": "480/576p",
    "4": "720p",
    "5": "1080i",
    "6": "1080p",
    "7": "1080/24p",
    "8": "4K",
    "9": "4K/24p"
}
