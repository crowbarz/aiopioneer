"""aiopioneer response parsers for informational responses."""

from ..const import Zone
from ..params import PioneerAVRParams
from .code_map import AVRCodeDefault, AVRCodeStrDictMap
from .response import Response


class AudioSignalInputInfo(AVRCodeStrDictMap):
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


class AudioSignalInputFreq(AVRCodeStrDictMap):
    """Audio signal input frequency."""

    code_map = {
        AVRCodeDefault(): None,
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


class AudioWorkingPqls(AVRCodeStrDictMap):
    """Audio working PQLS."""

    code_map = {"0": "off", "1": "2h", "2": "Multi-channel", "3": "Bitstream"}


class VideoSignalInputTerminal(AVRCodeStrDictMap):
    """Video signal input terminal."""

    code_map = {
        AVRCodeDefault(): None,
        # "0": "---",
        "1": "VIDEO",
        "2": "S-VIDEO",
        "3": "COMPONENT",
        "4": "HDMI",
        "5": "Self OSD/JPEG",
    }


class VideoSignalFormats(AVRCodeStrDictMap):
    """Video signal formats."""

    code_map = {
        AVRCodeDefault(): None,
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


class VideoSignalAspects(AVRCodeStrDictMap):
    """Video signal aspects."""

    code_map = {
        AVRCodeDefault(): None,
        # "0": "---",
        "1": "4:3",
        "2": "16:9",
        "3": "14:9",
    }


class VideoSignalColorspace(AVRCodeStrDictMap):
    """Video signal colorspace."""

    code_map = {
        AVRCodeDefault(): None,
        # "0": "---",
        "1": "RGB Limit",
        "2": "RGB Full",
        "3": "YcbCr444",
        "4": "YcbCr422",
        "5": "YcbCr420",
    }


class VideoSignalBits(AVRCodeStrDictMap):
    """Video signal bits."""

    code_map = {
        AVRCodeDefault(): None,
        # "0": "---",
        "1": "24bit (8bit*3)",
        "2": "30bit (10bit*3)",
        "3": "36bit (12bit*3)",
        "4": "48bit (16bit*3)",
    }


class VideoSignalExtColorspace(AVRCodeStrDictMap):
    """Video signal ext colorspace."""

    code_map = {
        AVRCodeDefault(): None,
        # "0": "---",
        "1": "Standard",
        "2": "xvYCC601",
        "3": "xvYCC709",
        "4": "sYCC",
        "5": "AdobeYCC601",
        "6": "AdobeRGB",
    }


class VideoSignal3DModes(AVRCodeStrDictMap):
    """Video signal 3D modes."""

    code_map = {
        AVRCodeDefault(): None,
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


class InformationParsers:
    """AVR operation information parsers."""

    @staticmethod
    def audio_information(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="AST"
    ) -> list[Response]:
        """Response parser for audio information."""
        parsed = []

        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_signal",
                zone=zone,
                value=AudioSignalInputInfo[raw[:2]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_frequency",
                zone=zone,
                value=AudioSignalInputFreq[raw[2:4]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.L",
                zone=zone,
                value="active" if bool(int(raw[4])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.C",
                zone=zone,
                value="active" if bool(int(raw[5])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.R",
                zone=zone,
                value="active" if bool(int(raw[6])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.SL",
                zone=zone,
                value="active" if bool(int(raw[7])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.SR",
                zone=zone,
                value="active" if bool(int(raw[8])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.SBL",
                zone=zone,
                value="active" if bool(int(raw[9])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.SBC",
                zone=zone,
                value="active" if bool(int(raw[10])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.SBR",
                zone=zone,
                value="active" if bool(int(raw[11])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.LFE",
                zone=zone,
                value="active" if bool(int(raw[12])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.FHL",
                zone=zone,
                value="active" if bool(int(raw[13])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.FHR",
                zone=zone,
                value="active" if bool(int(raw[14])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.FWL",
                zone=zone,
                value="active" if bool(int(raw[15])) else "inactive",
                queue_commands=None,
            )
        )

        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.FWR",
                zone=zone,
                value="active" if bool(int(raw[16])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.XL",
                zone=zone,
                value="active" if bool(int(raw[17])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.XC",
                zone=zone,
                value="active" if bool(int(raw[18])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_channels.XR",
                zone=zone,
                value="active" if bool(int(raw[19])) else "inactive",
                queue_commands=None,
            )
        )

        ## (data21) to (data25) are reserved according to FY16AVRs
        ## Decode output signal data
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="output_channels.L",
                zone=zone,
                value="active" if bool(int(raw[25])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="output_channels.C",
                zone=zone,
                value="active" if bool(int(raw[26])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="output_channels.R",
                zone=zone,
                value="active" if bool(int(raw[27])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="output_channels.SL",
                zone=zone,
                value="active" if bool(int(raw[28])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="output_channels.SR",
                zone=zone,
                value="active" if bool(int(raw[29])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="output_channels.SBL",
                zone=zone,
                value="active" if bool(int(raw[30])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="output_channels.SB",
                zone=zone,
                value="active" if bool(int(raw[31])) else "inactive",
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="output_channels.SBR",
                zone=zone,
                value="active" if bool(int(raw[32])) else "inactive",
                queue_commands=None,
            )
        )

        ## Some older AVRs do not have more than 33 data bits
        if len(raw) > 33:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.SW",
                    zone=zone,
                    value="active" if bool(int(raw[33])) else "inactive",
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.FHL",
                    zone=zone,
                    value="active" if bool(int(raw[34])) else "inactive",
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.FHR",
                    zone=zone,
                    value="active" if bool(int(raw[35])) else "inactive",
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.FWL",
                    zone=zone,
                    value="active" if bool(int(raw[36])) else "inactive",
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.FWR",
                    zone=zone,
                    value="active" if bool(int(raw[37])) else "inactive",
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.TML",
                    zone=zone,
                    value="active" if bool(int(raw[38])) else "inactive",
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.TMR",
                    zone=zone,
                    value="active" if bool(int(raw[39])) else "inactive",
                    queue_commands=None,
                )
            )

            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.TRL",
                    zone=zone,
                    value="active" if bool(int(raw[40])) else "inactive",
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.TRR",
                    zone=zone,
                    value="active" if bool(int(raw[41])) else "inactive",
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_channels.SW2",
                    zone=zone,
                    value="active" if bool(int(raw[42])) else "inactive",
                    queue_commands=None,
                )
            )

        ## FY11 AVRs do not have more than data 43 data bits (VSX-1021)
        if len(raw) > 43:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_frequency",
                    zone=zone,
                    value=AudioSignalInputFreq[raw[43:45]],
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_bits",
                    zone=zone,
                    value=int(raw[45:47]),
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_pqls",
                    zone=zone,
                    value=AudioWorkingPqls[raw[51:52]],
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_auto_phase_control_plus",
                    zone=zone,
                    value=int(raw[52:54]),
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="audio",
                    property_name="output_reverse_phase",
                    zone=zone,
                    value=bool(raw[54:55]),
                    queue_commands=None,
                )
            )

        ## Set multichannel value
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_multichannel",
                zone=zone,
                value=(bool(int(raw[4])) and bool(int(raw[5])) and bool(int(raw[6]))),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def video_information(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VST"
    ) -> list[Response]:
        """Response parser for video information."""
        parsed = []

        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_input_terminal",
                zone=zone,
                value=VideoSignalInputTerminal[raw[0]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_input_resolution",
                zone=zone,
                value=VideoSignalFormats[raw[1:3]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_input_aspect",
                zone=zone,
                value=VideoSignalAspects[raw[3]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_input_color_format",
                zone=zone,
                value=VideoSignalColorspace[raw[4]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_input_bit",
                zone=zone,
                value=VideoSignalBits[raw[5]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_input_extended_colorspace",
                zone=zone,
                value=VideoSignalExtColorspace[raw[6]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_output_resolution",
                zone=zone,
                value=VideoSignalFormats[raw[7:9]],
                queue_commands=None,
            )
        )

        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_output_aspect",
                zone=zone,
                value=VideoSignalAspects[raw[9]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_output_color_format",
                zone=zone,
                value=VideoSignalColorspace[raw[10]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_output_bit",
                zone=zone,
                value=VideoSignalBits[raw[11]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_output_extended_colorspace",
                zone=zone,
                value=VideoSignalExtColorspace[raw[12]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_hdmi1_recommended_resolution",
                zone=zone,
                value=VideoSignalFormats[raw[13:15]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_hdmi1_deepcolor",
                zone=zone,
                value=VideoSignalBits[raw[15]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_hdmi2_recommended_resolution",
                zone=zone,
                value=VideoSignalFormats[raw[21:23]],
                queue_commands=None,
            )
        )
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_hdmi2_deepcolor",
                zone=zone,
                value=VideoSignalBits[raw[23]],
                queue_commands=None,
            )
        )

        ## FY11 AVRs only return 25 data values
        if len(raw) > 40:
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="video",
                    property_name="signal_hdmi3_recommended_resolution",
                    zone=zone,
                    value=VideoSignalFormats[raw[29:31]],
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="video",
                    property_name="signal_hdmi3_deepcolor",
                    zone=zone,
                    value=VideoSignalBits[raw[31]],
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="video",
                    property_name="input_3d_format",
                    zone=zone,
                    value=VideoSignal3DModes[raw[37:39]],
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="video",
                    property_name="output_3d_format",
                    zone=zone,
                    value=VideoSignal3DModes[raw[39:41]],
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="video",
                    property_name="signal_hdmi4_recommended_resolution",
                    zone=zone,
                    value=VideoSignalFormats[raw[41:43]],
                    queue_commands=None,
                )
            )
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="video",
                    property_name="signal_hdmi4_deepcolor",
                    zone=zone,
                    value=VideoSignalBits[raw[44]],
                    queue_commands=None,
                )
            )
        return parsed

    @staticmethod
    def device_display_information(
        raw: str, _params: PioneerAVRParams, zone=None, command="FL"
    ) -> list[Response]:
        """Response parser for AVR display text."""
        display_str = (
            "".join([chr(int(raw[i : i + 2], 16)) for i in range(2, len(raw) - 1, 2)])
            .expandtabs(1)
            .rstrip("\n")
        )
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="amp",
                property_name="display",
                zone=zone,
                value=display_str,
                queue_commands=None,
            )
        )
        return parsed
