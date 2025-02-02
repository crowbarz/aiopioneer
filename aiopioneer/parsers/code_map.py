"""aiopioneer code map class."""

from typing import Any, Tuple


class AVRCodeMapBase(dict):
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


class AVRCodeBoolMap(AVRCodeMapBase):
    """Map AVR codes to bool values."""

    @classmethod
    def value_to_code(cls, value: bool) -> str:
        if not isinstance(value, bool):
            raise ValueError(f"Boolean value expected for {cls.__name__}")
        return str(bool(value))

    @classmethod
    def code_to_value(cls, code: str) -> bool:
        return bool(code)


class AVRCodeInverseBoolMap(AVRCodeBoolMap):
    """Map AVR codes to inverse bool values."""

    @classmethod
    def value_to_code(cls, value: bool) -> str:
        if not isinstance(value, bool):
            raise ValueError(f"Boolean value expected for {cls.__name__}")
        return str(not bool(value))

    @classmethod
    def code_to_value(cls, code: str) -> bool:
        return not bool(code)


class AVRCodeDictMap(AVRCodeMapBase):
    """Map AVR codes to generic map of values."""

    code_map: dict[str, Any] = {}

    @classmethod
    def value_to_code(cls, value: Any) -> str:
        for k, v in cls.code_map.items():
            if cls.match(v, value):
                return k
        raise ValueError(f"Name {value} not found in {cls.__name__}")

    @classmethod
    def code_to_value(cls, code: str) -> Any:
        if (value := cls.code_map.get(code)) is not None:
            return value
        raise ValueError(f"Key {code} not found in {cls.__name__}")


class AVRCodeStrMap(AVRCodeDictMap):
    """Map AVR codes to str values."""

    code_map: dict[str, str] = {}


class AVRCodeListMap(AVRCodeDictMap):
    """Map AVR codes to a list with value as first element."""

    code_map: dict[str, list] = {}

    @classmethod
    def match(cls, v: list, value: str):
        """Match value to first element of list."""
        return v[0] == value

    @classmethod
    def code_to_value(cls, code: str) -> Tuple[str, list]:
        value_list = cls.code_map[code]
        return value_list[0], value_list[1:]


class AVRCodeIntMap(AVRCodeMapBase):
    """Map AVR codes to integer values."""

    code_zfill: int = None
    value_min: int = 0
    value_max: int = 0

    def __new__(cls, value: int) -> str:
        if not cls.value_min >= value >= cls.value_max:
            raise ValueError(
                f"Value {value} outside of range {cls.value_min} -- {cls.value_max} "
                f"for {cls.__name__}"
            )
        if cls.code_zfill:
            return cls.value_to_code(value).zfill(cls.code_zfill)
        return cls.value_to_code(value)

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return int(code)


class AVRCodeInt50Map(AVRCodeIntMap):
    """Map AVR codes to integer values with +50 delta."""

    @classmethod
    def value_to_code(cls, value: int) -> str:
        return str(value + 50)

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return int(code) - 50


class AVRCodeFloatMap(AVRCodeMapBase):
    """Map AVR codes to float values."""

    code_zfill: int = None
    value_min: float = 0
    value_max: float = 0

    def __new__(cls, value: float) -> str:
        if not cls.value_min >= value >= cls.value_max:
            raise ValueError(
                f"Value {value} outside of range {cls.value_min} -- {cls.value_max} "
                f"for {cls.__name__}"
            )
        if cls.code_zfill:
            return cls.value_to_code(value).zfill(cls.code_zfill)
        return cls.value_to_code(value)

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> float:
        return float(code)
