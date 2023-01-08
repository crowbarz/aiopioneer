#!/usr/bin/env python3
""" Pioneer AVR testing script. """
# pylint: disable=import-error,broad-except

import asyncio
import logging

from aiopioneer import PioneerAVR

_LOGGER = logging.getLogger(__name__)


async def main():
    """ Main loop. """
    _LOGGER.debug(">> main()")

    pioneer = PioneerAVR("10.10.2.218")

    try:
        await pioneer.connect()
    except Exception as e:  # pylint: disable=invalid-name
        print(f"Could not connect to AVR: {type(e).__name__}: {e.args}")
        return False

    await pioneer.query_device_info()
    print(
        f"AVR device info: model={pioneer.model}, mac_addr={pioneer.mac_addr}, software_version={pioneer.software_version}"
    )
    await pioneer.query_zones()
    print(f"AVR zones discovered: {pioneer.zones}")
    print("Discovering zones")
    await pioneer.build_source_dict()
    
    
    await pioneer.update()
    await asyncio.sleep(15)
    ## Turn on main zone for tests
    # await pioneer.turn_on("1")

    for z in pioneer.zones:
        print(f"Power for zone - {z} {pioneer.power.get(z)}")
        print(f"Volume for zone - {z} {pioneer.volume.get(z)}")
        print(f"Source for zone - {z} {pioneer.source.get(z)}")
        print(f"Listening Modes for zone - {z} {pioneer.get_sound_modes(z)}")

    #await pioneer.select_source("TUNER", "1")
    #await pioneer.set_tuner_frequency("AM", 580, "1")
    
    await pioneer.set_dsp_settings(phase_control="off", zone="1")

    # print("...")
    # await pioneer.disconnect()

    while True:
        #for property, value in vars(pioneer).items():
            #print(property, ":", value)
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
    rc = asyncio.run(main())  ## pylint: disable=invalid-name
    exit(0 if rc else 1)
