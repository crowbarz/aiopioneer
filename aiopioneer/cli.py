"""CLI for Pioneer AVR asyncio API."""

import asyncio
import logging
import sys
import json
import argparse
from collections.abc import Callable
from typing import Any

import aioconsole
import yaml

from aiopioneer import PioneerAVR
from aiopioneer.commands import PIONEER_COMMANDS
from aiopioneer.const import Zone, DEFAULT_PORT, TunerBand
from aiopioneer.decoders.code_map import CodeMapBase
from aiopioneer.params import (
    PARAM_DEBUG_LISTENER,
    PARAM_DEBUG_UPDATER,
    PARAM_DEBUG_COMMAND,
    PARAM_DEBUG_COMMAND_QUEUE,
    PARAMS_DICT_INT_KEY,
)

_LOGGER = logging.getLogger(__name__)

LOGGING_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

PROPS_ALL = [
    "zones",
    # "zones_initial_refresh",
    "power",
    "volume",
    "max_volume",
    "mute",
    "source_id",
    "source_name",
    # "listening_mode",
    # "listening_mode_id",
    # "listening_modes_all",
    # "available_listening_modes",
    "media_control_mode",
    "tone",
    "amp",
    "tuner",
    "dsp",
    "video",
    "system",
    "audio",
    "channel_levels",
]


# pylint: disable=unused-argument
class PioneerAVRCli(aioconsole.AsynchronousCli):
    """Pioneer AVR CLI class."""

    def __init__(self, pioneer: PioneerAVR):
        super().__init__(commands=self.get_commands(), prog="aiopioneer")

        self.pioneer = pioneer
        self.zone = Zone.Z1

    def get_default_banner(self):
        return ""

    @staticmethod
    def convert_bool_arg(arg: str) -> bool:
        """Convert an arg to a bool."""
        valid_args = (["on", "true"], ["off", "false"])
        valid_args_all = [k for l in valid_args for k in l]
        if (argl := arg.lower()) not in valid_args_all:
            raise ValueError("")
        return argl in valid_args[0]

    @staticmethod
    def dump(obj, flow_style: bool = False) -> str:
        """Dump an object to YAML."""
        return yaml.dump(obj, sort_keys=False, default_flow_style=flow_style)

    async def connect(self, reader, writer, reconnect: bool):
        """Connect to AVR."""
        return await self.pioneer.connect(reconnect=reconnect)

    async def disconnect(self, reader, writer, reconnect: bool):
        """Connect to AVR."""
        return await self.pioneer.disconnect(reconnect=reconnect)

    async def set_zone(self, reader, writer, zone: Zone):
        """Set AVR active zone."""
        self.zone = zone

    async def set_logging_level(self, reader=None, writer=None, level: str = "debug"):
        """Set root logging level."""
        logging.getLogger().setLevel(LOGGING_LEVELS.get(level))
        return self.dump({"logging_level": level})

    async def get_params(self, reader, writer) -> str:
        """Get active parameters."""
        return self.dump(self.pioneer.params.params_all)

    async def get_user_params(self, reader, writer) -> str:
        """Get user parameters."""
        return self.dump(self.pioneer.params.user_params)

    async def set_user_params(self, reader, writer, params: dict) -> str:
        """Set user parameters."""
        return self.pioneer.params.set_user_params(params)

    async def get_properties(self, reader, writer, prop_show: list[str] = None) -> str:
        """Get cached properties."""

        def scrub_property(prop):
            if isinstance(prop, (set, list)):
                return list(scrub_property(v) for v in prop)
            if isinstance(prop, dict):
                return {scrub_property(k): v for k, v in prop.items()}
            if isinstance(prop, Zone):
                return prop.value
            return prop

        return self.dump(
            {
                prop: scrub_property(getattr(self.pioneer.properties, prop))
                for prop in [p for p in PROPS_ALL if not prop_show or p in prop_show]
            },
            flow_style=None,
        )

    async def get_scan_interval(self, reader, writer):
        """Get scan interval."""
        return self.dump({"scan_interval": self.pioneer.scan_interval})

    async def set_scan_interval(self, reader, writer, scan_interval: float):
        """Set scan interval."""
        await self.pioneer.set_scan_interval(scan_interval)
        return await self.get_scan_interval(reader, writer)

    async def avr_update(self, reader, writer, full: bool):
        """Update zone."""
        await self.pioneer.update(None if full else self.zone)

    async def query_device_info(self, reader, writer) -> str:
        """Query device info."""
        await self.pioneer.query_device_info()
        return self.dump(
            {
                k: self.pioneer.properties.amp.get(k)
                for k in ["model", "mac_addr", "software_version"]
            }
        )

    async def query_zones(self, reader, writer) -> str:
        """Query zones."""
        await self.pioneer.query_zones()
        return await self.get_properties(reader, writer, prop_show=["zones"])

    async def get_source_dict(self, reader, writer) -> str:
        """Get source dict."""
        return self.dump(self.pioneer.properties.get_source_dict())

    async def set_source_dict(self, reader, writer, source_dict: dict) -> str:
        """Set source dict."""
        self.pioneer.properties.set_source_dict(source_dict)
        return await self.get_source_dict(reader, writer)

    async def build_source_dict(self, reader, writer) -> str:
        """Build source dict."""
        await self.pioneer.build_source_dict()
        return await self.get_source_dict(reader, writer)

    async def get_listening_modes(self, reader, writer) -> str:
        """Get zone listening mode."""
        return self.dump(self.pioneer.get_listening_modes())

    async def set_tuner_frequency(
        self, reader, writer, band: str, frequency: float
    ) -> str:
        """Set tuner band and frequency."""
        return await self.pioneer.set_tuner_frequency(TunerBand(band), frequency)

    async def debug_listener(self, reader, writer, state: str) -> str:
        """Set debug_listener flag."""
        state_bool = self.convert_bool_arg(state)
        self.pioneer.params.set_user_param(PARAM_DEBUG_LISTENER, state_bool)
        return self.dump({"debug_listener": state_bool})

    async def debug_updater(self, reader, writer, state: str) -> str:
        """Set debug_updater flag."""
        state_bool = self.convert_bool_arg(state)
        self.pioneer.params.set_user_param(PARAM_DEBUG_UPDATER, state_bool)
        return self.dump({"debug_updater": state_bool})

    async def debug_command(self, reader, writer, state: str) -> str:
        """Set debug_command flag."""
        state_bool = self.convert_bool_arg(state)
        self.pioneer.params.set_user_param(PARAM_DEBUG_COMMAND, state_bool)
        return self.dump({"debug_command": state_bool})

    async def debug_command_queue(self, reader, writer, state: str) -> str:
        """Set debug_command_queue flag."""
        state_bool = self.convert_bool_arg(state)
        self.pioneer.params.set_user_param(PARAM_DEBUG_COMMAND_QUEUE, state_bool)
        return self.dump({"debug_command_queue": state_bool})

    async def send_raw_command(self, reader, writer, command: str) -> str:
        """Send a raw command."""
        return await self.pioneer.send_raw_command(command)

    def gen_avr_send_command(self, command: str):
        """Generate a function for sending an AVR command."""

        async def avr_send_command(reader, writer, **kwargs) -> str:
            return await self.pioneer.send_command(
                command, zone=self.zone, *kwargs.values()
            )

        return avr_send_command

    def get_commands(
        self,
    ) -> dict[str, tuple[Callable[..., str], argparse.ArgumentParser]]:
        """Get commands list for CLI."""

        def get_command_parser(method: Callable[..., str]):
            """Get parser for command method."""
            return argparse.ArgumentParser(description=str(method.__doc__).rstrip("."))

        def get_command(
            method: Callable[..., str],
            name: str = None,
            parser: argparse.ArgumentParser = None,
        ) -> tuple[str, tuple[Callable[..., str], argparse.ArgumentParser]]:
            """Get command dictionary entry."""
            if name is None:
                name = method.__name__
            if parser is None:
                parser = get_command_parser(method)
            return name, (method, parser)

        def json_arg(
            arg: str, value_type: type, convert_func: Callable[[dict], dict] = None
        ) -> dict:
            """Validate and optionally convert a JSON argument to a dict."""
            try:
                if not isinstance(value := json.loads(arg), value_type):
                    raise ValueError
                if convert_func:
                    return convert_func(value)
                return value
            except (json.decoder.JSONDecodeError, ValueError) as exc:
                raise argparse.ArgumentTypeError from exc

        def convert_int_key_dict(dictv: dict[str, Any]) -> dict[int, Any]:
            """Convert dict keys to int."""
            return {int(k): v for k, v in dictv.items()}

        def params_json_arg(arg: str) -> dict:
            """Validate and convert a parameters JSON object to a dict."""
            value = json_arg(arg, dict)
            for param in PARAMS_DICT_INT_KEY:  ## Convert int key params
                if param in value:
                    value[param] = convert_int_key_dict(param)
            return value

        def source_json_arg(arg: str) -> dict:
            """Validate and convert a source JSON map to a dict."""
            return json_arg(arg, dict, convert_func=convert_int_key_dict)

        connect_parser = get_command_parser(self.connect)
        connect_parser.add_argument(
            "--reconnect",
            "-R",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="reconnect to the AVR on disconnect",
        )
        disconnect_parser = get_command_parser(self.connect)
        disconnect_parser.add_argument(
            "--reconnect",
            "-R",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="attempt to reconnect to the AVR after disconnecting",
        )
        zone_parser = get_command_parser(self.set_zone)
        zone_parser.add_argument(
            "zone", choices=[z.value for z in Zone], type=Zone, help="new zone"
        )
        logging_level_parser = get_command_parser(self.set_logging_level)
        logging_level_parser.add_argument(
            "level", choices=list(LOGGING_LEVELS.keys()), help="new logging level"
        )
        user_params_parser = get_command_parser(self.set_user_params)
        user_params_parser.add_argument(
            "params", type=params_json_arg, help="user parameters"
        )
        properties_parser = get_command_parser(self.get_properties)
        for prop in PROPS_ALL:
            properties_parser.add_argument(
                f"--{prop}",
                dest="prop_show",
                action="append_const",
                const=prop,
                help=f"show {prop} properties",
            )
        scan_interval_parser = get_command_parser(self.set_scan_interval)
        scan_interval_parser.add_argument(
            "scan_interval", type=float, help="scan interval"
        )
        update_parser = get_command_parser(self.avr_update)
        update_parser.add_argument("--full", "-f", action="store_true")
        source_dict_parser = get_command_parser(self.set_source_dict)
        source_dict_parser.add_argument(
            "source_dict", type=source_json_arg, help="source dict (JSON)"
        )
        tuner_frequency_parser = get_command_parser(self.set_tuner_frequency)
        tuner_frequency_parser.add_argument(
            "band", choices=[v.value for v in TunerBand], help="tuner band"
        )
        tuner_frequency_parser.add_argument(
            "frequency", type=float, help="tuner frequency"
        )
        debug_listener_parser = get_command_parser(self.debug_listener)
        debug_listener_parser.add_argument(
            "state",
            choices=["on", "off"],
            help="debug_listener state",
        )
        debug_updater_parser = get_command_parser(self.debug_updater)
        debug_updater_parser.add_argument(
            "state",
            choices=["on", "off"],
            help="debug_updater state",
        )
        debug_command_parser = get_command_parser(self.debug_command)
        debug_command_parser.add_argument(
            "state",
            choices=["on", "off"],
            help="debug_command state",
        )
        debug_command_queue_parser = get_command_parser(self.debug_command_queue)
        debug_command_queue_parser.add_argument(
            "state",
            choices=["on", "off"],
            help="debug_command_queue state",
        )
        raw_command_parser = get_command_parser(self.send_raw_command)
        raw_command_parser.add_argument(
            "command", type=str, help="raw command to send to AVR"
        )
        raw_command_parser_2 = get_command_parser(self.send_raw_command)
        raw_command_parser_2.add_argument(
            "command", type=str, help="raw command to send to AVR"
        )

        def get_avr_command(
            command, args: list[CodeMapBase] | None
        ) -> tuple[Callable[..., str], argparse.ArgumentParser]:
            parser = argparse.ArgumentParser()
            if args:
                for code_map in args:
                    code_map.get_parser(parser)

            return self.gen_avr_send_command(command), parser

        command_list = [
            get_command(self.connect, parser=connect_parser),
            get_command(self.disconnect, parser=disconnect_parser),
            get_command(self.set_zone, "zone", parser=zone_parser),
            get_command(
                self.set_logging_level, "logging_level", parser=logging_level_parser
            ),
            get_command(self.get_params),
            get_command(self.get_user_params),
            get_command(self.set_user_params, parser=user_params_parser),
            get_command(self.get_properties, parser=properties_parser),
            get_command(self.get_scan_interval),
            get_command(self.set_scan_interval, parser=scan_interval_parser),
            get_command(self.avr_update, "update", update_parser),
            get_command(self.query_device_info),
            get_command(self.query_zones),
            get_command(self.get_source_dict),
            get_command(self.set_source_dict, parser=source_dict_parser),
            get_command(self.build_source_dict),
            get_command(self.get_listening_modes),
            get_command(self.set_tuner_frequency, parser=tuner_frequency_parser),
            get_command(self.debug_listener, parser=debug_listener_parser),
            get_command(self.debug_updater, parser=debug_updater_parser),
            get_command(self.debug_command, parser=debug_command_parser),
            get_command(self.debug_command_queue, parser=debug_command_queue_parser),
            get_command(self.send_raw_command, parser=raw_command_parser),
            get_command(self.send_raw_command, ">", parser=raw_command_parser_2),
        ]
        return dict(command_list) | {
            command: get_avr_command(command, supported_zones.get("args"))
            for command, supported_zones in PIONEER_COMMANDS.items()
        }


class CliPrompt:
    """CLI prompt."""

    def __init__(self, cli: PioneerAVRCli):
        self.cli = cli

    def __str__(self):
        zone = self.cli.zone
        vol_ind = ""
        if self.cli.pioneer.properties.power.get(zone):
            vol_ind = " [X]"
            if not self.cli.pioneer.properties.mute.get(zone):
                vol_ind = f" [{self.cli.pioneer.properties.volume.get(zone)}]"
        return f"{zone.full_name}{vol_ind} >>> "

    def encode(self):
        """Return the CLI prompt."""
        return self.__str__()  # pylint: disable=unnecessary-dunder-call


async def async_cli_main(args: argparse.Namespace):
    """Async CLI entry point."""
    pioneer = PioneerAVR(args.hostname, args.port)
    cli = PioneerAVRCli(pioneer)
    await cli.set_logging_level()
    sys.ps1 = CliPrompt(cli)

    try:
        await pioneer.connect(reconnect=args.reconnect)
    except Exception as exc:  # pylint: disable=broad-except
        _LOGGER.error("could not connect to AVR: %s", repr(exc))
        return False

    print(f"Using default params: {pioneer.params.user_params}")
    pioneer.params.set_user_param(PARAM_DEBUG_LISTENER, True)
    if args.query_zones:
        await pioneer.query_zones()
        _LOGGER.info("AVR zones discovered: %s", pioneer.properties.zones)

    return await cli.interact()


def main():
    """Main entry point."""

    debug_level = logging.WARNING
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    log_format_color = "%(log_color)s" + log_format
    date_format = "%Y-%m-%d %H:%M:%S"
    try:
        import colorlog  # pylint: disable=import-outside-toplevel

        colorlog.basicConfig(
            level=debug_level, format=log_format_color, datefmt=date_format
        )
    except:  # pylint: disable=bare-except
        logging.basicConfig(level=debug_level, format=log_format, datefmt=date_format)

    parser = argparse.ArgumentParser(
        prog="aiopioneer",
        description="Debug CLI for aiopioneer package",
        prefix_chars="-+",
    )
    parser.add_argument(
        "hostname", default="avr.local", help="hostname for AVR connection"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=DEFAULT_PORT, help="port for AVR connection"
    )
    parser.add_argument(
        "--no-query-zones",
        "+Z",
        dest="query_zones",
        action="store_false",
        default=True,
        help="skip AVR zone query",
    )
    parser.add_argument(
        "--reconnect",
        "-R",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="reconnect to the AVR on disconnect",
    )
    args = parser.parse_args()

    rcode = False
    try:
        rcode = asyncio.run(async_cli_main(args))
    except KeyboardInterrupt:
        _LOGGER.info("KeyboardInterrupt")
    exit(0 if rcode else 1)
