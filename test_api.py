#!/usr/bin/env python3
""" Pioneer AVR testing script. """
# pylint: disable=import-error,broad-except

import asyncio
import logging
import sys
import getopt

from aiopioneer import PioneerAVR
from aiopioneer.const import Zone

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
    except Exception as exc:
        print(f"Could not connect to AVR: {repr(exc)}")
        return False

    await pioneer.query_device_info()
    print(
        f"AVR device info: model={pioneer.properties.amp.get("model")}, "
        + f"mac_addr={pioneer.properties.amp.get("mac_addr")}, "
        + f"software_version={pioneer.properties.amp.get("software_version")}"
    )
    await pioneer.query_zones()
    print(f"AVR zones discovered: {pioneer.properties.zones}")
    print("Discovering zones")
    await pioneer.build_source_dict()

    await pioneer.update()
    await asyncio.sleep(15)
    ## Turn on main zone for tests
    await pioneer.turn_on(zone=Zone.Z1)

    # await pioneer.select_source(source="TUNER", zone=Zone.Z1)
    # await pioneer.set_tuner_frequency(band=TunerBand.AM, frequency=580)

    await pioneer.set_dsp_settings(phase_control="off", zone=Zone.Z1)

    # print("...")
    # await pioneer.disconnect()

    while True:
        for prop, value in vars(pioneer.properties).items():
            print(prop, ":", value)

        await asyncio.sleep(60)
        print("Update ...")
        await pioneer.update()

    # await pioneer.send_raw_request("?RGD", "RGD", ignore_error=True)
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
