Python library for controlling a Pioneer AVI via its built-in API.

Inspired by the [original Pioneer Home Assistant integation](https://www.home-assistant.io/integrations/pioneer/).
Tested on a VSX-930 (Main Zone and HDZone outputs).

## Features

- Implemented in asyncio.
- Maintains single continuous telnet session to AVR, with automatic reconnect.
- Eliminates status polling where AVR sends keepalive responses (on port 8102).
- Auto-detects Zones 1, 2, 3 and HDZONE.
- Automatically polls AVR for source names - no longer need to manually code them in your config any more if your AVR supports their retrieval.
- Queries device parameters: MAC address, software version, model.
- Includes workaround for AVRs with an initial volume set on the Main Zone.

## Known issues/Future plans

- Implement a command line to send commands and receive responses from the AVR, though this appears to be tricky as console I/O isn't well supported in asyncio.

## References

- Home Assistant Pioneer integration: https://www.home-assistant.io/integrations/pioneer/
- Pioneer commands references: https://github.com/rwifall/pioneer-receiver-notes
- Another asyncio Pioneer HA component: https://github.com/realthk/asyncpioneer
