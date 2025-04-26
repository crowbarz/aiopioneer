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
from ..property_entry import AVRCommand, gen_query_property, gen_set_property
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
                    CommandItem(
                        "_delayed_refresh_zone",
                        zone,
                        queue_id=2,
                        skip_if_refreshing=True,
                    ),
                )
            if properties.power.get(zone) is not False:  ## zone is not off
                return []

            if zone is Zone.Z1 and params.get_param(PARAM_POWER_ON_VOLUME_BOUNCE):
                _LOGGER.info("queueing volume workaround for Main Zone")
                ## NOTE: volume bounce queues ahead of refresh
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
            return cls.index_map_class.value_to_code(
                value=properties.source_name_to_id[value]
            )
        if isinstance(value, int):
            return cls.index_map_class.value_to_code(value=value)
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


PROPERTIES_AMP = [
    gen_query_property(
        Power,
        {Zone.Z1: "P", Zone.Z2: "AP", Zone.Z3: "BP", Zone.HDZ: "ZEP"},
        {Zone.Z1: "PWR", Zone.Z2: "APR", Zone.Z3: "BPR", Zone.HDZ: "ZEP"},
        extra_commands=[
            AVRCommand(
                "power_on",
                {Zone.Z1: "PO", Zone.Z2: "APO", Zone.Z3: "BPO", Zone.HDZ: "ZEO"},
                wait_for_response=True,
                retry_on_fail=True,
            ),
            AVRCommand(
                "power_off",
                {Zone.Z1: "PF", Zone.Z2: "APF", Zone.Z3: "BPF", Zone.HDZ: "ZEF"},
                wait_for_response=True,
                retry_on_fail=True,
            ),
        ],
    ),
    gen_set_property(
        Volume,
        {Zone.Z1: "V", Zone.Z2: "ZV", Zone.Z3: "YV", Zone.HDZ: "HZV"},
        {Zone.Z1: "VOL", Zone.Z2: "ZV", Zone.Z3: "YV", Zone.HDZ: "XV"},
        set_command=AVRCommand(
            "set_volume_level",
            {Zone.Z1: "VL", Zone.Z2: "ZV", Zone.Z3: "YV", Zone.HDZ: "HZV"},
            wait_for_response=True,
            retry_on_fail=True,
        ),
        extra_commands=[
            AVRCommand(
                "volume_up",
                {Zone.Z1: "VU", Zone.Z2: "ZU", Zone.Z3: "YU", Zone.HDZ: "HZU"},
                wait_for_response=True,
            ),
            AVRCommand(
                "volume_down",
                {Zone.Z1: "VD", Zone.Z2: "ZD", Zone.Z3: "YD", Zone.HDZ: "HZD"},
                wait_for_response=True,
            ),
        ],
    ),
    gen_set_property(
        Source,
        {Zone.Z1: "F", Zone.Z2: "ZS", Zone.Z3: "ZT", Zone.HDZ: "ZEA"},
        {Zone.Z1: "FN", Zone.Z2: "Z2F", Zone.Z3: "Z3F", Zone.HDZ: "ZEA"},
        query_command="query_source",
        set_command=AVRCommand(
            "select_source",
            {Zone.Z1: "FN", Zone.Z2: "ZS", Zone.Z3: "ZT", Zone.HDZ: "ZEA"},
            wait_for_response=True,
            retry_on_fail=True,
        ),
    ),
    gen_query_property(
        Mute,
        {Zone.Z1: "M", Zone.Z2: "Z2M", Zone.Z3: "Z3M", Zone.HDZ: "HZM"},
        {Zone.Z1: "MUT", Zone.Z2: "Z2MUT", Zone.Z3: "Z3MUT", Zone.HDZ: "HZMUT"},
        extra_commands=[
            AVRCommand(
                "mute_on",
                {Zone.Z1: "MO", Zone.Z2: "Z2MO", Zone.Z3: "Z3MO", Zone.HDZ: "HZMO"},
                wait_for_response=True,
                retry_on_fail=True,
            ),
            AVRCommand(
                "mute_off",
                {Zone.Z1: "MF", Zone.Z2: "Z2MF", Zone.Z3: "Z3MF", Zone.HDZ: "HZMF"},
                wait_for_response=True,
                retry_on_fail=True,
            ),
        ],
    ),
    gen_set_property(
        SourceName,
        {Zone.ALL: "RGB"},
        query_command=AVRCommand(
            avr_args=[CodeMapBlank(), SourceId],
            is_query_command=True,
            wait_for_response=True,
        ),
        set_command=AVRCommand(
            avr_commands={Zone.Z1: "1RGB"},
            avr_args=[SourceName, SourceId],
            wait_for_response=True,
        ),
        extra_commands=[
            AVRCommand(
                "set_default_source_name",
                {Zone.Z1: "0RGB"},
                [CodeMapBlank(), SourceId],
                wait_for_response=True,
                retry_on_fail=True,
            )
        ],
    ),
    gen_set_property(SpeakerMode, {Zone.ALL: "SPK"}),
    gen_set_property(HdmiOut, {Zone.ALL: "HO"}),
    gen_set_property(Hdmi3Out, {Zone.ALL: "HDO"}),
    gen_set_property(HdmiAudio, {Zone.ALL: "HA"}),
    gen_set_property(Pqls, {Zone.ALL: "PQ"}),
    gen_query_property(
        DisplayText, {Zone.ALL: "FL"}, query_command="query_display_information"
    ),
    gen_set_property(Dimmer, {Zone.ALL: "SAA"}, query_command=None),
    ## NOTE: no dimmer query
    gen_set_property(SleepTime, {Zone.ALL: "SAB"}),
    gen_set_property(AmpMode, {Zone.ALL: "SAC"}),
    gen_set_property(PanelLock, {Zone.ALL: "PKL"}),
    gen_set_property(RemoteLock, {Zone.ALL: "RML"}),
    gen_query_property(
        SystemMacAddress, {Zone.ALL: "SVB"}, query_command="system_query_mac_addr"
    ),
    gen_query_property(SystemAvrModel, {Zone.ALL: "RGD"}, query_command="query_model"),
    gen_query_property(
        SystemSoftwareVersion,
        {Zone.ALL: "SSI"},
        query_command="system_query_software_version",
    ),
    # gen_response_property(AudioParameterProhibition, {Zone.Z1: "AUA"}),
    # gen_response_property(AudioParameterWorking, {Zone.Z1: "AUB"}),
]

EXTRA_COMMANDS_AMP = [
    AVRCommand("amp_status_display", {Zone.Z1: "STS"}),
    AVRCommand("amp_cursor_up", {Zone.Z1: "CUP"}),
    AVRCommand("amp_cursor_down", {Zone.Z1: "CDN"}),
    AVRCommand("amp_cursor_right", {Zone.Z1: "CRI"}),
    AVRCommand("amp_cursor_left", {Zone.Z1: "CLE"}),
    AVRCommand("amp_cursor_enter", {Zone.Z1: "CEN"}),
    AVRCommand("amp_cursor_return", {Zone.Z1: "CRT"}),
    AVRCommand("amp_audio_parameter", {Zone.Z1: "ATA"}),
    AVRCommand("amp_output_parameter", {Zone.Z1: "HPA"}),
    AVRCommand("amp_video_parameter", {Zone.Z1: "VPA"}),
    AVRCommand("amp_channel_select", {Zone.Z1: "CLC"}),
    AVRCommand("amp_home_menu", {Zone.Z1: "HM"}),
    AVRCommand("amp_key_off", {Zone.Z1: "KOF"}),
]
