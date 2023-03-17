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
    VIDEO_SIGNAL_EXT_COLORSPACE)
from .const import Response

def ast(raw: str, _param: dict) -> list:
    parsed = []

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_signal",
                         zone="1",
                         value=AUDIO_SIGNAL_INPUT_INFO.get(raw[:2]),
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_frequency",
                         zone="1",
                         value=AUDIO_SIGNAL_INPUT_FREQ.get(raw[2:4]),
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.L",
                         zone="1",
                         value="active" if bool(int(raw[4])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.C",
                         zone="1",
                         value="active" if bool(int(raw[5])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.R",
                         zone="1",
                         value="active" if bool(int(raw[6])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.SL",
                         zone="1",
                         value="active" if bool(int(raw[7])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.SR",
                         zone="1",
                         value="active" if bool(int(raw[8])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.SBL",
                         zone="1",
                         value="active" if bool(int(raw[9])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.SBC",
                         zone="1",
                         value="active" if bool(int(raw[10])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.SBR",
                         zone="1",
                         value="active" if bool(int(raw[11])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.LFE",
                         zone="1",
                         value="active" if bool(int(raw[12])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.FHL",
                         zone="1",
                         value="active" if bool(int(raw[13])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.FHR",
                         zone="1",
                         value="active" if bool(int(raw[14])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.FWL",
                         zone="1",
                         value="active" if bool(int(raw[15])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.FWR",
                         zone="1",
                         value="active" if bool(int(raw[16])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.XL",
                         zone="1",
                         value="active" if bool(int(raw[17])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.XC",
                         zone="1",
                         value="active" if bool(int(raw[18])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_channels.XR",
                         zone="1",
                         value="active" if bool(int(raw[19])) else "inactive",
                         queue_commands=None))

    ## (data21) to (data25) are reserved according to FY16AVRs
    ## Decode output signal data

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="output_channels.L",
                         zone="1",
                         value="active" if bool(int(raw[25])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="output_channels.C",
                         zone="1",
                         value="active" if bool(int(raw[26])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="output_channels.R",
                         zone="1",
                         value="active" if bool(int(raw[27])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="output_channels.SL",
                         zone="1",
                         value="active" if bool(int(raw[28])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="output_channels.SR",
                         zone="1",
                         value="active" if bool(int(raw[29])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="output_channels.SBL",
                         zone="1",
                         value="active" if bool(int(raw[30])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="output_channels.SB",
                         zone="1",
                         value="active" if bool(int(raw[31])) else "inactive",
                         queue_commands=None))

    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="output_channels.SBR",
                         zone="1",
                         value="active" if bool(int(raw[32])) else "inactive",
                         queue_commands=None))

    ## Some older AVRs do not have more than 33 data bits
    if len(raw) > 33:
        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.SW",
                            zone="1",
                            value="active" if bool(int(raw[33])) else "inactive",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.FHL",
                            zone="1",
                            value="active" if bool(int(raw[34])) else "inactive",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.FHR",
                            zone="1",
                            value="active" if bool(int(raw[35])) else "inactive",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.FWL",
                            zone="1",
                            value="active" if bool(int(raw[36])) else "inactive",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.FWR",
                            zone="1",
                            value="active" if bool(int(raw[37])) else "inactive",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.TML",
                            zone="1",
                            value="active" if bool(int(raw[38])) else "inactive",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.TMR",
                            zone="1",
                            value="active" if bool(int(raw[39])) else "inactive",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.TRL",
                            zone="1",
                            value="active" if bool(int(raw[40])) else "inactive",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.TRR",
                            zone="1",
                            value="active" if bool(int(raw[41])) else "inactive",
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_channels.SW2",
                            zone="1",
                            value="active" if bool(int(raw[42])) else "inactive",
                            queue_commands=None))

    ## FY11 AVRs do not have more than data 43 data bits (VSX-1021)
    if len(raw) > 43:
        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_frequency",
                            zone="1",
                            value=AUDIO_SIGNAL_INPUT_FREQ.get(raw[43:45]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_bits",
                            zone="1",
                            value=int(raw[45:47]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_pqls",
                            zone="1",
                            value=AUDIO_WORKING_PQLS.get(raw[51:52]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_auto_phase_control_plus",
                            zone="1",
                            value=int(raw[52:54]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="ast",
                            base_property="audio",
                            property_name="output_reverse_phase",
                            zone="1",
                            value=bool(raw[54:55]),
                            queue_commands=None))

    # set multichannel value
    parsed.append(Response(raw=raw,
                         response_command="ast",
                         base_property="audio",
                         property_name="input_multichannel",
                         zone="1",
                         value=(bool(int(raw[4])) and bool(int(raw[5])) and bool(int(raw[6]))),
                         queue_commands=None))

    return parsed

def vst(raw: str, _param: dict) -> list:
    parsed = []

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_input_terminal",
                        zone="1",
                        value=VIDEO_SIGNAL_INPUT_TERMINAL.get(raw[0]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_input_resolution",
                        zone="1",
                        value=VIDEO_SIGNAL_FORMATS.get(raw[2:4]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_input_aspect",
                        zone="1",
                        value=VIDEO_SIGNAL_ASPECTS.get(raw[3]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_input_color_format",
                        zone="1",
                        value=VIDEO_SIGNAL_COLORSPACE.get(raw[4]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_input_bit",
                        zone="1",
                        value=VIDEO_SIGNAL_BITS.get(raw[5]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_input_extended_colorspace",
                        zone="1",
                        value=VIDEO_SIGNAL_EXT_COLORSPACE.get(raw[6]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_output_resolution",
                        zone="1",
                        value=VIDEO_SIGNAL_FORMATS.get(raw[7:9]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_output_aspect",
                        zone="1",
                        value=VIDEO_SIGNAL_ASPECTS.get(raw[9]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_output_color_format",
                        zone="1",
                        value=VIDEO_SIGNAL_COLORSPACE.get(raw[10]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_output_bit",
                        zone="1",
                        value=VIDEO_SIGNAL_BITS.get(raw[11]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_output_extended_colorspace",
                        zone="1",
                        value=VIDEO_SIGNAL_EXT_COLORSPACE.get(raw[12]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_hdmi1_recommended_resolution",
                        zone="1",
                        value=VIDEO_SIGNAL_FORMATS.get(raw[13:15]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_hdmi1_deepcolor",
                        zone="1",
                        value=VIDEO_SIGNAL_BITS.get(raw[15]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_hdmi2_recommended_resolution",
                        zone="1",
                        value=VIDEO_SIGNAL_FORMATS.get(raw[21:23]),
                        queue_commands=None))

    parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_hdmi2_deepcolor",
                        zone="1",
                        value=VIDEO_SIGNAL_BITS.get(raw[23]),
                        queue_commands=None))

    if len(raw) > 40: ## FY11 AVRs only return 25 data values
        parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_hdmi3_recommended_resolution",
                        zone="1",
                        value=VIDEO_SIGNAL_FORMATS.get(raw[29:31]),
                        queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="vst",
                            base_property="video",
                            property_name="signal_hdmi3_deepcolor",
                            zone="1",
                            value=VIDEO_SIGNAL_BITS.get(raw[31]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="vst",
                            base_property="video",
                            property_name="input_3d_format",
                            zone="1",
                            value=VIDEO_SIGNAL_3D_MODES.get(raw[37:39]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="vst",
                            base_property="video",
                            property_name="output_3d_format",
                            zone="1",
                            value=VIDEO_SIGNAL_3D_MODES.get(raw[39:41]),
                            queue_commands=None))

        parsed.append(Response(raw=raw,
                        response_command="vst",
                        base_property="video",
                        property_name="signal_hdmi4_recommended_resolution",
                        zone="1",
                        value=VIDEO_SIGNAL_FORMATS.get(raw[41:43]),
                        queue_commands=None))

        parsed.append(Response(raw=raw,
                            response_command="vst",
                            base_property="video",
                            property_name="signal_hdmi4_deepcolor",
                            zone="1",
                            value=VIDEO_SIGNAL_BITS.get(raw[44]),
                            queue_commands=None))

    return parsed
