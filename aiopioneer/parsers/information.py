"""aiopioneer response parsers for informational responses."""

from ..const import Zone
from ..params import PioneerAVRParams
from .code_map import (
    CodeStrMap,
    CodeDefault,
    CodeBoolMap,
    CodeDictStrMap,
    CodeIntMap,
)
from .response import Response


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


class AudioChannelActive(CodeDictStrMap):
    """Audio active."""

    code_map = {
        "0": "inactive",
        "1": "active",
    }


class AudioWorkingPqls(CodeDictStrMap):
    """Audio working PQLS."""

    code_map = {"0": "off", "1": "2h", "2": "Multi-channel", "3": "Bitstream"}


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


class InformationParsers:
    """AVR operation information parsers."""

    @staticmethod
    def audio_information(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="AST"
    ) -> list[Response]:
        """Response parser for audio information."""

        def audio_response(property_name: str, value: str) -> Response:
            return Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name=property_name,
                zone=zone,
                value=value,
                queue_commands=None,
            )

        def input_channel(channel: str, raw: str) -> Response:
            return audio_response(f"input_channels.{channel}", AudioChannelActive[raw])

        def output_channel(channel: str, raw: str) -> Response:
            return audio_response(f"output_channels.{channel}", AudioChannelActive[raw])

        parsed = []
        parsed += [
            audio_response("input_signal", AudioSignalInputInfo[raw[:2]]),
            audio_response("input_frequency", AudioSignalInputFreq[raw[2:4]]),
            input_channel("L", raw[4]),
            input_channel("C", raw[5]),
            input_channel("R", raw[6]),
            input_channel("SL", raw[7]),
            input_channel("SR", raw[8]),
            input_channel("SBL", raw[9]),
            input_channel("SBC", raw[10]),
            input_channel("SBR", raw[11]),
            input_channel("LFE", raw[12]),
            input_channel("FHL", raw[13]),
            input_channel("FHR", raw[14]),
            input_channel("FWL", raw[15]),
            input_channel("FWR", raw[16]),
            input_channel("XL", raw[17]),
            input_channel("XC", raw[18]),
            input_channel("XR", raw[19]),
        ]

        ## (data21) to (data25) are reserved according to FY16AVRs
        ## Decode output signal data
        parsed += [
            output_channel("L", raw[25]),
            output_channel("C", raw[26]),
            output_channel("R", raw[27]),
            output_channel("SL", raw[28]),
            output_channel("SR", raw[29]),
            output_channel("SBL", raw[30]),
            output_channel("SB", raw[31]),
            output_channel("SBR", raw[32]),
        ]

        ## Some older AVRs do not have more than 33 data bits
        if len(raw) > 33:
            parsed += [
                output_channel("SW", raw[33]),
                output_channel("FHL", raw[34]),
                output_channel("FHR", raw[35]),
                output_channel("FWL", raw[36]),
                output_channel("FWR", raw[37]),
                output_channel("TML", raw[38]),
                output_channel("TMR", raw[39]),
                output_channel("TRL", raw[40]),
                output_channel("TRR", raw[41]),
                output_channel("SW2", raw[42]),
            ]

        ## FY11 AVRs do not have more than data 43 data bits (VSX-1021)
        if len(raw) > 43:
            for property_name, value in {
                "output_frequency": AudioSignalInputFreq[raw[43:45]],
                "output_bits": CodeIntMap[raw[45:47]],
                "output_pqls": AudioWorkingPqls[raw[51]],
                "output_auto_phase_control_plus": CodeIntMap[raw[52:54]],
                "output_reverse_phase": CodeBoolMap[raw[54]],
            }.items():
                audio_response(property_name, value)

        ## Set multichannel value
        parsed.append(
            audio_response(
                "input_multichannel", all([CodeBoolMap[r] for r in raw[4:7]])
            )
        )
        return parsed

    @staticmethod
    def video_information(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VST"
    ) -> list[Response]:
        """Response parser for video information."""

        def video_response(property_name: str, value: str) -> Response:
            return Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name=property_name,
                zone=zone,
                value=value,
                queue_commands=None,
            )

        parsed = []
        for property_name, value in {
            "signal_input_terminal": VideoSignalInputTerminal[raw[0]],
            "signal_input_resolution": VideoSignalFormat[raw[1:3]],
            "signal_input_aspect": VideoSignalAspect[raw[3]],
            "signal_input_color_format": VideoSignalColorspace[raw[4]],
            "signal_input_bit": VideoSignalBits[raw[5]],
            "signal_input_extended_colorspace": VideoSignalExtColorspace[raw[6]],
            "signal_output_resolution": VideoSignalFormat[raw[7:9]],
            "signal_output_aspect": VideoSignalAspect[raw[9]],
            "signal_output_color_format": VideoSignalColorspace[raw[10]],
            "signal_output_bit": VideoSignalBits[raw[11]],
            "signal_output_extended_colorspace": VideoSignalExtColorspace[raw[12]],
            "signal_hdmi1_recommended_resolution": VideoSignalFormat[raw[13:15]],
            "signal_hdmi1_deepcolor": VideoSignalBits[raw[15]],
            "signal_hdmi2_recommended_resolution": VideoSignalFormat[raw[21:23]],
            "signal_hdmi2_deepcolor": VideoSignalBits[raw[23]],
        }.items():
            parsed.append(video_response(property_name, value))

        ## FY11 AVRs only return 25 data values
        if len(raw) > 40:
            for property_name, value in {
                "signal_hdmi3_recommended_resolution": VideoSignalFormat[raw[29:31]],
                "signal_hdmi3_deepcolor": VideoSignalBits[raw[31]],
                "input_3d_format": VideoSignal3DMode[raw[37:39]],
                "output_3d_format": VideoSignal3DMode[raw[39:41]],
                "signal_hdmi4_recommended_resolution": VideoSignalFormat[raw[41:43]],
                "signal_hdmi4_deepcolor": VideoSignalBits[raw[44]],
            }.items():
                parsed.append(video_response(property_name, value))
        return parsed
