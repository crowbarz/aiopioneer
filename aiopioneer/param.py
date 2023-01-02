"""AVR device parameters."""

from collections import OrderedDict

PARAM_IGNORED_ZONES = "ignored_zones"
PARAM_COMMAND_DELAY = "command_delay"
PARAM_MAX_SOURCE_ID = "max_source_id"
PARAM_MAX_VOLUME = "max_volume"
PARAM_MAX_VOLUME_ZONEX = "max_volume_zonex"
PARAM_POWER_ON_VOLUME_BOUNCE = "power_on_volume_bounce"
PARAM_VOLUME_STEP_ONLY = "volume_step_only"
PARAM_IGNORE_VOLUME_CHECK = "ignore_volume_check"
PARAM_DEBUG_LISTENER = "debug_listener"
PARAM_DEBUG_RESPONDER = "debug_responder"
PARAM_DEBUG_UPDATER = "debug_updater"
PARAM_DEBUG_COMMAND = "debug_command"
PARAM_MULTI_CH_SOURCES = "multi_channel_sources"

PARAM_DEFAULTS = {
    PARAM_IGNORED_ZONES: [],
    PARAM_COMMAND_DELAY: 0.1,
    PARAM_MAX_SOURCE_ID: 60,
    PARAM_MAX_VOLUME: 185,
    PARAM_MAX_VOLUME_ZONEX: 81,
    PARAM_POWER_ON_VOLUME_BOUNCE: False,
    PARAM_VOLUME_STEP_ONLY: False,
    PARAM_IGNORE_VOLUME_CHECK: False,
    PARAM_DEBUG_LISTENER: False,
    PARAM_DEBUG_RESPONDER: False,
    PARAM_DEBUG_UPDATER: False,
    PARAM_DEBUG_COMMAND: False,
    PARAM_MULTI_CH_SOURCES: ["19","20","21", "22", "23", "24", "25", "34", "05"]
}

PARAMS_ALL = PARAM_DEFAULTS.keys()

PARAM_MODEL_DEFAULTS = OrderedDict(
    [
        (
            r"^VSX-930",
            {
                PARAM_POWER_ON_VOLUME_BOUNCE: True,
            },
        ),
        (
            r"^VSX-S510",
            {
                PARAM_VOLUME_STEP_ONLY: True,
            },
        ),
        (
            r"^VSX-528",
            {
                PARAM_VOLUME_STEP_ONLY: True,
            },
        ),
        (
            r"^SC-LX57",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
            },
        ),
        (
            r"^VSX-1123",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
            },
        ),
    ]
)

PARAM_LISTENING_MODES = {
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

PARAM_TONE_MODES = {
    "0": "Bypass",
    "1": "ON",
    "9": "TONE (Cyclic)",
}

PARAM_TONE_DB_VALUES = {
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

PARAM_SPEAKER_MODES = {
    "0": "OFF",
    "1": "A",
    "2": "B",
    "3": "A+B",
}

PARAM_HDMI_OUT_MODES = {
    "0": "ALL",
    "1": "HDMI 1",
    "2": "HDMI 2",
    "3": "HDMI (cyclic)",
}

PARAM_HDMI_AUDIO_MODES = {
    "0": "AMP",
    "1": "PASSTHROUGH",
}

PARAM_PANEL_LOCK = {
    "0": "OFF",
    "1": "PANEL ONLY",
    "2": "PANEL + VOLUME",
}

PARAM_PQLS_MODES = {
    "0": "OFF",
    "1": "AUTO",
}

PARAM_AMP_MODES = {
    "0": "AMP ON",
    "1": "AMP Front OFF",
    "2": "AMP Front & Center OFF",
    "3": "AMP OFF",
}

PARAM_VIDEO_OBJ = {
    "converter": None,
    "resolution": None,
    "pure_cinema": None,
    "prog_motion": None,
    "stream_smoother": None,
    "advanced_video_adjust": None,
    "ynr": None,
    "cnr": None,
    "bnr": None,
    "mnr": None,
    "detail": None,
    "sharpness": None,
    "brightness": None,
    "contrast": None,
    "hue": None,
    "chroma": None,
    "black_setup": None,
    "aspect": None,
}

PARAM_VIDEO_RESOLUTION_MODES = {
    "0": "AUTO",
    "1": "PURE",
    "3": "480/576p",
    "4": "720p",
    "5": "1080i",
    "6": "1080p",
    "7": "1080/24p",
}

PARAM_VIDEO_PURE_CINEMA_MODES = {
    "0": "AUTO",
    "1": "ON",
    "2": "OFF",
}

PARAM_VIDEO_STREAM_SMOOTHER_MODES = {
    "0": "OFF",
    "1": "ON",
    "2": "AUTO"
}

PARAM_VIDEO_ASPECT_MODES = {
    "0": "PASSTHROUGH",
    "1": "NORMAL",
}

PARAM_ADVANCED_VIDEO_ADJUST_MODES = {
    "0": "PDP",
    "1": "LCD",
    "2": "FPJ",
    "3": "Professional",
    "4": "Memory",
}

PARAM_CHANNEL_LEVELS_OBJ = {
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

PARAM_DSP_OBJ = {
    "mcacc_memory_set": None,
    "phase_control": None,
    "virtual_sb": None,
    "virtual_height": None,
    "sound_retriever": None,
    "signal_select": None,
    "analog_input_att": None,
    "eq": None,
    "standing_wave": None,
    "phase_control_plus": None,
    "sound_delay": None,
    "digital_noise_reduction": None,
    "digital_dialog_enhancement": None,
    "hi_bit": None,
    "dual_mono": None,
    "fixed_pcm": None,
    "drc": None,
    "lfe_att": None,
    "sacd_gain": None,
    "auto_delay": None,
    "center_width": None,
    "panorama": None,
    "dimension": None,
    "center_image": None,
    "effect": None,
    "height_gain": None,
    "virtual_depth": None,
    "digital_filter": None,
    "loudness_management": None,
    "virtual_wide": None
}

PARAM_DSP_PHASE_CONTROL = {
    "0": "off",
    "1": "on",
    "2": "full band on"
}

PARAM_DSP_SIGNAL_SELECT = {
    "0": "AUTO",
    "1": "ANALOG",
    "2": "DIGITAL",
    "3": "HDMI"
}

PARAM_DSP_DIGITAL_DIALOG_ENHANCEMENT = {
    "0": "off",
    "1": "flat",
    "2": "+1",
    "3": "+2",
    "4": "+3",
    "5": "+4"
}

PARAM_DSP_DUAL_MONO = {
    "0": "CH1+CH2",
    "1": "CH1",
    "2": "CH2"
}

PARAM_DSP_DRC = {
    "0": "off",
    "1": "auto",
    "2": "mid",
    "3": "max"
}

PARAM_DSP_HEIGHT_GAIN = {
    "0": "low",
    "1": "mid",
    "2": "high"
}

PARAM_DSP_VIRTUAL_DEPTH = {
    "0": "off",
    "1": "min",
    "2": "mid",
    "3": "max"
}

PARAM_DSP_DIGITAL_FILTER = {
    "0": "slow",
    "1": "sharp",
    "2": "short"
}