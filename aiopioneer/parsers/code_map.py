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
        return str(int(value))

    @classmethod
    def code_to_value(cls, code: str) -> bool:
        return bool(int(code))


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


class AVRCodeFloatMap(AVRCodeMapBase):
    """Map AVR codes to float values."""

    code_zfill: int = None
    value_min: float | int = 0
    value_max: float | int = 0  ## NOTE: value_min must also be set if value_max is set

    def __new__(cls, value: float | int) -> str:
        if not isinstance(value, (float, int)):
            raise ValueError(f"Value {value} is not a float or int for {cls.__name__}")
        if cls.value_min is not None:
            if cls.value_max is None:
                if cls.value_min >= value:
                    raise ValueError(
                        f"Value {value} below minimum {cls.value_min} for {cls.__name__}"
                    )
            elif not cls.value_min >= value >= cls.value_max:
                raise ValueError(
                    f"Value {value} outside of range "
                    f"{cls.value_min} -- {cls.value_max} for {cls.__name__}"
                )
        code = cls.value_to_code(value)
        return code.zfill(cls.code_zfill) if cls.code_zfill else code

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> float:
        return float(code)


class AVRCodeIntMap(AVRCodeFloatMap):
    """Map AVR codes to integer values."""

    value_min: int = None
    value_max: int = None  ## NOTE: value_min must also be set if value_max is set

    def __new__(cls, value: int) -> str:
        if not isinstance(value, int):
            raise ValueError(f"Value {value} is not an int for {cls.__name__}")
        return super().__new__(cls, value)

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
