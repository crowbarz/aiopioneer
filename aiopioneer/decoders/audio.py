"""aiopioneer response decoders for audio responses."""

from ..command_queue import CommandItem
from ..const import Zone, CHANNELS_ALL
from ..exceptions import AVRCommandUnavailableError
from ..params import AVRParams
from ..properties import AVRProperties
from .code_map import (
    CodeDefault,
    CodeMapBlank,
    CodeMapSequence,
    CodeMapQuery,
    CodeDynamicDictStrMap,
    CodeDynamicDictListMap,
    CodeDictStrMap,
    CodeStrMap,
    CodeBoolMap,
    CodeIntMap,
    CodeFloatMap,
)
from .response import Response


class AudioChannelActive(CodeDictStrMap):
    """Audio channel active."""

    friendly_name = "audio channel active"
    base_property = "audio"
    property_name = "channel_active"  # unused

    code_map = {
        "0": "inactive",
        "1": "active",
    }

    def __new__(cls, channel_type: str, channel: str):
        """Create a subclass for channel type and name."""
        return type(
            f"AudioChannelActive_{channel_type}_{channel}",
            (AudioChannelActive,),
            {
                "friendly_name": f"{channel_type} channel {channel}",
                "property_name": f"{channel_type}_channels.{channel}",
            },
        )


class AudioInputMultichannel(CodeBoolMap):
    """Audio input multichannel."""

    friendly_name = "audio input multichannel"
    base_property = "audio"
    property_name = "input_multichannel"

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for input multichannel."""

        def check_input_multichannel(response: Response) -> list[Response]:
            """Trigger listening mode update if input multichannel has changed."""
            if response.properties.audio.get("input_multichannel") == response.value:
                return []
            response.update(
                queue_commands=[CommandItem("_update_listening_modes", queue_id=3)]
            )
            return [response]

        super().decode_response(response=response, params=params)
        response.update(callback=check_input_multichannel)
        return [response]

    @classmethod
    def code_to_value(cls, code: str) -> bool:
        return all([CodeBoolMap[c] for c in code])


class AudioSignalInputInfo(CodeDictStrMap):
    """Audio signal input info."""

    friendly_name = "audio input signal"  # NOTE: inconsistent
    base_property = "audio"
    property_name = "input_signal"

    code_map = {
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


class AudioSignalFrequency(CodeDictStrMap):
    """Audio signal frequency."""

    friendly_name = "audio frequency"
    base_property = "audio"
    property_name = "frequency"  # unused

    code_map = {
        CodeDefault(): None,
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


class AudioInputFrequency(AudioSignalFrequency):
    """Audio input frequency."""

    friendly_name = "audio input frequency"
    base_property = "audio"
    property_name = "input_frequency"


class AudioOutputFrequency(AudioSignalFrequency):
    """Audio output frequency."""

    friendly_name = "audio output frequency"
    base_property = "audio"
    property_name = "output_frequency"


class AudioOutputBits(CodeIntMap):
    """Audio output bits."""

    friendly_name = "audio output bits"
    base_property = "audio"
    property_name = "output_bits"

    code_zfill = 2


class AudioOutputPqls(CodeDictStrMap):
    """Audio output PQLS."""

    friendly_name = "audio output PQLS"
    base_property = "audio"
    property_name = "output_pqls"

    code_map = {"0": "off", "1": "2h", "2": "Multi-channel", "3": "Bitstream"}


class AudioOutputAutoPhaseControlPlus(CodeIntMap):
    """Audio output auto phase control plus."""

    friendly_name = "audio output auto phase control plus"
    base_property = "audio"
    property_name = "output_auto_phase_control_plus"

    code_zfill = 2


class AudioOutputReversePhase(CodeBoolMap):
    """Audio output reverse phase."""

    friendly_name = "audio output reverse phase"
    base_property = "audio"
    property_name = "output_reverse_phase"


class AudioInformation(CodeMapSequence):
    """Audio information."""

    friendly_name = "audio information"
    base_property = "audio"
    property_name = "information"  # unused

    code_map_sequence = [
        AudioSignalInputInfo,  # [0:2] audio.input_signal
        AudioInputFrequency,  # [2:4] audio.input_frequency
        AudioChannelActive("input", "L"),  # [4]
        AudioChannelActive("input", "C"),  # [5]
        AudioChannelActive("input", "R"),  # [6]
        AudioChannelActive("input", "SL"),  # [7]
        AudioChannelActive("input", "SR"),  # [8]
        AudioChannelActive("input", "SBL"),  # [9]
        AudioChannelActive("input", "SBC"),  # [10]
        AudioChannelActive("input", "SBR"),  # [11]
        AudioChannelActive("input", "LFE"),  # [12]
        AudioChannelActive("input", "FHL"),  # [13]
        AudioChannelActive("input", "FHR"),  # [14]
        AudioChannelActive("input", "FWL"),  # [15]
        AudioChannelActive("input", "FWR"),  # [16]
        AudioChannelActive("input", "XL"),  # [17]
        AudioChannelActive("input", "XC"),  # [18]
        AudioChannelActive("input", "XR"),  # [19]
        CodeMapBlank(5),  ## (data21) to (data25) are reserved according to FY16AVRs
        AudioChannelActive("output", "L"),  # [25]
        AudioChannelActive("output", "C"),  # [26]
        AudioChannelActive("output", "R"),  # [27]
        AudioChannelActive("output", "SL"),  # [28]
        AudioChannelActive("output", "SR"),  # [29]
        AudioChannelActive("output", "SBL"),  # [30]
        AudioChannelActive("output", "SB"),  # [31]
        AudioChannelActive("output", "SBR"),  # [32]
    ]
    code_map_sequence_extra_1 = [
        *code_map_sequence,
        AudioChannelActive("output", "SW"),  # [33]
        AudioChannelActive("output", "FHL"),  # [34]
        AudioChannelActive("output", "FHR"),  # [35]
        AudioChannelActive("output", "FWL"),  # [36]
        AudioChannelActive("output", "FWR"),  # [37]
        AudioChannelActive("output", "TML"),  # [38]
        AudioChannelActive("output", "TMR"),  # [39]
        AudioChannelActive("output", "TRL"),  # [40]
        AudioChannelActive("output", "TRR"),  # [41]
        AudioChannelActive("output", "SW2"),  # [42]
    ]
    code_map_sequence_extra_2 = [
        *code_map_sequence_extra_1,
        AudioOutputFrequency,  # [43:45] audio.output_frequency
        AudioOutputBits,  # [45:47] audio.output_bits
        CodeMapBlank(4),
        AudioOutputPqls,  # [51] audio.output_pqls
        AudioOutputAutoPhaseControlPlus,  # [52:54] audio.output_auto_phase_control_plus
        AudioOutputReversePhase,  # [54] audio.output_reverse_phase
    ]

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for audio information."""
        code_map_sequence = cls.code_map_sequence

        if len(response.code) >= 55:
            code_map_sequence = cls.code_map_sequence_extra_2
        elif len(response.code) >= 43:
            ## FY11 AVRs do not have more than 43 data bits (VSX-1021)
            code_map_sequence = cls.code_map_sequence_extra_1

        responses = AudioInputMultichannel.decode_response(
            response=response.clone(code=response.code[4:7]), params=params
        )
        responses.extend(
            cls.decode_response_sequence(
                response=response, params=params, code_map_sequence=code_map_sequence
            )
        )
        return responses


class ChannelLevel(CodeFloatMap):
    """Channel level. (1step=0.5dB)"""

    friendly_name = "channel level"

    value_min = -12
    value_max = 12
    value_step = 0.5
    value_divider = 0.5
    value_offset = 25
    code_zfill = 2


class SpeakerChannel(CodeStrMap):
    """Speaker channel."""

    friendly_name = "speaker channel"

    code_len = 3

    @classmethod
    def value_to_code(cls, value: str) -> str:
        if value == "all":
            value = value.upper()
        elif value not in CHANNELS_ALL:
            raise ValueError(f"unknown channel {value} for {cls.get_name()}")
        return super().value_to_code(value=value)

    @classmethod
    def code_to_value(cls, code: str) -> str:
        return super().code_to_value(code=code).upper()

    @classmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
    ) -> str:
        channel: str = args[0]
        if channel != "all" and zone in properties.zones_initial_refresh:
            if (channel_levels := properties.channel_levels.get(zone)) is None:
                raise AVRCommandUnavailableError(
                    command=command, err_key="channel_levels", zone=zone
                )
            if channel_levels.get(channel) is None:
                raise AVRCommandUnavailableError(
                    command=command, err_key="channel", zone=zone, channel=channel
                )
        return super().parse_args(
            command=command, args=args, zone=zone, params=params, properties=properties
        )


class SpeakerChannelLevel(CodeMapSequence):
    """Speaker channel level."""

    friendly_name = "speaker channel level"
    base_property = "channel_levels"
    code_map_sequence = [SpeakerChannel, ChannelLevel]

    @classmethod
    def decode_response(cls, response: Response, params: AVRParams) -> list[Response]:
        responses = super().decode_response(response=response, params=params)
        speaker = responses[0].value
        level = responses[1].value
        level_code = responses[1].code
        if speaker == "ALL":
            responses = []
            channel_levels = response.properties.channel_levels.get(response.zone, {})
            for channel in channel_levels.keys():
                responses.append(
                    response.clone(code=level_code, property_name=channel, value=level)
                )
            return responses
        response.update(code=level_code, property_name=speaker, value=level)
        return [response]


class ListeningModeIndex(CodeIntMap):
    """Listening mode index."""

    friendly_name = "listening mode"

    value_min = 0
    value_max = 9999
    code_zfill = 4


class ListeningMode(CodeDynamicDictListMap):
    """Listening mode."""

    friendly_name = "listening mode"
    base_property = "listening_mode"

    index_map_class = ListeningModeIndex

    @classmethod
    def value_to_code(cls, value: str, properties: AVRProperties = None) -> str:
        if not isinstance(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        return cls.value_to_code_dynamic(value, code_map=properties.listening_modes_all)

    @classmethod
    def code_to_value(cls, code: str, properties: AVRProperties = None) -> str:
        if not isinstance(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        return cls.code_to_value_dynamic(code, code_map=properties.listening_modes_all)

    @classmethod
    def parse_args(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,  # pylint: disable=unused-argument
        params: AVRParams,  # pylint: disable=unused-argument
        properties: AVRProperties,
    ) -> str:
        return cls.parse_args_dynamic(
            command=command,
            args=args,
            zone=zone,
            params=params,
            properties=properties,
            code_map=properties.listening_modes_all,
        )

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for listening mode."""
        cls.decode_response_dynamic(
            response=response,
            params=params,
            code_map=response.properties.listening_modes_all,
        )
        return [
            response,
            response.clone(
                base_property="listening_mode_raw",
                value=cls.index_map_class.code_to_value(code=response.code),
            ),
        ]


# pylint: disable=abstract-method
class AvailableListeningMode(CodeDynamicDictStrMap):
    """Available listening mode."""

    index_map_class = ListeningModeIndex

    @classmethod
    def value_to_code(cls, value: str | int, properties: AVRProperties = None) -> str:
        if not isinstance(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        if isinstance(value, int):
            return cls.index_map_class(value=value)
        return cls.value_to_code_dynamic(
            value, code_map=properties.available_listening_modes
        )

    @classmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,  # pylint: disable=unused-argument
        params: AVRParams,  # pylint: disable=unused-argument
        properties: AVRProperties,
    ) -> str:
        return cls.parse_args_dynamic(
            command=command,
            args=args,
            zone=zone,
            params=params,
            properties=properties,
            code_map=properties.available_listening_modes,
        )

    ## NOTE: code_to_value unimplemented


class ToneMode(CodeDictStrMap):
    """Tone mode."""

    friendly_name = "channel level"
    base_property = "tone"
    property_name = "status"

    code_map = {"0": "bypass", "1": "on"}


class ToneDb(CodeIntMap):
    """Tone dB value."""

    value_min = -6
    value_max = 6
    value_divider = -1
    value_offset = -6
    code_zfill = 2


class ToneBass(ToneDb):
    """Tone bass."""

    friendly_name = "tone bass"
    base_property = "tone"
    property_name = "bass"


class ToneTreble(ToneDb):
    """Tone treble."""

    friendly_name = "tone treble"
    base_property = "tone"
    property_name = "treble"


COMMANDS_AUDIO = {
    "query_basic_audio_information": {Zone.Z1: ["?AST", "AST"]},
    "query_listening_mode": {Zone.Z1: ["?S", "SR"]},
    "set_listening_mode": {Zone.Z1: ["SR", "SR"], "args": [AvailableListeningMode]},
    "query_tone_status": {Zone.Z1: ["?TO", "TO"], Zone.Z2: ["?ZGA", "ZGA"]},
    "query_tone_bass": {Zone.Z1: ["?BA", "BA"], Zone.Z2: ["?ZGB", "ZGB"]},
    "query_tone_treble": {Zone.Z1: ["?TR", "TR"], Zone.Z2: ["?ZGC", "ZGC"]},
    "set_tone_mode": {
        Zone.Z1: ["TO", "TO"],
        Zone.Z2: ["ZGA", "ZGA"],
        "args": [ToneMode],
    },
    "set_tone_bass": {
        Zone.Z1: ["BA", "BA"],
        Zone.Z2: ["ZGB", "ZGB"],
        "args": [ToneBass],
    },
    "set_tone_treble": {
        Zone.Z1: ["TR", "TR"],
        Zone.Z2: ["ZGC", "ZGC"],
        "args": [ToneTreble],
    },
    ## channels
    "set_channel_levels": {
        Zone.Z1: ["CLV", "CLV"],
        Zone.Z2: ["ZGE", "ZGE"],
        Zone.Z3: ["ZHE", "ZHE"],
        "args": [SpeakerChannelLevel],
    },
    "query_channel_levels": {
        Zone.Z1: ["CLV", "CLV"],
        Zone.Z2: ["ZGE", "ZGE"],
        Zone.Z3: ["ZHE", "ZHE"],
        "args": [CodeMapQuery(SpeakerChannel)],
    },
}

RESPONSE_DATA_AUDIO = [
    ("AST", AudioInformation, Zone.ALL),  # audio
    ("CLV", SpeakerChannelLevel, Zone.Z1),  # channel_levels
    ("ZGE", SpeakerChannelLevel, Zone.Z2),  # channel_levels
    ("ZHE", SpeakerChannelLevel, Zone.Z3),  # channel_levels
    ("SR", ListeningMode, Zone.ALL),  # listening_mode
    ("TO", ToneMode, Zone.Z1),  # tone.status
    ("BA", ToneBass, Zone.Z1),  # tone.bass
    ("TR", ToneTreble, Zone.Z1),  # tone.treble
    ("ZGA", ToneMode, Zone.Z2),  # tone.status
    ("ZGB", ToneBass, Zone.Z2),  # tone.bass
    ("ZGC", ToneTreble, Zone.Z2),  # tone.treble
]
