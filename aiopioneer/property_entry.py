"""aiopioneer property entry."""

from .const import Zone
from .decoders.code_map import CodeMapBase
from .exceptions import AVRUnknownCommandError


class AVRCommand:
    """AVR command class."""

    def __init__(
        self,
        name: str = None,
        avr_commands: dict[Zone, str | list[str]] = None,
        avr_args: list[type[CodeMapBase]] = None,
        avr_responses: dict[Zone, str] = None,
        is_query_command: bool = False,
        wait_for_response: bool = False,
        retry_on_fail: bool = False,
    ):
        self.name = name
        self.avr_commands = avr_commands
        self.avr_args = avr_args
        self.avr_responses = avr_responses
        self.is_query_command = is_query_command
        self.wait_for_response = wait_for_response
        self.retry_on_fail = retry_on_fail

    def __repr__(self):
        return (
            f"AVRCommand(name={repr(self.name)}, "
            f"avr_commands={repr(self.avr_commands)}, "
            f"avr_args={[a.__name__ for a in (self.avr_args or [])]}, "
            f"avr_responses={repr(self.avr_responses)}, "
            f"is_query_command={self.is_query_command}, "
            f"wait_for_response={self.wait_for_response}, "
            f"retry_on_fail={self.retry_on_fail})"
        )

    def setdefault(
        self,
        name: str = None,
        avr_commands: dict[Zone, str] = None,
        avr_args: list[type[CodeMapBase]] = None,
        avr_responses: dict[Zone, str] = None,
    ) -> None:
        """Set defaults for a command if not already specified."""
        if self.name is None:
            self.name = name
        if self.avr_args is None:
            self.avr_args = avr_args
        if self.avr_commands is None:
            self.avr_commands = avr_commands
        if self.avr_responses is None:
            self.avr_responses = avr_responses

    def get_avr_command(self, zone: Zone) -> str:
        """Get AVR command."""
        if self.avr_commands is None:
            raise RuntimeError(f"AVR commands not defined for command {self.name}")
        if zone not in self.avr_commands:
            raise AVRUnknownCommandError(command=self.name, zone=zone)
        if isinstance(command := self.avr_commands[zone], list):
            command = command[0]
        return f"?{command}" if self.is_query_command else command

    def get_avr_response(self, zone: Zone) -> str | None:
        """Get expected response from AVR for command."""
        if isinstance(command := self.avr_commands[zone], list):
            return command[1]
        responses = self.avr_responses or self.avr_commands
        if not (self.wait_for_response and responses):
            return None
        try:
            if zone is Zone.Z1:
                return responses[zone] if zone in responses else responses[Zone.ALL]
            return responses[zone]
        except KeyError as exc:
            raise RuntimeError(
                f"AVR response not defined for zone {zone} for command {self.name}"
            ) from exc


class AVRPropertyEntry:
    """AVR property entry class."""

    def __init__(
        self,
        code_map: type[CodeMapBase],
        avr_commands: dict[Zone, str],
        avr_responses: dict[Zone, str] = None,
        query_command: bool | str | AVRCommand = True,
        query_group: str = None,
        set_command: bool | str | AVRCommand = None,
        retry_set_on_fail: bool = True,
        extra_commands: list[AVRCommand] = None,
    ):
        if avr_responses is None:
            avr_responses = avr_commands
        if Zone.ALL in avr_commands:  ## Convert Zone.ALL to Zone.Z1
            avr_commands = {
                Zone.Z1 if z is Zone.ALL else z: c for z, c in avr_commands.items()
            }
        self.code_map = code_map
        self.avr_commands = avr_commands
        self.avr_responses = avr_responses
        self.query_command: AVRCommand = None
        self.set_command: AVRCommand = None
        self.commands: list[AVRCommand] = []

        if (property_name_full := code_map.base_property) is None:
            raise ValueError(f"base property undefined for {code_map.__name__}")
        if code_map.property_name is not None:
            property_name_full += f"_{code_map.property_name}"

        query_command_name = "query"
        if query_group:
            query_command_name += f"_{query_group}"
        query_command_name += f"_{property_name_full}"
        if query_command is True:
            query_command = AVRCommand(is_query_command=True, wait_for_response=True)
        elif isinstance(query_command, str):
            query_command = AVRCommand(
                name=query_command,
                is_query_command=True,
                wait_for_response=True,
            )
        if isinstance(query_command, AVRCommand):
            query_command.setdefault(
                name=query_command_name,
                avr_commands=avr_commands,
                avr_responses=avr_responses,
                # avr_args=[CodeMapQuery(CodeMapBlank)],  ## TODO: update
            )
            self.query_command = query_command
            self.commands.append(query_command)
        elif query_command is not None:
            raise RuntimeError(f"invalid query_command {query_command}")

        set_command_name = f"set_{property_name_full}"
        if set_command is True:
            set_command = AVRCommand(
                wait_for_response=True, retry_on_fail=retry_set_on_fail
            )
        elif isinstance(set_command, str):
            set_command = AVRCommand(
                set_command, wait_for_response=True, retry_on_fail=retry_set_on_fail
            )
        if isinstance(set_command, AVRCommand):
            set_command.setdefault(
                name=set_command_name,
                avr_commands=avr_commands,
                avr_responses=avr_responses,
                avr_args=[code_map],
            )
            self.set_command = set_command
            self.commands.append(set_command)
        elif set_command is not None:
            raise RuntimeError(f"invalid set_command {set_command}")

        if extra_commands is not None:
            for command in extra_commands:
                command.setdefault(avr_responses=avr_responses)
            self.commands.extend(extra_commands)

    def __repr__(self):
        return (
            f"AVRPropertyEntry(code_map={self.code_map.__name__}), "
            f"avr_commands={repr(self.avr_commands)}, "
            f"avr_responses={repr(self.avr_responses)}, "
            f"commands={repr(self.commands)}, "
        )

    @property
    def responses(self) -> list[tuple[str, type[CodeMapBase], Zone]]:
        """Get handled responses for property entry."""
        return ((r, self.code_map, z) for z, r in self.avr_responses.items())


def gen_response_property(
    code_map: type[CodeMapBase], commands: dict[Zone, str], *args, **kwargs
) -> AVRPropertyEntry:
    """Convenience function to create a response only AVRPropertyEntry."""
    if "query_command" not in kwargs:
        kwargs["query_command"] = None
    if "set_command" not in kwargs:
        kwargs["set_command"] = None
    return AVRPropertyEntry(code_map, commands, *args, **kwargs)


def gen_query_property(
    code_map: type[CodeMapBase], commands: dict[Zone, str], *args, **kwargs
) -> AVRPropertyEntry:
    """Convenience function to create an AVRPropertyEntry with query command."""
    return AVRPropertyEntry(code_map, commands, *args, **kwargs)


def gen_set_property(
    code_map: type[CodeMapBase], commands: dict[Zone, str], *args, **kwargs
) -> AVRPropertyEntry:
    """Convenience function to create an AVRPropertyEntry with set command."""
    if "set_command" not in kwargs:
        kwargs["set_command"] = True
    return AVRPropertyEntry(code_map, commands, *args, **kwargs)
