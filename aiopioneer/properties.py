"""Pioneer AVR properties."""

import copy

from typing import Any
from types import MappingProxyType

from .commands import PIONEER_COMMANDS
from .const import Zones, MEDIA_CONTROL_COMMANDS
from .param import PioneerAVRParams, PARAM_ZONE_SOURCES


class PioneerAVRProperties(PioneerAVRParams):
    """Pioneer AVR properties class."""

    def __init__(self, params: dict[str, str] = None):
        super().__init__(params)

        ## AVR base properties
        self.power: dict[Zones, bool] = {}
        self.volume: dict[Zones, int] = {}
        self.max_volume: dict[Zones, int] = {}
        self.mute: dict[Zones, bool] = {}
        self.source: dict[Zones, str] = {}
        self.listening_mode = ""
        self.listening_mode_raw = ""
        self.media_control_mode: dict[Zones, str] = {}
        self.tone: dict[Zones, dict] = {}
        self.amp: dict[str, Any] = {}
        self.tuner: dict[str, Any] = {}
        self.dsp: dict[str, Any] = {}
        self.video: dict[str, Any] = {}
        self.system: dict[str, Any] = {}
        self.audio: dict[str, Any] = {}

        ## Complex object that holds multiple different props for the CHANNEL/DSP functions
        self.channel_levels: dict[str, Any] = {}

        ## Source name mappings
        self._source_name_to_id: dict[str, str] = {}
        self._source_id_to_name: dict[str, str] = {}

    def set_source_dict(self, sources: dict[str, str]) -> None:
        """Manually set source id<->name translation tables."""
        self._set_query_sources(False)
        self._source_name_to_id = copy.deepcopy(sources)
        self._source_id_to_name = {v: k for k, v in sources.items()}

    def get_source_list(self, zone: Zones = Zones.Z1) -> list[str]:
        """Return list of available input sources."""
        source_ids = self._params.get(PARAM_ZONE_SOURCES[zone], [])
        return list(
            self._source_name_to_id.keys()
            if not source_ids
            else [
                self._source_id_to_name[s]
                for s in source_ids
                if s in self._source_id_to_name
            ]
        )

    def get_source_dict(self, zone: Zones = None) -> dict[str, str]:
        """Return source id<->name translation tables."""
        if zone is None:
            return MappingProxyType(self._source_name_to_id)
        source_ids = self._params.get(PARAM_ZONE_SOURCES[zone], [])
        return (
            self._source_name_to_id
            if not source_ids
            else {k: v for k, v in self._source_name_to_id.items() if v in source_ids}
        )

    def get_source_name(self, source_id: str) -> str:
        """Return name for given source ID."""
        return (
            self._source_id_to_name.get(source_id, source_id)
            if self._source_name_to_id
            else source_id
        )

    def clear_source_id(self, source_id: str) -> None:
        """Clear name mapping for given source ID."""
        source_name = None
        if source_id in self._source_id_to_name:
            source_name = self._source_id_to_name[source_id]
            self._source_id_to_name.pop(source_id)
        if source_name in self._source_name_to_id:
            self._source_name_to_id.pop(source_name)

    def get_ipod_control_commands(self) -> list[str]:
        """Return a list of all valid iPod control modes."""
        return list(
            [
                k.replace("operation_ipod_", "")
                for k in PIONEER_COMMANDS
                if k.startswith("operation_ipod")
            ]
        )

    def get_tuner_control_commands(self) -> list[str]:
        """Return a list of all valid tuner control commands."""
        return list(
            [
                k.replace("operation_tuner_", "")
                for k in PIONEER_COMMANDS
                if k.startswith("operation_tuner")
            ]
        )

    def get_supported_media_controls(self, zone: Zones) -> list[str] | None:
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
