"""AVR device parameters."""

# pylint: disable=too-many-lines

from collections import OrderedDict
from .const import Zones

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
PARAM_ZONE_1_SOURCES = "zone_1_sources"  ## All possible valid input sources for Zone 1
PARAM_ZONE_2_SOURCES = "zone_2_sources"  ## All possible valid input sources for Zone 2
PARAM_ZONE_3_SOURCES = "zone_3_sources"  ## All possible valid input sources for Zone 3
PARAM_HDZONE_SOURCES = "hdzone_sources"  ## All possible valid input sources for HDZone
PARAM_ZONE_SOURCES = {
    Zones.Z1: PARAM_ZONE_1_SOURCES,
    Zones.Z2: PARAM_ZONE_2_SOURCES,
    Zones.Z3: PARAM_ZONE_3_SOURCES,
    Zones.HDZ: PARAM_HDZONE_SOURCES,
}

## All possible valid speaker system settings for HDZone volume functions to be available
PARAM_HDZONE_VOLUME_REQUIREMENTS = "hdzone_volume_requirements"
## All possible speaker system modes. Different AVR models will have different available options
PARAM_SPEAKER_SYSTEM_MODES = "amp_speaker_system_modes"
## All valid video resolution modes
PARAM_VIDEO_RESOLUTION_MODES = "video_resolution_modes"
PARAM_MHL_SOURCE = "mhl_source"
## Stores all the enabled high level categories for the AVR.
PARAM_ENABLED_FUNCTIONS = "enabled_functions"
## If set to True, the AVR won't auto query additional attributes in high level
## categories, instead we rely on the AVR returning them as they are changed.
PARAM_DISABLE_AUTO_QUERY = "disable_auto_query"
## List of additional listening modes. Overrides LISTENING_MODES. Non-unique
## display names will be ignored
## key: [display_name, 2ch_source_bool, multichannel_source_bool]
PARAM_EXTRA_LISTENING_MODES = "extra_amp_listening_modes"
## List of enabled listening mode IDs. If specified, then no listening modes
## are added by default
PARAM_ENABLED_LISTENING_MODES = "enabled_amp_listening_modes"
## List of disabled listening mode IDs. Override IDs that are also specified in
## PARAM_EXTRA_LISTENING_MODES
PARAM_DISABLED_LISTENING_MODES = "disabled_amp_listening_modes"
## Tuner step for AM frequencies. If None, calculate automatically when tuner is first used
PARAM_TUNER_AM_FREQ_STEP = "am_frequency_step"

## System params
PARAM_QUERY_SOURCES = "query_sources"
## List of all possible listening modes
PARAM_ALL_LISTENING_MODES = "all_listening_modes"
## List of listening modes available for selection on AVR
PARAM_AVAILABLE_LISTENING_MODES = "available_listening_modes"

DEFAULT_PARAM_ENABLED_FUNCTIONS = [
    "amp",
    "dsp",
    "tuner",
    "tone",
    "channels",
    "video",
    "system",
    "audio",
    "display",
]

PARAM_ENABLED_FUNCTIONS_NO_VIDEO = [
    "amp",
    "dsp",
    "tuner",
    "tone",
    "channels",
    "system",
    "audio",
    "display",
]

PARAM_DEFAULTS_SYSTEM = {
    PARAM_QUERY_SOURCES: None,
    PARAM_AVAILABLE_LISTENING_MODES: None,
}

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
    PARAM_ENABLED_FUNCTIONS: DEFAULT_PARAM_ENABLED_FUNCTIONS,
    PARAM_DISABLE_AUTO_QUERY: False,
    PARAM_ZONE_1_SOURCES: [],
    PARAM_ZONE_2_SOURCES: [
        "04",
        "06",
        "15",
        "26",
        "38",
        "53",
        "41",
        "44",
        "45",
        "17",
        "13",
        "05",
        "01",
        "02",
        "33",
        "46",
        "47",
        "99",
        "10",
    ],
    PARAM_ZONE_3_SOURCES: [
        "04",
        "06",
        "15",
        "26",
        "38",
        "53",
        "41",
        "44",
        "45",
        "17",
        "13",
        "05",
        "01",
        "02",
        "33",
        "46",
        "47",
        "99",
        "10",
    ],
    PARAM_HDZONE_SOURCES: [
        "25",
        "04",
        "06",
        "10",
        "15",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "34",
        "35",
        "26",
        "38",
        "53",
        "41",
        "44",
        "45",
        "17",
        "13",
        "33",
        "31",
        "46",
        "47",
        "48",
    ],
    PARAM_HDZONE_VOLUME_REQUIREMENTS: ["13", "15", "05", "25"],
    PARAM_SPEAKER_SYSTEM_MODES: {
        "00": "Normal / 5.2.2ch / 7.2ch",
        "01": "7.2ch SB/FW",
        "02": "Speaker B",
        "03": "Front Bi-Amp",
        "04": "Zone 2",
        "05": "HDZone",
        "07": "5.2ch",
        "08": "Front Bi-Amp",
        "09": "Speaker B",
        "10": "9.1ch FH/FW",
        "11": "7.2.2/7.2ch +SP-B",
        "12": "7.2ch Front Bi-Amp",
        "13": "7.2ch + HDZONE",
        "14": "7.1ch FH/FW + ZONE 2",
        "15": "5.2ch Bi-Amp + HDZONE",
        "16": "5.2ch + ZONE 2+3",
        "17": "5.2ch + SP-B Bi-Amp",
        "18": "5.2ch F+Surr Bi-Amp",
        "19": "5.2ch F+C Bi-Amp",
        "20": "5.2ch C+Surr Bi-Amp",
        "21": "Multi-ZONE Music",
        "22": "7.2.2ch TMd/FW",
        "23": "7.2.2ch TMd/FH",
        "24": "5.2.4ch",
        "25": "5.2ch ZONE 2 + HDZONE",
        "26": "7.2.2/5.2.2/7.2ch",
        "27": "7.2.2c Front Bi-Amp",
        "30": "9.2.2ch TMd/FH",
        "31": "7.2.4ch SB Pre Out",
        "32": "7.2.4ch Front Pre Out",
    },
    PARAM_EXTRA_LISTENING_MODES: {},
    PARAM_DISABLED_LISTENING_MODES: [],
    PARAM_ENABLED_LISTENING_MODES: [],
    PARAM_VIDEO_RESOLUTION_MODES: ["0", "1", "3", "4", "5", "6", "7", "8", "9"],
    PARAM_MHL_SOURCE: None,
    PARAM_TUNER_AM_FREQ_STEP: None,
}

PARAMS_ALL = PARAM_DEFAULTS.keys()

PARAM_DISABLED_LISTENING_MODES_SC_LX79 = [
    "0004",
    "0011",
    "0016",
    "0017",
    "0025",
    "0028",
    "0029",
    "0053",
    "0055",
    "0059",
    "0073",
    "0076",
    "0077",
    "0078",
    "0083",
    "0084",
    "0085",
    "0102",
    "0104",
    "0105",
    "0106",
    "0109",
    "0116",
]

PARAM_DISABLED_LISTENING_MODES_SC_2023 = [
    "0004",
    "0011",
    "0016",
    "0017",
    "0025",
    "0028",
    "0029",
    "0051",
    "0052",
    "0053",
    "0054",
    "0055",
    "0056",
    "0057",
    "0058",
    "0059",
    "0060",
    "0061",
    "0062",
    "0063",
    "0064",
    "0065",
    "0066",
    "0067",
    "0068",
    "0069",
    "0070",
    "0071",
    "0072",
    "0073",
    "0074",
    "0075",
    "0076",
    "0077",
    "0078",
    "0079",
    "0080",
    "0081",
    "0082",
    "0083",
    "0084",
    "0085",
    "0086",
    "0087",
    "0088",
    "0089",
    "0090",
    "0091",
    "0092",
    "0093",
    "0094",
    "0095",
    "0096",
    "0097",
    "0102",
    "0104",
    "0105",
    "0106",
    "0109",
    "0116",
    "0152",
    "0201",
    "0202",
    "0203",
    "0204",
    "0205",
    "0206",
]

PARAM_SPEAKER_SYSTEM_MODES_SC_LX79 = {
    "00": "Normal (SB/FH)",
    "01": "Normal (SB/FW)",
    "02": "Speaker B",
    "03": "Front Bi-Amp",
    "04": "Zone 2",
    "10": "9.1ch FH/FW",
    "11": "7.1ch + Speaker B",
    "12": "7.1ch Front Bi-Amp",
    "13": "7.1ch + ZONE2",
    "14": "7.1ch FH/FW + ZONE 2",
    "15": "5.1ch Bi-Amp + ZONE2",
    "16": "5.1ch + ZONE 2+3",
    "17": "5.1ch + SP-B Bi-Amp",
    "18": "5.1ch F+Surr Bi-Amp",
    "19": "5.1ch F+C Bi-Amp",
    "20": "5.1ch C+Surr Bi-Amp",
    "21": "Multi-ZONE Music",
}

PARAM_MODEL_DEFAULTS = OrderedDict(
    [
        (
            r"^VSX-930",
            {
                PARAM_EXTRA_LISTENING_MODES: {
                    "0040": ["Dolby Surround", True, True],
                    "0041": ["EXTENDED STEREO", True, True],
                    "0100": ["ADVANCED SURROUND (cyclic)", True, True],
                },
                PARAM_ENABLED_LISTENING_MODES: [
                    "0005",
                    "0006",
                    "0007",
                    "0008",
                    "0009",
                    "0010",
                    "0016",
                    "0040",
                    "0041",
                    "0100",
                    "0151",
                    "0212",
                ],
                # Zone 1 volume returns E02 if only HDZone is on
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_ENABLED_FUNCTIONS: PARAM_ENABLED_FUNCTIONS_NO_VIDEO,
            },
        ),
        (
            r"^VSX-1130",
            {
                PARAM_EXTRA_LISTENING_MODES: {
                    "0040": ["Dolby Surround", True, True],
                },
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
            r"^SC-LX79",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-LX87",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_ZONE_2_SOURCES: [
                    "04",
                    "06",
                    "15",
                    "26",
                    "38",
                    "53",
                    "44",
                    "45",
                    "17",
                    "05",
                    "01",
                    "02",
                    "33",
                    "46",
                    "47",
                    "99",
                    "10",
                    "13",
                ],
                PARAM_ZONE_3_SOURCES: [
                    "04",
                    "06",
                    "15",
                    "26",
                    "38",
                    "53",
                    "44",
                    "45",
                    "17",
                    "13",
                    "05",
                    "01",
                    "02",
                    "33",
                    "46",
                    "47",
                    "99",
                    "10",
                ],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-77",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-LX77",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_ZONE_2_SOURCES: [
                    "04",
                    "06",
                    "15",
                    "26",
                    "38",
                    "53",
                    "44",
                    "45",
                    "17",
                    "05",
                    "01",
                    "02",
                    "33",
                    "46",
                    "47",
                    "99",
                    "10",
                ],
                PARAM_ZONE_3_SOURCES: [
                    "04",
                    "06",
                    "15",
                    "26",
                    "38",
                    "53",
                    "44",
                    "45",
                    "17",
                    "13",
                    "05",
                    "01",
                    "02",
                    "33",
                    "46",
                    "47",
                    "99",
                    "10",
                ],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-75",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-1523",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-1528",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-LX57",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_ZONE_2_SOURCES: [
                    "04",
                    "06",
                    "15",
                    "26",
                    "38",
                    "53",
                    "44",
                    "45",
                    "17",
                    "05",
                    "01",
                    "02",
                    "33",
                    "46",
                    "47",
                    "99",
                    "10",
                ],
                PARAM_ZONE_3_SOURCES: [
                    "04",
                    "06",
                    "15",
                    "05",
                    "01",
                    "02",
                    "33",
                    "10",
                    "99",
                ],
                PARAM_MHL_SOURCE: "23",
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-72",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-1323",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-1328",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_LX79,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-2023",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_ZONE_3_SOURCES: [
                    "04",
                    "06",
                    "15",
                    "05",
                    "01",
                    "02",
                    "33",
                    "10",
                    "99",
                ],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_2023,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-71",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-1223",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_2023,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^SC-1228",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^VSX-1123",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_2023,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^VSX-1128",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^VSX-1028",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (
            r"^VSX-923",
            {
                PARAM_IGNORE_VOLUME_CHECK: True,
                PARAM_HDZONE_VOLUME_REQUIREMENTS: [],
                PARAM_DISABLED_LISTENING_MODES: PARAM_DISABLED_LISTENING_MODES_SC_2023,
                PARAM_SPEAKER_SYSTEM_MODES: PARAM_SPEAKER_SYSTEM_MODES_SC_LX79,
            },
        ),
        (r"^VSX-45", {PARAM_HDZONE_VOLUME_REQUIREMENTS: []}),
        (r"^VSX-830", {PARAM_HDZONE_VOLUME_REQUIREMENTS: []}),
    ]
)
