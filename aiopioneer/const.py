"""Constants for aiopioneer."""

from enum import StrEnum


VERSION = "0.10.0"
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

    def __repr__(self) -> str:
        return f"Zone.{self.name}"

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


SOURCE_TUNER = 2

# Listening modes is a dict with a nested array for the following structure:
# key: [display_name, 2ch_source_bool, multichannel_source_bool]
LISTENING_MODES = {
    1: ["STEREO", True, True],
    3: ["Front Stage Surround Advance", True, True],
    4: ["Front Stage Surround Advance Wide", True, True],
    5: ["AUTO SURR/STREAM DIRECT", True, True],
    6: ["AUTO SURROUND", True, True],
    7: ["DIRECT", True, True],
    8: ["PURE DIRECT", True, True],
    9: ["STEREO (direct)", True, False],
    10: ["STANDARD", True, False],
    11: ["2ch", True, False],
    12: ["PRO LOGIC", True, False],
    13: ["PRO LOGIC2 MOVIE", True, False],
    14: ["PRO LOGIC2 MUSIC", True, False],
    15: ["PRO LOGIC2 GAME", True, False],
    16: ["Neo:6 CINEMA", True, False],
    17: ["Neo:6 MUSIC", True, False],
    18: ["PRO LOGIC2x MOVIE", True, False],
    19: ["PRO LOGIC2x MUSIC", True, False],
    20: ["PRO LOGIC2x GAME", True, False],
    21: ["Multi ch", False, True],
    22: ["DOLBY EX", False, True],
    23: ["PRO LOGIC2x MOVIE (2)", False, True],
    24: ["PRO LOGIC2x MUSIC (2)", False, True],
    25: ["DTS-ES Neo", False, True],
    26: ["DTS-ES matrix", False, True],
    27: ["DTS-ES discrete", False, True],
    28: ["XM HD SURROUND", True, True],
    29: ["NEURAL SURROUND", True, True],
    30: ["DTS-ES 8ch discrete", False, True],
    31: ["PRO LOGIC2z HEIGHT", True, True],
    32: ["WIDE SURROUND MOVIE", True, True],
    33: ["WIDE SURROUND MUSIC", True, True],
    34: ["PRO LOGIC2z HEIGHT (2)", False, True],
    35: ["WIDE SURROUND MOVIE (2)", False, True],
    36: ["WIDE SURROUND MUSIC (2)", False, True],
    37: ["Neo:X CINEMA", True, True],
    38: ["Neo:X MUSIC", True, True],
    39: ["Neo:X GAME", True, True],
    40: ["NEURAL SURROUND+Neo:X CINEMA", True, True],
    41: ["NEURAL SURROUND+Neo:X MUSIC", True, True],
    42: ["NEURAL SURROUND+Neo:X GAME", True, True],
    43: ["Neo:X CINEMA (2)", False, True],
    44: ["Neo:X MUSIC (2)", False, True],
    45: ["Neo:X GAME (2)", False, True],
    51: ["PROLOGIC + THX CINEMA", True, True],
    52: ["PL2 MOVIE + THX CINEMA", True, True],
    53: ["Neo:6 CINEMA + THX CINEMA", True, True],
    54: ["PL2x MOVIE + THX CINEMA", True, True],
    55: ["THX SELECT2 GAMES", True, True],
    56: ["THX CINEMA", False, True],
    57: ["THX SURROUND EX", False, True],
    58: ["PL2x MOVIE + THX CINEMA (2)", False, True],
    59: ["ES Neo:6 + THX CINEMA", False, True],
    60: ["ES MATRIX + THX CINEMA", False, True],
    61: ["ES DISCRETE + THX CINEMA", False, True],
    62: ["THX SELECT2 CINEMA", False, True],
    63: ["THX SELECT2 MUSIC", False, True],
    64: ["THX SELECT2 GAMES (2)", False, True],
    65: ["THX ULTRA2 CINEMA", False, True],
    66: ["THX ULTRA2 MUSIC", False, True],
    67: ["ES 8ch DISCRETE + THX CINEMA", False, True],
    68: ["THX CINEMA (2)", True, False],
    69: ["THX MUSIC (2)", True, False],
    70: ["THX GAMES (2)", True, False],
    71: ["PL2 MUSIC + THX MUSIC", True, True],
    72: ["PL2x MUSIC + THX MUSIC", True, True],
    73: ["Neo:6 MUSIC + THX MUSIC", True, True],
    74: ["PL2 GAME + THX GAMES", True, True],
    75: ["PL2x GAME + THX GAMES", True, True],
    76: ["THX ULTRA2 GAMES", True, True],
    77: ["PROLOGIC + THX MUSIC", True, True],
    78: ["PROLOGIC + THX GAMES", True, True],
    79: ["THX ULTRA2 GAMES (2)", False, True],
    80: ["THX MUSIC", False, True],
    81: ["THX GAMES", False, True],
    82: ["PL2x MUSIC + THX MUSIC (2)", False, True],
    83: ["EX + THX GAMES", False, True],
    84: ["Neo:6 + THX MUSIC", False, True],
    85: ["Neo:6 + THX GAMES", False, True],
    86: ["ES MATRIX + THX MUSIC", False, True],
    87: ["ES MATRIX + THX GAMES", False, True],
    88: ["ES DISCRETE + THX MUSIC", False, True],
    89: ["ES DISCRETE + THX GAMES", False, True],
    90: ["ES 8CH DISCRETE + THX MUSIC", False, True],
    91: ["ES 8CH DISCRETE + THX GAMES", False, True],
    92: ["PL2z HEIGHT + THX CINEMA", True, False],
    93: ["PL2z HEIGHT + THX MUSIC", True, False],
    94: ["PL2z HEIGHT + THX GAMES", True, False],
    95: ["PL2z HEIGHT + THX CINEMA (2)", False, True],
    96: ["PL2z HEIGHT + THX MUSIC (2)", False, True],
    97: ["PL2z HEIGHT + THX GAMES (2)", False, True],
    101: ["ACTION", True, True],
    102: ["SCI-FI", True, True],
    103: ["DRAMA", True, True],
    104: ["ENTERTAINMENT SHOW", True, True],
    105: ["MONO FILM", True, True],
    106: ["EXPANDED THEATER", True, True],
    107: ["CLASSICAL", True, True],
    109: ["UNPLUGGED", True, True],
    110: ["ROCK/POP", True, True],
    112: ["EXTENDED STEREO", True, True],
    113: ["PHONES SURROUND", True, True],
    116: ["TV SURROUND", True, True],
    117: ["SPORTS", True, True],
    118: ["ADVANCED GAME", True, True],
    151: ["Auto Level Control", True, True],
    152: ["OPTIMUM SURROUND", True, True],
    153: ["RETRIEVER AIR", True, True],
    200: ["ECO MODE", True, True],
    201: ["Neo:X CINEMA + THX CINEMA", True, False],
    202: ["Neo:X MUSIC + THX MUSIC", True, False],
    203: ["Neo:X GAME + THX GAMES", True, False],
    204: ["Neo:X CINEMA + THX CINEMA (2)", False, True],
    205: ["Neo:X MUSIC + THX MUSIC (2)", False, True],
    206: ["Neo:X GAME + THX GAMES (2)", False, True],
    212: ["ECO MODE 1", True, True],
    213: ["ECO MODE 2", True, True],
}

MEDIA_CONTROL_SOURCES = {
    26: "NETWORK",
    38: "NETWORK",
    44: "NETWORK",
    2: "TUNER",
    13: "ADAPTERPORT",
    41: "NETWORK",
    53: "NETWORK",
    17: "IPOD",
    33: "BLUETOOTH",
}

MEDIA_CONTROL_COMMANDS = {
    "NETWORK": {
        "play": "network_play",
        "pause": "network_pause",
        "stop": "network_stop",
        "ff": "network_fastforward",
        "rw": "network_rewind",
        "next": "network_next",
        "previous": "network_previous",
        "repeat": "network_repeat",
        "shuffle": "network_random",
    },
    "IPOD": {
        "play": "ipod_play",
        "pause": "ipod_pause",
        "stop": "ipod_stop",
        "ff": "ipod_fastforward",
        "rw": "ipod_rewind",
        "next": "ipod_next",
        "previous": "ipod_previous",
        "repeat": "ipod_repeat",
        "shuffle": "ipod_shuffle",
    },
    "TUNER": {
        "ff": "tuner_increase_frequency",
        "rw": "tuner_decrease_frequency",
        "next": "tuner_next_preset",
        "previous": "tuner_previous_preset",
    },
    "ADAPTERPORT": {
        "play": "adapterport_play",
        "pause": "adapterport_pause",
        "stop": "adapterport_stop",
        "previous": "adapterport_previous",
        "next": "adapterport_next",
        "rw": "adapterport_rewind",
        "ff": "adapterport_fastforward",
        "repeat": "adapterport_repeat",
        "shuffle": "adapterport_random",
    },
    "BLUETOOTH": {
        "play": "bluetooth_play",
        "pause": "bluetooth_pause",
        "stop": "bluetooth_stop",
        "previous": "bluetooth_previous",
        "next": "bluetooth_next",
        "rw": "bluetooth_rewind",
        "ff": "bluetooth_fastforward",
        "repeat": "bluetooth_repeat",
        "shuffle": "bluetooth_random",
    },
    "MHL": {
        "play": "mhl_play",
        "pause": "mhl_pause",
        "stop": "mhl_stop",
        "record": "mhl_record",
        "rw": "mhl_rewind",
        "ff": "mhl_fastforward",
        "eject": "mhl_eject",
        "next": "mhl_next",
        "previous": "mhl_previous",
    },
}
MEDIA_CONTROL_COMMANDS_ALL = set(
    sum([list(v.keys()) for v in MEDIA_CONTROL_COMMANDS.values()], [])
)
