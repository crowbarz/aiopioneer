"""aiopioneer response decoders for informational responses."""

from ..command_queue import CommandItem
from ..const import Zone
from ..params import AVRParams
from .code_map import (
    CodeMapSequence,
    CodeStrMap,
    CodeDefault,
    CodeBoolMap,
    CodeDictStrMap,
    CodeIntMap,
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

    @classmethod
    def subclass(cls, channel_type: str, channel: str):
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
        AudioChannelActive.subclass("input", "L"),  # [4]
        AudioChannelActive.subclass("input", "C"),  # [5]
        AudioChannelActive.subclass("input", "R"),  # [6]
        AudioChannelActive.subclass("input", "SL"),  # [7]
        AudioChannelActive.subclass("input", "SR"),  # [8]
        AudioChannelActive.subclass("input", "SBL"),  # [9]
        AudioChannelActive.subclass("input", "SBC"),  # [10]
        AudioChannelActive.subclass("input", "SBR"),  # [11]
        AudioChannelActive.subclass("input", "LFE"),  # [12]
        AudioChannelActive.subclass("input", "FHL"),  # [13]
        AudioChannelActive.subclass("input", "FHR"),  # [14]
        AudioChannelActive.subclass("input", "FWL"),  # [15]
        AudioChannelActive.subclass("input", "FWR"),  # [16]
        AudioChannelActive.subclass("input", "XL"),  # [17]
        AudioChannelActive.subclass("input", "XC"),  # [18]
        AudioChannelActive.subclass("input", "XR"),  # [19]
        5,  ## (data21) to (data25) are reserved according to FY16AVRs
        AudioChannelActive.subclass("output", "L"),  # [25]
        AudioChannelActive.subclass("output", "C"),  # [26]
        AudioChannelActive.subclass("output", "R"),  # [27]
        AudioChannelActive.subclass("output", "SL"),  # [28]
        AudioChannelActive.subclass("output", "SR"),  # [29]
        AudioChannelActive.subclass("output", "SBL"),  # [30]
        AudioChannelActive.subclass("output", "SB"),  # [31]
        AudioChannelActive.subclass("output", "SBR"),  # [32]
    ]
    code_map_sequence_extra = [
        *code_map_sequence,
        10,
        AudioOutputFrequency,  # [43:45] audio.output_frequency
        AudioOutputBits,  # [45:47] audio.output_bits
        4,
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

        ## FY11 AVRs do not have more than 43 data bits (VSX-1021)
        if len(response.code) > 43:
            code_map_sequence = cls.code_map_sequence_extra

        responses = AudioInputMultichannel.decode_response(
            response=response.clone(code=response.code[4:7]), params=params
        )
        responses.extend(
            cls.decode_response_sequence(
                response=response, params=params, code_map_sequence=code_map_sequence
            )
        )
        return responses


class VideoSignalInputTerminal(CodeDictStrMap):
    """Video signal input terminal."""

    friendly_name = "video signal input terminal"
    base_property = "video"
    property_name = "signal_input_terminal"

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "VIDEO",
        "2": "S-VIDEO",
        "3": "COMPONENT",
        "4": "HDMI",
        "5": "Self OSD/JPEG",
    }


class VideoSignalFormat(CodeDictStrMap):
    """Video signal format."""

    friendly_name = "video signal format"
    base_property = "video"
    property_name = "signal_format"  # unused

    code_map = {
        CodeDefault(): None,
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


class VideoSignalInputResolution(VideoSignalFormat):
    """Video signal input resolution."""

    friendly_name = "video signal input resolution"
    base_property = "video"
    property_name = "signal_input_resolution"


class VideoSignalOutputResolution(VideoSignalFormat):
    """Video signal output resolution."""

    friendly_name = "video signal output resolution"
    base_property = "video"
    property_name = "signal_output_resolution"


class VideoSignalHdmi1RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI1 recommended resolution."""

    friendly_name = "video signal HDMI1 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi1_recommended_resolution"


class VideoSignalHdmi2RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI2 recommended resolution."""

    friendly_name = "video signal HDMI2 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi2_recommended_resolution"


class VideoSignalHdmi3RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI3 recommended resolution."""

    friendly_name = "video signal HDMI3 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi3_recommended_resolution"


class VideoSignalHdmi4RecommendedResolution(VideoSignalFormat):
    """Video signal HDMI4 recommended resolution."""

    friendly_name = "video signal HDMI4 recommended resolution"
    base_property = "video"
    property_name = "signal_hdmi4_recommended_resolution"


class VideoSignalAspect(CodeDictStrMap):
    """Video signal aspect."""

    friendly_name = "video signal aspect"
    base_property = "video"
    property_name = "signal_aspect"  # unused

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "4:3",
        "2": "16:9",
        "3": "14:9",
    }


class VideoSignalInputAspect(VideoSignalAspect):
    """Video signal input aspect."""

    friendly_name = "video signal input aspect"
    base_property = "video"
    property_name = "signal_input_aspect"


class VideoSignalOutputAspect(VideoSignalAspect):
    """Video signal output aspect."""

    friendly_name = "video signal output aspect"
    base_property = "video"
    property_name = "signal_output_aspect"


class VideoSignalColorspace(CodeDictStrMap):
    """Video signal colorspace."""

    friendly_name = "video signal colorspace"
    base_property = "video"
    property_name = "signal_colorspace"  # unused

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "RGB Limit",
        "2": "RGB Full",
        "3": "YcbCr444",
        "4": "YcbCr422",
        "5": "YcbCr420",
    }


class VideoSignalInputColorspace(VideoSignalColorspace):
    """Video signal input colorspace."""

    friendly_name = "video signal input colorspace"
    base_property = "video"
    property_name = "signal_input_color_format"  # NOTE: inconsistent


class VideoSignalOutputColorspace(VideoSignalColorspace):
    """Video signal output colorspace."""

    friendly_name = "video signal output colorspace"
    base_property = "video"
    property_name = "signal_output_color_format"  # NOTE: inconsistent


class VideoSignalBits(CodeDictStrMap):
    """Video signal bits."""

    friendly_name = "video signal bits"
    base_property = "video"
    property_name = "signal_bits"  # unused

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "24bit (8bit*3)",
        "2": "30bit (10bit*3)",
        "3": "36bit (12bit*3)",
        "4": "48bit (16bit*3)",
    }


class VideoSignalInputBits(VideoSignalBits):
    """Video signal input bits."""

    friendly_name = "video signal input bits"
    base_property = "video"
    property_name = "signal_input_bit"  # NOTE: inconsistent


class VideoSignalOutputBits(VideoSignalBits):
    """Video signal output bits."""

    friendly_name = "video signal output bits"
    base_property = "video"
    property_name = "signal_output_bit"  # NOTE: inconsistent


class VideoSignalHdmi1Deepcolor(VideoSignalBits):
    """Video signal HDMI1 deepcolor."""

    friendly_name = "video signal HDMI1 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi1_deepcolor"  # NOTE: inconsistent


class VideoSignalHdmi2Deepcolor(VideoSignalBits):
    """Video signal HDMI2 deepcolor."""

    friendly_name = "video signal HDMI2 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi2_deepcolor"  # NOTE: inconsistent


class VideoSignalHdmi3Deepcolor(VideoSignalBits):
    """Video signal HDMI3 deepcolor."""

    friendly_name = "video signal HDMI3 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi3_deepcolor"  # NOTE: inconsistent


class VideoSignalHdmi4Deepcolor(VideoSignalBits):
    """Video signal HDMI4 deepcolor."""

    friendly_name = "video signal HDMI4 deepcolor"
    base_property = "video"
    property_name = "signal_hdmi4_deepcolor"  # NOTE: inconsistent


class VideoSignalExtendedColorspace(CodeDictStrMap):
    """Video signal ext colorspace."""

    friendly_name = "video signal ext colorspace"
    base_property = "video"
    property_name = "signal_ext_colorspace"  # unused

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "Standard",
        "2": "xvYCC601",
        "3": "xvYCC709",
        "4": "sYCC",
        "5": "AdobeYCC601",
        "6": "AdobeRGB",
    }


class VideoSignalInputExtendedColorspace(VideoSignalExtendedColorspace):
    """Video signal input extended colorspace."""

    friendly_name = "video signal input extended colorspace"
    base_property = "video"
    property_name = "signal_input_extended_colorspace"


class VideoSignalOutputExtendedColorspace(VideoSignalExtendedColorspace):
    """Video signal output extended colorspace."""

    friendly_name = "video signal output extended colorspace"
    base_property = "video"
    property_name = "signal_output_extended_colorspace"


class VideoSignal3DFormat(CodeDictStrMap):
    """Video signal 3D mode."""

    friendly_name = "video signal 3D mode"
    base_property = "video"
    property_name = "signal_3d_format"  # unused

    code_map = {
        CodeDefault(): None,
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


class VideoSignalInput3DFormat(VideoSignal3DFormat):
    """Video signal input 3D format."""

    friendly_name = "video signal input 3D format"
    base_property = "video"
    property_name = "input_3d_format"


class VideoSignalOutput3DFormat(VideoSignal3DFormat):
    """Video signal output 3D format."""

    friendly_name = "video signal output 3D format"
    base_property = "video"
    property_name = "output_3d_format"


class VideoInformation(CodeMapSequence):
    """Video information."""

    friendly_name = "video information"
    base_property = "video"
    property_name = "information"  # unused

    code_map_sequence = [
        VideoSignalInputTerminal,  # [0] signal_input_terminal
        VideoSignalInputResolution,  # [1:3] signal_input_resolution
        VideoSignalInputAspect,  # [3] signal_input_aspect
        VideoSignalInputColorspace,  # [4] signal_input_color_format
        VideoSignalInputBits,  # [5] signal_input_bit
        VideoSignalInputExtendedColorspace,  # [6] signal_input_extended_colorspace
        VideoSignalOutputResolution,  # [7:9] signal_output_resolution
        VideoSignalOutputAspect,  # [9] signal_output_aspect
        VideoSignalOutputColorspace,  # [10] signal_output_color_format
        VideoSignalOutputBits,  # [11] signal_output_bit
        VideoSignalOutputExtendedColorspace,  # [12] signal_output_extended_colorspace
        VideoSignalHdmi1RecommendedResolution,  # [13:15] signal_hdmi1_recommended_resolution
        VideoSignalHdmi1Deepcolor,  # [15] signal_hdmi1_deepcolor
        5,
        VideoSignalHdmi2RecommendedResolution,  # [21:23] signal_hdmi2_recommended_resolution
        VideoSignalHdmi2Deepcolor,  # [23] signal_hdmi2_deepcolor
    ]

    code_map_sequence_extra = [
        *code_map_sequence,
        5,
        VideoSignalHdmi3RecommendedResolution,  # [29:31] signal_hdmi3_recommended_resolution
        VideoSignalHdmi3Deepcolor,  # [31] signal_hdmi3_deepcolor
        5,
        VideoSignalInput3DFormat,  # [37:39] input_3d_format
        VideoSignalOutput3DFormat,  # [39:41] output_3d_format
        VideoSignalHdmi4RecommendedResolution,  # [41:43] signal_hdmi4_recommended_resolution
        VideoSignalHdmi4Deepcolor,  # [44] signal_hdmi4_deepcolor
    ]

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for video information."""
        code_map_sequence = cls.code_map_sequence

        ## FY11 AVRs only return 25 data values
        if len(response.code) > 40:
            code_map_sequence = cls.code_map_sequence_extra

        return cls.decode_response_sequence(
            response=response, params=params, code_map_sequence=code_map_sequence
        )


class DisplayText(CodeStrMap):
    """Display text."""

    friendly_name = "display text"
    base_property = "amp"
    property_name = "display"

    ## NOTE: value_to_code not implemented

    @classmethod
    def code_to_value(cls, code: str) -> str:
        """Convert code to value."""
        return (
            "".join([chr(int(code[i : i + 2], 16)) for i in range(2, len(code) - 1, 2)])
            .expandtabs(1)
            .strip()
        )


RESPONSE_DATA_INFO = [
    ["AST", AudioInformation, Zone.ALL, "audio"],
    ["VST", VideoInformation, Zone.ALL, "video"],
    ["FL", DisplayText, Zone.ALL, "amp", "display"],
]
