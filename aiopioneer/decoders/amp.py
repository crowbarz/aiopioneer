"""aiopioneer response decoders for amp responses."""

import argparse
import logging
import re

from ..command_queue import CommandItem
from ..const import MEDIA_CONTROL_SOURCES, Zone
from ..params import (
    AVRParams,
    PARAM_MHL_SOURCE,
    PARAM_POWER_ON_VOLUME_BOUNCE,
)
from ..properties import AVRProperties
from .code_map import (
    CodeMapBlank,
    CodeMapHasPropertyMixin,
    CodeBoolMap,
    CodeStrMap,
    CodeInverseBoolMap,
    CodeDynamicDictStrMap,
    CodeDictStrMap,
    CodeIntMap,
)
from .response import Response

_LOGGER = logging.getLogger(__name__)


class Power(CodeInverseBoolMap):
    """Zone power status."""

    friendly_name = "zone power"
    base_property = "power"

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for zone power status."""

        def power_on(response: Response) -> list[Response]:
            """Power on."""
            zone = response.zone
            properties = response.properties

            queue_commands = [
                CommandItem("_delayed_query_basic", 2.5, queue_id=3),
            ]
            if zone not in properties.zones_initial_refresh:
                _LOGGER.info("queueing initial refresh for %s", zone.full_name)
                queue_commands.append(
                    CommandItem("_delayed_refresh_zone", zone, queue_id=2),
                )
            elif properties.power.get(zone):  ## zone is already on
                return []

            if zone is Zone.Z1 and params.get_param(PARAM_POWER_ON_VOLUME_BOUNCE):
                _LOGGER.info("queueing volume workaround for Main Zone")
                ## NOTE: volume bounce queues before refresh
                queue_commands.extend(
                    [
                        CommandItem("volume_up", queue_id=0, skip_if_queued=False),
                        CommandItem("volume_down", queue_id=0, skip_if_queued=False),
                    ]
                )

            response.update(queue_commands=queue_commands)
            return [response]

        def power_off(response: Response) -> list[Response]:
            """Power off."""
            zone = response.zone
            properties = response.properties
            if properties.power.get(zone) is False:  ## zone is already off
                return []
            response.update(
                queue_commands=[CommandItem("_delayed_query_basic", 4.5, queue_id=3)]
            )
            return [response]

        super().decode_response(response=response, params=params)
        if not response.properties.command_queue.is_starting():
            if response.value:
                response.update(callback=power_on)
            else:
                response.update(callback=power_off)
        response.update(update_zones={Zone.ALL})
        return [response]


class Volume(CodeIntMap):
    """Zone volume. (1step = 0.5dB for Main Zone, 1step = 1.0dB for other zones)"""

    friendly_name = "volume"
    base_property = "volume"
    value_min = 0
    # value_max: 185 for Main Zone, 81 for other Zones

    @classmethod
    def value_to_code(
        cls, value: str, zone: Zone = None, properties: AVRProperties = None
    ) -> str:
        if not isinstance(zone, Zone):
            raise RuntimeError(f"Zone required for {cls.get_name()}")
        if not isinstance(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        if (value_max := properties.max_volume.get(zone)) is None:
            raise ValueError(f"volume for {zone.full_name} is not available")
        code = cls.value_to_code_bounded(value=value, value_max=value_max)
        return code.zfill(3 if zone is Zone.Z1 else 2)

    @classmethod
    def parse_args(
        cls,
        command: str,  # pylint: disable=unused-argument
        args: list,
        zone: Zone,
        params: AVRParams,  # pylint: disable=unused-argument
        properties: AVRProperties,
    ) -> str:
        cls.check_args(args)
        return cls.value_to_code(value=args[0], zone=zone, properties=properties)


class SourceId(CodeIntMap):
    """Source ID."""

    friendly_name = "source ID"
    base_property = "source_id"  # unused

    code_zfill = 2
    value_min = 0
    value_max = 99

    @classmethod
    def value_to_code(cls, value: str | int):
        if isinstance(value, str):
            value = int(value)
        return super().value_to_code(value=value)


class SourceName(CodeStrMap):
    """Source name."""

    friendly_name = "source name"
    base_property = "source_name"  # unused

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for source name."""

        if not response.properties.query_sources:
            ## Only update AVR source mappings if AVR sources are being queried
            return []

        def clear_source_id(response: Response) -> list[Response]:
            """Clear source ID before applying new source ID mapping."""
            properties = response.properties
            source_name = None
            if (source_id := response.value) in properties.source_id_to_name:
                source_name = properties.source_id_to_name[source_id]
                properties.source_id_to_name.pop(source_id)
            if source_name in properties.source_name_to_id:
                properties.source_name_to_id.pop(source_name)
            return []

        super().decode_response(response=response, params=params)
        source_id, source_name = response.value
        return [
            response.clone(callback=clear_source_id, value=source_id),
            response.clone(
                base_property="source_name_to_id",
                property_name=source_name,
                value=source_id,
            ),
            response.clone(
                base_property="source_id_to_name",
                property_name=source_id,
                value=source_name,
            ),
        ]

    @classmethod
    def value_to_code(cls, value: str) -> str:
        if len(value) > 14:
            raise ValueError(f"source name {value} is longer than 14 characters")
        return value

    @classmethod
    def code_to_value(cls, code: str) -> tuple[str, str]:
        return SourceId.code_to_value(code[:2]), code[3:]  ## NOTE: [2] ignored


class Source(CodeDynamicDictStrMap):
    """Zone source."""

    friendly_name = "source"
    base_property = "source_name"

    index_map_class = SourceId

    @classmethod
    def get_parser(cls, parser: argparse.ArgumentParser) -> None:

        def convert_source_arg(arg: str) -> int | str:
            try:
                SourceId.value_to_code(arg)  ## type and bounds check source ID
                return int(arg)
            except ValueError:
                return arg

        parser.add_argument("source", help=cls.friendly_name, type=convert_source_arg)

    @classmethod
    def code_to_value_dynamic(cls, code: str, code_map: dict[int, str]) -> str:
        try:
            return super().code_to_value_dynamic(code=code, code_map=code_map)
        except KeyError:
            return code  ## if no mapping

    @classmethod
    def value_to_code(cls, value: str | int, properties: AVRProperties = None) -> str:
        if not isinstance(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        if isinstance(value, str) and value in properties.source_name_to_id:
            return cls.index_map_class(value=properties.source_name_to_id[value])
        if isinstance(value, int):
            return cls.index_map_class(value=value)
        raise ValueError(f"value {value} not found for {cls.get_name()}")

    @classmethod
    def code_to_value(cls, code: str, properties: AVRProperties = None) -> str:
        if not isinstance(properties, AVRProperties):
            raise RuntimeError(f"AVRProperties required for {cls.get_name()}")
        return cls.code_to_value_dynamic(code, code_map=properties.source_id_to_name)

    @classmethod
    def parse_args(
        cls,
        command: str,
        args: list,
        zone: Zone,  # pylint: disable=unused-argument
        params: AVRParams,  # pylint: disable=unused-argument
        properties: AVRProperties,
    ) -> str:
        cls.check_args(args)
        return cls.value_to_code(value=args[0], properties=properties)

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for listening mode."""
        cls.decode_response_dynamic(
            response=response,
            params=params,
            code_map=response.properties.source_id_to_name,
        )
        source_id = cls.index_map_class.code_to_value(code=response.code)
        queue_commands = []
        if response.properties.is_source_tuner(source_id):
            queue_commands.extend(
                [
                    CommandItem("query_tuner_frequency"),
                    CommandItem("query_tuner_preset"),
                ]
            )
        queue_commands.append(CommandItem("_delayed_query_basic", 2.5, queue_id=3))
        if source_id in MEDIA_CONTROL_SOURCES:
            media_control_mode = MEDIA_CONTROL_SOURCES.get(source_id)
        elif source_id == params.get_param(PARAM_MHL_SOURCE):
            media_control_mode = "MHL"
        else:
            media_control_mode = None

        return [
            response,
            response.clone(
                base_property="source_id",
                value=source_id,
                update_zones={Zone.ALL},
                queue_commands=queue_commands,
            ),
            response.clone(
                base_property="media_control_mode",
                inherit_value=False,
                value=media_control_mode,
            ),
        ]


class Mute(CodeInverseBoolMap):
    """Mute."""

    friendly_name = "mute"
    base_property = "mute"


class SpeakerMode(CodeMapHasPropertyMixin, CodeDictStrMap):
    """Speaker mode."""

    friendly_name = "speaker mode"
    base_property = "amp"
    property_name = "speaker_mode"

    code_map = {"0": "off", "1": "A", "2": "B", "3": "A+B"}


class HdmiOut(CodeMapHasPropertyMixin, CodeDictStrMap):
    """HDMI out."""

    friendly_name = "HDMI out"
    base_property = "amp"
    property_name = "hdmi_out"

    code_map = {"0": "all", "1": "HDMI 1", "2": "HDMI 2"}


class Hdmi3Out(CodeMapHasPropertyMixin, CodeBoolMap):
    """HDMI3 out."""

    friendly_name = "HDMI3 out"
    base_property = "amp"
    property_name = "hdmi3_out"

    code_true = "1"
    code_false = "3"


class HdmiAudio(CodeMapHasPropertyMixin, CodeDictStrMap):
    """HDMI audio."""

    friendly_name = "HDMI audio"
    base_property = "amp"
    property_name = "hdmi_audio"

    code_map = {"0": "amp", "1": "passthrough"}


class Pqls(CodeMapHasPropertyMixin, CodeDictStrMap):
    """PQLS."""

    friendly_name = "PQLS"
    base_property = "amp"
    property_name = "pqls"

    code_map = {"0": "off", "1": "auto"}


class DisplayText(CodeStrMap):
    """Display text."""

    friendly_name = "display text"
    base_property = "amp"
    property_name = "display"

    ## NOTE: value_to_code not implemented

    @classmethod
    def code_to_value(cls, code: str) -> str:
        """Convert code to value."""
        return (
            "".join([chr(int(code[i : i + 2], 16)) for i in range(2, len(code) - 1, 2)])
            .expandtabs(1)
            .strip()
        )


class Dimmer(CodeDictStrMap):
    """Dimmer."""

    friendly_name = "dimmer"
    base_property = "amp"
    property_name = "dimmer"

    code_map = {
        "0": "brightest",
        "1": "bright",
        "2": "dark",
        "3": "off",
    }


class SleepTime(CodeIntMap):
    """Sleep time remaining."""

    friendly_name = "sleep time"
    base_property = "amp"
    property_name = "sleep_time"

    value_min = 0
    value_max = 90
    value_step = 30
    code_zfill = 3


class AmpMode(CodeMapHasPropertyMixin, CodeDictStrMap):
    """AMP status."""

    friendly_name = "AMP status"
    base_property = "amp"
    property_name = "mode"

    code_map = {
        "0": "amp on",
        "1": "amp front off",
        "2": "amp front & center off",
        "3": "amp off",
    }


class PanelLock(CodeDictStrMap):
    """Panel lock."""

    friendly_name = "panel lock"
    base_property = "amp"
    property_name = "panel_lock"

    code_map = {"0": "off", "1": "panel only", "2": "panel + volume"}


class RemoteLock(CodeBoolMap):
    """Remote lock."""

    friendly_name = "remote lock"
    base_property = "amp"
    property_name = "remote_lock"


class SystemMacAddress(CodeStrMap):
    """System MAC address."""

    friendly_name = "system MAC address"
    base_property = "amp"
    property_name = "mac_addr"

    ## NOTE: value_to_code not implemented

    @classmethod
    def code_to_value(cls, code: str) -> str:
        return ":".join([code[i : i + 2] for i in range(0, len(code), 2)])


class SystemAvrModel(CodeStrMap):
    """System AVR model."""

    friendly_name = "system AVR model"
    base_property = "amp"
    property_name = "model"
    ## NOTE: value_to_code not implemented

    @classmethod
    def code_to_value(cls, code: str) -> str:
        value = "unknown"
        if matches := re.search(r"<([^>/]{5,})(/.[^>]*)?>", code):
            value = matches.group(1)
        return value


class SystemSoftwareVersion(CodeStrMap):
    """System software version."""

    friendly_name = "system software version"
    base_property = "amp"
    property_name = "software_version"

    ## NOTE: value_to_code not implemented

    @classmethod
    def code_to_value(cls, code: str) -> str:
        value = "unknown"
        if matches := re.search(r'"([^)]*)"', code):
            value = matches.group(1)
        return value


class AudioParameterProhibition(CodeStrMap):
    """Audio parameter prohibition."""

    friendly_name = "audio parameter prohibition"

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for audio parameter prohibition."""
        response.update(
            queue_commands=[CommandItem("_delayed_query_basic", 2.5, queue_id=3)]
        )
        return [response]


class AudioParameterWorking(CodeStrMap):
    """Audio parameter working."""

    friendly_name = "audio parameter working"

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for audio parameter working."""
        response.update(
            queue_commands=[CommandItem("_delayed_query_basic", 2.5, queue_id=3)]
        )
        return [response]


COMMANDS_AMP = {
    "power_on": {
        Zone.Z1: ["PO", "PWR"],
        Zone.Z2: ["APO", "APR"],
        Zone.Z3: ["BPO", "BPR"],
        Zone.HDZ: ["ZEO", "ZEP"],
        "retry_on_fail": True,
    },
    "power_off": {
        Zone.Z1: ["PF", "PWR"],
        Zone.Z2: ["APF", "APR"],
        Zone.Z3: ["BPF", "BPR"],
        Zone.HDZ: ["ZEF", "ZEP"],
        "retry_on_fail": True,
    },
    "select_source": {
        Zone.Z1: ["FN", "FN"],
        Zone.Z2: ["ZS", "Z2F"],
        Zone.Z3: ["ZT", "Z3F"],
        Zone.HDZ: ["ZEA", "ZEA"],
        "args": [Source],
        "retry_on_fail": True,
    },
    "volume_up": {
        Zone.Z1: ["VU", "VOL"],
        Zone.Z2: ["ZU", "ZV"],
        Zone.Z3: ["YU", "YV"],
        Zone.HDZ: ["HZU", "XV"],
    },
    "volume_down": {
        Zone.Z1: ["VD", "VOL"],
        Zone.Z2: ["ZD", "ZV"],
        Zone.Z3: ["YD", "YV"],
        Zone.HDZ: ["HZD", "XV"],
    },
    "set_volume_level": {
        Zone.Z1: ["VL", "VOL"],
        Zone.Z2: ["ZV", "ZV"],
        Zone.Z3: ["YV", "YV"],
        Zone.HDZ: ["HZV", "XV"],
        "args": [Volume],
        "retry_on_fail": True,
    },
    "mute_on": {
        Zone.Z1: ["MO", "MUT"],
        Zone.Z2: ["Z2MO", "Z2MUT"],
        Zone.Z3: ["Z3MO", "Z3MUT"],
        Zone.HDZ: ["HZMO", "HZMUT"],
        "retry_on_fail": True,
    },
    "mute_off": {
        Zone.Z1: ["MF", "MUT"],
        Zone.Z2: ["Z2MF", "Z2MUT"],
        Zone.Z3: ["Z3MF", "Z3MUT"],
        Zone.HDZ: ["HZMF", "HZMUT"],
        "retry_on_fail": True,
    },
    "query_power": {
        Zone.Z1: ["?P", "PWR"],
        Zone.Z2: ["?AP", "APR"],
        Zone.Z3: ["?BP", "BPR"],
        Zone.HDZ: ["?ZEP", "ZEP"],
    },
    "query_volume": {
        Zone.Z1: ["?V", "VOL"],
        Zone.Z2: ["?ZV", "ZV"],
        Zone.Z3: ["?YV", "YV"],
        Zone.HDZ: ["?HZV", "XV"],
    },
    "query_mute": {
        Zone.Z1: ["?M", "MUT"],
        Zone.Z2: ["?Z2M", "Z2MUT"],
        Zone.Z3: ["?Z3M", "Z3MUT"],
        Zone.HDZ: ["?HZM", "HZMUT"],
    },
    "query_source": {
        Zone.Z1: ["?F", "FN"],
        Zone.Z2: ["?ZS", "Z2F"],
        Zone.Z3: ["?ZT", "Z3F"],
        Zone.HDZ: ["?ZEA", "ZEA"],
    },
    "query_model": {Zone.Z1: ["?RGD", "RGD"]},
    "system_query_mac_addr": {Zone.Z1: ["?SVB", "SVB"]},
    "system_query_software_version": {Zone.Z1: ["?SSI", "SSI"]},
    "query_source_name": {Zone.Z1: ["?RGB", "RGB"], "args": [CodeMapBlank(), SourceId]},
    "set_source_name": {Zone.Z1: ["1RGB", "RGB"], "args": [SourceName, SourceId]},
    "set_default_source_name": {
        Zone.Z1: ["0RGB", "RGB"],
        "args": [CodeMapBlank(), SourceId],
        "retry_on_fail": True,
    },
    "query_amp_speaker_mode": {Zone.Z1: ["?SPK", "SPK"]},
    "set_amp_speaker_mode": {
        Zone.Z1: ["SPK", "SPK"],
        "args": [SpeakerMode],
        "retry_on_fail": True,
    },
    "query_amp_hdmi_out": {Zone.Z1: ["?HO", "HO"]},
    "set_amp_hdmi_out": {
        Zone.Z1: ["HO", "HO"],
        "args": [HdmiOut],
        "retry_on_fail": True,
    },
    "query_amp_hdmi3_out": {Zone.Z1: ["?HDO", "HDO"]},
    "set_amp_hdmi3_out": {
        Zone.Z1: ["HDO", "HDO"],
        "args": [Hdmi3Out],
        "retry_on_fail": True,
    },
    "query_amp_hdmi_audio": {Zone.Z1: ["?HA", "HA"]},
    "set_amp_hdmi_audio": {
        Zone.Z1: ["HA", "HA"],
        "args": [HdmiAudio],
        "retry_on_fail": True,
    },
    "query_amp_pqls": {Zone.Z1: ["?PQ", "PQ"]},
    "set_amp_pqls": {Zone.Z1: ["PQ", "PQ"], "args": [Pqls], "retry_on_fail": True},
    "set_amp_dimmer": {
        Zone.Z1: ["SAA", "SAA"],
        "args": [Dimmer],
        "retry_on_fail": True,
    },
    ## NOTE: no amp dimmer query command
    "query_amp_sleep_time": {Zone.Z1: ["?SAB", "SAB"]},
    "set_amp_sleep_time": {
        Zone.Z1: ["SAB", "SAB"],
        "args": [SleepTime],
        "retry_on_fail": True,
    },
    "query_amp_mode": {Zone.Z1: ["?SAC", "SAC"]},
    "set_amp_mode": {Zone.Z1: ["SAC", "SAC"], "args": [AmpMode], "retry_on_fail": True},
    "query_amp_panel_lock": {Zone.Z1: ["?PKL", "PKL"]},
    "set_amp_panel_lock": {
        Zone.Z1: ["PKL", "PKL"],
        "args": [PanelLock],
        "retry_on_fail": True,
    },
    "query_amp_remote_lock": {Zone.Z1: ["?RML", "RML"]},
    "set_amp_remote_lock": {
        Zone.Z1: ["RML", "RML"],
        "args": [RemoteLock],
        "retry_on_fail": True,
    },
    "query_display_information": {Zone.Z1: ["?FL", "FL"]},
    "amp_status_display": {Zone.Z1: "STS"},
    "amp_cursor_up": {Zone.Z1: "CUP"},
    "amp_cursor_down": {Zone.Z1: "CDN"},
    "amp_cursor_right": {Zone.Z1: "CRI"},
    "amp_cursor_left": {Zone.Z1: "CLE"},
    "amp_cursor_enter": {Zone.Z1: "CEN"},
    "amp_cursor_return": {Zone.Z1: "CRT"},
    "amp_audio_parameter": {Zone.Z1: "ATA"},
    "amp_output_parameter": {Zone.Z1: "HPA"},
    "amp_video_parameter": {Zone.Z1: "VPA"},
    "amp_channel_select": {Zone.Z1: "CLC"},
    "amp_home_menu": {Zone.Z1: "HM"},
    "amp_key_off": {Zone.Z1: "KOF"},
}

RESPONSE_DATA_AMP = [
    ("PWR", Power, Zone.Z1),  # power
    ("APR", Power, Zone.Z2),  # power
    ("BPR", Power, Zone.Z3),  # power
    ("ZEP", Power, Zone.HDZ),  # power
    ("VOL", Volume, Zone.Z1),  # volume
    ("ZV", Volume, Zone.Z2),  # volume
    ("YV", Volume, Zone.Z3),  # volume
    ("XV", Volume, Zone.HDZ),  # volume
    ("FN", Source, Zone.Z1),  # source_name, source_id
    ("Z2F", Source, Zone.Z2),  # source_name, source_id
    ("Z3F", Source, Zone.Z3),  # source_name, source_id
    ("ZEA", Source, Zone.HDZ),  # source_name, source_id
    ("RGB", SourceName, Zone.ALL),  # source_name_to_id, source_id_to_name
    ("MUT", Mute, Zone.Z1),  # mute
    ("Z2MUT", Mute, Zone.Z2),  # mute
    ("Z3MUT", Mute, Zone.Z3),  # mute
    ("HZMUT", Mute, Zone.HDZ),  # mute
    ("SPK", SpeakerMode, Zone.ALL),  # amp.speaker_mode
    ("HO", HdmiOut, Zone.ALL),  # amp.hdmi_out
    ("HDO", Hdmi3Out, Zone.ALL),  # amp.hdmi3_out
    ("HA", HdmiAudio, Zone.ALL),  # amp.hdmi_audio
    ("PQ", Pqls, Zone.ALL),  # amp.pqls
    ("FL", DisplayText, Zone.ALL),  # amp.display
    ("SAA", Dimmer, Zone.ALL),  # amp.dimmer
    ("SAB", SleepTime, Zone.ALL),  # amp.sleep_time
    ("SAC", AmpMode, Zone.ALL),  # amp.mode
    ("PKL", PanelLock, Zone.ALL),  # amp.panel_lock
    ("RML", RemoteLock, Zone.ALL),  # amp.remote_lock
    ("SVB", SystemMacAddress, Zone.ALL),  # amp.mac_addr
    ("RGD", SystemAvrModel, Zone.ALL),  # amp.model
    ("SSI", SystemSoftwareVersion, Zone.ALL),  # amp.software_version
    ("AUA", AudioParameterProhibition, Zone.Z1),
    ("AUB", AudioParameterWorking, Zone.Z1),
]
