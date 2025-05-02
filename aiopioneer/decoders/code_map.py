"""aiopioneer code map class."""

import argparse
import logging
import re
from abc import abstractmethod
from typing import Any

from ..const import Zone
from ..exceptions import AVRCommandUnavailableError
from ..params import AVRParams
from ..properties import AVRProperties
from .response import Response

CODE_MAP_NDIGITS = 3
CODE_MAP_EXP = pow(10, CODE_MAP_NDIGITS)

_LOGGER = logging.getLogger(__name__)


class CodeDefault:
    """Default code for map."""

    def __hash__(self):
        return hash("default")

    def __eq__(self, value):
        return isinstance(value, CodeDefault)


class CodeMapBase:
    """Map AVR codes to values."""

    friendly_name: str = None
    base_property: str = None
    property_name: str = None
    supported_zones: set[Zone] = {}
    icon: str = "mdi:audio-video"
    ha_auto_entity: bool = True  ## add as HA entity automatically
    ha_enable_default: bool = False  ## enable entity by default

    def __new__(cls, value, **kwargs):
        _LOGGER.warning("deprecated __new__ method called for class %s", cls)
        return cls.value_to_code(value, **kwargs)

    def __class_getitem__(cls, code: str):
        return cls.code_to_value(code)

    @classmethod
    def get_ss_class_name(cls) -> str:
        """Get space separated code map name."""
        if cls.friendly_name:
            return " ".join(s[0].upper() + s[1:] for s in cls.friendly_name.split(" "))
        return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", cls.__name__)

    @classmethod
    def get_name(cls) -> str:
        """Get code map name, using friendly name if defined."""
        return cls.friendly_name if cls.friendly_name else cls.get_ss_class_name()

    @classmethod
    def get_helptext(cls) -> str:
        """Get code map help text."""
        return str(cls.__doc__).rstrip(".")

    @classmethod
    @abstractmethod
    def get_len(cls) -> int:
        """Get class field length."""
        raise NotImplementedError(f"class length undefined for {cls.get_name()}")

    @classmethod
    def get_nargs(cls) -> int:
        """Get number of arguments consumed by code map."""
        return 1

    @classmethod
    def get_parser(cls, parser: argparse.ArgumentParser) -> None:
        """Get argument parser for code map."""

    @classmethod
    def check_args(cls, args: list, extra_args: bool = False) -> None:
        """Check sufficient arguments have been supplied."""
        if not isinstance(args, list):
            raise TypeError(f"invalid argument list for {cls.get_name()}")
        nargs = cls.get_nargs()
        if (not extra_args and nargs != len(args)) or (
            extra_args and nargs > len(args)
        ):
            plural = "s" if nargs > 1 else ""
            raise ValueError(f"{nargs} argument{plural} expected for {cls.get_name()}")

    @classmethod
    def set_response_properties(cls, response: Response) -> None:
        """Set response properties from code map class if defined."""
        if cls.base_property is not None:
            response.update(base_property=cls.base_property)
        if cls.property_name is not None:
            response.update(property_name=cls.property_name)

    @classmethod
    @abstractmethod
    def value_to_code(cls, value) -> str:
        """Convert value to code."""
        raise NotImplementedError(f"value_to_code unsupported for {cls.get_name()}")

    @classmethod
    @abstractmethod
    def code_to_value(cls, code: str) -> Any:
        """Convert code to value."""
        raise NotImplementedError(f"code_to_value unsupported for {cls.get_name()}")

    @classmethod
    def parse_args(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,  # pylint: disable=unused-argument
        params: AVRParams,  # pylint: disable=unused-argument
        properties: AVRProperties,  # pylint: disable=unused-argument
    ) -> str:
        """Convert arg(s) to code."""
        cls.check_args(args)
        return cls.value_to_code(args[0])

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Decode a response."""
        cls.set_response_properties(response)
        response.update(value=cls.code_to_value(response.code))
        return [response]


# pylint: disable=abstract-method
class CodeMapComplexMixin(CodeMapBase):
    """Mixin for complex code maps that do not support value_to_code and code_to_value."""

    @classmethod
    def value_to_code(cls, value) -> str:
        """Unsupported method."""
        raise RuntimeError(f"value_to_code unsupported for {cls.get_name()}")

    @classmethod
    def code_to_value(cls, code: str) -> Any:
        """Unsupported method."""
        raise RuntimeError(f"code_to_value unsupported for {cls.get_name()}")


class CodeMapBlank(CodeMapComplexMixin, CodeMapBase):
    """Blank code map."""

    code_len = None

    def __new__(cls, code_len: int = None):
        """Create a subclass for a code map of code_len characters."""
        return type(f"CodeMapBlank_{code_len}", (CodeMapBlank,), {"code_len": code_len})

    @classmethod
    def get_len(cls) -> int:
        if cls.code_len is None:
            raise NotImplementedError(f"code_len not set for {cls.get_name()}")
        return cls.code_len

    @classmethod
    def get_nargs(cls) -> int:
        return 0

    @classmethod
    def parse_args(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
    ) -> str:
        return ""

    @classmethod
    def decode_response(cls, response: Response, params: AVRParams) -> list[Response]:
        return []


# pylint: disable=abstract-method
class CodeMapSequence(CodeMapComplexMixin, CodeMapBase):
    """Map AVR codes to a sequence of code maps."""

    code_map_sequence: list[type[CodeMapBase]] = []
    code_fillchar = "_"

    @classmethod
    def get_len_sequence(cls, code_map_sequence: list[type[CodeMapBase]] = None) -> int:
        """Get length of sequence."""

        if code_map_sequence is None:
            code_map_sequence = cls.code_map_sequence
        return sum(child_map.get_len() for child_map in code_map_sequence)

    @classmethod
    def get_nargs_sequence(
        cls, code_map_sequence: list[type[CodeMapBase]] = None
    ) -> int:
        """Get number of args for sequence."""

        if code_map_sequence is None:
            code_map_sequence = cls.code_map_sequence
        return sum(child_map.get_nargs() for child_map in code_map_sequence)

    @classmethod
    def get_parser_sequence(
        cls,
        parser: argparse.ArgumentParser,
        code_map_sequence: list[type[CodeMapBase]] = None,
    ) -> None:
        """Get parsers for sequence."""

        if code_map_sequence is None:
            code_map_sequence = cls.code_map_sequence
        for code_map in code_map_sequence:
            code_map.get_parser(parser)

    @classmethod
    def get_len(cls) -> int:
        return cls.get_len_sequence(code_map_sequence=cls.code_map_sequence)

    @classmethod
    def get_nargs(cls) -> int:
        return cls.get_nargs_sequence(code_map_sequence=cls.code_map_sequence)

    @classmethod
    def get_parser(cls, parser: argparse.ArgumentParser) -> None:
        return cls.get_parser_sequence(parser, code_map_sequence=cls.code_map_sequence)

    @classmethod
    def parse_args_sequence(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
        code_map_sequence: list[type[CodeMapBase]],
    ) -> str:
        """Convert arg to code with code map sequence."""

        def parse_child_map(child_map: CodeMapBase, args: list) -> str:
            child_map.check_args(args, extra_args=True)
            return child_map.parse_args(
                command=command,
                args=args,
                zone=zone,
                params=params,
                properties=properties,
            )

        def parse_child_item(child_item: CodeMapBase) -> str:
            if isinstance(child_item, int):  ## item is gap length
                if child_item < 0:
                    return ""
                child_len = child_item
                return "".ljust(child_len, cls.code_fillchar)
            if issubclass(child_item, CodeMapBase):
                child_map = child_item
            else:
                raise RuntimeError(
                    f"invalid sequence item {child_item} for {cls.get_name()}"
                )
            child_nargs = child_map.get_nargs()
            child_code = parse_child_map(child_map=child_map, args=args[:child_nargs])
            del args[:child_nargs]
            return child_code

        return "".join(
            [parse_child_item(child_item) for child_item in code_map_sequence]
        )

    @classmethod
    def decode_response_sequence(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
        code_map_sequence: list[type[CodeMapBase]] = None,
    ) -> list[Response]:
        """Decode a response with code map sequence."""
        cls.set_response_properties(response)
        code_index = 0
        responses = []
        if code_map_sequence is None:
            code_map_sequence = cls.code_map_sequence

        for child_map in code_map_sequence:
            child_len = child_map.get_len()
            if issubclass(child_map, CodeMapBlank):
                if child_len < 0:
                    code_index = len(response.code)
                code_index += child_len
                continue
            child_code = response.code[code_index : code_index + child_len]
            child_response = response.clone(code=child_code)
            responses.extend(
                child_map.decode_response(response=child_response, params=params)
            )
            code_index += child_len

        return responses

    @classmethod
    def parse_args(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
    ) -> str:
        return cls.parse_args_sequence(
            command=command,
            args=args,
            zone=zone,
            params=params,
            properties=properties,
            code_map_sequence=cls.code_map_sequence,
        )

    @classmethod
    def decode_response(cls, response: Response, params: AVRParams) -> list[Response]:
        return cls.decode_response_sequence(
            response=response, params=params, code_map_sequence=cls.code_map_sequence
        )


class CodeMapQuery(CodeMapBase):
    """Query code map."""

    def __new__(cls, code_map_class: type[CodeMapBase]) -> type[CodeMapSequence]:
        """Create a query code map class for base code map class."""
        return type(
            f"CodeMapQuery_{code_map_class.__name__}",
            (CodeMapSequence,),
            {"code_map_sequence": [CodeMapQuery, code_map_class]},
        )

    @classmethod
    def get_len(cls) -> int:
        return 1

    @classmethod
    def get_nargs(cls) -> int:
        return 0

    # pylint: disable=unused-argument
    @classmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
    ) -> str:
        return "?"

    @classmethod
    def decode_response(cls, response: Response, params: AVRParams) -> list[Response]:
        return []


# pylint: disable=abstract-method
class CodeMapHasPropertyMixin(CodeMapBase):
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

    code_len = None
    code_fillchar = "_"
    value_min_len = None
    value_max_len = None
    ha_text_mode = None
    ha_pattern = None

    @classmethod
    def get_len(cls) -> int:
        return cls.code_len if cls.code_len is not None else super().get_len()

    @classmethod
    def get_parser(cls, parser: argparse.ArgumentParser) -> None:
        if prop_name := cls.property_name or cls.base_property:
            parser.add_argument(prop_name, help=cls.get_helptext(), type=str)

    @classmethod
    def value_to_code(cls, value: str) -> str:
        if cls.code_len:
            return value.ljust(cls.code_len, cls.code_fillchar)
        return value

    @classmethod
    def code_to_value(cls, code: str) -> str:
        if cls.code_len and cls.code_fillchar:
            return str(code).rstrip(cls.code_fillchar)
        return str(code)


class CodeBoolMap(CodeMapBase):
    """Map AVR codes to bool values."""

    code_true = "1"
    code_false = "0"

    @classmethod
    def get_len(cls) -> int:
        return 1

    @classmethod
    def get_parser(cls, parser: argparse.ArgumentParser) -> None:
        if prop_name := cls.property_name or cls.base_property:
            parser.add_argument(
                prop_name, choices=["on", "off"], help=cls.get_helptext()
            )

    @classmethod
    def value_to_code(cls, value: bool | str) -> str:
        if isinstance(value, str) and value in ["on", "off"]:
            return cls.code_true if value == "on" else cls.code_false
        if not isinstance(value, bool):
            raise TypeError(f"boolean value expected for {cls.get_name()}")
        return cls.code_true if value else cls.code_false

    @classmethod
    def code_to_value(cls, code: str) -> bool:
        return True if code == cls.code_true else False


class CodeInverseBoolMap(CodeBoolMap):
    """Map AVR codes to inverse bool values."""

    code_true = "0"
    code_false = "1"


class CodeDynamicDictMap(CodeMapComplexMixin, CodeMapBase):
    """Map AVR codes to dynamic map of values."""

    code_len: int = None
    index_map_class: type[CodeMapBase] = None

    @classmethod
    def get_len(cls) -> int:
        return cls.code_len if cls.code_len is not None else super().get_len()

    @classmethod
    def get_parser(cls, parser: argparse.ArgumentParser) -> None:
        if prop_name := cls.property_name or cls.base_property:
            parser.add_argument(prop_name, help=cls.get_helptext(), type=str)

    @classmethod
    def match(cls, v, value):
        """Default value match function."""
        return v == value

    @classmethod
    def value_to_code_dynamic(cls, value: Any, code_map: dict[Any, Any]) -> str:
        """Convert value to code for code map."""
        for k, v in code_map.items():
            if cls.match(v, value):
                if cls.index_map_class:
                    return cls.index_map_class.value_to_code(value=k)
                return k
        raise ValueError(f"value {value} not found for {cls.get_name()}")

    @classmethod
    def code_to_value_dynamic(cls, code: str, code_map: dict[Any, Any]) -> Any:
        """Convert code to value for code map."""
        index = code
        if cls.index_map_class:
            index = cls.index_map_class.code_to_value(code=code)
        if index in code_map:
            return code_map[index]
        if CodeDefault() in code_map:
            return code_map[CodeDefault()]
        raise KeyError(f"key {code} not found for {cls.get_name()}")

    @classmethod
    def parse_args_dynamic(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,  # pylint: disable=unused-argument
        params: AVRParams,  # pylint: disable=unused-argument
        properties: AVRProperties,  # pylint: disable=unused-argument
        code_map: dict[str, Any],
    ) -> str:
        """Convert arg to code for code map."""
        cls.check_args(args)
        return cls.value_to_code_dynamic(args[0], code_map=code_map)

    @classmethod
    def decode_response_dynamic(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
        code_map: dict[str, Any],
    ) -> list[Response]:
        """Decode a response using a code map."""
        cls.set_response_properties(response)
        response.update(
            value=cls.code_to_value_dynamic(response.code, code_map=code_map)
        )
        return [response]

    # pylint: disable=unused-argument
    @classmethod
    @abstractmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
    ) -> str:
        raise NotImplementedError(f"parse_args unsupported for {cls.get_name()}")

    # pylint: disable=unused-argument
    @classmethod
    @abstractmethod
    def decode_response(cls, response: Response, params: AVRParams) -> list[Response]:
        raise NotImplementedError(f"decode_response unsupported for {cls.get_name()}")


class CodeDynamicDictStrMap(CodeDynamicDictMap):
    """Map AVR codes to dynamic dict of str values."""


class CodeDynamicDictListMap(CodeDynamicDictMap):
    """Map AVR codes to dynamic dict of list items with value as first element."""

    @classmethod
    def code_to_value_dynamic(cls, code: str, code_map: dict[Any, Any]) -> Any:
        value_list = super().code_to_value_dynamic(code, code_map=code_map)
        return value_list[0]

    @classmethod
    def match(cls, v: list, value: str):
        """Match value to first element of list."""
        return v[0] == value


class CodeDictMap(CodeDynamicDictMap):
    """Map AVR codes to static code map."""

    code_map: dict[str, Any] = {}

    @classmethod
    def get_len(cls) -> int:
        ## NOTE: assumes that all codes in dict are of the same length
        if cls.code_len is not None:
            return cls.code_len
        return len(next(k for k in cls.code_map if k != CodeDefault()))

    @classmethod
    def get_parser(cls, parser: argparse.ArgumentParser) -> None:
        if prop_name := cls.property_name or cls.base_property:
            parser.add_argument(
                prop_name,
                help=cls.get_helptext(),
                choices=list(cls.code_map.values()),
                type=str,
            )

    @classmethod
    def value_to_code(cls, value: Any) -> str:
        return cls.value_to_code_dynamic(value, code_map=cls.code_map)

    @classmethod
    def code_to_value(cls, code: str) -> Any:
        return cls.code_to_value_dynamic(code, code_map=cls.code_map)

    @classmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,
        params: AVRParams,
        properties: AVRProperties,
    ) -> str:
        return cls.parse_args_dynamic(
            command=command,
            args=args,
            zone=zone,
            params=params,
            properties=properties,
            code_map=cls.code_map,
        )

    @classmethod
    def decode_response(cls, response: Response, params: AVRParams) -> list[Response]:
        return cls.decode_response_dynamic(
            response=response, params=params, code_map=cls.code_map
        )

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
    def code_to_value(cls, code: str) -> tuple[str, list]:
        value_list = super().code_to_value(code=code)
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
    value_max: float | int = None
    value_step: float | int = 1
    value_divider: float | int = 1
    value_offset: float | int = 0
    unit_of_measurement: str = None
    ha_device_class: str = None  ## integration default
    ha_number_mode: str = None  ## integration default

    @classmethod
    def get_len(cls) -> int:
        return cls.code_zfill if cls.code_zfill is not None else super().get_len()

    @classmethod
    def get_parser(cls, parser: argparse.ArgumentParser) -> None:
        if prop_name := cls.property_name or cls.base_property:
            parser.add_argument(prop_name, help=cls.get_helptext(), type=float)

    @classmethod
    def value_to_code(cls, value: float | int):
        return cls.value_to_code_bounded(
            value=value, value_min=cls.value_min, value_max=cls.value_max
        )

    @classmethod
    def value_to_code_bounded(
        cls,
        value: float | int,
        value_min: float | int = None,
        value_max: float | int = None,
        value_step: float | int = None,
    ) -> str:
        """Convert float or int value to code with bounds."""
        if not isinstance(value, (float, int)):
            raise TypeError(f"{value} is not a float or int for {cls.get_name()}")
        if value_min is None:
            value_min = cls.value_min
        if value_max is None:
            value_max = cls.value_max
        if value_min is not None:
            if value_max is None:
                if not value_min <= value:
                    raise ValueError(
                        f"{value} is below minimum {value_min} for {cls.get_name()}"
                    )
            elif not value_min <= value <= value_max:
                raise ValueError(
                    f"{value} is outside of range "
                    f"{value_min} -- {value_max} for {cls.get_name()}"
                )
        elif value_max is not None:
            if not value <= value_max:
                raise ValueError(
                    f"{value} is above maximum {value_max} for {cls.get_name()}"
                )
        if value_step is None:
            value_step = cls.value_step
        if value_step != 1 and int(value * CODE_MAP_EXP) % int(
            value_step * CODE_MAP_EXP
        ):
            raise ValueError(
                f"{value} is not a multiple of {value_step} for {cls.get_name()}"
            )
        code = str(
            int(
                round(
                    (value + cls.value_offset) / cls.value_divider - cls.code_offset,
                    CODE_MAP_NDIGITS,
                )
            )
        )
        return code.zfill(cls.code_zfill) if cls.code_zfill else code

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> float:
        return round(
            (int(code) + cls.code_offset) * cls.value_divider - cls.value_offset,
            CODE_MAP_NDIGITS,
        )


class CodeIntMap(CodeFloatMap):
    """Map AVR codes to integer values."""

    code_offset: int = 0
    value_min: int = None
    value_max: int = None
    value_step: int = 1
    value_divider: int = 1
    value_offset: int = 0

    @classmethod
    def get_parser(cls, parser: argparse.ArgumentParser) -> None:
        if prop_name := cls.property_name or cls.base_property:
            parser.add_argument(prop_name, help=cls.get_helptext(), type=int)

    @classmethod
    def value_to_code(cls, value: int):
        return cls.value_to_code_bounded(
            value=value, value_min=cls.value_min, value_max=cls.value_max
        )

    @classmethod
    def value_to_code_bounded(
        cls,
        value: int,
        value_min: int = None,
        value_max: int = None,
        value_step: int = None,
    ) -> str:
        """Convert int value to code with bounds."""
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        elif not isinstance(value, int):
            raise TypeError(f"{value} is not an int for {cls.get_name()}")
        return super().value_to_code_bounded(
            value=value, value_min=value_min, value_max=value_max, value_step=value_step
        )

    ## NOTE: codes are not validated to value_min/value_max

    @classmethod
    def code_to_value(cls, code: str) -> int:
        return (int(code) + cls.code_offset) * cls.value_divider - cls.value_offset
