"""CLI for Pioneer AVR asyncio API."""

import asyncio
import logging
import sys
import json
import argparse

from aiopioneer import PioneerAVR
from aiopioneer.const import Zones, DEFAULT_PORT
from aiopioneer.param import (
    PARAM_DEBUG_LISTENER,
    PARAM_DEBUG_RESPONDER,
    PARAM_DEBUG_UPDATER,
    PARAM_DEBUG_COMMAND,
)
from aiopioneer.pioneer_avr import PIONEER_COMMANDS

_LOGGER = logging.getLogger(__name__)


async def connect_stdin_stdout():
    """Set up stdin/out for asyncio."""
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    w_transport, w_protocol = await loop.connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)
    return reader, writer


def set_log_level(arg):
    """Set root logging level."""
    level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }.get(arg)
    if level:
        print(f"Setting log level to {arg}")
        logging.getLogger().setLevel(level)
    else:
        print(f"ERROR: Unknown log level {arg}")


def get_bool_arg(arg):
    """Parse boolean argument."""
    return arg in ["true", "True", "TRUE", "on", "On", "ON", "1"]


async def cli_main(args: argparse.Namespace):
    """Main async entrypoint."""
    pioneer = PioneerAVR(args.hostname, args.port)

    try:
        await pioneer.connect(reconnect=False)
    except Exception as exc:  # pylint: disable=broad-except
        _LOGGER.error("could not connect to AVR: %s: %s", type(exc).__name__, exc.args)
        return False

    set_log_level("debug")
    params = pioneer.get_user_params()
    params[PARAM_DEBUG_LISTENER] = True
    print(f"Setting default params to: {params}")
    pioneer.set_user_params(params)

    if args.query_device_info:
        await pioneer.query_device_info()
    if args.query_zones:
        await pioneer.query_zones()
        _LOGGER.info("AVR zones discovered: %s", pioneer.zones)

    reader, _writer = await connect_stdin_stdout()
    zone = Zones.Z1
    while True:
        print(f"Current zone is {zone}")
        res = await reader.readline()
        if not res:
            break
        tokens = res.decode().strip().split(maxsplit=1)
        num_tokens = len(tokens)
        if num_tokens <= 0:
            continue

        cmd = tokens[0]
        arg = None if num_tokens == 1 else tokens[1]
        if cmd == "zone":
            zone_new = Zones(arg)
            if zone_new and zone_new in pioneer.zones:
                zone = zone_new
                print(f"Setting current zone to {zone}")
            else:
                print(f"ERROR: Unknown zone {zone_new}")
        elif cmd == "exit" or cmd == "quit":
            print("Exiting")
            break
        elif cmd == "log_level":
            set_log_level(arg)
        elif cmd == "update":
            await pioneer.update()
        elif cmd == "update_full":
            await pioneer.update(full=True)
        elif cmd == "query_device_info":
            await pioneer.query_device_info()
            print(
                f"Device info: model={pioneer.model}, "
                f"mac_addr={pioneer.mac_addr}, "
                f"software_version={pioneer.software_version}"
            )
        elif cmd == "query_zones":
            await pioneer.query_zones()
            print(f"Zones discovered: {pioneer.zones}")
        elif cmd == "build_source_dict":
            await pioneer.build_source_dict()
        elif cmd == "set_source_dict":
            try:
                source_dict = json.loads(arg)
                print(f"Setting source dict to: {json.dumps(source_dict)}")
                pioneer.set_source_dict(source_dict)
            except json.JSONDecodeError:
                print(f'ERROR: Invalid JSON source dict: "{arg}""')
        elif cmd == "get_source_list":
            print(f"Source list: {json.dumps(pioneer.get_source_list())}")
        elif cmd == "get_zone_listening_modes":
            print(
                f"Available listening modes: {json.dumps(pioneer.get_listening_modes())}"
            )
        elif cmd == "get_params":
            print(f"Params: {json.dumps(pioneer.get_params())}")
        elif cmd == "get_user_params":
            print(f"User Params: {json.dumps(pioneer.get_user_params())}")
        elif cmd == "set_user_params":
            try:
                params = json.loads(arg)
                print(f"Set user params: {json.dumps(params)}")
                pioneer.set_user_params(params)
            except json.JSONDecodeError:
                print(f'ERROR: Invalid JSON params: "{arg}""')

        elif cmd == "get_tone":
            audio_attrs = {
                "listening_mode": pioneer.listening_mode,
                "listening_mode_raw": pioneer.listening_mode_raw,
                "media_control_mode": pioneer.media_control_mode,
                "tone": pioneer.tone,
            }
            print(json.dumps(audio_attrs))
        elif cmd == "get_amp":
            print(json.dumps(pioneer.amp))
        elif cmd == "get_tuner":
            print(json.dumps(pioneer.tuner))
        elif cmd == "get_channel_levels":
            print(json.dumps(pioneer.channel_levels))
        elif cmd == "get_dsp":
            print(json.dumps(pioneer.dsp))
        elif cmd == "get_video":
            print(json.dumps(pioneer.video))
        elif cmd == "get_audio":
            print(json.dumps(pioneer.audio))
        elif cmd == "get_system":
            print(json.dumps(pioneer.system))

        elif cmd == "debug_listener":
            arg_bool = get_bool_arg(arg)
            params = pioneer.get_user_params()
            params[PARAM_DEBUG_LISTENER] = arg_bool
            print(f"Setting debug_listener to: {arg_bool}")
            pioneer.set_user_params(params)
        elif cmd == "debug_responder":
            arg_bool = get_bool_arg(arg)
            params = pioneer.get_user_params()
            params[PARAM_DEBUG_RESPONDER] = arg_bool
            print(f"Setting debug_responder to: {arg_bool}")
            pioneer.set_user_params(params)
        elif cmd == "debug_updater":
            arg_bool = get_bool_arg(arg)
            params = pioneer.get_user_params()
            params[PARAM_DEBUG_UPDATER] = arg_bool
            print(f"Setting debug_updater to: {arg_bool}")
            pioneer.set_user_params(params)
        elif cmd == "debug_command":
            arg_bool = get_bool_arg(arg)
            params = pioneer.get_user_params()
            params[PARAM_DEBUG_COMMAND] = arg_bool
            print(f"Setting debug_command to: {arg_bool}")
            pioneer.set_user_params(params)
        elif cmd == "set_scan_interval":
            try:
                scan_interval = float(arg)
                print(f"Setting scan interval to {scan_interval}")
                await pioneer.set_scan_interval(scan_interval)
            except Exception:  # pylint: disable=broad-except
                print(f'ERROR: Invalid scan interval "{arg}"')
        elif cmd == "get_scan_interval":
            print(f"Scan interval: {pioneer.scan_interval}")
        elif cmd == "set_volume_level":
            try:
                volume_level = int(arg)
                await pioneer.set_volume_level(volume_level, zone=zone)
            except Exception as exc:  # pylint: disable=broad-except
                print(f'ERROR: Invalid volume level "{arg}": {exc}')
        elif cmd == "select_source":
            source = arg if arg else ""
            await pioneer.select_source(source, zone=zone)
        elif cmd == "set_listening_mode":
            listening_mode = arg if arg else ""
            await pioneer.select_listening_mode(listening_mode)
        elif cmd == "set_tuner_frequency":
            subargs = arg.split(" ", maxsplit=1)
            try:
                band = subargs[0]
                frequency = float(subargs[1]) if len(subargs) > 1 else None
                await pioneer.set_tuner_frequency(band, frequency)
            except Exception as exc:  # pylint: disable=broad-except
                print(
                    f'ERROR: Invalid parameters for set_tuner_frequency "{arg}": {exc}'
                )
        elif cmd == "tuner_previous_preset":
            await pioneer.tuner_previous_preset()
        elif cmd == "tuner_next_preset":
            await pioneer.tuner_next_preset()
        elif cmd in ["send_raw_command", ">"]:
            if arg:
                print(f"Sending raw command {arg}")
                await pioneer.send_raw_command(arg)
            else:
                print("ERROR: No raw command specified")
        elif cmd in PIONEER_COMMANDS:
            print(f"Executing command {cmd}")
            cur_zone = zone
            if (
                not isinstance(PIONEER_COMMANDS[cmd], dict)
                or zone not in PIONEER_COMMANDS[cmd]
            ):
                cur_zone = "1"
            prefix = (suffix := "")
            if arg:
                prefix, _, suffix = arg.partition("|")
            print(
                f"Sending command {cmd}"
                + (f", prefix {prefix}" if prefix else "")
                + (f", suffix {suffix}" if suffix else "")
            )
            await pioneer.send_command(
                cmd, zone=cur_zone, prefix=prefix, suffix=suffix, ignore_error=True
            )
        else:
            print(f"ERROR: Unknown command {cmd}")

    await pioneer.shutdown()
    return True


def main():
    """Main entry point."""
    # import asyncio
    # import logging

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
        "hostname", help="hostname for AVR connection", default="avr.local"
    )
    parser.add_argument(
        "-p", "--port", type=int, help="port for AVR connection", default=DEFAULT_PORT
    )
    parser.add_argument(
        "+Q",
        "--no-query-device-info",
        dest="query_device_info",
        help="skip AVR device info query",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "+Z",
        "--no-query-zones",
        dest="query_zones",
        help="skip AVR zone query",
        action="store_false",
        default=True,
    )
    args = parser.parse_args()

    rcode = False
    try:
        rcode = asyncio.run(cli_main(args))
    except KeyboardInterrupt:
        _LOGGER.info("KeyboardInterrupt")
    exit(0 if rcode else 1)
