<!-- markdownlint-disable MD041 -->
Python library for controlling a Pioneer AVI via its built-in API.

Inspired by the [original Pioneer Home Assistant integration](https://www.home-assistant.io/integrations/pioneer/).
Tested on a VSX-930 (Main Zone and HDZone outputs).

## Features

- Implemented in asyncio.
- Maintains single continuous telnet session to AVR, with automatic reconnect.
- Eliminates status polling where AVR sends keepalive responses (on port 8102).
- Auto-detects Zones 1, 2, 3 and HDZONE.
- Automatically polls AVR for source names - no longer need to manually code them in your config any more if your AVR supports their retrieval. Can also set source names manually.
- Ignore specific zones, for AVRs that report phantom zones.
- Queries device parameters: MAC address, software version, model.
- Ability to set internal parameters to change the API functionality, eg. maximum volume, volume step change delta.
- Includes workaround for AVRs with an initial volume set on the Main Zone (eg. VSX-930).
- Supports AVRs that do not support setting the volume level by emulating using up/down commands (eg. VSX-S510).

## Known issues and future plans

- Document PioneerAVR API
- Implement a command line to send commands and receive responses from the AVR, though this appears to be tricky as console I/O isn't well supported in asyncio.

## Major breaking changes

- **0.1**\
  `_PioneerAVR.__init__()` no longer accepts `command_delay`, `volume_workaround` and `volume_steps` arguments. Configure these parameters using the equivalent `PARAM_*` keys in the `params` dict, passed in via the constructure or set via `set_user_params()`.

## References

- Home Assistant Pioneer integration: [https://www.home-assistant.io/integrations/pioneer/](https://www.home-assistant.io/integrations/pioneer/)
- Pioneer commands references: [https://github.com/rwifall/pioneer-receiver-notes](https://github.com/rwifall/pioneer-receiver-notes)
- Another asyncio Pioneer HA component: [https://github.com/realthk/asyncpioneer](https://github.com/realthk/asyncpioneer)
