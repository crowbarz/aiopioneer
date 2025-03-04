"""aiopioneer response decoders for informational responses."""

from ..command_queue import CommandItem
from ..params import AVRParams
from .code_map import (
    CodeMapBase,
    CodeMapSequence,
    CodeStrMap,
    CodeDefault,
    CodeBoolMap,
    CodeDictStrMap,
    CodeIntMap,
)
from .response import Response


class AudioChannelActive(CodeDictStrMap):
    """Audio active."""

    code_map = {
        "0": "inactive",
        "1": "active",
    }


class InputMultichannel(CodeBoolMap):
    """Input multichannel."""

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

        super().decode_response(response, params)
        response.update(callback=check_input_multichannel)
        return [response]

    @classmethod
    def code_to_value(cls, code: str) -> bool:
        return all([CodeBoolMap[c] for c in code])


class AudioSignalInputInfo(CodeDictStrMap):
    """Audio signal input info."""

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


class AudioSignalInputFreq(CodeDictStrMap):
    """Audio signal input frequency."""

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


class AudioOutputBits(CodeIntMap):
    """Audio output bits."""

    code_zfill = 2


class AudioWorkingPqls(CodeDictStrMap):
    """Audio working PQLS."""

    code_map = {"0": "off", "1": "2h", "2": "Multi-channel", "3": "Bitstream"}


class AudioOutputAutoPhaseControlPlus(CodeIntMap):
    """Audio output phase control plus."""

    code_zfill = 2


class AudioInformation(CodeMapSequence):
    """Audio information."""

    code_map_sequence = [
        (AudioSignalInputInfo, "input_signal"),  # [0:2]
        (AudioSignalInputFreq, "input_frequency"),  # [2:4]
        (AudioChannelActive, "input_channels.L"),  # [4]
        (AudioChannelActive, "input_channels.C"),  # [5]
        (AudioChannelActive, "input_channels.R"),  # [6]
        (AudioChannelActive, "input_channels.SL"),  # [7]
        (AudioChannelActive, "input_channels.SR"),  # [8]
        (AudioChannelActive, "input_channels.SBL"),  # [9]
        (AudioChannelActive, "input_channels.SBC"),  # [10]
        (AudioChannelActive, "input_channels.SBR"),  # [11]
        (AudioChannelActive, "input_channels.LFE"),  # [12]
        (AudioChannelActive, "input_channels.FHL"),  # [13]
        (AudioChannelActive, "input_channels.FHR"),  # [14]
        (AudioChannelActive, "input_channels.FWL"),  # [15]
        (AudioChannelActive, "input_channels.FWR"),  # [16]
        (AudioChannelActive, "input_channels.XL"),  # [17]
        (AudioChannelActive, "input_channels.XC"),  # [18]
        (AudioChannelActive, "input_channels.XR"),  # [19]
        5,  ## (data21) to (data25) are reserved according to FY16AVRs
        (AudioChannelActive, "output.channels.L"),  # [25]
        (AudioChannelActive, "output.channels.C"),  # [26]
        (AudioChannelActive, "output.channels.R"),  # [27]
        (AudioChannelActive, "output.channels.SL"),  # [28]
        (AudioChannelActive, "output.channels.SR"),  # [29]
        (AudioChannelActive, "output.channels.SBL"),  # [30]
        (AudioChannelActive, "output.channels.SB"),  # [31]
        (AudioChannelActive, "output.channels.SBR"),  # [32]
    ]
    code_map_sequence_extra = [
        *code_map_sequence,
        10,
        (AudioSignalInputFreq, "output_frequency"),  # [43:45]
        (AudioOutputBits, "output_bits"),  # [45:47]
        4,
        (AudioWorkingPqls, "output_pqls"),  # [51]
        (AudioOutputAutoPhaseControlPlus, "output_auto_phase_control_plus"),  # [52:54]
        (CodeBoolMap, "output_reverse_phase"),  # [54]
    ]

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
        code_map_sequence: list[tuple[CodeMapBase, str] | int] = None,  # ignored
    ) -> list[Response]:
        """Response decoder for audio information."""
        code_map_sequence = cls.code_map_sequence

        ## FY11 AVRs do not have more than 43 data bits (VSX-1021)
        if len(response.code) > 43:
            code_map_sequence = cls.code_map_sequence_extra

        responses = InputMultichannel.decode_response(
            response=response.clone(
                code=response.code[4:7], property_name="input_multichannel"
            ),
            params=params,
        )
        responses.extend(
            super().decode_response(
                response=response, params=params, code_map_sequence=code_map_sequence
            )
        )
        return responses


class VideoSignalInputTerminal(CodeDictStrMap):
    """Video signal input terminal."""

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


class VideoSignalAspect(CodeDictStrMap):
    """Video signal aspect."""

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "4:3",
        "2": "16:9",
        "3": "14:9",
    }


class VideoSignalColorspace(CodeDictStrMap):
    """Video signal colorspace."""

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "RGB Limit",
        "2": "RGB Full",
        "3": "YcbCr444",
        "4": "YcbCr422",
        "5": "YcbCr420",
    }


class VideoSignalBits(CodeDictStrMap):
    """Video signal bits."""

    code_map = {
        CodeDefault(): None,
        # "0": "---",
        "1": "24bit (8bit*3)",
        "2": "30bit (10bit*3)",
        "3": "36bit (12bit*3)",
        "4": "48bit (16bit*3)",
    }


class VideoSignalExtColorspace(CodeDictStrMap):
    """Video signal ext colorspace."""

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


class VideoSignal3DMode(CodeDictStrMap):
    """Video signal 3D mode."""

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


class VideoInformation(CodeMapSequence):
    """Video information."""

    code_map_sequence = [
        (VideoSignalInputTerminal, "signal_input_terminal"),  # [0]
        (VideoSignalFormat, "signal_input_resolution"),  # [1:3]
        (VideoSignalAspect, "signal_input_aspect"),  # [3]
        (VideoSignalColorspace, "signal_input_color_format"),  # [4]
        (VideoSignalBits, "signal_input_bit"),  # [5]
        (VideoSignalExtColorspace, "signal_input_extended_colorspace"),  # [6]
        (VideoSignalFormat, "signal_output_resolution"),  # [7:9]
        (VideoSignalAspect, "signal_output_aspect"),  # [9]
        (VideoSignalColorspace, "signal_output_color_format"),  # [10]
        (VideoSignalBits, "signal_output_bit"),  # [11]
        (VideoSignalExtColorspace, "signal_output_extended_colorspace"),  # [12]
        (VideoSignalFormat, "signal_hdmi1_recommended_resolution"),  # [13:15]
        (VideoSignalBits, "signal_hdmi1_deepcolor"),  # [15]
        5,
        (VideoSignalFormat, "signal_hdmi2_recommended_resolution"),  # [21:23]
        (VideoSignalBits, "signal_hdmi2_deepcolor"),  # [23]
    ]

    code_map_sequence_extra = [
        *code_map_sequence,
        5,
        (VideoSignalFormat, "signal_hdmi3_recommended_resolution"),  # [29:31]
        (VideoSignalBits, "signal_hdmi3_deepcolor"),  # [31]
        5,
        (VideoSignal3DMode, "input_3d_format"),  # [37:39]
        (VideoSignal3DMode, "output_3d_format"),  # [39:41]
        (VideoSignalFormat, "signal_hdmi4_recommended_resolution"),  # [41:43]
        (VideoSignalBits, "signal_hdmi4_deepcolor"),  # [44]
    ]

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
        code_map_sequence: list[tuple[CodeMapBase, str] | int] = None,  # ignored
    ) -> list[Response]:
        """Response decoder for video information."""
        code_map_sequence = cls.code_map_sequence

        ## FY11 AVRs only return 25 data values
        if len(response.code) > 40:
            code_map_sequence = cls.code_map_sequence_extra

        return super().decode_response(
            response=response, params=params, code_map_sequence=code_map_sequence
        )


class DisplayText(CodeStrMap):
    """Display information."""

    ## NOTE: value_to_code not implemented

    @classmethod
    def code_to_value(cls, code: str) -> str:
        """Convert code to value."""
        return (
            "".join([chr(int(code[i : i + 2], 16)) for i in range(2, len(code) - 1, 2)])
            .expandtabs(1)
            .strip()
        )
