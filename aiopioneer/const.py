"""Constants for aiopioneer."""

from enum import StrEnum


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
