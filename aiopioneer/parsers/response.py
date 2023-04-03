"""Response model"""

class Response():
    """Model defining a parsed response for dynamic parsing into aiopioneer properties."""

    def __init__(
            self,
            raw: str,
            response_command: str,
            base_property: str,
            property_name: str,
            zone: str,
            value,
            queue_commands: list
        ):
        self.raw = raw
        self.response_command =  response_command
        self.base_property = base_property
        self.property_name = property_name
        self.zone = zone
        self.value = value
        self.command_queue = queue_commands
