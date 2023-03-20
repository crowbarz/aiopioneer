"""Pioneer AVR response parsers for video parameters."""

from aiopioneer.const import VIDEO_RESOLUTION_MODES, ADVANCED_VIDEO_ADJUST_MODES, Zones
from .response import Response

class VideoParsers():
    """Video related parsers."""
    @staticmethod
    def video_converter(raw: str, _param: dict) -> list:
        """Response parser for video converter setting"""
        value = int(raw)
        if value == 1:
            value = "on"
        else:
            value = "off"

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VTB",
                            base_property="video",
                            property_name="converter",
                            zone=Zones.Z1,
                            value=value,
                            queue_commands=None))
        return parsed

    @staticmethod
    def video_resolution(raw: str, _param: dict) -> list:
        """Response parser for video resolution setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VTC",
                            base_property="video",
                            property_name="resolution",
                            zone=Zones.Z1,
                            value=VIDEO_RESOLUTION_MODES.get(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def pure_cinema(raw: str, _param: dict) -> list:
        """Response parser for pure cinema setting"""
        value = int(raw)
        if value == 0:
            value = "auto"
        elif value == 2:
            value = "on"
        else:
            value = "off"

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VTD",
                            base_property="video",
                            property_name="pure_cinema",
                            zone=Zones.Z1,
                            value=value,
                            queue_commands=None))
        return parsed

    @staticmethod
    def prog_motion(raw: str, _param: dict) -> list:
        """Response parser for prog motion setting"""
        value = int(raw)
        if value < 55:
            value = value - 50

            parsed = []
            parsed.append(Response(raw=raw,
                                response_command="VTE",
                                base_property="video",
                                property_name="prog_motion",
                                zone=Zones.Z1,
                                value=value,
                                queue_commands=None))
            return parsed

    @staticmethod
    def stream_smoother(raw: str, _param: dict) -> list:
        """Response parser for stream smoother setting"""
        value = int(raw)
        if value == 0:
            value = "off"
        elif value == "1":
            value = "on"
        else:
            value = "auto"

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VTF",
                            base_property="video",
                            property_name="stream_smoother",
                            zone=Zones.Z1,
                            value=value,
                            queue_commands=None))
        return parsed

    @staticmethod
    def advanced_video_adjust(raw: str, _param: dict) -> list:
        """Response parser for advanced video adjust setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VTG",
                            base_property="video",
                            property_name="advanced_video_adjust",
                            zone=Zones.Z1,
                            value=ADVANCED_VIDEO_ADJUST_MODES.get(raw),
                            queue_commands=None))
        return parsed

    @staticmethod
    def output_ynr(raw: str, _param: dict) -> list:
        """Response parser for output YNR setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VTH",
                            base_property="video",
                            property_name="ynr",
                            zone=Zones.Z1,
                            value=int(raw) - 50,
                            queue_commands=None))
        return parsed

    @staticmethod
    def output_cnr(raw: str, _param: dict) -> list:
        """Response parser for output CNR setting"""
        parsed = VideoParsers.output_ynr(raw, _param)
        parsed[0].property_name = "cnr"
        parsed[0].response_command = "VTI"
        return parsed

    @staticmethod
    def output_bnr(raw: str, _param: dict) -> list:
        """Response parser for output BNR setting"""
        parsed = VideoParsers.output_ynr(raw, _param)
        parsed[0].property_name = "bnr"
        parsed[0].response_command = "VTJ"
        return parsed

    @staticmethod
    def output_mnr(raw: str, _param: dict) -> list:
        """Response parser for output MNR setting"""
        parsed = VideoParsers.output_ynr(raw, _param)
        parsed[0].property_name = "mnr"
        parsed[0].response_command = "VTK"
        return parsed

    @staticmethod
    def output_detail(raw: str, _param: dict) -> list:
        """Response parser for output detail setting"""
        parsed = VideoParsers.output_ynr(raw, _param)
        parsed[0].property_name = "detail"
        parsed[0].response_command = "VTL"
        return parsed

    @staticmethod
    def output_sharpness(raw: str, _param: dict) -> list:
        """Response parser for output sharpness setting"""
        parsed = VideoParsers.output_ynr(raw, _param)
        parsed[0].property_name = "sharpness"
        parsed[0].response_command = "VTM"
        return parsed

    @staticmethod
    def output_brightness(raw: str, _param: dict) -> list:
        """Response parser for output brightness setting"""
        parsed = VideoParsers.output_ynr(raw, _param)
        parsed[0].property_name = "brightness"
        parsed[0].response_command = "VTN"
        return parsed

    @staticmethod
    def output_contrast(raw: str, _param: dict) -> list:
        """Response parser for output contrast setting"""
        parsed = VideoParsers.output_ynr(raw, _param)
        parsed[0].property_name = "contrast"
        parsed[0].response_command = "VTO"
        return parsed

    @staticmethod
    def output_hue(raw: str, _param: dict) -> list:
        """Response parser for output hue setting"""
        parsed = VideoParsers.output_ynr(raw, _param)
        parsed[0].property_name = "hue"
        parsed[0].response_command = "VTP"
        return parsed

    @staticmethod
    def output_chroma(raw: str, _param: dict) -> list:
        """Response parser for output chroma setting"""
        parsed = VideoParsers.output_ynr(raw, _param)
        parsed[0].property_name = "chroma"
        parsed[0].response_command = "VTQ"
        return parsed

    @staticmethod
    def black_setup(raw: str, _param: dict) -> list:
        """Response parser for black setup setting"""
        value = int(raw)
        if value == 0:
            value = 0
        elif value == 1:
            value = 7.5

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VTR",
                            base_property="video",
                            property_name="black_setup",
                            zone=Zones.Z1,
                            value=value,
                            queue_commands=None))
        return parsed

    @staticmethod
    def aspect(raw: str, _param: dict) -> list:
        """Response parser for output aspect setting"""
        value = int(raw)
        if value == 0:
            value = "passthrough"
        elif value == 1:
            value = "normal"

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VTS",
                            base_property="video",
                            property_name="aspect",
                            zone=Zones.Z1,
                            value=value,
                            queue_commands=None))
        return parsed
