<!-- markdownlint-disable MD033 MD041 -->

Python library for controlling a Pioneer AVI via its built-in API.

Used by the [pioneer_async](https://github.com/crowbarz/ha-pioneer_async) integration for Home Assistant, which was inspired by the [original Pioneer Home Assistant integration](https://www.home-assistant.io/integrations/pioneer/).
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
- Supports all listening mode functions
- Supports all video related functions
- Supports panel and remote locking
- Supports most AMP related functions
- Supports all tone functions
- Supports most zone power functions
- Supports all zone input functions
- Supports all zone volumne and mute functions
- Supports some basic tuner functions

## Params

A `params` object may be passed to the library that modifies its functionality.

The default parameters listed below are for AVR models that do not match any custom profile. Custom profiles apply additional default parameters based on the model identifier retrieved from the AVR, and are defined in [`aiopioneer/param.py`](https://github.com/crowbarz/aiopioneer/blob/main/aiopioneer/param.py). If you need to modify parameters for the library to work for your AVR model, then please create a PR to add a custom profile for your AVR model, or log an issue containing your model number and the parameters that were modified requesting a custom profile to be created.

> **NOTE:** YAML syntax is used in the table below. Use Python equivalents (`false` -> `False`, `true` -> `True`, `null` -> `None` etc.) when calling the Python API directly, and JSON syntax if manually specifying via the Home Assistant integration.

| Name | Type | Default | Description
| ---- | ---- | ------- | -----------
| `ignored_zones` | list | `[]` | List of zones to ignore even if they are auto-discovered. Specify Zone IDs as strings: "1", "2", "3" and "Z".
| `command_delay` | float | `0.1` | Insert a delay between sequential commands that are sent to the AVR. This appears to make the AVR behave more reliably during status polls. Increase this value if debug logging shows that your AVR times out between commands.
| `max_source_id` | int | `60` | Maximum source ID that the source discovery queries. Reduce this if your AVR returns errors.
| `max_volume` | int | `185` | Maximum volume for the Main Zone.
| `max_volume_zonex` | int | `185` | Maximum volume for zones other than the Main Zone.
| `power_on_volume_bounce` | bool | `false` | On some AVRs (eg. VSX-930) where a power-on is set, the initial volume is not reported by the AVR correctly until a volume change is made. This option enables a workaround that sends a volume up and down command to the AVR on power-on to correct the reported volume without affecting the power-on volume.
| `volume_step_only` | bool | `false` | On some AVRs (eg. VSX-S510), setting the volume level is not supported natively by the API. This option emulates setting the volume level using volume up and down commands.
| `ignore_volume_check` | bool | `false` | Don't check volume when determining whether a zone exists on the AVR. Useful for AVRs with an HDZone that passes through audio.
| `zone_1_sources` | list | `[]` | (>0.4) Customises the available sources for use with Zone 1. Defaults to all available sources.
| `zone_2_sources` | list | `["04", "06", "15", "26", "38", "53", "41", "44", "45", "17", "13", "05", "01", "02", "33", "46", "47", "99", "10"]` | Customises the available sources for use with Zone 2 (some AVRs do not support all sources).
| `zone_3_sources` | list | `["04", "06", "15", "26", "38", "53", "41", "44", "45", "17", "13", "05", "01", "02", "33", "46", "47", "99", "10"]` | Customises the available sources for use with Zone 3 (some AVRs do not support all sources).
| `hdzone_sources` | list | `["25", "04", "06", "10", "15", "19", "20", "21", "22", "23", "24", "34", "35", "26", "38", "53", "41", "44", "45", "17", "13", "33", "31", "46", "47", "48"]` | Customises the available sources for use with HDZone (some AVRs do not support all sources).
| `hdzone_volume_requirements` | list | `["13", "15", "05", "25"]` | A list of sources that HDZone must be set to for volume control, some AVRs do not support HDZone volume at all (see `ignore_volume_check` above) and some only allow control of certain sources.
| `amplifier_speaker_system_modes` | dict | `....` | Customises the names of speaker system modes. Different generations of AVR will name zones slighty differently. For example, the SC-LX57 names speaker system mode `15` as `5.1ch Bi-Amp + ZONE2` however this can also be called `5.2ch Bi-Amp + HDZONE` on newer AVRs.
| `disabled_amplifier_listening_modes` | list | `[]` | A list of disabled listening modes / sound modes, all modes are enabled by default, some AVRs have definitions already to disable unsupported modes. If you try to change sound mode to a mode that has not been enabled, the AVR will return an error (usually `E02`).
| `video_resolution_modes` | list | `['0', '1', '3', '4', '5', '6', '7', '8', '9']` | Sets the available video resolutions. Not all AVRs support the same resolution settings. This defaults to all of the latest resolutions from FY16.
| `mhl_source` | string | `null` | Sets the MHL source ID. This is used for media controls. This information cannot be queried automatically
| `enabled_functions` | list | `["amp", "dsp", "tuner", "tone", "channels", "video", "system", "audio"]` | Change the functions that are enabled by the API, adding more functions will increase the amount of time it takes to complete a full init and update.
| `disable_autoquery` | bool | `false` | Setting to `true` will disable auto queries on init for all functions apart from basic functionality (power, source, volume and mute). If you only need those functions, you can set this to `true`
| `am_frequency_step` | int | `null` | Optional setting to configure the AM frequency step. If this is set to `null`, a function is queued to detect this information by stepping up and down the frequency when the tuner is first used while set to AM.
| `debug_listener` | bool | `false` | Enables additional debug logging for the listener task.
| `debug_responder` | bool | `false` | Enables additional debug logging for the responder task.
| `debug_updater` | bool | `false` | Enables additional debug logging for the updater task.
| `debug_command` | bool | `false` | Enables additional debug logging for commands sent and responses received.

## Command line interface (CLI) (>= 0.1.3, CLI arguments >= 0.3)

A very simple command line interface `aiopioneer` is available to connect to the AVR, send commands and receive responses. It can be used to test the capabilities of the library against your specific AVR.

On Home Assistant, you can run the CLI when the `pioneer_async` Home Assistant integration has been installed. On Home Assistant Supervised or Container, start the CLI from within the HA container: `docker exec -it homeassistant aiopioneer`.

Invoke the CLI with the following arguments:

| Argument | Default | Description
| --- | --- | ---
| hostname | required | hostname for AVR connection
| `-p`<br>`--port` | 8102 | port for AVR connection
| `+Q`<br>`--no-query-device-info` | None | skip AVR device info query
| `+Z`<br>`--no-query-zones` | None | skip AVR zone query

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
| `get_tone` | | Returns the current AVR tone attributes.
| `get_amp` | | Returns the current AVR amp attributes.
| `get_tuner` | | Returns the current AVR tuner attributes.
| `get_channel_levels` | | Returns the current AVR channel levels.
| `get_dsp` | | Returns the current AVR DSP attributes.
| `get_video` | | Returns the current AVR video parameters.
| `get_audio` | | Returns the current AVR audio parameters.
| `get_system` | | Returns the AVR system attributes.
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

## Source list

| ID | Default Name
| -- | ---
| 25 | BD
| 04 | DVD
| 06 | SAT/CBL
| 15 | DVR/BDR
| 19 | HDMI 1
| 20 | HDMI 2
| 21 | HDMI 3
| 22 | HDMI 4
| 23 | HDMI 5
| 24 | HDMI 6
| 34 | HDMI 7
| 26 | NETWORK (cyclic)
| 38 | INTERNET RADIO
| 53 | Spotify
| 41 | PANDORA
| 44 | MEDIA SERVER
| 45 | FAVORITES
| 17 | iPod/USB
| 05 | TV
| 01 | CD
| 13 | USB-DAC
| 02 | TUNER
| 00 | PHONO
| 12 | MULTI CH IN
| 33 | BT AUDIO
| 31 | HDMI (cyclic)
| 46 | AirPlay (Information only)
| 47 | DMR (Information only)

## Known issues and future plans

- Document PioneerAVR API

## Breaking changes

- **0.4**\
  `zone_z_sources` was renamed `hdzone_sources` for even more consistency.

- **0.3**\
  `zone_h_sources` was renamed `zone_z_sources` for consistency.

- **0.2**\
  `volume_step_delta` has been removed entirely.

  By default, a number of additional queries are sent at module startup to the AVR to gather amp, tuner and channel levels attributes. If your AVR does not handle these additional queries well, they can be disabled by setting parameter `disable_autoquery` to `true`.

- **0.1**\
  `_PioneerAVR.__init__()` no longer accepts `command_delay`, `volume_workaround` and `volume_steps` arguments. Configure these parameters using the equivalent `PARAM_*` keys in the `params` dict, passed in via the constructure or set via `set_user_params()`.

## References

- Home Assistant Pioneer integration: [https://www.home-assistant.io/integrations/pioneer/](https://www.home-assistant.io/integrations/pioneer/)
- Pioneer commands references: [https://github.com/rwifall/pioneer-receiver-notes](https://github.com/rwifall/pioneer-receiver-notes)
- Another asyncio Pioneer HA component: [https://github.com/realthk/asyncpioneer](https://github.com/realthk/asyncpioneer)
- Pioneer IP and serial IO control documentation: [https://www.pioneerelectronics.com/PUSA/Support/Home-Entertainment-Custom-Install/RS-232+&+IP+Codes/A+V+Receivers](https://www.pioneerelectronics.com/PUSA/Support/Home-Entertainment-Custom-Install/RS-232+&+IP+Codes/A+V+Receivers)
