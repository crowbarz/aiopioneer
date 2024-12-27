"""aiopioneer response parsers for tuner parameters."""

from ..const import Zone, TunerBand
from ..params import PioneerAVRParams, PARAM_TUNER_AM_FREQ_STEP
from .response import Response


class TunerParsers:
    """Tuner response parsers."""

    _ignore_preset = True  # ignore first preset response
    _current_preset_raw: str = None  # current value of preset
    _cached_preset_raw: str = None  # cached preset, update after tuner frequency update
    _current_freq: float = None  # current frequency, clear preset when changed

    @staticmethod
    def frequency_fm(
        raw: str, params: PioneerAVRParams, zone=Zone.ALL, command="FR"
    ) -> list[Response]:
        """Response parser for FM tuner frequency."""
        new_freq = float(raw) / 100
        current_freq = TunerParsers._current_freq
        parsed = []
        parsed.extend(
            [
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="tuner",
                    property_name="band",
                    zone=zone,
                    value=TunerBand.FM,
                    queue_commands=None,
                ),
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="tuner",
                    property_name="frequency",
                    zone=zone,
                    value=new_freq,
                    queue_commands=None,
                ),
            ]
        )
        if TunerParsers._cached_preset_raw:
            parsed.extend(TunerParsers._update_preset(params, zone))
        elif current_freq != new_freq:
            parsed.extend(TunerParsers._clear_preset(params, zone))
        TunerParsers._current_freq = new_freq
        return parsed

    @staticmethod
    def frequency_am(
        raw: str, params: PioneerAVRParams, zone=Zone.ALL, command="FR"
    ) -> list[Response]:
        """Response parser AM tuner frequency."""
        new_freq = float(raw)
        current_freq = TunerParsers._current_freq
        parsed = []
        command_queue = None
        if params.get_param(PARAM_TUNER_AM_FREQ_STEP) is None:
            command_queue = [["_sleep", 2], "_calculate_am_frequency_step"]

        parsed.extend(
            [
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="tuner",
                    property_name="band",
                    zone=zone,
                    value=TunerBand.AM,
                    queue_commands=command_queue,
                ),
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="tuner",
                    property_name="frequency",
                    zone=zone,
                    value=new_freq,
                    queue_commands=None,
                ),
            ]
        )
        if TunerParsers._cached_preset_raw:
            parsed.extend(TunerParsers._update_preset(params, zone))
        elif current_freq != new_freq:
            parsed.extend(TunerParsers._clear_preset(params, zone))
            TunerParsers._current_freq = new_freq
        return parsed

    @staticmethod
    def preset(
        raw: str, _params: PioneerAVRParams, zone=Zone.ALL, command="PR"
    ) -> list[Response]:
        """Response parser for tuner preset. Cache until next frequency update."""
        parsed = []
        command_queue = [["_oob", "query_tuner_frequency"]]
        TunerParsers._cached_preset_raw = raw
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property=None,
                property_name=None,
                zone=zone,
                value=raw,
                queue_commands=command_queue,
            )
        )
        return parsed

    @staticmethod
    def _update_preset(
        _params: PioneerAVRParams, zone=Zone.ALL, command="PR"
    ) -> list[Response]:
        """Parse and update tuner preset from cached values."""
        parsed = []
        current_preset_raw = TunerParsers._current_preset_raw
        cached_preset_raw = TunerParsers._cached_preset_raw
        ignore_preset = TunerParsers._ignore_preset

        TunerParsers._current_preset_raw = cached_preset_raw
        if cached_preset_raw is None or current_preset_raw == cached_preset_raw:
            return parsed
        if ignore_preset:
            ## Ignore first preset response
            TunerParsers._cached_preset_raw = None
            TunerParsers._ignore_preset = False
            return parsed

        # pylint: disable=unsubscriptable-object
        tuner_class = cached_preset_raw[:1]
        tuner_preset = int(cached_preset_raw[1:])
        TunerParsers._cached_preset_raw = None
        parsed.extend(
            [
                Response(
                    raw=cached_preset_raw,
                    response_command=command,
                    base_property="tuner",
                    property_name="class",
                    zone=zone,
                    value=tuner_class,
                    queue_commands=None,
                ),
                Response(
                    raw=cached_preset_raw,
                    response_command=command,
                    base_property="tuner",
                    property_name="preset",
                    zone=zone,
                    value=tuner_preset,
                    queue_commands=None,
                ),
            ]
        )
        return parsed

    @staticmethod
    def _clear_preset(
        _params: PioneerAVRParams, zone=Zone.ALL, command="PR"
    ) -> list[Response]:
        """Clear tuner presets."""
        raw = ""
        parsed = []
        parsed.extend(
            [
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="tuner",
                    property_name="class",
                    zone=zone,
                    value=None,
                    queue_commands=None,
                ),
                Response(
                    raw=raw,
                    response_command=command,
                    base_property="tuner",
                    property_name="preset",
                    zone=zone,
                    value=None,
                    queue_commands=None,
                ),
            ]
        )
        TunerParsers._current_preset_raw = None
        TunerParsers._cached_preset_raw = None
        return parsed

    @staticmethod
    def am_frequency_step(
        raw: str, params: PioneerAVRParams, zone=None, command="SUQ"
    ) -> list[Response]:
        """Response parser for AM frequency step. (Supported on very few AVRs)"""
        frequency_step = 9 if raw == "0" else 10
        parsed = []
        params.set_runtime_param(PARAM_TUNER_AM_FREQ_STEP, frequency_step)
        parsed.append(
            Response(
                raw=raw,
                response_command=command,
                base_property="tuner",
                property_name="am_frequency_step",
                zone=zone,
                value=frequency_step,
                queue_commands=None,
            )
        )
        return parsed
