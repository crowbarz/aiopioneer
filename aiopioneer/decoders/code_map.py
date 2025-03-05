"""aiopioneer code map class."""

from typing import Any, Tuple

from ..const import Zone
from ..exceptions import AVRCommandUnavailableError
from ..params import AVRParams
from ..properties import AVRProperties
from .response import Response

CODE_MAP_NDIGITS = 3
CODE_MAP_EXP = pow(10, CODE_MAP_NDIGITS)


class CodeDefault:
    """Default code for map."""

    def __hash__(self):
        return hash("default")

    def __eq__(self, value):
        return isinstance(value, CodeDefault)


class CodeMapBase:
    """Map AVR codes to values."""

    friendly_name = None
    base_property = None
    property_name = None

    def __new__(cls, value):
        return cls.value_to_code(value)

    def __class_getitem__(cls, code: str):
        return cls.code_to_value(code)

    @classmethod
    def get_name(cls) -> str:
        """Get class name, using friendly name if defined."""
        return cls.friendly_name if cls.friendly_name else cls.__name__

    @classmethod
    def get_len(cls) -> int:
        """Get class field length."""
        raise ValueError(f"class length undefined for {cls.get_name()}")

    @classmethod
    def get_nargs(cls, min_nargs: int = None) -> int:
        """Get or check number of args consumed by class."""
        if min_nargs is not None and min_nargs > 1:
            raise ValueError(f"insufficient arguments for {cls.get_name()}")
        return 1

    @classmethod
    def value_to_code(cls, value) -> str:
        """Convert value to code."""
        return str(value)

    @classmethod
    def code_to_value(cls, code: str) -> Any:
        """Convert code to value."""
        return str(code)

    @classmethod
    def parse_args(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,  # pylint: disable=unused-argument
        params: AVRParams,  # pylint: disable=unused-argument
        properties: AVRProperties,  # pylint: disable=unused-argument
    ) -> str:
        """Convert and pop argument(s) to code."""
        if not isinstance(args, list) or len(args) == 0:
            raise ValueError(f"insufficient arguments for {cls.get_name()}")
        return cls.value_to_code(args.pop(0))

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Decode a response."""
        if cls.base_property is not None:
            response.update(base_property=cls.base_property)
        if cls.property_name is not None:
            response.update(property_name=cls.property_name)
        response.update(value=cls.code_to_value(response.code))
        return [response]


class CodeMapSequence(CodeMapBase):
    """Map AVR codes to a sequence of code maps."""

    code_map_sequence: list[tuple[CodeMapBase, str] | int] = []
    code_fillchar = "_"

    @classmethod
    def get_len(cls) -> int:
        return sum([child_map.get_len() for child_map, _ in cls.code_map_sequence])

    @classmethod
    def get_nargs(cls, min_nargs: int = None) -> int:
        nargs = sum([child_map.get_nargs() for child_map, _ in cls.code_map_sequence])
        if min_nargs is not None and min_nargs > nargs:
            raise ValueError(f"insufficient arguments for {cls.get_name()}")
        return nargs

    @classmethod
    def value_to_code(cls, value) -> str:
        raise ValueError(f"value_to_code unsupported for {cls.get_name()}")

    @classmethod
    def code_to_value(cls, code: str) -> Any:
        raise ValueError(f"code_to_value unsupported for {cls.get_name()}")

    @classmethod
    def parse_args(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
        code_map_sequence: list[tuple[CodeMapBase, str] | int] = None,
    ) -> str:
        if code_map_sequence is None:
            code_map_sequence = cls.code_map_sequence

        def parse_child_item(child_item: tuple[CodeMapBase, str] | int) -> str:
            if isinstance(child_item, tuple):  ## item is (code_map, property)
                child_map, _ = child_item
                return child_map.parse_args(
                    command=command,
                    args=args,
                    zone=zone,
                    params=params,
                    properties=properties,
                )
            elif isinstance(child_item, int):  ## item is gap
                child_len = child_item
                return "".ljust(child_len, cls.code_fillchar)
            else:
                raise RuntimeError(
                    f"invalid sequence item {child_item} for {cls.get_name()}"
                )

        return "".join(
            [parse_child_item(child_item) for child_item in code_map_sequence]
        )

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
        code_map_sequence: list[tuple[CodeMapBase, str]] = None,
    ) -> list[Response]:
        code_index = 0
        responses = []
        if code_map_sequence is None:
            code_map_sequence = cls.code_map_sequence

        for child_item in code_map_sequence:
            if isinstance(child_item, tuple):  ## item is (code_map, property)
                child_map, child_property_name = child_item
                child_len = child_map.get_len()
                child_code = response.code[code_index : code_index + child_len]
                child_response = response.clone(
                    code=child_code, property_name=child_property_name
                )
                responses.extend(
                    child_map.decode_response(response=child_response, params=params)
                )
            elif isinstance(child_item, int):  ## item is gap
                child_len = child_item
            else:
                raise RuntimeError(
                    f"invalid sequence item {child_item} for {cls.get_name()}"
                )
            code_index += child_len

        return responses


class CodeMapHasProperty(CodeMapBase):
    """
    Code map mixin that checks settable property is supported by AVR.

    Requires cls.base_property and cls.property_name to be set in class.
    """

    @classmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
    ) -> str:
        if getattr(properties, cls.base_property, {}).get(cls.property_name) is None:
            raise AVRCommandUnavailableError(command=command, err_key=command)
        return super().parse_args(
            command=command, args=args, zone=zone, params=params, properties=properties
        )


class CodeStrMap(CodeMapBase):
    """Map AVR codes to str values of fixed length."""

    code_len = 0
    code_fillchar = "_"

    @classmethod
    def get_len(cls) -> int:
        return cls.code_len if cls.code_len else super().get_len()

    @classmethod
    def value_to_code(cls, value: str) -> str:
        if cls.code_len:
            return value.ljust(cls.code_len, cls.code_fillchar)
        return value


class CodeBoolMap(CodeMapBase):
    """Map AVR codes to bool values."""

    code_true = "1"
    code_false = "0"

    @classmethod
    def get_len(cls) -> int:
        return 1

    @classmethod
    def value_to_code(cls, value: bool) -> str:
        if not isinstance(value, bool):
            raise ValueError(f"boolean value expected for {cls.get_name()}")
        return cls.code_true if value else cls.code_false

    @classmethod
    def code_to_value(cls, code: str) -> bool:
        return True if code == cls.code_true else False


class CodeInverseBoolMap(CodeBoolMap):
    """Map AVR codes to inverse bool values."""

    code_true = "0"
    code_false = "1"


class CodeDictMap(CodeMapBase):
    """Map AVR codes to generic map of values."""

    code_map: dict[str, Any] = {}

    @classmethod
    def get_len(cls) -> int:
        ## NOTE: assumes that all codes in dict are of the same length
        return len(next(k for k in cls.code_map if k != CodeDefault()))

    @classmethod
    def value_to_code(cls, value: Any) -> str:
        for k, v in cls.code_map.items():
            if cls.match(v, value):
                return k
        raise ValueError(f"value {value} not found for {cls.get_name()}")

    @classmethod
    def code_to_value(cls, code: str) -> Any:
        if code in cls.code_map:
            return cls.code_map[code]
        if CodeDefault() in cls.code_map:
            return cls.code_map[CodeDefault()]
        raise ValueError(f"key {code} not found for {cls.get_name()}")

    @classmethod
    def match(cls, v, value):
        """Default value match function."""
        return v == value

    @classmethod
    def keys(cls) -> list[str]:
        """Return list of keys for code map."""
        return cls.code_map.keys()

    @classmethod
    def values(cls) -> list[Any]:
        """Return list of values for code map."""
        return cls.code_map.values()

    @classmethod
    def items(cls) -> list[tuple[str, Any]]:
        """Return list of items for code map."""
        return cls.code_map.items()


class CodeDictStrMap(CodeDictMap):
    """Map AVR codes to dict of str values."""

    code_map: dict[str, str] = {}


class CodeDictListMap(CodeDictMap):
    """Map AVR codes to a dict of list items with value as first element."""

    code_map: dict[str, list] = {}

    @classmethod
    def code_to_value(cls, code: str) -> Tuple[str, list]:
        value_list = super().code_to_value(code)
        return value_list[0]

    @classmethod
    def match(cls, v: list, value: str):
        """Match value to first element of list."""
        return v[0] == value

    @classmethod
    def values(cls) -> list[Any]:
        """Return list of first element of list items for code map."""
        return [value_list[0] for value_list in cls.code_map.values()]

    @classmethod
    def items(cls) -> list[tuple[str, Any]]:
        """Return list of first element of list items for code map."""
        return [(key, value_list[0]) for key, value_list in cls.code_map.items()]


class CodeFloatMap(CodeMapBase):
    """
    Map AVR codes to float values.

    code = str(((value + value_offset) / value_divider) - code_offset)
    value = ((int(code) + code_offset) * value_divider) - value_offset
    """

    code_zfill: int = None
    code_offset: float | int = 0
    value_min: float | int = None
    value_max: float | int = None  ## NOTE: value_min must be set if value_max is set
    value_step: float | int = 1
    value_divider: float | int = 1
    value_offset: float | int = 0

    @classmethod
    def get_len(cls) -> int:
        return cls.code_zfill if cls.code_zfill else super().get_len()

    def __new__(cls, value: float | int) -> str:
        if not isinstance(value, (float, int)):
            raise ValueError(f"{value} is not a float or int for {cls.get_name()}")
        if cls.value_min is not None:
            if cls.value_max is None:
                if cls.value_min >= value:
                    raise ValueError(
                        f"{value} below minimum {cls.value_min} for {cls.get_name()}"
                    )
            elif not cls.value_min <= value <= cls.value_max:
                raise ValueError(
                    f"{value} outside of range "
                    f"{cls.value_min} -- {cls.value_max} for {cls.get_name()}"
                )
        if cls.value_step != 1 and int(value * CODE_MAP_EXP) % int(
            cls.value_step * CODE_MAP_EXP
        ):
            raise ValueError(
                f"{value} is not a multiple of {cls.value_step} for {cls.get_name()}"
            )
        code = cls.value_to_code(value)
        return code.zfill(cls.code_zfill) if cls.code_zfill else code

    @classmethod
    def value_to_code(cls, value) -> str:
        """Convert value to code."""
        return str(
            int(
                round(
                    (value + cls.value_offset) / cls.value_divider - cls.code_offset,
                    CODE_MAP_NDIGITS,
                )
            )
        )

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> float:
        return round(
            (int(code) + cls.code_offset) * cls.value_divider - cls.value_offset,
            CODE_MAP_NDIGITS,
        )


class CodeIntMap(CodeFloatMap):
    """Map AVR codes to integer values."""

    value_min: int = None
    value_max: int = None  ## NOTE: value_min must be set if value_max is set
    value_step: int = 1
    value_divider: int = 1
    value_offset: int = 0

    def __new__(cls, value: int) -> str:
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        elif not isinstance(value, int):
            raise ValueError(f"{value} is not an int for {cls.get_name()}")
        return super().__new__(cls, value)

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return int(code) * cls.value_divider - cls.value_offset
