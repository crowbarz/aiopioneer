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
- Defaults for internal parameters can be changed based on custom profiles based on AVR model.
- Includes workaround for AVRs with an initial volume set on the Main Zone (eg. VSX-930).
- Supports AVRs that do not support setting the volume level by emulating using up/down commands (eg. VSX-S510).
- Command line client for sending commands and testing

## Command line interface (CLI) (>= 0.1.3)

A very simple command line interface `aiopioneer` is available to connect to the AVR, send commands and receive responses. It can be used to test the capabilities of the library against your specific AVR.

The CLI accepts all API commands, as well as the following:
| Command | Argument | Description
| --- | --- | ---
| `exit` or `quit` | | Exit the CLI.
| `zone` | _zone_ | Change current zone to _zone_.
| `log_level` | _log_level_ | Change debug level to _log_level_. Valid log levels are: `debug`, `info`, `warning`, `error`, `critical`.
| `update` | | Request update of AVR. An update is scheduled in the updater task if a scan interval is set, if it is not set then the update is performed synchronously.
| `update_full` | | Request a full update of AVR irrespective of when the previous update was performed. An update is scheduled in the updater task if a scan interval is set, if it is not set then the update is performed synchronously.
| `query_device_info` | | Query the AVR for device information.
| `query_zones` | | Query the AVR for available zones. Ignore zones specified in parameter `ignored_zones` (list).
| `build_source_dict` | | Query the sources from the AVR.
| `set_source_dict` | _sources_ (JSON) | Manually set the sources to _sources_.
| `get_source_list` | | Return the current set of available source names that can be used with the `select_source` command.
| `get_params` | | Return the currently active set of parameters.
| `get_user_params` | | Return the currently active set of user parameters.
| `set_user_params` | _params_ (JSON) | Set the user parameters to _params_.
| `debug_listener` | _state_ (bool) | Enable/disable the `debug_listener` parameter.
| `debug_responder` | _state_ (bool) | Enable/disable the `debug_responder` parameter.
| `debug_updater` | _state_ (bool) | Enable/disable the `debug_updater` parameter.
| `debug_command` | _state_ (bool) | Enable/disable the `debug_command` parameter.
| `set_scan_interval` | _scan_interval_ (float) | Set the scan interval to _scan_interval_.
| `get_scan_interval` | | Return the current scan interval.
| `set_volume_level` | _volume_level_ (int) | Set the volume level for the current zone.
| `select_source` | _source_name_ | Set the input source for the current zone.
| `send_raw_command` | _raw_command_ | Send the raw command _raw_command_ to the AVR.

**NOTE:** The CLI interface may change in the future, and should not be used in scripts. Use the Python API instead.

## Known issues and future plans

- Document PioneerAVR API

## Breaking changes

- **0.1**\
  `_PioneerAVR.__init__()` no longer accepts `command_delay`, `volume_workaround` and `volume_steps` arguments. Configure these parameters using the equivalent `PARAM_*` keys in the `params` dict, passed in via the constructure or set via `set_user_params()`.

## References

- Home Assistant Pioneer integration: [https://www.home-assistant.io/integrations/pioneer/](https://www.home-assistant.io/integrations/pioneer/)
- Pioneer commands references: [https://github.com/rwifall/pioneer-receiver-notes](https://github.com/rwifall/pioneer-receiver-notes)
- Another asyncio Pioneer HA component: [https://github.com/realthk/asyncpioneer](https://github.com/realthk/asyncpioneer)
