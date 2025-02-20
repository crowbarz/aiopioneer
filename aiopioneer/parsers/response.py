"""aiopioneer parsed response model."""

from collections.abc import Callable
from typing import Any, Self
from ..const import Zone
from ..properties import PioneerAVRProperties


class Response:
    """Structured response for dynamic parsing into aiopioneer properties."""

    def __init__(
        self,
        raw: str,
        response_command: str,
        base_property: str = None,
        property_name: str = None,
        zone: Zone = None,
        update_zones: set[Zone] = None,
        value: Any = None,
        queue_commands: list = None,
        callback: Callable[[PioneerAVRProperties, Self], list[Self]] = None,
    ):
        self.raw = raw
        self.response_command = response_command
        self.base_property = base_property
        self.property_name = property_name
        self.zone = zone
        self.update_zones = set() if update_zones is None else update_zones
        self.value = value
        self.command_queue = queue_commands
        self.callback = callback

    def update(
        self,
        raw: str = None,
        response_command: str = None,
        base_property: str = None,
        property_name: str = None,
        zone: Zone = None,
        update_zones: set[Zone] = None,
        value: Any = None,
        queue_commands: list = None,
        callback: Callable[[PioneerAVRProperties, Self], list[Self]] = None,
        clear_property: bool = False,
        clear_value: bool = False,
    ):
        """Update a Response with changed attributes."""
        if raw is not None:
            self.raw = raw
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
            self.command_queue = queue_commands

    def clone(
        self,
        raw: str = None,
        response_command: str = None,
        base_property: str = None,
        property_name: str = None,
        zone: Zone = None,
        update_zones: set[Zone] = None,  ## NOTE: merged with existing
        value: Any = None,
        queue_commands: list = None,
        callback: Callable[[Any, Self], list[Self]] = None,
        inherit_property: bool = True,
        inherit_value: bool = True,
    ) -> Self:
        """Clone a Response with modified attributes."""
        if raw is None:
            raw = self.raw
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
            raw=raw,
            response_command=response_command,
            base_property=base_property,
            property_name=property_name,
            zone=zone,
            value=value,
            queue_commands=queue_commands,
            callback=callback,
        )
