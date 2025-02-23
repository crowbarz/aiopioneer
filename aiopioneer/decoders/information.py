"""aiopioneer response decoders for informational responses."""

from ..params import PioneerAVRParams
from .code_map import (
    CodeMapBase,
    CodeStrMap,
    CodeDefault,
    CodeBoolMap,
    CodeDictStrMap,
    CodeIntMap,
)
from .response import Response


class AudioInformation(CodeMapBase):
    """Audio information."""

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: PioneerAVRParams,
    ) -> list[Response]:
        """Response decoder for audio information."""

        def decode_child_response(
            property_name: str, code: str, code_map: CodeMapBase
        ) -> list[Response]:
            """Decode a child response."""
            child_response = response.clone(property_name=property_name, code=code)
            return code_map.decode_response(child_response, params)

        def decode_input_channel(channel: str, code: str) -> list[Response]:
            return decode_child_response(
                property_name=f"input_channels.{channel}",
                code=code,
                code_map=AudioChannelActive,
            )

        def decode_output_channel(channel: str, code: str) -> list[Response]:
            return decode_child_response(
                property_name=f"output_channels.{channel}",
                code=code,
                code_map=AudioChannelActive,
            )

        responses = [
            *decode_child_response(
                property_name="input_signal",
                code=response.code[:2],
                code_map=AudioSignalInputInfo,
            ),
            *decode_child_response(
                property_name="input_frequency",
                code=response.code[2:4],
                code_map=AudioSignalInputFreq,
            ),
            *decode_child_response(
                property_name="input_multichannel",
                code=response.code[4:7],
                code_map=InputMultichannel,
            ),
            *decode_input_channel(channel="L", code=response.code[4]),
            *decode_input_channel(channel="C", code=response.code[5]),
            *decode_input_channel(channel="R", code=response.code[6]),
            *decode_input_channel(channel="SL", code=response.code[7]),
            *decode_input_channel(channel="SR", code=response.code[8]),
            *decode_input_channel(channel="SBL", code=response.code[9]),
            *decode_input_channel(channel="SBC", code=response.code[10]),
            *decode_input_channel(channel="SBR", code=response.code[11]),
            *decode_input_channel(channel="LFE", code=response.code[12]),
            *decode_input_channel(channel="FHL", code=response.code[13]),
            *decode_input_channel(channel="FHR", code=response.code[14]),
            *decode_input_channel(channel="FWL", code=response.code[15]),
            *decode_input_channel(channel="FWR", code=response.code[16]),
            *decode_input_channel(channel="XL", code=response.code[17]),
            *decode_input_channel(channel="XC", code=response.code[18]),
            *decode_input_channel(channel="XR", code=response.code[19]),
        ]

        ## (data21) to (data25) are reserved according to FY16AVRs
        ## Decode output signal data
        responses.extend(
            [
                *decode_output_channel(channel="L", code=response.code[25]),
                *decode_output_channel(channel="C", code=response.code[26]),
                *decode_output_channel(channel="R", code=response.code[27]),
                *decode_output_channel(channel="SL", code=response.code[28]),
                *decode_output_channel(channel="SR", code=response.code[29]),
                *decode_output_channel(channel="SBL", code=response.code[30]),
                *decode_output_channel(channel="SB", code=response.code[31]),
                *decode_output_channel(channel="SBR", code=response.code[32]),
            ]
        )

        ## FY11 AVRs do not have more than data 43 data bits (VSX-1021)
        if len(response.code) > 43:
            responses.extend(
                [
                    *decode_child_response(
                        property_name="output_frequency",
                        code=response.code[43:45],
                        code_map=AudioSignalInputFreq,
                    ),
                    *decode_child_response(
                        property_name="output_bits",
                        code=response.code[45:47],
                        code_map=CodeIntMap,
                    ),
                    *decode_child_response(
                        property_name="output_pqls",
                        code=response.code[51],
                        code_map=AudioWorkingPqls,
                    ),
                    *decode_child_response(
                        property_name="output_auto_phase_control_plus",
                        code=response.code[52:54],
                        code_map=CodeIntMap,
                    ),
                    *decode_child_response(
                        property_name="output_reverse_phase",
                        code=response.code[54],
                        code_map=CodeBoolMap,
                    ),
                ]
            )

        return responses


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
        params: PioneerAVRParams,
    ) -> list[Response]:
        """Response decoder for input multichannel."""

        def check_input_multichannel(response: Response) -> list[Response]:
            """Trigger listening mode update if input multichannel has changed."""
            if response.properties.audio.get("input_multichannel") == response.value:
                return []
            response.update(queue_commands=["_update_listening_modes"])
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


class VideoInformation(CodeMapBase):
    """Video information."""

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: PioneerAVRParams,
    ) -> list[Response]:
        """Response decoder for video information."""

        def decode_child_response(
            property_name: str, code: str, code_map: CodeMapBase
        ) -> list[Response]:
            """Decode a child response."""
            child_response = response.clone(property_name=property_name, code=code)
            return code_map.decode_response(child_response, params)

        responses = [
            *decode_child_response(
                property_name="signal_input_terminal",
                code=response.code[0],
                code_map=VideoSignalInputTerminal,
            ),
            *decode_child_response(
                property_name="signal_input_resolution",
                code=response.code[1:3],
                code_map=VideoSignalFormat,
            ),
            *decode_child_response(
                property_name="signal_input_aspect",
                code=response.code[3],
                code_map=VideoSignalAspect,
            ),
            *decode_child_response(
                property_name="signal_input_color_format",
                code=response.code[4],
                code_map=VideoSignalColorspace,
            ),
            *decode_child_response(
                property_name="signal_input_bit",
                code=response.code[5],
                code_map=VideoSignalBits,
            ),
            *decode_child_response(
                property_name="signal_input_extended_colorspace",
                code=response.code[6],
                code_map=VideoSignalExtColorspace,
            ),
            *decode_child_response(
                property_name="signal_output_resolution",
                code=response.code[7:9],
                code_map=VideoSignalFormat,
            ),
            *decode_child_response(
                property_name="signal_output_aspect",
                code=response.code[9],
                code_map=VideoSignalAspect,
            ),
            *decode_child_response(
                property_name="signal_output_color_format",
                code=response.code[10],
                code_map=VideoSignalColorspace,
            ),
            *decode_child_response(
                property_name="signal_output_bit",
                code=response.code[11],
                code_map=VideoSignalBits,
            ),
            *decode_child_response(
                property_name="signal_output_extended_colorspace",
                code=response.code[12],
                code_map=VideoSignalExtColorspace,
            ),
            *decode_child_response(
                property_name="signal_hdmi1_recommended_resolution",
                code=response.code[13:15],
                code_map=VideoSignalFormat,
            ),
            *decode_child_response(
                property_name="signal_hdmi1_deepcolor",
                code=response.code[15],
                code_map=VideoSignalBits,
            ),
            *decode_child_response(
                property_name="signal_hdmi2_recommended_resolution",
                code=response.code[21:23],
                code_map=VideoSignalFormat,
            ),
            *decode_child_response(
                property_name="signal_hdmi2_deepcolor",
                code=response.code[23],
                code_map=VideoSignalBits,
            ),
        ]

        ## FY11 AVRs only return 25 data values
        if len(response.code) > 40:
            responses.extend(
                [
                    *decode_child_response(
                        property_name="signal_hdmi3_recommended_resolution",
                        code=response.code[29:31],
                        code_map=VideoSignalFormat,
                    ),
                    *decode_child_response(
                        property_name="signal_hdmi3_deepcolor",
                        code=response.code[31],
                        code_map=VideoSignalBits,
                    ),
                    *decode_child_response(
                        property_name="input_3d_format",
                        code=response.code[37:39],
                        code_map=VideoSignal3DMode,
                    ),
                    *decode_child_response(
                        property_name="output_3d_format",
                        code=response.code[39:41],
                        code_map=VideoSignal3DMode,
                    ),
                    *decode_child_response(
                        property_name="signal_hdmi4_recommended_resolution",
                        code=response.code[41:43],
                        code_map=VideoSignalFormat,
                    ),
                    *decode_child_response(
                        property_name="signal_hdmi4_deepcolor",
                        code=response.code[44],
                        code_map=VideoSignalBits,
                    ),
                ]
            )

        return responses


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
