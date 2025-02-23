"""aiopioneer response decoders for tuner parameters."""

from ..const import TunerBand
from ..params import AVRParams
from .code_map import CodeMapBase, CodeIntMap, CodeFloatMap
from .response import Response


class FrequencyFM(CodeFloatMap):
    """Tuner FM frequency."""

    value_min = 87.5
    value_max = 108.0
    value_step = 0.05
    value_divider = 0.01

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for tuner FM frequency."""
        super().decode_response(response, params)
        return [
            response.clone(property_name="band", value=TunerBand.FM),
            *Preset.update_preset(response),
            response,
        ]


class FrequencyAM(CodeIntMap):
    """Tuner AM frequency."""

    value_min = 530
    value_max = 1701
    value_step = 1  # default/unknown AM frequency step

    VALUE_MIN_STEP = {9: 531, 10: 530}
    VALUE_MAX_STEP = {9: 1701, 10: 1700}

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for tuner AM frequency."""
        super().decode_response(response, params)

        def glean_frequency_step(response: Response) -> list[Response]:
            """Determine frequency step from current frequency."""
            frequency_step = response.properties.tuner.get("am_frequency_step")

            ## Check whether new frequency is divisible by 9 or 10
            if frequency_step is None:
                freq_div9 = response.value % 9 == 0
                freq_div10 = response.value % 10 == 0
                if freq_div9 and not freq_div10:
                    frequency_step = 9
                elif not freq_div9 and freq_div10:
                    frequency_step = 10
                if frequency_step:
                    return cls.update_frequency_step(
                        response=response, frequency_step=frequency_step
                    )
            return []

        queue_commands = []
        current_tuner_band = response.properties.tuner.get("band")
        frequency_step = response.properties.tuner.get("am_frequency_step")
        if current_tuner_band is not TunerBand.AM and not frequency_step:
            queue_commands = [["_sleep", 2], "_calculate_am_frequency_step"]
        return [
            response.clone(
                property_name="band", value=TunerBand.AM, queue_commands=queue_commands
            ),
            *Preset.update_preset(response),
            response.clone(callback=glean_frequency_step),
            response,
        ]

    @classmethod
    def update_frequency_step(
        cls, response: Response, frequency_step: int
    ) -> list[Response]:
        """Generate response to update AM frequency step."""

        def set_frequency_step(response: Response) -> list[Response]:
            """Set AM frequency step."""
            if (frequency_step := response.value) not in [9, 10]:
                raise ValueError(
                    f"invalid frequency step {frequency_step}, must be 9 or 10"
                )
            FrequencyAM.value_step = frequency_step
            FrequencyAM.value_min = cls.VALUE_MIN_STEP[frequency_step]
            FrequencyAM.value_max = cls.VALUE_MAX_STEP[frequency_step]
            return [response]

        return [
            response.clone(
                property_name="am_frequency_step",
                value=frequency_step,
                callback=set_frequency_step,
            )
        ]


class Preset(CodeMapBase):
    """Tuner preset."""

    cached_preset: tuple[str, int] = []

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for tuner preset."""

        def cache_preset(response: Response) -> list[Response]:
            """Cache preset for later update."""
            cls.cached_preset = response.value
            return [response]

        super().decode_response(response, params)
        response.update(
            clear_property=True,
            queue_commands=[["_oob", "query_tuner_frequency"]],
            callback=cache_preset,
        )
        return [response]

    @classmethod
    def update_preset(cls, response: Response) -> list[Response]:
        """Update tuner preset from cached preset and frequency update."""

        def check_cached_preset(response: Response) -> list[Response]:
            """Update preset based on cached preset."""
            if cls.cached_preset is not None:
                # pylint: disable=unbalanced-tuple-unpacking
                (tuner_class, tuner_preset) = cls.cached_preset
                cls.cached_preset = None
                return [
                    response.clone(property_name="class", value=tuner_class),
                    response.clone(property_name="preset", value=tuner_preset),
                ]
            if response.value != response.properties.tuner.get("frequency"):
                return [
                    response.clone(property_name="class", inherit_value=False),
                    response.clone(property_name="preset", inherit_value=False),
                ]
            return []

        ## NOTE: response.value = updated frequency
        return [response.clone(callback=check_cached_preset)]

    @classmethod
    def value_to_code(cls, value: tuple[str, int]) -> str:
        """Convert tuner class and preset to code."""
        tuner_class, tuner_preset = value
        if not (
            isinstance(tuner_class, str)
            and len(tuner_class) == 1
            and "A" <= tuner_class <= "G"
        ):
            raise ValueError(f"class {tuner_class} outside of range A to G")
        if not (isinstance(tuner_preset, int) and 0 <= tuner_preset <= 9):
            raise ValueError(f"preset {tuner_preset} outside of range 0 -- 9")
        return f"{tuner_class.upper()}{str(tuner_preset).zfill(2)}"

    @classmethod
    def code_to_value(cls, code: str) -> tuple[str, int]:
        """Convert code to value."""
        return code[0], int(code[1:])


class FrequencyAMStep(CodeIntMap):
    """AM frequency step. (Supported on very few AVRs)"""

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for AM frequency step."""

        super().decode_response(response, params)
        return FrequencyAM.update_frequency_step(
            response=response, frequency_step=response.value
        )

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return 9 if code == "0" else 10

    ## NOTE: value_to_code unimplemented
