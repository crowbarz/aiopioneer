"""Pioneer AVR properties."""

import logging

from typing import Any

from .command_queue import CommandQueue
from .const import Zone, MEDIA_CONTROL_COMMANDS, LISTENING_MODES, SOURCE_TUNER
from .exceptions import AVRLocalCommandError
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
        self.source_id: dict[Zone, int] = {}
        self.source_name: dict[Zone, str] = {}
        self.listening_mode: str = None
        self.listening_mode_id: int = None
        self.listening_modes_all: dict[int, list] = {}
        self.available_listening_modes: dict[int, str] = {}
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
        self.channel_levels: dict[Zone, dict[str, Any]] = {}

        ## Source name mappings
        self.query_sources = None
        self.source_name_to_id: dict[str, int] = {}
        self.source_id_to_name: dict[int, str] = {}

    def reset(self) -> None:
        """Reset AVR properties."""
        _LOGGER.info("resetting cached AVR properties")
        self.zones_initial_refresh: set[Zone] = set()
        self.command_queue.purge()
        self.power = {}
        self.volume = {}
        self.mute = {}
        self.listening_mode = None
        self.listening_mode_id = None
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

    def set_source_dict(self, sources: dict[int, str] | dict[str, str]) -> None:
        """Set source ID to name mapping."""
        self.query_sources = False
        try:
            if sources and isinstance(list(sources.keys())[0], str):
                ## TODO: deprecate legacy (source_name, str(src_id)) format
                _LOGGER.warning("converting legacy source dict format")
                self.source_name_to_id = {k: int(v) for k, v in sources.items()}
                self.source_id_to_name = {int(v): k for k, v in sources.items()}
            else:
                self.source_id_to_name = sources.copy()
                self.source_name_to_id = {v: k for k, v in sources.items()}
        except (ValueError, KeyError) as exc:
            raise AVRLocalCommandError(command="set_source_dict", exc=exc) from exc

    def get_source_list(self, zone: Zone = Zone.Z1) -> list[str]:
        """Return list of available input sources for zone."""
        source_ids: list[int] = None
        if zone is not None:
            source_ids = self._params.get_param(PARAM_ZONE_SOURCES[zone], [])
        if not source_ids:
            return list(self.source_id_to_name.values())
        return list(v for k, v in self.source_id_to_name.items() if k in source_ids)

    def get_source_dict(self, zone: Zone = None) -> dict[int, str]:
        """Return source ID to name mapping for zone."""
        source_ids: list[int] = None
        if zone is not None:
            source_ids = self._params.get_param(PARAM_ZONE_SOURCES[zone], [])
        if not source_ids:
            return self.source_id_to_name.copy()
        return {k: v for k, v in self.source_id_to_name.items() if k in source_ids}

    def get_source_name(self, source_id: int) -> str:
        """Return source name for source ID."""
        if self.source_name_to_id is None:
            return str(source_id)
        return self.source_id_to_name.get(source_id, str(source_id))

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
