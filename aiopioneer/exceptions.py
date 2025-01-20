""" Pioneer AVR exceptions. """


class PioneerError(RuntimeError):
    """Generic Pioneer AVR exception."""


class AVRConnectError(PioneerError):
    """Could not connect to AVR error."""

    translation_key = "avr_connect_error"


class AVRUnavailableError(PioneerError):
    """AVR connection not available exception."""

    translation_key = "avr_unavailable"


class AVRUnknownCommandError(PioneerError):
    """Invalid AVR command requested exception."""

    translation_key = "unknown_command"


class AVRResponseTimeoutError(PioneerError):
    """Expected AVR response was not received."""

    translation_key = "response_timeout"


class AVRCommandError(PioneerError):
    """AVR command returned an error."""

    translation_key = "command_error"


PioneerErrorFormatText = {
    "avr_connect_error": "Unable to connect to AVR",
    "avr_unavailable": "AVR connection is not available",
    "unknown_command": "Unknown AVR command {command} for zone {zone}",
    "response_timeout": "AVR command {command} timed out",
    "command_error": "AVR command {command} returned error: {exc}",
    "unknown_exception": "AVR command {command} returned exception: {exc}",
}
