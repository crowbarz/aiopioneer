"""aiopioneer response decode model."""

from collections.abc import Callable
from typing import Any, Self
from ..const import Zone
from ..properties import AVRProperties


class Response:
    """Structured response for dynamic decoding into aiopioneer properties."""

    def __init__(
        self,
        properties: AVRProperties,
        code: str,
        response_command: str,
        base_property: str = None,
        property_name: str = None,
        zone: Zone = None,
        update_zones: set[Zone] = None,
        value: Any = None,
        queue_commands: list[str | list] = None,
        callback: Callable[[Self], list[Self]] = None,
    ):
        self.properties = properties
        self.code = code
        self.response_command = response_command
        self.base_property = base_property
        self.property_name = property_name
        self.zone = zone
        self.update_zones = set() if update_zones is None else update_zones
        self.value = value
        self.queue_commands = queue_commands if queue_commands is not None else []
        self.callback = callback

    def __repr__(self):
        return (
            f"Response(code={repr(self.code)}, "
            f"response_command={repr(self.response_command)}, "
            f"base_property={repr(self.base_property)}, "
            f"property_name={repr(self.property_name)}, "
            f"zone={self.zone}, "
            f"update_zones={self.update_zones}, "
            f"value={repr(self.value)}, "
            f"queue_commands={self.queue_commands}, "
            f"callback={self.callback})"
        )

    def update(
        self,
        code: str = None,
        response_command: str = None,
        base_property: str = None,
        property_name: str = None,
        zone: Zone = None,
        update_zones: set[Zone] = None,
        value: Any = None,
        queue_commands: list[str | list] = None,
        append_queue_commands: list[str | list] = None,
        callback: Callable[[Self], list[Self]] = None,
        clear_property: bool = False,
        clear_value: bool = False,
    ) -> None:
        """Update a Response with changed attributes."""
        if code is not None:
            self.code = code
        if response_command is not None:
            self.response_command = response_command
        if clear_property:
            self.base_property = None
            self.property_name = None
        if base_property is not None:
            self.base_property = base_property
        if property_name is not None:
            self.property_name = property_name
        if zone is not None:
            self.zone = zone
        if update_zones is not None:
            self.update_zones = set() if update_zones is None else update_zones
        if clear_value:
            self.value = None
        if value is not None:
            self.value = value
        if callback is not None:
            self.callback = callback
        if queue_commands is not None:
            self.queue_commands = queue_commands
        if append_queue_commands is not None:
            self.queue_commands.extend(append_queue_commands)

    def clone(
        self,
        code: str = None,
        response_command: str = None,
        base_property: str = None,
        property_name: str = None,
        zone: Zone = None,
        update_zones: set[Zone] = None,  ## NOTE: merged with existing
        value: Any = None,
        queue_commands: list[str | list] = None,
        callback: Callable[[Self], list[Self]] = None,
        inherit_property: bool = True,
        inherit_value: bool = True,
    ) -> Self:
        """Clone a Response with modified attributes."""
        if code is None:
            code = self.code
        if response_command is None:
            response_command = self.response_command
        if inherit_property and base_property is None:
            base_property = self.base_property
        if inherit_property and property_name is None:
            property_name = self.property_name
        if zone is None:
            zone = self.zone
        if update_zones is None:
            update_zones = self.update_zones
        if inherit_value and value is None:
            value = self.value
        ## NOTE: queue_commands and callback are not inherited by clone
        return Response(
            properties=self.properties,
            code=code,
            response_command=response_command,
            base_property=base_property,
            property_name=property_name,
            zone=zone,
            value=value,
            queue_commands=queue_commands,
            callback=callback,
        )
