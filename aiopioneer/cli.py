"""CLI for Pioneer AVR asyncio API."""

import asyncio
import logging
import sys

from aiopioneer import PioneerAVR
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


async def cli_main():
    pioneer = PioneerAVR("avr")

    try:
        await pioneer.connect()
    except Exception as exc:
        _LOGGER.error("could not connect to AVR: %s: %s", type(exc).__name__, exc.args)
        return False

    await pioneer.query_device_info()
    _LOGGER.info(
        "AVR device info: model=%s, mac_addr=%s, software_version=%s",
        pioneer.model,
        pioneer.mac_addr,
        pioneer.software_version,
    )
    await pioneer.query_zones()
    _LOGGER.info("AVR zones discovered: %s", pioneer.zones)

    reader, writer = await connect_stdin_stdout()
    zone = "1"
    while True:
        print(f"Current zone is {zone}")
        res = await reader.readline()
        if not res:
            break
        tokens = res.decode().strip().split()
        if len(tokens) <= 0:
            continue

        cmd = tokens[0]
        if cmd == "zone":
            zone_new = tokens[1]
            if zone_new in pioneer.zones:
                zone = zone_new
                print(f"Setting current zone to {zone}")
            else:
                print(f"Unknown zone {zone_new}")
        elif cmd == "exit" or cmd == "quit":
            print("Exiting")
            break
        elif cmd in PIONEER_COMMANDS:
            print(f"Executing command {cmd}")
            cur_zone = zone
            if (
                not isinstance(PIONEER_COMMANDS[cmd], dict)
                or zone not in PIONEER_COMMANDS[cmd]
            ):
                cur_zone = "1"
            prefix = tokens[1] if len(tokens) >= 2 else ""
            await pioneer.send_command(cmd, zone=cur_zone, prefix=prefix)
        else:
            print(f"Unknown command {cmd}")

    await pioneer.shutdown()
    return True


def main():
    import asyncio
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    rc = asyncio.run(cli_main())
    exit(0 if rc else 1)
