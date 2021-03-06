"""CLI for Pioneer AVR asyncio API."""

import asyncio
import logging
import sys
import json

from aiopioneer import PioneerAVR
from aiopioneer.param import (
    PARAM_DEBUG_LISTENER,
    PARAM_DEBUG_RESPONDER,
    PARAM_DEBUG_UPDATER,
    PARAM_DEBUG_COMMAND,
)
from aiopioneer.pioneer_avr import PIONEER_COMMANDS

_LOGGER = logging.getLogger(__name__)


async def connect_stdin_stdout():
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


async def cli_main():
    pioneer = PioneerAVR("avr")

    try:
        await pioneer.connect(reconnect=False)
    except Exception as exc:
        _LOGGER.error("could not connect to AVR: %s: %s", type(exc).__name__, exc.args)
        return False

    # await pioneer.query_device_info()
    # await pioneer.query_zones()
    # _LOGGER.info("AVR zones discovered: %s", pioneer.zones)

    reader, writer = await connect_stdin_stdout()
    zone = "1"
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
            zone_new = arg
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
                "Device info: model=%s, mac_addr=%s, software_version=%s"
                % (pioneer.model, pioneer.mac_addr, pioneer.software_version)
            )
        elif cmd == "query_zones":
            await pioneer.query_zones()
            print(f"Zones discovered: {pioneer.zones}")
        elif cmd == "build_source_dict":
            await pioneer.build_source_dict()
        elif cmd == "set_source_dict":
            try:
                source_dict = json.loads(arg)
                print("Setting source dict to: %s" % json.dumps(source_dict))
                pioneer.set_source_dict(source_dict)
            except json.JSONDecodeError:
                print(f'ERROR: Invalid JSON source dict: "{arg}""')
        elif cmd == "get_source_list":
            print(f"Source list: {json.dumps(pioneer.get_source_list())}")
        elif cmd == "get_params":
            print(f"Params: {json.dumps(pioneer.get_params())}")
        elif cmd == "get_user_params":
            print(f"User Params: {json.dumps(pioneer.get_user_params())}")
        elif cmd == "set_user_params":
            try:
                params = json.loads(arg)
                print("Set user params: %s" % json.dumps(params))
                pioneer.set_user_params(params)
            except json.JSONDecodeError:
                print(f'ERROR: Invalid JSON params: "{arg}""')
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
            except Exception as exc:
                print(f'ERROR: Invalid scan interval "{arg}"')
        elif cmd == "get_scan_interval":
            print(f"Scan interval: {pioneer.scan_interval}")
        elif cmd == "set_volume_level":
            try:
                volume_level = int(arg)
                await pioneer.set_volume_level(volume_level, zone=zone)
            except Exception as exc:
                print(f'ERROR: Invalid volume level "{arg}": {exc}')
        elif cmd == "select_source":
            source = arg if arg else ""
            await pioneer.select_source(source, zone=zone)
        elif cmd == "send_raw_command":
            if arg:
                print(f"Sending raw command {arg}")
                await pioneer.send_raw_command(arg)
            else:
                print(f"ERROR: No raw command specified")
        elif cmd in PIONEER_COMMANDS:
            print(f"Executing command {cmd}")
            cur_zone = zone
            if (
                not isinstance(PIONEER_COMMANDS[cmd], dict)
                or zone not in PIONEER_COMMANDS[cmd]
            ):
                cur_zone = "1"
            prefix = arg if arg else ""
            await pioneer.send_command(cmd, zone=cur_zone, prefix=prefix)
        else:
            print(f"ERROR: Unknown command {cmd}")

    await pioneer.shutdown()
    return True


def main():
    import asyncio
    import logging

    debug_level = logging.WARNING
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    log_format_color = "%(log_color)s" + log_format
    date_format = "%Y-%m-%d %H:%M:%S"
    try:
        import colorlog

        colorlog.basicConfig(
            level=debug_level, format=log_format_color, datefmt=date_format
        )
    except:
        logging.basicConfig(level=debug_level, format=log_format, datefmt=date_format)

    rc = False
    try:
        rc = asyncio.run(cli_main())
    except KeyboardInterrupt:
        _LOGGER.info("KeyboardInterrupt")
    exit(0 if rc else 1)
