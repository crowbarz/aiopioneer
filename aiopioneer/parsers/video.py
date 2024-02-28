"""Pioneer AVR response parsers for video parameters."""

from aiopioneer.const import VIDEO_RESOLUTION_MODES, ADVANCED_VIDEO_ADJUST_MODES, Zones
from .response import Response


class VideoParsers:
    """Video related parsers."""

    @staticmethod
    def video_converter(raw: str, _params: dict, zone=Zones.Z1, command="VTB") -> list:
        """Response parser for video converter setting."""
        value = int(raw)
        if value == 1:
            value = "on"
        else:
            value = "off"

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="converter",
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def video_resolution(raw: str, _params: dict, zone=Zones.Z1, command="VTC") -> list:
        """Response parser for video resolution setting."""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="resolution",
                zone=zone,
                value=VIDEO_RESOLUTION_MODES.get(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def pure_cinema(raw: str, _params: dict, zone=Zones.Z1, command="VTD") -> list:
        """Response parser for pure cinema setting."""
        value = int(raw)
        if value == 0:
            value = "auto"
        elif value == 2:
            value = "on"
        else:
            value = "off"

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="pure_cinema",
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def prog_motion(raw: str, _params: dict, zone=Zones.Z1, command="VTE") -> list:
        """Response parser for prog motion setting."""
        value = int(raw)
        if value < 55:
            value = value - 50

            parsed = []
            parsed.append(
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="video",
                    property_name="prog_motion",
                    zone=zone,
                    value=value,
                    queue_commands=None,
                )
            )
            return parsed

    @staticmethod
    def stream_smoother(raw: str, _params: dict, zone=Zones.Z1, command="VTF") -> list:
        """Response parser for stream smoother setting."""
        value = int(raw)
        if value == 0:
            value = "off"
        elif value == "1":
            value = "on"
        else:
            value = "auto"

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="stream_smoother",
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def advanced_video_adjust(
        raw: str, _params: dict, zone=Zones.Z1, command="VTG"
    ) -> list:
        """Response parser for advanced video adjust setting."""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="advanced_video_adjust",
                zone=zone,
                value=ADVANCED_VIDEO_ADJUST_MODES.get(raw),
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def output_ynr(raw: str, _param: dict, zone = Zones.Z1, command = "VTH") -> list:
        """Response parser for output YNR setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="video",
                            property_name="ynr",
                            zone=zone,
                            value=int(raw) - 50,
                            queue_commands=None))
        return parsed

    @staticmethod
    def output_cnr(raw: str, _param: dict, zone = Zones.Z1, command = "VTI") -> list:
        """Response parser for output CNR setting"""
        parsed = VideoParsers.output_ynr(raw, _param, zone=zone, command=command)
        parsed[0].property_name = "cnr"
        return parsed

    @staticmethod
    def output_bnr(raw: str, _param: dict, zone = Zones.Z1, command = "VTJ") -> list:
        """Response parser for output BNR setting"""
        parsed = VideoParsers.output_ynr(raw, _param, zone=zone, command=command)
        parsed[0].property_name = "bnr"
        return parsed

    @staticmethod
    def output_mnr(raw: str, _param: dict, zone = Zones.Z1, command = "VTK") -> list:
        """Response parser for output MNR setting"""
        parsed = VideoParsers.output_ynr(raw, _param, zone=zone, command=command)
        parsed[0].property_name = "mnr"
        return parsed

    @staticmethod
    def output_detail(raw: str, _param: dict, zone = Zones.Z1, command = "VTL") -> list:
        """Response parser for output detail setting"""
        parsed = VideoParsers.output_ynr(raw, _param, zone=zone, command=command)
        parsed[0].property_name = "detail"
        return parsed

    @staticmethod
    def output_sharpness(raw: str, _param: dict, zone = Zones.Z1, command = "VTM") -> list:
        """Response parser for output sharpness setting"""
        parsed = VideoParsers.output_ynr(raw, _param, zone=zone, command=command)
        parsed[0].property_name = "sharpness"
        return parsed

    @staticmethod
    def output_brightness(raw: str, _param: dict, zone = Zones.Z1, command = "VTN") -> list:
        """Response parser for output brightness setting"""
        parsed = VideoParsers.output_ynr(raw, _param, zone=zone, command=command)
        parsed[0].property_name = "brightness"
        return parsed

    @staticmethod
    def output_contrast(raw: str, _param: dict, zone = Zones.Z1, command = "VTO") -> list:
        """Response parser for output contrast setting"""
        parsed = VideoParsers.output_ynr(raw, _param, zone=zone, command=command)
        parsed[0].property_name = "contrast"
        return parsed

    @staticmethod
    def output_hue(raw: str, _param: dict, zone = Zones.Z1, command = "VTP") -> list:
        """Response parser for output hue setting"""
        parsed = VideoParsers.output_ynr(raw, _param, zone=zone, command=command)
        parsed[0].property_name = "hue"
        return parsed

    @staticmethod
    def output_chroma(raw: str, _param: dict, zone = Zones.Z1, command = "VTQ") -> list:
        """Response parser for output chroma setting"""
        parsed = VideoParsers.output_ynr(raw, _param, zone=zone, command=command)
        parsed[0].property_name = "chroma"
        return parsed

    @staticmethod
    def black_setup(raw: str, _params: dict, zone=Zones.Z1, command="VTR") -> list:
        """Response parser for black setup setting."""
        value = int(raw)
        if value == 0:
            value = 0
        elif value == 1:
            value = 7.5

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="black_setup",
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def aspect(raw: str, _params: dict, zone=Zones.Z1, command="VTS") -> list:
        """Response parser for output aspect setting."""
        value = int(raw)
        if value == 0:
            value = "passthrough"
        elif value == 1:
            value = "normal"

        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name="aspect",
                zone=zone,
                value=value,
                queue_commands=None,
            )
        )
        return parsed
