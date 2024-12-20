"""Pioneer AVR properties."""

import copy

from typing import Any
from types import MappingProxyType

from .commands import PIONEER_COMMANDS
from .const import Zone, MEDIA_CONTROL_COMMANDS
from .param import PioneerAVRParams, PARAM_ZONE_SOURCES, PARAM_QUERY_SOURCES


class PioneerAVRProperties:
    """Pioneer AVR properties class."""

    def __init__(self, params: PioneerAVRParams):
        self.params = params

        ## AVR base properties
        self.model = None
        self.software_version = None
        self.mac_addr: str = None
        self.zones: list[Zone] = []
        self.power: dict[Zone, bool] = {}
        self.volume: dict[Zone, int] = {}
        self.max_volume: dict[Zone, int] = {}
        self.mute: dict[Zone, bool] = {}
        self.source_id: dict[Zone, str] = {}
        self.source_name: dict[Zone, str] = {}
        self.listening_mode = ""
        self.listening_mode_raw = ""
        self.media_control_mode: dict[Zone, str] = {}
        self.tone: dict[Zone, dict] = {}
        self.amp: dict[str, Any] = {}
        self.tuner: dict[str, Any] = {}
        self.dsp: dict[str, Any] = {}
        self.video: dict[str, Any] = {}
        self.system: dict[str, Any] = {}
        self.audio: dict[str, Any] = {}

        ## Complex object that holds multiple different props for the CHANNEL/DSP functions
        self.channel_levels: dict[str, Any] = {}

        ## Source name mappings
        self.source_name_to_id: dict[str, str] = {}
        self.source_id_to_name: dict[str, str] = {}

    def set_source_dict(self, sources: dict[str, str]) -> None:
        """Manually set source id<->name translation tables."""
        self.params.set_system_param(PARAM_QUERY_SOURCES, False)
        self.source_name_to_id = copy.deepcopy(sources)
        self.source_id_to_name = {v: k for k, v in sources.items()}

    def get_source_list(self, zone: Zone = Zone.Z1) -> list[str]:
        """Return list of available input sources."""
        source_ids = self.params.get_param(PARAM_ZONE_SOURCES[zone], [])
        return list(
            self.source_name_to_id.keys()
            if not source_ids
            else [
                self.source_id_to_name[s]
                for s in source_ids
                if s in self.source_id_to_name
            ]
        )

    def get_source_dict(self, zone: Zone = None) -> dict[str, str]:
        """Return source id<->name translation tables."""
        if zone is None:
            return MappingProxyType(self.source_name_to_id)
        source_ids = self.params.get_param(PARAM_ZONE_SOURCES[zone], [])
        return (
            self.source_name_to_id
            if not source_ids
            else {k: v for k, v in self.source_name_to_id.items() if v in source_ids}
        )

    def get_source_name(self, source_id: str) -> str:
        """Return name for given source ID."""
        return (
            self.source_id_to_name.get(source_id, source_id)
            if self.source_name_to_id
            else source_id
        )

    def clear_source_id(self, source_id: str) -> None:
        """Clear name mapping for given source ID."""
        source_name = None
        if source_id in self.source_id_to_name:
            source_name = self.source_id_to_name[source_id]
            self.source_id_to_name.pop(source_id)
        if source_name in self.source_name_to_id:
            self.source_name_to_id.pop(source_name)

    @property
    def ipod_control_commands(self) -> list[str]:
        """Return a list of all valid iPod control modes."""
        return list(
            [
                k.replace("operation_ipod_", "")
                for k in PIONEER_COMMANDS
                if k.startswith("operation_ipod")
            ]
        )

    @property
    def tuner_control_commands(self) -> list[str]:
        """Return a list of all valid tuner control commands."""
        return list(
            [
                k.replace("operation_tuner_", "")
                for k in PIONEER_COMMANDS
                if k.startswith("operation_tuner")
            ]
        )

    def get_supported_media_controls(self, zone: Zone) -> list[str] | None:
        """Return a list of all valid media control actions for a given zone.
        If the provided zone source is not currently compatible with media controls,
        null will be returned."""
        if self.media_control_mode.get(zone) is not None:
            return list(
                [
                    k
                    for k in MEDIA_CONTROL_COMMANDS.get(
                        self.media_control_mode.get(zone)
                    ).keys()
                ]
            )
        else:
            return None
