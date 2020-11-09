"""AVR device parameters."""

from collections import OrderedDict

PARAM_IGNORED_ZONES = "ignored_zones"
PARAM_COMMAND_DELAY = "command_delay"
PARAM_MAX_SOURCE_ID = "max_source_id"
PARAM_MAX_VOLUME = "max_volume"
PARAM_MAX_VOLUME_ZONEX = "max_volume_zonex"
PARAM_VOLUME_BOUNCE_WORKAROUND = "volume_bounce_workaround"
PARAM_VOLUME_STEP_ONLY = "volume_step_only"
PARAM_VOLUME_STEP_DELTA = "volume_step_delta"
PARAM_DEBUG_LISTENER = "debug_listener"
PARAM_DEBUG_RESPONDER = "debug_responder"
PARAM_DEBUG_UPDATER = "debug_updater"
PARAM_DEBUG_COMMAND = "debug_command"

PARAM_DEFAULTS = {
    PARAM_IGNORED_ZONES: [],
    PARAM_COMMAND_DELAY: 0.1,
    PARAM_MAX_SOURCE_ID: 60,
    PARAM_MAX_VOLUME: 185,
    PARAM_MAX_VOLUME_ZONEX: 81,
    PARAM_VOLUME_BOUNCE_WORKAROUND: False,
    PARAM_VOLUME_STEP_ONLY: False,
    PARAM_VOLUME_STEP_DELTA: 1,
    PARAM_DEBUG_LISTENER: False,
    PARAM_DEBUG_RESPONDER: False,
    PARAM_DEBUG_UPDATER: False,
    PARAM_DEBUG_COMMAND: False,
}

PARAMS_ALL = PARAM_DEFAULTS.keys()

PARAM_MODEL_DEFAULTS = OrderedDict(
    [
        (
            r"^VSX-930",
            {
                PARAM_VOLUME_BOUNCE_WORKAROUND: True,
            },
        ),
        (
            r"^VSX-S510",
            {
                PARAM_VOLUME_STEP_ONLY: True,
                PARAM_VOLUME_STEP_DELTA: 2,
            },
        ),
    ]
)
