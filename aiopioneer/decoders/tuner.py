"""aiopioneer response decoders for tuner parameters."""

from ..const import Zone
from ..command_queue import CommandItem
from ..const import TunerBand
from ..exceptions import AVRLocalCommandError
from ..params import AVRParams
from ..properties import AVRProperties
from ..property_entry import AVRCommand, gen_query_property, gen_set_property
from .code_map import (
    CodeMapBase,
    CodeMapSequence,
    CodeStrMap,
    CodeDictMap,
    CodeIntMap,
    CodeFloatMap,
)
from .response import Response


class TunerFMFrequency(CodeFloatMap):
    """Tuner FM frequency (1step = 0.01MHz)."""

    friendly_name = "tuner FM frequency"
    base_property = "tuner"
    property_name = "frequency"
    unit_of_measurement = "MHz"

    value_min = 87.5
    value_max = 108.0
    value_step = 0.05
    value_divider = 0.01
    code_zfill = 5

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for tuner FM frequency."""
        super().decode_response(response=response, params=params)
        return [
            response.clone(property_name="band", value=TunerBand.FM),
            *TunerPreset.update_preset(response),
            response,
        ]


class TunerAMFrequency(CodeIntMap):
    """Tuner AM frequency (1step = 1kHz)."""

    friendly_name = "tuner AM frequency"
    base_property = "tuner"
    property_name = "frequency"
    unit_of_measurement = "kHz"
    code_zfill = 5

    value_bounds = {9: (531, 1701), 10: (530, 1700), None: (530, 1701)}

    @classmethod
    def get_frequency_bounds(cls, am_frequency_step: int) -> tuple[int, int]:
        """Get bounds for frequency AM step."""
        return cls.value_bounds[am_frequency_step]

    @classmethod
    def value_to_code(cls, value: str, properties: AVRProperties = None) -> str:
        if not isinstance(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        if not (am_frequency_step := properties.tuner.get("am_frequency_step")):
            raise AVRLocalCommandError(
                command="set_tuner_frequency", err_key="freq_step_unknown"
            )
        value_min, value_max = cls.get_frequency_bounds(am_frequency_step)
        return cls.value_to_code_bounded(
            value=value,
            value_min=value_min,
            value_max=value_max,
            value_step=am_frequency_step,
        )

    @classmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,  # pylint: disable=unused-argument
        params: AVRParams,  # pylint: disable=unused-argument
        properties: AVRProperties,
    ) -> str:
        cls.check_args(args)
        return cls.value_to_code(value=args[0], properties=properties)

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for tuner AM frequency."""
        super().decode_response(response=response, params=params)

        def glean_frequency_step(response: Response) -> list[Response]:
            """Determine frequency step from current frequency."""
            properties = response.properties
            frequency_step = properties.tuner.get("am_frequency_step")

            if frequency_step:
                return []

            ## Check whether new frequency is divisible by 9 or 10
            freq_div9 = response.value % 9 == 0
            freq_div10 = response.value % 10 == 0
            if freq_div9 and not freq_div10:
                frequency_step = 9
            elif not freq_div9 and freq_div10:
                frequency_step = 10
            if frequency_step:
                return TunerAMFrequencyStep.update_frequency_step(
                    response=response.clone(), frequency_step=frequency_step
                )

            ## Trigger frequency bounce if source is tuner
            if not properties.is_source_tuner():
                return []
            response.update(
                clear_property=True,
                queue_commands=[
                    CommandItem("_calculate_am_frequency_step", queue_id=0),
                    ## NOTE: skipped if currently running
                ],
            )
            return [response]

        return [
            response.clone(inherit_property=False, callback=glean_frequency_step),
            response.clone(property_name="band", value=TunerBand.AM),
            *TunerPreset.update_preset(response),
            response,
        ]


class TunerFrequencyBand(CodeDictMap):
    """Tuner frequency band."""

    friendly_name = "tuner frequency band"
    base_property = "tuner"
    property_name = "band"

    code_map = {"A": TunerBand.AM, "F": TunerBand.FM}


class TunerFrequency(CodeMapSequence):
    """Tuner frequency."""

    friendly_name = "tuner frequency"
    base_property = "tuner"
    property_name = "frequency"

    code_map_sequence = [TunerFrequencyBand, TunerFMFrequency]  ## NOTE: placeholder

    BAND_MAP: dict[TunerBand, type[CodeMapBase]] = {
        TunerBand.AM: TunerAMFrequency,
        TunerBand.FM: TunerFMFrequency,
    }

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for tuner frequency."""
        band_code = response.code[0]
        response.update(code=response.code[1:])
        band = TunerFrequencyBand.code_to_value(code=band_code)
        return cls.BAND_MAP[band].decode_response(response, params=params)


class TunerAMFrequencyStep(CodeIntMap):
    """AM frequency step (Supported on very few AVRs)."""

    friendly_name = "tuner AM frequency step"
    base_property = "tuner"
    property_name = "am_frequency_step"

    value_min = 9
    value_max = 10
    value_offset = -9
    code_zfill = 1

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return 9 if code == "0" else 10

    ## NOTE: value_to_code unimplemented

    @classmethod
    def update_frequency_step(
        cls, response: Response, frequency_step: int
    ) -> list[Response]:
        """Generate response to update AM frequency step."""

        if frequency_step not in [9, 10]:
            raise ValueError(
                f"invalid frequency step {frequency_step}, must be 9 or 10"
            )
        cls.set_response_properties(response=response)
        response.update(value=frequency_step)
        return [response]


class TunerPreset(CodeStrMap):
    """Tuner preset."""

    friendly_name = "tuner preset"
    base_property = "tuner"
    property_name = "preset"
    supported_zones = (Zone.ALL,)
    icon = "mdi:radio"
    ha_auto_entity = False
    ha_enable_default = True

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for tuner preset."""

        def cache_preset(response: Response) -> list[Response]:
            """Cache preset for later update."""
            response.properties.tuner["cached_preset"] = response.value
            return [response]

        super().decode_response(response=response, params=params)
        response.update(
            clear_property=True,
            queue_commands=[CommandItem("query_tuner_frequency")],
            callback=cache_preset,
        )
        return [response]

    @classmethod
    def update_preset(cls, response: Response) -> list[Response]:
        """Update tuner preset from cached preset and frequency update."""

        def check_cached_preset(response: Response) -> list[Response]:
            """Update preset based on cached preset."""
            properties = response.properties
            cached_preset = properties.tuner.get("cached_preset")
            response.update(base_property="tuner")
            if cached_preset is not None:
                # pylint: disable=unbalanced-tuple-unpacking
                (tuner_class, tuner_preset) = cached_preset
                properties.tuner["cached_preset"] = None
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
        return [response.clone(inherit_property=False, callback=check_cached_preset)]

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


PROPERTIES_TUNER = [
    gen_query_property(TunerFrequency, {Zone.ALL: "FR"}),
    gen_set_property(
        TunerPreset,
        {Zone.ALL: "PR"},
        set_command="select_tuner_preset",
        retry_set_on_fail=True,
    ),
    gen_query_property(TunerAMFrequencyStep, {Zone.ALL: "SUQ"}),
]

EXTRA_COMMANDS_TUNER = [
    AVRCommand("tuner_next_preset", {Zone.Z1: ["TPI", "PR"]}),
    AVRCommand("tuner_previous_preset", {Zone.Z1: ["TPD", "PR"]}),
    AVRCommand("tuner_band_am", {Zone.Z1: ["01TN", "FR"]}, retry_on_fail=True),
    AVRCommand("tuner_band_fm", {Zone.Z1: ["00TN", "FR"]}, retry_on_fail=True),
    AVRCommand("tuner_increase_frequency", {Zone.Z1: ["TFI", "FR"]}),
    AVRCommand("tuner_decrease_frequency", {Zone.Z1: ["TFD", "FR"]}),
    AVRCommand("tuner_direct_access", {Zone.Z1: ["TAC", "TAC"]}),
    AVRCommand("tuner_digit", {Zone.Z1: ["TP", "TP"]}),
    AVRCommand("tuner_edit", {Zone.Z1: ["02TN", "TN"]}),
    AVRCommand("tuner_enter", {Zone.Z1: ["03TN", "TN"]}),
    AVRCommand("tuner_return", {Zone.Z1: ["04TN", "TN"]}),
    AVRCommand("tuner_mpx_noise_cut", {Zone.Z1: ["05TN", "TN"]}),
    AVRCommand("tuner_display", {Zone.Z1: ["06TN", "TN"]}),
    AVRCommand("tuner_pty_search", {Zone.Z1: ["07TN", "TN"]}),
]
