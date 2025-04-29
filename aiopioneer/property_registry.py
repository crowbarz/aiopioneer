"""aiopioneer property registry."""

import logging

from .const import Zone
from .exceptions import AVRUnknownCommandError
from .property_entry import AVRCommand, AVRPropertyEntry
from .decoders.amp import PROPERTIES_AMP, EXTRA_COMMANDS_AMP
from .decoders.audio import PROPERTIES_AUDIO
from .decoders.code_map import CodeMapBase
from .decoders.dsp import PROPERTIES_DSP
from .decoders.system import PROPERTIES_SYSTEM
from .decoders.tuner import PROPERTIES_TUNER, EXTRA_COMMANDS_TUNER
from .decoders.video import PROPERTIES_VIDEO

_LOGGER = logging.getLogger(__name__)


class AVRPropertyRegistry:
    """AVR property registry class."""

    def __init__(
        self,
        property_entries: list[AVRPropertyEntry],
        extra_commands: list[AVRCommand] = None,
    ):
        if extra_commands is None:
            extra_commands = []
        self.property_entries = property_entries
        self.responses: list[tuple[str, type[CodeMapBase], Zone]] = []
        self.commands: list[AVRCommand] = extra_commands or []
        self.code_map_index: dict[type[CodeMapBase], AVRPropertyEntry] = {}
        self.command_index: dict[str, AVRCommand] = {c.name: c for c in extra_commands}

        for property_entry in property_entries:
            self.responses += list(property_entry.responses)
            self.commands += property_entry.commands
            if code_map := property_entry.code_map:
                if code_map in self.code_map_index:
                    _LOGGER.warning(
                        "duplicate property entry for code map %s detected",
                        code_map.get_name(),
                    )
                self.code_map_index[code_map] = property_entry
            for command in property_entry.commands:
                if command.name in self.command_index:
                    _LOGGER.warning(
                        "duplicate command %s for code map %s detected",
                        command.name,
                        code_map.get_name(),
                    )
                self.command_index[command.name] = command

    def get_command(self, command: str, zone: Zone) -> AVRCommand:
        """Return AVR command for zone."""
        if command in self.command_index:
            command_item = self.command_index[command]
            if zone in command_item.avr_commands:
                return command_item
        raise AVRUnknownCommandError(command=command, zone=zone)

    def get_commands(self, prefix: str = None, zone: Zone = None) -> list[AVRCommand]:
        """Return commands matching optional prefix and base_property."""
        return (
            c
            for c in self.commands
            if (not prefix or c.name.startswith(prefix))
            and (zone is None or zone in c.avr_commands)
        )

    def get_code_maps(
        self,
        base_class: type[CodeMapBase],
        zone: Zone = None,
        is_ha_auto_entity: bool = False,
    ) -> list[type[CodeMapBase]]:
        """Return property entries matching a CodeMapBase subclass."""
        classes: list[type[CodeMapBase]] = []
        for code_map in self.code_map_index:
            if issubclass(code_map, base_class):
                if (zone is None or zone in code_map.supported_zones) and (
                    not is_ha_auto_entity or code_map.ha_auto_entity
                ):
                    classes.append(code_map)
        return classes

    def match_response(self, raw_resp: str) -> tuple[str, type[CodeMapBase], Zone]:
        """Return code map for response."""
        return next((r for r in self.responses if raw_resp.startswith(r[0])), None)


EXTRA_COMMANDS_IPOD = [
    AVRCommand("ipod_play", {Zone.Z1: ["00IP", "IP"]}),
    AVRCommand("ipod_pause", {Zone.Z1: ["01IP", "IP"]}),
    AVRCommand("ipod_stop", {Zone.Z1: ["02IP", "IP"]}),
    AVRCommand("ipod_previous", {Zone.Z1: ["03IP", "IP"]}),
    AVRCommand("ipod_next", {Zone.Z1: ["04IP", "IP"]}),
    AVRCommand("ipod_rewind", {Zone.Z1: ["05IP", "IP"]}),
    AVRCommand("ipod_fastforward", {Zone.Z1: ["06IP", "IP"]}),
    AVRCommand("ipod_repeat", {Zone.Z1: ["07IP", "IP"]}),
    AVRCommand("ipod_shuffle", {Zone.Z1: ["08IP", "IP"]}),
    AVRCommand("ipod_display", {Zone.Z1: ["09IP", "IP"]}),
    AVRCommand("ipod_control", {Zone.Z1: ["10IP", "IP"]}),
    AVRCommand("ipod_cursor_up", {Zone.Z1: ["13IP", "IP"]}),
    AVRCommand("ipod_cursor_down", {Zone.Z1: ["14IP", "IP"]}),
    AVRCommand("ipod_cursor_right", {Zone.Z1: ["15IP", "IP"]}),
    AVRCommand("ipod_cursor_left", {Zone.Z1: ["16IP", "IP"]}),
    AVRCommand("ipod_enter", {Zone.Z1: ["17IP", "IP"]}),
    AVRCommand("ipod_return", {Zone.Z1: ["18IP", "IP"]}),
    AVRCommand("ipod_top_menu", {Zone.Z1: ["19IP", "IP"]}),
    AVRCommand("ipod_iphone_direct_control", {Zone.Z1: ["20IP", "IP"]}),
]
EXTRA_COMMANDS_NETWORK = [
    AVRCommand("network_numeric_0", {Zone.Z1: ["00NW", "NW"]}),
    AVRCommand("network_numeric_1", {Zone.Z1: ["01NW", "NW"]}),
    AVRCommand("network_numeric_2", {Zone.Z1: ["02NW", "NW"]}),
    AVRCommand("network_numeric_3", {Zone.Z1: ["03NW", "NW"]}),
    AVRCommand("network_numeric_4", {Zone.Z1: ["04NW", "NW"]}),
    AVRCommand("network_numeric_5", {Zone.Z1: ["05NW", "NW"]}),
    AVRCommand("network_numeric_6", {Zone.Z1: ["06NW", "NW"]}),
    AVRCommand("network_numeric_7", {Zone.Z1: ["07NW", "NW"]}),
    AVRCommand("network_numeric_8", {Zone.Z1: ["08NW", "NW"]}),
    AVRCommand("network_numeric_9", {Zone.Z1: ["09NW", "NW"]}),
    AVRCommand("network_play", {Zone.Z1: ["10NW", "NW"]}),
    AVRCommand("network_pause", {Zone.Z1: ["11NW", "NW"]}),
    AVRCommand("network_previous", {Zone.Z1: ["12NW", "NW"]}),
    AVRCommand("network_next", {Zone.Z1: ["13NW", "NW"]}),
    AVRCommand("network_rewind", {Zone.Z1: ["14NW", "NW"]}),
    AVRCommand("network_fastforward", {Zone.Z1: ["15NW", "NW"]}),
    AVRCommand("network_display", {Zone.Z1: ["18NW", "NW"]}),
    AVRCommand("network_stop", {Zone.Z1: ["20NW", "NW"]}),
    AVRCommand("network_up", {Zone.Z1: ["26NW", "NW"]}),
    AVRCommand("network_down", {Zone.Z1: ["27NW", "NW"]}),
    AVRCommand("network_right", {Zone.Z1: ["28NW", "NW"]}),
    AVRCommand("network_left", {Zone.Z1: ["29NW", "NW"]}),
    AVRCommand("network_enter", {Zone.Z1: ["30NW", "NW"]}),
    AVRCommand("network_return", {Zone.Z1: ["31NW", "NW"]}),
    AVRCommand("network_program", {Zone.Z1: ["32NW", "NW"]}),
    AVRCommand("network_clear", {Zone.Z1: ["33NW", "NW"]}),
    AVRCommand("network_repeat", {Zone.Z1: ["34NW", "NW"]}),
    AVRCommand("network_random", {Zone.Z1: ["35NW", "NW"]}),
    AVRCommand("network_menu", {Zone.Z1: ["36NW", "NW"]}),
    AVRCommand("network_edit", {Zone.Z1: ["37NW", "NW"]}),
    AVRCommand("network_class", {Zone.Z1: ["38NW", "NW"]}),
]
EXTRA_COMMANDS_ADAPTERPORT = [  ## same as bluetooth
    AVRCommand("adapterport_play_pause", {Zone.Z1: ["20BT", "BT"]}),
    AVRCommand("adapterport_play", {Zone.Z1: ["10BT", "BT"]}),
    AVRCommand("adapterport_pause", {Zone.Z1: ["11BT", "BT"]}),
    AVRCommand("adapterport_stop", {Zone.Z1: ["12BT", "BT"]}),
    AVRCommand("adapterport_previous", {Zone.Z1: ["13BT", "BT"]}),
    AVRCommand("adapterport_next", {Zone.Z1: ["14BT", "BT"]}),
    AVRCommand("adapterport_rewind", {Zone.Z1: ["15BT", "BT"]}),
    AVRCommand("adapterport_fastforward", {Zone.Z1: ["16BT", "BT"]}),
    AVRCommand("adapterport_repeat", {Zone.Z1: ["17BT", "BT"]}),
    AVRCommand("adapterport_random", {Zone.Z1: ["18BT", "BT"]}),
    AVRCommand("adapterport_display", {Zone.Z1: ["19BT", "BT"]}),
    AVRCommand("adapterport_cursor_up", {Zone.Z1: ["21BT", "BT"]}),
    AVRCommand("adapterport_cursor_down", {Zone.Z1: ["22BT", "BT"]}),
    AVRCommand("adapterport_cursor_right", {Zone.Z1: ["23BT", "BT"]}),
    AVRCommand("adapterport_cursor_left", {Zone.Z1: ["24BT", "BT"]}),
    AVRCommand("adapterport_enter", {Zone.Z1: ["25BT", "BT"]}),
    AVRCommand("adapterport_return", {Zone.Z1: ["26BT", "BT"]}),
    AVRCommand("adapterport_top_menu", {Zone.Z1: ["27BT", "BT"]}),
    AVRCommand("adapterport_sound_retriever_air", {Zone.Z1: ["28BT", "BT"]}),
]
EXTRA_COMMANDS_BLUETOOTH = [  ## same as adapterport
    AVRCommand("bluetooth_play_pause", {Zone.Z1: ["20BT", "BT"]}),
    AVRCommand("bluetooth_play", {Zone.Z1: ["10BT", "BT"]}),
    AVRCommand("bluetooth_pause", {Zone.Z1: ["11BT", "BT"]}),
    AVRCommand("bluetooth_stop", {Zone.Z1: ["12BT", "BT"]}),
    AVRCommand("bluetooth_previous", {Zone.Z1: ["13BT", "BT"]}),
    AVRCommand("bluetooth_next", {Zone.Z1: ["14BT", "BT"]}),
    AVRCommand("bluetooth_rewind", {Zone.Z1: ["15BT", "BT"]}),
    AVRCommand("bluetooth_fastforward", {Zone.Z1: ["16BT", "BT"]}),
    AVRCommand("bluetooth_repeat", {Zone.Z1: ["17BT", "BT"]}),
    AVRCommand("bluetooth_random", {Zone.Z1: ["18BT", "BT"]}),
    AVRCommand("bluetooth_display", {Zone.Z1: ["19BT", "BT"]}),
    AVRCommand("bluetooth_cursor_up", {Zone.Z1: ["21BT", "BT"]}),
    AVRCommand("bluetooth_cursor_down", {Zone.Z1: ["22BT", "BT"]}),
    AVRCommand("bluetooth_cursor_right", {Zone.Z1: ["23BT", "BT"]}),
    AVRCommand("bluetooth_cursor_left", {Zone.Z1: ["24BT", "BT"]}),
    AVRCommand("bluetooth_enter", {Zone.Z1: ["25BT", "BT"]}),
    AVRCommand("bluetooth_return", {Zone.Z1: ["26BT", "BT"]}),
    AVRCommand("bluetooth_top_menu", {Zone.Z1: ["27BT", "BT"]}),
    AVRCommand("bluetooth_sound_retriever_air", {Zone.Z1: ["28BT", "BT"]}),
]
EXTRA_COMMANDS_MHL = [
    AVRCommand("mhl_select", {Zone.Z1: ["00MHL", "MHL"]}),
    AVRCommand("mhl_up", {Zone.Z1: ["01MHL", "MHL"]}),
    AVRCommand("mhl_down", {Zone.Z1: ["02MHL", "MHL"]}),
    AVRCommand("mhl_left", {Zone.Z1: ["03MHL", "MHL"]}),
    AVRCommand("mhl_right", {Zone.Z1: ["04MHL", "MHL"]}),
    AVRCommand("mhl_root_menu", {Zone.Z1: ["05MHL", "MHL"]}),
    AVRCommand("mhl_exit", {Zone.Z1: ["06MHL", "MHL"]}),
    AVRCommand("mhl_numeric_0", {Zone.Z1: ["07MHL", "MHL"]}),
    AVRCommand("mhl_numeric_1", {Zone.Z1: ["08MHL", "MHL"]}),
    AVRCommand("mhl_numeric_2", {Zone.Z1: ["09MHL", "MHL"]}),
    AVRCommand("mhl_numeric_3", {Zone.Z1: ["10MHL", "MHL"]}),
    AVRCommand("mhl_numeric_4", {Zone.Z1: ["11MHL", "MHL"]}),
    AVRCommand("mhl_numeric_5", {Zone.Z1: ["12MHL", "MHL"]}),
    AVRCommand("mhl_numeric_6", {Zone.Z1: ["13MHL", "MHL"]}),
    AVRCommand("mhl_numeric_7", {Zone.Z1: ["14MHL", "MHL"]}),
    AVRCommand("mhl_numeric_8", {Zone.Z1: ["15MHL", "MHL"]}),
    AVRCommand("mhl_numeric_9", {Zone.Z1: ["16MHL", "MHL"]}),
    AVRCommand("mhl_enter", {Zone.Z1: ["17MHL", "MHL"]}),
    AVRCommand("mhl_clear", {Zone.Z1: ["18MHL", "MHL"]}),
    AVRCommand("mhl_channel_up", {Zone.Z1: ["19MHL", "MHL"]}),
    AVRCommand("mhl_channel_down", {Zone.Z1: ["20MHL", "MHL"]}),
    AVRCommand("mhl_previous_channel", {Zone.Z1: ["21MHL", "MHL"]}),
    AVRCommand("mhl_sound_select", {Zone.Z1: ["22MHL", "MHL"]}),
    AVRCommand("mhl_play", {Zone.Z1: ["23MHL", "MHL"]}),
    AVRCommand("mhl_stop", {Zone.Z1: ["24MHL", "MHL"]}),
    AVRCommand("mhl_pause", {Zone.Z1: ["25MHL", "MHL"]}),
    AVRCommand("mhl_record", {Zone.Z1: ["26MHL", "MHL"]}),
    AVRCommand("mhl_rewind", {Zone.Z1: ["27MHL", "MHL"]}),
    AVRCommand("mhl_fastforward", {Zone.Z1: ["28MHL", "MHL"]}),
    AVRCommand("mhl_eject", {Zone.Z1: ["29MHL", "MHL"]}),
    AVRCommand("mhl_next", {Zone.Z1: ["30MHL", "MHL"]}),
    AVRCommand("mhl_previous", {Zone.Z1: ["31MHL", "MHL"]}),
    AVRCommand("mhl_play_function", {Zone.Z1: ["32MHL", "MHL"]}),
    AVRCommand("mhl_pause_play_function", {Zone.Z1: ["33MHL", "MHL"]}),
    AVRCommand("mhl_record_function", {Zone.Z1: ["34MHL", "MHL"]}),
    AVRCommand("mhl_pause_record_function", {Zone.Z1: ["35MHL", "MHL"]}),
    AVRCommand("mhl_stop_function", {Zone.Z1: ["36MHL", "MHL"]}),
    AVRCommand("mhl_show_information", {Zone.Z1: ["37MHL", "MHL"]}),
]

PROPERTY_REGISTRY = AVRPropertyRegistry(
    PROPERTIES_AMP
    + PROPERTIES_SYSTEM
    + PROPERTIES_DSP
    + PROPERTIES_AUDIO
    + PROPERTIES_TUNER
    + PROPERTIES_VIDEO,
    extra_commands=EXTRA_COMMANDS_AMP
    + EXTRA_COMMANDS_TUNER
    + EXTRA_COMMANDS_IPOD
    + EXTRA_COMMANDS_NETWORK
    + EXTRA_COMMANDS_ADAPTERPORT
    + EXTRA_COMMANDS_BLUETOOTH
    + EXTRA_COMMANDS_MHL,
)


def get_property_entry(code_map: type[CodeMapBase]) -> AVRPropertyEntry:
    """Return property entry for code map."""
    return PROPERTY_REGISTRY.code_map_index[code_map]


def get_code_maps(
    base_class: type[CodeMapBase], zone: Zone = None, is_ha_auto_entity: bool = False
) -> list[type[CodeMapBase]]:
    """Convenience function to return property entries matching a CodeMapBase subclass."""
    return PROPERTY_REGISTRY.get_code_maps(
        base_class=base_class, zone=zone, is_ha_auto_entity=is_ha_auto_entity
    )
