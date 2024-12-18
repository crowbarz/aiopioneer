#!/usr/bin/env python3
""" Pioneer AVR testing script. """
# pylint: disable=import-error,broad-except

import asyncio
import logging
import sys
import getopt

from aiopioneer import PioneerAVR

_LOGGER = logging.getLogger(__name__)


async def main(argv):
    """Main loop."""
    _LOGGER.debug(">> main()")

    host = ""
    try:
        opts, _ = getopt.getopt(argv, "h:", ["host="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--host"):
            host = arg

    if host == "":
        _LOGGER.fatal("Host not specified.")
        sys.exit(2)

    pioneer = PioneerAVR(host)

    try:
        await pioneer.connect()
    except Exception as e:  # pylint: disable=invalid-name
        print(f"Could not connect to AVR: {type(e).__name__}: {e.args}")
        return False

    await pioneer.query_device_info()
    print(
        f"AVR device info: model={pioneer.properties.model}, "
        + f"mac_addr={pioneer.properties.mac_addr}, "
        + f"software_version={pioneer.properties.software_version}"
    )
    await pioneer.query_zones()
    print(f"AVR zones discovered: {pioneer.properties.zones}")
    print("Discovering zones")
    await pioneer.build_source_dict()

    await pioneer.update()
    await asyncio.sleep(15)
    ## Turn on main zone for tests
    # await pioneer.turn_on("1")

    # await pioneer.select_source("TUNER", "1")
    # await pioneer.set_tuner_frequency("AM", 580, "1")

    await pioneer.set_dsp_settings(phase_control="off", zone="1")

    # print("...")
    # await pioneer.disconnect()

    while True:
        for prop, value in vars(pioneer).items():
            print(prop, ":", value)

        await asyncio.sleep(60)
        print("Update ...")
        await pioneer.update()

    # if not pioneer.available:
    #     try:
    #         await pioneer.connect()
    #     except Exception as e:  # pylint: disable=invalid-name
    #         print(f"Could not reconnect to AVR: {type(e).__name__}: {e.args}")
    #         await pioneer.shutdown()
    #         return False

    # await pioneer.send_raw_request("?RGD", "PWR")
    # print("...")
    # await asyncio.sleep(5)
    # print("...")
    # await pioneer.update()
    # print("...")
    # await asyncio.sleep(5)
    # print("...")
    await pioneer.shutdown()

    return True


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    rc = asyncio.run(main(sys.argv[1:]))  ## pylint: disable=invalid-name
    exit(0 if rc else 1)
