"""aiopioneer code map class."""

from typing import Any, Tuple
from .response import Response
from ..params import PioneerAVRParams
from ..properties import PioneerAVRProperties

CODE_MAP_NDIGITS = 3
CODE_MAP_EXP = pow(10, CODE_MAP_NDIGITS)


class CodeDefault:
    """Default code for map."""

    def __hash__(self):
        return hash("default")

    def __eq__(self, value):
        return isinstance(value, CodeDefault)


class CodeMapBase(dict):
    """Map AVR codes to values."""

    def __new__(cls, value):
        return cls.value_to_code(value)

    def __class_getitem__(cls, code: str):
        return cls.code_to_value(code)

    @classmethod
    def value_to_code(cls, value) -> str:
        """Convert value to code."""
        return str(value)

    @classmethod
    def code_to_value(cls, code: str) -> Any:
        """Convert code to value."""
        return str(code)

    @classmethod
    def match(cls, v, value):
        """Default value match function."""
        return v == value

    @classmethod
    def parse_response(
        cls,
        response: Response,
        params: PioneerAVRParams,  # pylint: disable=unused-argument
        properties: PioneerAVRProperties,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Parse a response."""
        response.update(value=cls.code_to_value(response.raw))
        return [response]


class CodeBoolMap(CodeMapBase):
    """Map AVR codes to bool values."""

    code_true = "1"
    code_false = "0"

    @classmethod
    def value_to_code(cls, value: bool) -> str:
        if not isinstance(value, bool):
            raise ValueError(f"Boolean value expected for {cls.__name__}")
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
    def value_to_code(cls, value: Any) -> str:
        for k, v in cls.code_map.items():
            if cls.match(v, value):
                return k
        raise ValueError(f"Value {value} not found in {cls.__name__}")

    @classmethod
    def code_to_value(cls, code: str) -> Any:
        if code in cls.code_map:
            return cls.code_map[code]
        if CodeDefault() in cls.code_map:
            return cls.code_map[CodeDefault()]
        raise ValueError(f"Key {code} not found in {cls.__name__}")


class CodeDictStrMap(CodeDictMap):
    """Map AVR codes to dict of str values."""

    code_map: dict[str, str] = {}


class CodeDictListMap(CodeDictMap):
    """Map AVR codes to a dict of list items with value as first element."""

    code_map: dict[str, list] = {}

    @classmethod
    def match(cls, v: list, value: str):
        """Match value to first element of list."""
        return v[0] == value

    @classmethod
    def code_to_value(cls, code: str) -> Tuple[str, list]:
        value_list = super().code_to_value(code)
        return value_list[0], value_list[1:]


class CodeFloatMap(CodeMapBase):
    """Map AVR codes to float values."""

    code_zfill: int = None
    value_min: float | int = None
    value_max: float | int = None  ## NOTE: value_min must be set if value_max is set
    value_step: float | int = 1
    value_divider: float | int = 1
    value_offset: float | int = 0

    def __new__(cls, value: float | int) -> str:
        if not isinstance(value, (float, int)):
            raise ValueError(f"Value {value} is not a float or int for {cls.__name__}")
        if cls.value_min is not None:
            if cls.value_max is None:
                if cls.value_min >= value:
                    raise ValueError(
                        f"Value {value} below minimum {cls.value_min} for {cls.__name__}"
                    )
            elif not cls.value_min <= value <= cls.value_max:
                raise ValueError(
                    f"Value {value} outside of range "
                    f"{cls.value_min} -- {cls.value_max} for {cls.__name__}"
                )
        if cls.value_step != 1 and int(value * CODE_MAP_EXP) % int(
            cls.value_step * CODE_MAP_EXP
        ):
            raise ValueError(
                f"Value {value} is not a multiple of {cls.value_step} for {cls.__name__}"
            )
        code = cls.value_to_code(value)
        return code.zfill(cls.code_zfill) if cls.code_zfill else code

    @classmethod
    def value_to_code(cls, value) -> str:
        """Convert value to code."""
        return str(
            int(round((value + cls.value_offset) / cls.value_divider, CODE_MAP_NDIGITS))
        )

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> float:
        return round(
            float(code) * cls.value_divider - cls.value_offset, CODE_MAP_NDIGITS
        )


class CodeIntMap(CodeFloatMap):
    """Map AVR codes to integer values."""

    value_min: int = None
    value_max: int = None  ## NOTE: value_min must be set if value_max is set
    value_step: int = 1
    value_divider: int = 1
    value_offset: int = 0

    def __new__(cls, value: int) -> str:
        if not isinstance(value, int):
            raise ValueError(f"Value {value} is not an int for {cls.__name__}")
        return super().__new__(cls, value)

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return int(code) * cls.value_divider - cls.value_offset
