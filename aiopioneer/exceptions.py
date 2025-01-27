""" Pioneer AVR exceptions. """

from .const import Zone


class PioneerError(RuntimeError):
    """Generic Pioneer AVR exception."""

    translation_key = None

    def __init__(self, msg: str = None, **kwargs):
        self.kwargs = kwargs
        if msg:
            err_txt = msg
        else:
            err_key = self.translation_key
            try:
                err = ErrorFormatText[err_key]
                err_txt = err.format(**self.kwargs)
            except Exception as err_exc:  # pylint: disable=broad-except
                err_txt = f"exception generating error {err_key}: {repr(err_exc)}"
        super().__init__(err_txt)


class AVRConnectionError(PioneerError):
    """Base class for AVR connection errors."""

    translation_key = "avr_connection_error"

    def __init__(
        self, err: str = None, err_key: str = None, exc: Exception = None, **kwargs
    ):
        if err_key:
            err = ConnectErrorFormatText.get(err_key, err_key)
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
            err = LocalCommandErrorFormatText.get(err_key, err_key)
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
    "local_command_error": "Command {command} error: {err}",
}

LocalCommandErrorFormatText = {
    "tuner_unavailable": "AVR tuner is unavailable",
}

ConnectErrorFormatText = {
    "connect_timeout_error": "Connection timed out",
    "already_connected": "AVR is already connected",
    "already_connecting": "AVR is already connecting",
    "already_disconnecting": "AVR is already disconnecting",
    "protocol_error": "Device not responding to Pioneer AVR protocol",
}
