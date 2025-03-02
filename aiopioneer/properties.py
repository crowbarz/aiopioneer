"""Pioneer AVR properties."""

import copy
import logging

from typing import Any
from types import MappingProxyType

from .command_queue import CommandQueue
from .const import Zone, MEDIA_CONTROL_COMMANDS, LISTENING_MODES, SOURCE_TUNER
from .params import (
    AVRParams,
    PARAM_MODEL,
    PARAM_ZONE_SOURCES,
    PARAM_DISABLED_LISTENING_MODES,
    PARAM_ENABLED_LISTENING_MODES,
    PARAM_EXTRA_LISTENING_MODES,
    PARAM_TUNER_AM_FREQ_STEP,
)

_LOGGER = logging.getLogger(__name__)


class AVRProperties:
    """Pioneer AVR properties class."""

    def __init__(self, params: AVRParams):
        self._params = params

        ## AVR base properties
        self.zones: set[Zone] = set()
        self.zones_initial_refresh: set[Zone] = set()
        self.command_queue = CommandQueue(params)
        self.power: dict[Zone, bool] = {}
        self.volume: dict[Zone, int] = {}
        self.max_volume: dict[Zone, int] = {}
        self.mute: dict[Zone, bool] = {}
        self.source_id: dict[Zone, str] = {}
        self.source_name: dict[Zone, str] = {}
        self.listening_mode = None
        self.listening_mode_raw = None
        self.listening_modes_all: dict[str, list] = {}
        self.available_listening_modes: dict[str, str] = {}
        self.media_control_mode: dict[Zone, str] = {}
        self.tone: dict[Zone, dict] = {}
        self.amp: dict[str | Zone, Any] = {
            "model": params.get_param(PARAM_MODEL),
            "software_version": None,
            "mac_addr": None,
        }
        self.tuner: dict[str | Zone, Any] = {
            "am_frequency_step": self._params.get_param(PARAM_TUNER_AM_FREQ_STEP),
        }
        self.dsp: dict[str | Zone, Any] = {}
        self.video: dict[str | Zone, Any] = {}
        self.system: dict[str | Zone, Any] = {}
        self.audio: dict[str | Zone, Any] = {}

        ## Complex object that holds multiple different props for the CHANNEL/DSP functions
        self.channel_levels: dict[str, Any] = {}

        ## Source name mappings
        self.query_sources = None
        self.source_name_to_id: dict[str, str] = {}
        self.source_id_to_name: dict[str, str] = {}

    def reset(self) -> None:
        """Reset AVR properties."""
        self.command_queue.purge()
        self.power = {}
        self.volume = {}
        self.mute = {}
        self.listening_mode = ""
        self.listening_mode_raw = ""
        self.amp = {
            "model": self.amp.get("model"),
            "software_version": self.amp.get("software_version"),
            "mac_addr": self.amp.get("mac_addr"),
        }
        self.tuner = {"am_frequency_step": self.tuner.get("am_frequency_step")}
        self.dsp = {}
        self.video = {}
        self.system = {}
        self.audio = {}

    def set_source_dict(self, sources: dict[str, str]) -> None:
        """Manually set source id<->name translation tables."""
        self.query_sources = False
        self.source_name_to_id = copy.deepcopy(sources)
        self.source_id_to_name = {v: k for k, v in sources.items()}

    def get_source_list(self, zone: Zone = Zone.Z1) -> list[str]:
        """Return list of available input sources."""
        source_ids = self._params.get_param(PARAM_ZONE_SOURCES[zone], [])
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
        source_ids = self._params.get_param(PARAM_ZONE_SOURCES[zone], [])
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

    def is_source_tuner(self, source: str = None) -> bool:
        """Return whether current source is tuner."""
        if source is not None:
            return source == SOURCE_TUNER
        sources = [s for z, s in self.source_id.items() if self.power.get(z)]
        return SOURCE_TUNER in sources

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

    def update_listening_modes(self) -> None:
        """Update list of valid listening modes for current input source."""
        self.listening_modes_all = LISTENING_MODES | self._params.get_param(
            PARAM_EXTRA_LISTENING_MODES, {}
        )
        self.available_listening_modes = {}
        disabled_modes = self._params.get_param(PARAM_DISABLED_LISTENING_MODES, [])
        enabled_modes = self._params.get_param(PARAM_ENABLED_LISTENING_MODES, [])
        available_mode_names = []
        multichannel = self.audio.get("input_multichannel")

        _LOGGER.debug("determining available listening modes")
        for mode_id, mode_details in self.listening_modes_all.items():
            if mode_id in disabled_modes or (
                enabled_modes and mode_id not in enabled_modes
            ):
                continue
            mode_name, mode_2ch, mode_multich = mode_details
            if mode_name in available_mode_names:
                _LOGGER.warning("ignored duplicate listening mode name: %s", mode_name)
                continue
            if (multichannel and mode_multich) or (not multichannel and mode_2ch):
                self.available_listening_modes |= {mode_id: mode_name}
            available_mode_names.append(mode_name)
