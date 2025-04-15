"""Pioneer AVR exceptions."""

from .const import Zone


class AVRError(RuntimeError):
    """Generic Pioneer AVR exception."""

    base_err_key = None

    def __init__(self, msg: str = None, **kwargs):
        self.kwargs = kwargs
        if msg is None:
            msg = self.format_err(ErrorFormatText, self.base_err_key, **kwargs)
        super().__init__(msg)

    @staticmethod
    def format_err(err_dict: dict[str, str], err_key: str, **kwargs):
        """Get error message and interpolate arguments."""
        try:
            return err_dict.get(err_key, err_key).format(**kwargs)
        except Exception as err_exc:  # pylint: disable=broad-except
            return f"exception generating error {err_key}: {repr(err_exc)}"


class AVRConnectionError(AVRError):
    """Base class for AVR connection errors."""

    base_err_key = "avr_connection_error"

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

    base_err_key = "avr_connect_error"


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

    base_err_key = "avr_disconnect_error"


class AVRUnavailableError(AVRConnectionError):
    """AVR connection not available."""

    base_err_key = "avr_unavailable"


class AVRUnknownCommandError(AVRError):
    """Invalid AVR command requested."""

    base_err_key = "unknown_command"

    def __init__(self, command: str, zone: Zone, **kwargs):
        super().__init__(command=command, zone=zone, **kwargs)


class AVRUnknownLocalCommandError(AVRError):
    """Invalid local command requested."""

    base_err_key = "unknown_local_command"

    def __init__(self, command: str, **kwargs):
        super().__init__(command=command, **kwargs)


class AVRResponseTimeoutError(AVRError):
    """Expected AVR response was not received."""

    base_err_key = "response_timeout"

    def __init__(self, command: str, **kwargs):
        super().__init__(command=command, **kwargs)


class AVRCommandError(AVRError):
    """AVR command resulted in an error."""

    base_err_key = "command_error"

    def __init__(self, command: str, err: str = None, exc: Exception = None, **kwargs):
        if exc and err is None:
            err = repr(exc)
        super().__init__(command=command, err=err, exc=exc, **kwargs)


class AVRCommandResponseError(AVRCommandError):
    """AVR responded with an error."""

    def __init__(self, command: str, response: str, **kwargs):
        self.response = err = response
        if response in CommandResponseErrorFormatText:
            err = self.format_err(CommandResponseErrorFormatText, response, **kwargs)
        super().__init__(command=command, err=err, **kwargs)


class AVRCommandUnavailableError(AVRCommandError):
    """AVR responded with an error."""

    base_err_key = "command_unavailable"

    def __init__(self, command: str, err: str = None, err_key: str = None, **kwargs):
        if err_key:
            err = self.format_err(CommandUnavailableErrorFormatText, err_key, **kwargs)
        super().__init__(command=command, err=err, **kwargs)


class AVRResponseDecodeError(AVRError):
    """AVR response could not be decoded."""

    base_err_key = "response_decode_error"

    def __init__(self, response: str, exc: Exception, **kwargs):
        super().__init__(response=response, err=repr(exc), exc=exc, **kwargs)


class AVRLocalCommandError(AVRCommandError):
    """Local command resulted in an error."""

    base_err_key = "local_command_error"

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


class AVRTunerUnavailableError(AVRCommandUnavailableError):
    """Tuner is not available."""

    def __init__(self, command: str, **kwargs):
        super().__init__(command=command, err_key="tuner", **kwargs)


ErrorFormatText = {
    "avr_connection_error": "AVR connection error: {err}",
    "avr_connect_error": "unable to connect to AVR: {err}",
    "avr_disconnect_error": "error disconnect from AVR: {err}",
    "avr_unavailable": "AVR connection is not available",
    "unknown_command": "unknown AVR command {command} for zone {zone}",
    "unknown_local_command": "unknown command {command}",
    "command_unavailable": "AVR command {command} is unavailable: {err}",
    "response_timeout": "AVR command {command} timed out",
    "command_error": "AVR command {command} returned error: {err}",
    "response_decode_error": "exception decoding response: {response}: {err}",
    "local_command_error": "command {command} error: {err}",
}

LocalCommandErrorFormatText = {
    "freq_step_error": (
        "unable to calculate AM frequency step, "
        "parameter 'am_frequency_step' required"
    ),
    "freq_step_unknown": "unknown AM tuner frequency step, parameter 'am_frequency_step' required",
    "freq_step_max_exceeded": "maximum tuner frequency step count exceeded",
    "freq_set_failed": "unable to set tuner frequency to {frequency}",
}

CommandResponseErrorFormatText = {
    "B00": "AVR temporarily busy",
    "E02": "command currently unavailable",
    "E03": "unsupported command",
    "E04": "unknown command",
    "E06": "invalid parameter",
}

CommandUnavailableErrorFormatText = {
    "tuner": "AVR tuner is unavailable",
    "tone": "tone controls not supported for {zone.full_name}",
    "channel_levels": "channel levels not supported for {zone.full_name}",
    "channel": "channel {channel} unavailable for {zone.full_name}",
    "video_settings": "video settings not supported for {zone.full_name}",
    "dsp_settings": "DSP settings not supported for {zone.full_name}",
    "set_amp_speaker_mode": "speaker configuration not supported",
    "set_amp_hdmi_out": "HDMI out configuration not supported",
    "set_amp_hdmi3_out": "HDMI3 out configuration not supported",
    "set_amp_hdmi_audio": "HDMI audio configuration not supported",
    "set_amp_pqls": "PQLS configuration not supported",
    "set_amp_mode": "amp mode configuration not supported",
    "media_controls": "media controls not supported on source {source}",
    "media_action": "media action {action} not supported on source {source}",
    "resolution_unavailable": "resolution {resolution} unavailable",
}

ConnectErrorFormatText = {
    "connect_timeout_error": "connection timed out",
    "already_connected": "AVR is already connected",
    "already_connecting": "AVR is already connecting",
    "already_disconnecting": "AVR is already disconnecting",
    "protocol_error": "device not responding to Pioneer AVR protocol",
}
