"""aiopioneer response parsers for informational responses."""

from aiopioneer.const import (
    AUDIO_SIGNAL_INPUT_FREQ,
    AUDIO_SIGNAL_INPUT_INFO,
    AUDIO_WORKING_PQLS,
    VIDEO_SIGNAL_INPUT_TERMINAL,
    VIDEO_SIGNAL_FORMATS,
    VIDEO_SIGNAL_3D_MODES,
    VIDEO_SIGNAL_ASPECTS,
    VIDEO_SIGNAL_BITS,
    VIDEO_SIGNAL_COLORSPACE,
    VIDEO_SIGNAL_EXT_COLORSPACE,
    Zones,
)
from .response import Response


class InformationParsers:
    """AVR operation information parsers."""

    @staticmethod
    def audio_information(raw: str, _params: dict, zone=Zones.Z1, command="AST") -> list:
        """Response parser for audio information."""
        parsed = []

        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="audio",
                property_name="input_signal",
                zone=zone,
                value=AUDIO_SIGNAL_INPUT_INFO.get(raw[:2]),
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
                value=AUDIO_SIGNAL_INPUT_FREQ.get(raw[2:4]),
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
                    value=AUDIO_SIGNAL_INPUT_FREQ.get(raw[43:45]),
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
                    value=AUDIO_WORKING_PQLS.get(raw[51:52]),
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
    def video_information(raw: str, _params: dict, zone=Zones.Z1, command="VST") -> list:
        """Response parser for video information."""
        parsed = []

        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="signal_input_terminal",
                zone=zone,
                value=VIDEO_SIGNAL_INPUT_TERMINAL.get(raw[0]),
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
                value=VIDEO_SIGNAL_FORMATS.get(raw[2:4]),
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
                value=VIDEO_SIGNAL_ASPECTS.get(raw[3]),
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
                value=VIDEO_SIGNAL_COLORSPACE.get(raw[4]),
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
                value=VIDEO_SIGNAL_BITS.get(raw[5]),
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
                value=VIDEO_SIGNAL_EXT_COLORSPACE.get(raw[6]),
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
                value=VIDEO_SIGNAL_FORMATS.get(raw[7:9]),
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
                value=VIDEO_SIGNAL_ASPECTS.get(raw[9]),
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
                value=VIDEO_SIGNAL_COLORSPACE.get(raw[10]),
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
                value=VIDEO_SIGNAL_BITS.get(raw[11]),
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
                value=VIDEO_SIGNAL_EXT_COLORSPACE.get(raw[12]),
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
                value=VIDEO_SIGNAL_FORMATS.get(raw[13:15]),
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
                value=VIDEO_SIGNAL_BITS.get(raw[15]),
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
                value=VIDEO_SIGNAL_FORMATS.get(raw[21:23]),
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
                value=VIDEO_SIGNAL_BITS.get(raw[23]),
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
                    value=VIDEO_SIGNAL_FORMATS.get(raw[29:31]),
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
                    value=VIDEO_SIGNAL_BITS.get(raw[31]),
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
                    value=VIDEO_SIGNAL_3D_MODES.get(raw[37:39]),
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
                    value=VIDEO_SIGNAL_3D_MODES.get(raw[39:41]),
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
                    value=VIDEO_SIGNAL_FORMATS.get(raw[41:43]),
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
                    value=VIDEO_SIGNAL_BITS.get(raw[44]),
                    queue_commands=None,
                )
            )
        return parsed

    @staticmethod
    def device_display_information(
        raw: str, _params: dict, zone=None, command="FL"
    ) -> list:
        """Response parser for AVR display text."""
        display_str = "".join(
            [chr(int(raw[i : i + 2], 16)) for i in range(2, len(raw) - 2, 2)]
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
