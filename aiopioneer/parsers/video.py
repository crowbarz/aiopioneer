"""Pioneer AVR response parsers for video parameters."""

from ..const import VIDEO_RESOLUTION_MODES, ADVANCED_VIDEO_ADJUST_MODES, Zone
from ..param import PioneerAVRParams
from .response import Response


class VideoParsers:
    """Video related parsers."""

    @staticmethod
    def video_converter(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VTB"
    ) -> list[Response]:
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
    def video_resolution(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VTC"
    ) -> list[Response]:
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
    def pure_cinema(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VTD"
    ) -> list[Response]:
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
    def prog_motion(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VTE"
    ) -> list[Response]:
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
    def stream_smoother(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VTF"
    ) -> list[Response]:
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
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VTG"
    ) -> list[Response]:
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
    def output_video_property(
        raw: str,
        _params: PioneerAVRParams,
        zone=Zone.Z1,
        command=None,
        property_name=None,
    ) -> list[Response]:
        """General response parser for output video property."""
        parsed = []
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="video",
                property_name=property_name,
                zone=zone,
                value=int(raw) - 50,
                queue_commands=None,
            )
        )
        return parsed

    @staticmethod
    def output_ynr(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTH"
    ) -> list[Response]:
        """Response parser for output YNR setting."""
        return VideoParsers.output_video_property(raw, params, zone, command, "ynr")

    @staticmethod
    def output_cnr(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTI"
    ) -> list[Response]:
        """Response parser for output CNR setting."""
        return VideoParsers.output_video_property(raw, params, zone, command, "cnr")

    @staticmethod
    def output_bnr(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTJ"
    ) -> list[Response]:
        """Response parser for output BNR setting."""
        return VideoParsers.output_video_property(raw, params, zone, command, "bnr")

    @staticmethod
    def output_mnr(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTK"
    ) -> list[Response]:
        """Response parser for output MNR setting."""
        return VideoParsers.output_video_property(raw, params, zone, command, "mnr")

    @staticmethod
    def output_detail(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTL"
    ) -> list[Response]:
        """Response parser for output detail setting."""
        return VideoParsers.output_video_property(raw, params, zone, command, "detail")

    @staticmethod
    def output_sharpness(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTM"
    ) -> list[Response]:
        """Response parser for output sharpness setting."""
        return VideoParsers.output_video_property(
            raw, params, zone, command, "sharpness"
        )

    @staticmethod
    def output_brightness(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTN"
    ) -> list[Response]:
        """Response parser for output brightness setting."""
        return VideoParsers.output_video_property(
            raw, params, zone, command, "brightness"
        )

    @staticmethod
    def output_contrast(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTO"
    ) -> list[Response]:
        """Response parser for output contrast setting."""
        return VideoParsers.output_video_property(
            raw, params, zone, command, "contrast"
        )

    @staticmethod
    def output_hue(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTP"
    ) -> list[Response]:
        """Response parser for output hue setting."""
        return VideoParsers.output_video_property(raw, params, zone, command, "hue")

    @staticmethod
    def output_chroma(
        raw: str, params: PioneerAVRParams, zone=Zone.Z1, command="VTQ"
    ) -> list[Response]:
        """Response parser for output chroma setting."""
        return VideoParsers.output_video_property(raw, params, zone, command, "chroma")

    @staticmethod
    def black_setup(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VTR"
    ) -> list[Response]:
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
    def aspect(
        raw: str, _params: PioneerAVRParams, zone=Zone.Z1, command="VTS"
    ) -> list[Response]:
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
