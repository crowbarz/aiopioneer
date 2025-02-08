""" Pioneer AVR exceptions. """

from .const import Zone


class PioneerError(RuntimeError):
    """Generic Pioneer AVR exception."""

    translation_key = None

    def __init__(self, msg: str = None, **kwargs):
        self.kwargs = kwargs
        if msg is None:
            msg = self.format_err(ErrorFormatText, self.translation_key, **kwargs)
        super().__init__(msg)

    @staticmethod
    def format_err(err_dict: dict[str, str], err_key: str, **kwargs):
        """Get error message and interpolate arguments."""
        try:
            return err_dict[err_key].format(**kwargs)
        except Exception as err_exc:  # pylint: disable=broad-except
            return f"exception generating error {err_key}: {repr(err_exc)}"


class AVRConnectionError(PioneerError):
    """Base class for AVR connection errors."""

    translation_key = "avr_connection_error"

    def __init__(
        self, err: str = None, err_key: str = None, exc: Exception = None, **kwargs
    ):
        if err_key:
            err = self.format_err(ConnectErrorFormatText, err_key, exc=exc, **kwargs)
        elif exc and err is None:
            err = repr(exc)
        self.err = err
        super().__init__(err=err, exc=exc, **kwargs)


class AVRConnectError(AVRConnectionError):
    """Error with AVR connection."""

    translation_key = "avr_connect_error"


class AVRConnectTimeoutError(AVRConnectError):
    """Could not connect to AVR error due to a timeout."""

    def __init__(self, exc: Exception = None, **kwargs):
        super().__init__(err_key="connect_timeout_error", exc=exc, **kwargs)


class AVRConnectProtocolError(AVRConnectError):
    """Could not connect to AVR error due to API protocol error."""

    def __init__(self, exc: Exception = None, **kwargs):
        super().__init__(err_key="protocol_error", exc=exc, **kwargs)


class AVRDisconnectError(AVRConnectionError):
    """Error disconnecting from AVR."""

    translation_key = "avr_disconnect_error"


class AVRUnavailableError(AVRConnectionError):
    """AVR connection not available."""

    translation_key = "avr_unavailable"


class AVRUnknownCommandError(PioneerError):
    """Invalid AVR command requested."""

    translation_key = "unknown_command"

    def __init__(self, command: str, zone: Zone, **kwargs):
        super().__init__(command=command, zone=zone, **kwargs)


class AVRUnknownLocalCommandError(PioneerError):
    """Invalid local command requested."""

    translation_key = "unknown_local_command"

    def __init__(self, command: str, **kwargs):
        super().__init__(command=command, **kwargs)


class AVRResponseTimeoutError(PioneerError):
    """Expected AVR response was not received."""

    translation_key = "response_timeout"

    def __init__(self, command: str, **kwargs):
        super().__init__(command=command, **kwargs)


class AVRCommandError(PioneerError):
    """AVR command resulted in an error."""

    translation_key = "command_error"

    def __init__(self, command: str, err: str = None, exc: Exception = None, **kwargs):
        if exc and err is None:
            err = repr(exc)
        super().__init__(command=command, err=err, exc=exc, **kwargs)


class AVRCommandResponseError(AVRCommandError):
    """AVR responded with an error."""

    def __init__(self, command: str, err: str, **kwargs):
        super().__init__(command=command, err=err, **kwargs)


class AVRResponseParseError(PioneerError):
    """AVR response could not be parsed."""

    translation_key = "response_parse_error"

    def __init__(self, response: str, exc: Exception, **kwargs):
        super().__init__(response=response, err=repr(exc), exc=exc, **kwargs)


class AVRLocalCommandError(AVRCommandError):
    """Local command resulted in an error."""

    translation_key = "local_command_error"

    def __init__(
        self,
        command: str,
        err: str = None,
        err_key: str = None,
        exc: Exception = None,
        **kwargs,
    ):
        if err_key:
            err = self.format_err(
                LocalCommandErrorFormatText, err_key, exc=exc, **kwargs
            )
        elif exc and err is None:
            err = repr(exc)
        super().__init__(command=command, err=err, exc=exc, **kwargs)


class AVRTunerUnavailableError(AVRLocalCommandError):
    """Tuner is not available."""

    def __init__(self, command: str, **kwargs):
        super().__init__(command=command, err_key="tuner_unavailable", **kwargs)


ErrorFormatText = {
    "avr_connection_error": "AVR connection error: {err}",
    "avr_connect_error": "Unable to connect to AVR: {err}",
    "avr_disconnect_error": "Error disconnect from AVR: {err}",
    "avr_unavailable": "AVR connection is not available",
    "unknown_command": "Unknown AVR command {command} for zone {zone}",
    "unknown_local_command": "Unknown command {command}",
    "response_timeout": "AVR command {command} timed out",
    "command_error": "AVR command {command} returned error: {err}",
    "response_parse_error": "Exception parsing response: {response}: {err}",
    "local_command_error": "Command {command} error: {err}",
}

LocalCommandErrorFormatText = {
    "tuner_unavailable": "AVR tuner is unavailable",
    "tone_unavailable": "Tone controls not supported for {zone.full_name}",
    "freq_step_calc_error": "Unable to calculate AM frequency step",
    "freq_step_unknown": "Unknown AM tuner frequency step, parameter 'am_frequency_step' required",
    "freq_step_max_exceeded": "Maximum tuner frequency step count exceeded",
    "freq_set_failed": "Unable to set tuner frequency to {frequency}",
    "channel_levels_unavailable": "channel levels not supported for {zone.full_name}",
    "video_settings_unavailable": "video settings not supported for {zone.full_name}",
    "dsp_settings_unavailable": "DSP settings not supported for {zone.full_name}",
    "speaker_mode_unavailable": "speaker configuration not supported",
    "hdmi_out_unavailable": "HDMI out configuration not supported",
    "hdmi3_out_unavailable": "HDMI3 out configuration not supported",
    "hdmi_audio_unavailable": "HDMI audio configuration not supported",
    "media_controls_not_supported": "Media controls not supported on source {source}",
    "media_action_not_supported": "Media action {action} not supported on source {source}",
}

ConnectErrorFormatText = {
    "connect_timeout_error": "Connection timed out",
    "already_connected": "AVR is already connected",
    "already_connecting": "AVR is already connecting",
    "already_disconnecting": "AVR is already disconnecting",
    "protocol_error": "Device not responding to Pioneer AVR protocol",
}
