""" Pioneer AVR exceptions. """


class PioneerException(RuntimeError):
    """Generic Pioneer AVR exception."""


class AVRUnavailableException(PioneerException):
    """AVR connection not available exception."""

    translation_key = "avr_unavailable"


class AVRUnknownCommandException(PioneerException):
    """Invalid AVR command requested exception."""

    translation_key = "unknown_command"


class AVRResponseTimeoutException(PioneerException):
    """Expected AVR response was not received."""

    translation_key = "response_timeout"


class AVRCommandErrorException(PioneerException):
    """AVR command returned an error."""

    translation_key = "command_error"


PioneerExceptionFormatText = {
    "avr_unavailable": "AVR connection is not available",
    "unknown_command": "Unknown AVR command {command} for zone {zone}",
    "response_timeout": "AVR command {command} timed out",
    "command_error": "AVR command {command} returned error: {exc}",
    "unknown_exception": "AVR command {command} returned exception: {exc}",
}
