<!-- markdownlint-disable MD033 MD041 -->
# aiopioneer

Python library for controlling a Pioneer AVR via its built-in API.

Used by the [pioneer_async](https://github.com/crowbarz/ha-pioneer_async) integration for Home Assistant, which was inspired by the [original Pioneer Home Assistant integration](https://www.home-assistant.io/integrations/pioneer/).
Originally developed and tested on a VSX-930 (Main Zone and HDZone outputs) but has since been [tested on a larger set of models by the community](https://github.com/crowbarz/ha-pioneer_async/issues/20).

## Features

- Implemented in asyncio
- Maintains single continuous telnet session to AVR, with automatic reconnect. This method of accessing the AVR API crashes less often than the integration included with Home Assistant
- Eliminates status polling where AVR sends keepalive responses (on port 8102)
- Auto-detects Zones 1, 2, 3 and HDZone
- Ignore specific zones, for AVRs that report phantom zones
- Automatically polls AVR for source names - no longer need to manually code them in your config any more if your AVR supports their retrieval. Can also set source names manually
- Queries device information from the AVR where supported: MAC address, software version, model
- Ability to set internal parameters to change the API functionality, eg. maximum volume, volume step change delta
- Defaults for internal parameters set via custom profiles based on AVR model
- Includes workaround for AVRs with an initial volume set on the Main Zone (eg. VSX-930)
- Supports AVRs that do not support setting the volume level by emulating using up/down commands (eg. VSX-S510)
- Command line client for sending commands and testing
- Supports all known video related, amp, DSP, listening mode, tuner and zone power, input, volume, tone, channel and mute functions
- Supports many commonly used system setup functions
- Supports setting active MCACC memory set
- Supports iPod, network, Adapter Port/Bluetooth and MHL operational functions
- Supports setting tuner frequency directly for AVRs that support numerical entry, and also by stepping the frequency up/down for AVRs that support frequency stepping

## Parameters

There are several types of parameters that modify the library's functionality. These are listed below in order of increasing priority:

- **Default parameters**: these are the defaults for all of the parameters
- **Model parameters**: these parameters are determined by the AVR model as detected by the library. Custom profiles for specific AVR models are defined in [aiopioneer/param.py](https://github.com/crowbarz/aiopioneer/blob/main/aiopioneer/param.py)
- **User parameters**: these parameters are provided by the user at instantiation, and can also be updated via the `set_user_params` method

Where a parameter is specified at more than one level, the higher priority parameter takes precedence. Thus, a user specified parameter will override any value that is determined by the AVR model.

> [!NOTE]
> YAML syntax is used to indicate values the table below. This syntax is used when entering parameters manually in the Home Assistant integration. Use Python equivalents (`false` -> `False`, `true` -> `True`, `null` -> `None` etc.) when calling the [Python API](#python-api) directly.

> [!CAUTION]
> Sources, listening modes and speaker system modes are specified as a **dict*- with **int*- keys. JSON does not support **int*- for **dict*- keys. For such parameters, keys should be specified as **str**. Note that Python will [silently coerce **int*- keys for **dict*- to **str**](https://docs.python.org/3/library/json.html#basic-usage) when serialising such dictionaries to JSON.
>
> The Home Assistant integration automatically converts keys for impacted parameters back to **int*- keys, however other users of this module may also need to implement this conversion.

| Name | Type | Default | Description
| ---- | ---- | ------- | -----------
| `model` | str | | Device model of AVR. Queried from AVR on connect if not specified
| `ignored_zones` | list | `[]` | List of zones to ignore even if they are auto-discovered. Specify Zone IDs as strings: "1", "2", "3" and "Z"
| `command_delay` | float | `0.1` | Insert a delay between sequential commands that are sent to the AVR. This appears to make the AVR behave more reliably during status polls. Increase this value if debug logging shows that your AVR times out between commands
| `max_source_id` | int | `60` | Maximum source ID that the source discovery queries. Reduce this if your AVR returns errors
| `max_volume` | int | `185` | Maximum volume for the Main Zone
| `max_volume_zonex` | int | `185` | Maximum volume for zones other than the Main Zone
| `power_on_volume_bounce` | bool | `false` | On some AVRs (eg. VSX-930) where a power-on is set, the initial volume is not reported by the AVR correctly until a volume change is made. This option enables a workaround that sends a volume up and down command to the AVR on power-on to correct the reported volume without affecting the power-on volume
| `volume_step_only` | bool | `false` | On some AVRs (eg. VSX-S510), setting the volume level is not supported natively by the API. This option emulates setting the volume level using volume up and down commands.
| `ignore_volume_check` | bool | `false` | Don't check volume when determining whether a zone exists on the AVR. Useful for AVRs with an HDZone that passes through audio
| `zone_1_sources` | list[int] | `[]` | (>0.4) Customises the available sources for use with Zone 1. Defaults to all available sources
| `zone_2_sources` | list[int] | [see source](https://github.com/crowbarz/aiopioneer/blob/dev/aiopioneer/param.py#L61) | Customises the available sources for use with Zone 2 (some AVRs do not support all sources)
| `zone_3_sources` | list[int] | [see source](https://github.com/crowbarz/aiopioneer/blob/dev/aiopioneer/param.py#L61) | Customises the available sources for use with Zone 3 (some AVRs do not support all sources)
| `hdzone_sources` | list[int] | [see source](https://github.com/crowbarz/aiopioneer/blob/dev/aiopioneer/param.py#L61) | Customises the available sources for use with HDZone (some AVRs do not support all sources)
| `amp_speaker_system_modes` | dict[int, str] | [see source](https://github.com/crowbarz/aiopioneer/blob/dev/aiopioneer/params.py#L198) | Customises the names of speaker system modes. Different generations of AVR will name zones slighty differently. For example, the SC-LX57 names speaker system mode `15` as `5.1ch Bi-Amp + ZONE2` however this can also be called `5.2ch Bi-Amp + HDZONE` on newer AVRs
| `extra_amp_listening_modes` | dict[int, str] | [see source](https://github.com/crowbarz/aiopioneer/blob/dev/aiopioneer/const.py#L68) | (>0.5) Additional listening modes that are added to the list of all possible listening modes for the AVR. This list is used to decode the listening mode ID returned by the AVR. See the source for the format for listening mode definition
| `enabled_amp_listening_modes` | list[int] | `[]` | (>0.5) A list of listening mode IDs to be made available for selection. If specified, then no listening mode IDs will be included by default. All enabled source names must be unique, and duplicated names are ignored. The additional listening modes must be actually supported by the AVR, and will return an error (usually `E02`) when an unsupported listening mode is selected. This list is predefined for some AVRs, and specifying this parameter manually will override the model specific default disable list
| `disabled_amp_listening_modes` | list[int] | `[]` | A list of listening mode IDs to be disabled. Listening mode IDs that are also specified in `enabled_amp_listening_modes` will be disabled. This list is predefined for some AVRs, and specifying this parameter manually will override the model specific default disable list
| `video_resolution_modes` | list[str] | `['0', '1', '3', '4', '5', '6', '7', '8', '9']` | Sets the available video resolutions. Not all AVRs support the same resolution settings. This defaults to all of the latest resolutions from FY16
| `mhl_source` | string | `null` | Sets the MHL source ID. This is used for media controls. This information cannot be queried automatically
| `enabled_functions` | list[str] | `["basic", "audio", "amp", "dsp", "tone", "channel", "video", "tuner", "system", "display"]` | Change the functions that are enabled by the API, adding more functions will increase the amount of time it takes to complete a full init and update
| `disable_auto_query` | bool | `false` | Set to `true` to disable auto queries on first zone power on for all functions apart from core functionality (power, source, volume and mute)
| `am_frequency_step` | int | `null` | Optional setting to configure the tuner AM frequency step. If not specified, it will be queried from the AVR if supported by the AVR, otherwise it will be determined by stepping the frequency up and down when the AM tuner is first used
| `always_poll` | bool | `false` | Always poll the AVR every _scan_interval_. If set to `false`, out of band status responses from the AVR will reset the polling interval
| `debug_listener` | bool | `false` | Enables additional debug logging for the listener task
| `debug_updater` | bool | `false` | Enables additional debug logging for the updater task
| `debug_command` | bool | `false` | Enables additional debug logging for commands sent and responses received
| `debug_command_queue` | bool | `false` | Enables additional debug logging for the command queue task
<!-- unimplemented
| `hdzone_volume_requirements` | list | `["13", "15", "05", "25"]` | A list of sources that HDZone must be set to for volume control, some AVRs do not support HDZone volume at all (see `ignore_volume_check` above) and some only allow control of certain sources -->

If your model of AVR always needs specific parameters to be set for the library to function properly, then please create a PR to add a custom profile for the AVR model.

## Python API

The API documention can be found on the [Python API](python_api.md) page.

## AVR Properties

Listed below are the public attributes of a `AVRProperties` object that contains the current state of the AVR. Use a `Zone` enum to access zone specific attributes for those that are indexed by zone.

| Attribute | Type | Description
| --- | --- | ---
| `model` | **str*- \| **None*- | Model number returned by the AVR
| `software_version` | **str*- \| **None*- | Software version returned by the AVR
| `mac_addr` | **str*- \| **None*- | System MAC address returned by the AVR
| `zones` | **list**[Zone] | List of all zones detected on the AVR
| `power` | **dict**[Zone, **bool**] | Power status for each detected zone
| `volume` | **dict**[Zone, **int**] | Volume status for each detected zone
| `max_volume` | **dict**[Zone, **int**] | Maximum valid volume for each detected zone
| `mute` | **dict**[Zone, **bool**] | Mute status for each detected zone
| `source_id` | **dict**[Zone, **str**] | Active source ID for each detected zone
| `source_name` | **dict**[Zone, **str**] | Active source name for each detected zone
| `listening_mode` | **str*- | Name of the currently active listening mode
| `listening_mode_id` | **str*- | ID of the currently active listening mode
| `media_control_mode` | **dict**[Zone, **str**] | Media control mode for each detected zone
| `tone` | **dict**[Zone, **dict**] | Tone attributes for each detected zone
| `amp` | **dict**[**str*- \| Zone, **str**] | Current AVR amp attributes
| `tuner` | **dict**[**str*- \| Zone, **str**] | Current AVR tuner attributes
| `dsp` | **dict**[**str*- \| Zone, **str**] | Current AVR DSP attributes
| `video` | **dict**[**str*- \| Zone, **str**] | Current AVR video parameters
| `audio` | **dict**[**str*- \| Zone, **str**] | Current AVR audio parameters
| `system` | **dict**[**str*- \| Zone, **str**]| AVR system attributes
| `channel_level` | **dict**[**str**, dict[Zone, **Any**]] | Current AVR channel level, indexed by zone and channel name
| `ip_control_port_n` | **str*- | IP control ports configured on the AVR (where `n` is the port index)

## Command line interface (CLI)

A very simple command line interface `aiopioneer` is available to connect to the AVR, send commands and receive responses. It can be used to test the capabilities of the library against your specific AVR.

On Home Assistant, you can run the CLI within the Home Assistant container where the [`pioneer_async`](https://github.com/crowbarz/ha-pioneer_async) integration has been installed. Log into to the HA host via SSH, then run: `docker exec -it homeassistant aiopioneer <host>`.

Invoke the CLI with the following arguments:

| Argument | Default | Description
| --- | --- | ---
| hostname | required | hostname for AVR connection
| `--port`<br>`-p` | 8102 | port for AVR connection
| `--no-query-zones`<br>`+Z` | None | skip AVR zone query
| `--reconnect`\|`-R`<br>\| `--no-reconnect` | false | enable/disable AVR reconnection request

The CLI accepts all AVR commands, as well as the helper commands below. The `list` command shows all accepted commands and their arguments.

| Command | Argument | Description
| --- | --- | ---
| `exit` | | Exit the CLI
| `connect` | [`--reconnect`] | Connect to the AVR. If `--reconnect` is specified, reconnect to the AVR on disconnect
| `disconnect` | [`--reconnect`] | Disconnect from the AVR. If `--reconnect` is specified, attempt to reconnect to the AVR after disconnecting
| `zone` | _zone_ | Set the active AVR zone to _zone_
| `logging_level` | _log_level_ | Set the root logging level to _log_level_. Valid log levels are: `debug`, `info`, `warning`, `error`, `critical`
| `get_params` | | Show the currently active set of parameters
| `get_user_params` | | Show the currently active set of user parameters
| `set_user_params` | _params_ (JSON) | Set the user parameters to _params_ (see [CLI JSON arguments](#cli-json-arguments) below)
| `get_properties` | \[ `--zones` \]<br>\[ `--power` \]<br>\[ `--volume` \]<br>\[ `--max_volume` \]<br>\[ `--mute` \]<br>\[ `--source_id` \]<br>\[ `--source_name` \]<br>\[ `--media_control_mode` \]<br>\[ `--tone` \]<br>\[ `--amp` \]<br>\[ `--tuner` \]<br>\[ `--dsp` \]<br>\[ `--video` \]<br>\[ `--system` \]<br>\[ `--audio` \]<br>\[ `--channel_level` \] | Show the current cached AVR properties for the specified property groups, or all property groups if none are specified
| `get_scan_interval` | | Show the current scan interval.
| `set_scan_interval` | _scan_interval_ (float) | Set the scan interval to _scan_interval_
| `refresh` | [`--full`] | Refresh the cached AVR properties for the active zone, or all zones if `--full` is specified
| `query_device_info` | | Query the AVR for device information
| `query_zones` | | Query the AVR for available zones. Ignore zones specified in parameter `ignored_zones` (list)
| `get_source_dict` | | Show the set of available source names and IDs that can be used with the `select_source` command
| `set_source_dict` | _sources_ (JSON) | Set the sources mapping manually to _sources_ (see [CLI JSON arguments](#cli-json-arguments) below)
| `build_source_dict` | | Query the sources mapping from the AVR
| `get_listening_modes` | | Show the set of available listening modes
| `set_tuner_frequency` | _band_ _frequency_ | Set the tuner band and frequency. (Use `set_tuner_band_am` or `set_tuner_band_fm` to set the band only)
| `media_control` | `play` \| `pause` \| `stop` \| `previous` \| `next` \| `rw` \| `ff` \| `repeat` \| `shuffle` | Send media control command for active zone
| `get_supported_media_controls` | | Show the currently available media controls for the active zone
| `debug_listener` | \[ `on` \| `off` \] | Enable/disable the `debug_listener` parameter
| `debug_updater` | \[ `on` \| `off` \] | Enable/disable the `debug_updater` parameter
| `debug_command` | \[ `on` \| `off` \] | Enable/disable the `debug_command` parameter
| `debug_command_queue` | \[ `on` \| `off` \] | Enable/disable the `debug_command_queue` parameter
| `send_raw_command` or `>` | _raw_command_ | Send the raw command _raw_command_ to the AVR

**NOTE:*- The CLI interface may change in the future, and should not be used in scripts. Use the [Python API](#python-api) instead.

### CLI JSON arguments

> [!CAUTION]
> Sources, listening modes and speaker system modes are specified as a **dict*- with **int*- keys. JSON does not support **int*- for **dict*- keys. Where these parameters are provided as CLI arguments, keys should be specified as **str**. These will be converted to **int*- automatically.

## Source list

The list below shows the source ID that corresponds to each AVR source:

> [!NOTE]
> This list is not exhaustive. Some AVR models support sources additional to those listed below.

| ID | Default Name
| -- | ---
| 25 | BD
| 04 | DVD
| 06 | SAT/CBL
| 10 | VIDEO
| 15 | DVR/BDR
| 19 | HDMI1
| 20 | HDMI2
| 21 | HDMI3
| 22 | HDMI4
| 23 | HDMI5
| 24 | HDMI6
| 34 | HDMI7
| 49 | GAME
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

## Breaking changes

### 0.10

- `PioneerAVR.get_listening_modes` now returns **list**[**str**]. This was changed in 0.9.0 but inadvertently omitted from the list of breaking changes
- Several AVR properties have been renamed:
  - `listening_mode_raw` has been renamed `listening_mode_id` for consistency with `source_id`
  - `channel_levels` has been renamed to `channel_level`
  - System property `speaker_system_raw` has been renamed to `speaker_system_id` for consistency
- The values for the `amp.hdmi_out` and `system.external_hdmi_trigger_[12]` properties have been revised to harmonise HDMI port names
- Many AVR commands have been renamed for improved consistency:
  - `set_listening_mode` has been renamed to `select_listening_mode`
  - `operation_ipod_*` has been renamed to `ipod_*`
  - `operation_network` has been renamed to `network_*`
  - `operation_adapaterport_*` has been renamed to `adapterport_*` (with spelling correction)
  - `operation_mhl_*` has been renamed to `mhl_*`
  - `operation_amp_*` has been renamed to `amp_*`
  - `increase_tuner_preset` has been renamed to `tuner_next_preset`
  - `decrease_tuner_preset` has been renamed to `tuner_previous_preset`
  - `increase_tuner_frequency` has been renamed to `tuner_increase_frequency`
  - `decrease_tuner_frequency` has been renamed to `tuner_decrease_frequency`
  - `turn_on/off`has been renamed to `power_on/off` to align with AVR API documentation
  - `query_system_mcacc_diagnostics` has been renamed to `query_system_mcacc_diagnostic_status`
  - `query_dsp_mcacc_memory_query` has been renamed to `query_dsp_mcacc_memory_set`
  - `query_center_spread` has been renamed to `query_dsp_center_spread`
  - `query_rendering_mode` has been renamed to `query_dsp_rendering_mode`
  - `query_tuner_am_step` has been renamed to `query_tuner_am_frequency_step` to match the property and code map class name
  - `set/query_channel_levels` have been renamed to `set/query_channel_level` (singular)
- Several `PioneerAVR` methods have been renamed:
  - `update` has been renamed to `refresh` to better reflect what this method actually does
  - `set_channel_levels` has been renamed to `set_channel_level`
- The `PioneerAVR.properties.get_source_list` method has been removed. Use `PioneerAVR.properties.get_source_dict().values()` to retrieve the list of valid sources for a zone
- The `update` CLI command has also been renamed to `refresh` to match the `PioneerAVR` method
- `CommandItem` constructor arguments have been renamed:
  - `skip_if_startup` has been renamed `skip_if_starting`
  - `skip_if_executing` has been repurposed as `skip_if_refreshing` and skips queuing the command if a pending refresh has been set for the zone
- `CHANNELS_ALL` has moved from `aiopioneer.const` to the `aiopioneer.decoders.audio.SpeakerChannel` class


### 0.9

- The `query_device_model` method is now deprecated and no longer needs to be called on AVR connect. It will be invoked internally if param `model` is not set.
- Some AVR commands have been renamed for consistency:
  - Rename DSP commands: `digital_dialog_enhancement` -> `dialog_enhancement`, `analog_input_att` -> `input_attenuator`, `drc` -> `dynamic_range`, `lfe_att` -> `lfe_attenuator`
  - Rename amp commands: `speaker_status` -> `speaker_mode`, `hdmi_out_status` -> `hdmi_out`, `hdmi_audio_status` -> `hdmi_audio`, `pqls_status` -> `pqls`, `sleep_remain_time` -> `sleep_time`
  - Add `dsp` prefix to `center_spread` and `rendering_mode` commands
  - Add `video` prefix to `super_resolution` command
- `set_panel_lock`, `set_remote_lock` and `set_dimmer` methods have been deprecated as they can now be set via the `set_amp_settings` method
- Cyclic code map values have been removed. Set the new value explicitly instead
- `ipod_control_commands` and `tuner_control_commands` property methods have been removed as these were creating circular imports
- `get_runtime_param` and `set_runtime_param` methods are removed. All runtime params have been migrated to AVRProperties
- `Pioneer` have been dropped from `PioneerAVRConnection`, `PioneerAVRParams`, `PioneerAVRProperties`, and `PioneerError` class names for brevity
- `PioneerAVR.update_listening_mode` has been removed, `AVRProperties.update_listening_mode` should be used instead
- AVR command `query_source_name` now accepts a numeric source ID
- AVR command `set_source_name` accepts *source_name*=**None*- to reset name, and no longer accepts the *default- argument
- Params `zone_1_sources`, `zone_2_sources`, `zone_3_sources` and `hdzone_sources` are now of type **list[int]**
- Param `amp_speaker_system_modes` is now of type **dict[int, str]**
- Param `enabled_functions` now accepts `channel` as an item instead of `channels`
- `select_source` now accepts a single source, which can be a source name (**str**) or a source ID (**int**)
- `set_source_dict` now accepts a `sources` argument of type **dict[int, str]**. The source ID is now the key of the dict and the value is the source name, previously the key was the source name
- `get_source_dict` now returns a value of type **dict[int, str]**
- `get_source_dict` now returns a value of type **dict[int, str]**
- `get_listening_modes` now returns a value of type **list[str]**.

### 0.8

- To enable params to be accessible from AVR response parsers and also to reduce the size of the main class, the `PioneerAVR` class has been split out to the classes listed below. References to parameter and properties methods and attributes will need to be updated to be accessed via the `params` and `properties` attributes of the `PioneerAVR` object. All other public attributes have moved to the new classes.
  - `AVRParams` contains the user and run-time parameter get/set methods. Some method names have changed, please consult the updated documentation for details
  - `AVRProperties` contains the cache of AVR properties collected from its responses
  - `AVRConnection` contains the connection related methods, although `PioneerAVR` inherits from the new class so the connection methods are still accessible via the `PioneerAVR` class
- Commands that are sent to the AVR to perform full updates are now executed via the command queue. This eliminates the previous interaction between the updater and command queue threads, as the updater now simply schedules updates via the command queue
- The order of queries during a full update has been modified so that amp, DSP and tone queries are executed before video queries
- The `Zones` enum has been renamed `Zone` for improved consistency
- The `param` module has been renamed `params` for improved consistency
- Exception handling within the AVR interface methods has been made more robust. The AVR listener and responders will now only trigger disconnection from the AVR (and reconnection if requested) if the AVR connection drops. Notably, parser exceptions and timeouts to power, volume and mute queries will no longer cause the AVR connection to disconnect and reconnect. This should fully resolve issues such as crowbarz/ha-pioneer_async#54
- Not detecting Zone 1 on the AVR on module startup has been demoted from an error to a warning and Zone 1 is assumed to exist. Despite this change, most AVR commands will still not work when the AVR is in this state. It is now up to the client to check that Zone 1 has been discovered and handle the case when it is not
- The `source` AVR zone property has been renamed `source_id`, and an additional `source_name` property has been introduced that contains the mapped name for the source for each zone
- The `query_device_model` method has been introduced to query the device model and set default model parameters. Previously, the `query_device_info` queried all device information including the device model regardless of whether the AVR main zone was powered on. Clients that previously called `query_device_info` at module startup should now call `query_device_model`. `query_device_info` will be automatically called when the main zone is powered on for the first time after connecting, and no longer needs to be called by the client
- If Zone 1 is not powered on at integration startup, queries for AVR device info is deferred until Zone 1 is first powered on.
- The `query_audio_information` and `query_video_information` commands have been renamed `query_basic_audio_information` and `query_basic_video_information`. These basic query commands, in addition to `query_listening_mode`, are executed with a delay after all zone power and source operations whenever any zone is powered on
- The `system_query_source_name` has been renamed to `query_source_name` to avoid being sent during AVR device info queries
- The `query_sources` method has been removed. `AVRParams.get_runtime_param(PARAM_QUERY_SOURCES)` should be used instead
- The `update_zones` method has been removed. Change the AVR zones by recreating the `PioneerAVR` object with the new zones
- The `PioneerAVR.initial_update` property has moved to run-time param `PARAM_ZONES_INITIAL_REFRESH` and is now a set of `Zone`. The `AVRParams.zones_initial_refresh` property is provided as a convenience to access this run-time parameter
- System parameters have been re-termed as run-time parameters to better reflect their function
- The `AVRProperties.zones` property now has typing `set[Zone]`

### 0.7

- Most PioneerAVR methods now raise exceptions derived from `PioneerError` when an error is encountered, rather than returning `false`, `None` or similar error value. Some instances that currently raise `ValueError` or `SystemError` will also raise `PioneerError` subclasses in the near future
- `send_raw_request` no longer accepts an argument `ignore_error` and will always raise exceptions on error. Use `ignore_error` with `send_command` to have exceptions handled for you
- asyncio yields have been optimised and minimised, which may cause certain sequences of operations to happen in a different order

### 0.6

- Python requirement bumped to 3.11 for `StrEnum`
- `Zones` enum now used on all methods accepting zone arguments (except in params)
- Zone argument removed from tuner methods as tuner is independent of zone
- `TunerBand` enum now used to specify a tuner band
- `update` now waits for the update to finish by default
- `set_tuner_preset` has been renamed to `select_tuner_preset`
- `get_zone_listening_modes` has been renamed to `get_listening_modes`
- `set_listening_mode` has been renamed to `select_listening_mode`
- `tuner_*`, `get_zone_listening_modes`, `set_panel_lock`, `set_remote_lock` and `set_dimmer` methods no longer accept a zone argument
- The `suffix` argument of the `send_command` method has been reordered after the `prefix` argument
- Response codes marked `---` now return **None**
- Dimmer mode, tone mode and dB strings have been updated

### 0.5

- `get_sound_modes` was renamed to `get_zone_listening_modes` to reflect Pioneer AVR terminology
- `disable_autoquery` was renamed `disable_auto_query` to better match the underlying variable name
- `amplifier_speaker_system_modes` and `disabled_amplifier_listening_modes` were shortened to `amp_speaker_system_modes` and `disabled_amp_listening_modes` respectively

### 0.4

- `zone_z_sources` was renamed `hdzone_sources` for even more consistency

### 0.3

- `zone_h_sources` was renamed `zone_z_sources` for consistency

### 0.2

- `volume_step_delta` has been removed entirely
- By default, a number of additional queries are sent at module startup to the AVR to gather amp, tuner and channel levels attributes. If your AVR does not handle these additional queries well, they can be disabled by setting parameter `disable_autoquery` to `true`

### 0.1

- `_PioneerAVR.__init__()` no longer accepts `command_delay`, `volume_workaround` and `volume_steps` arguments. Configure these parameters using the equivalent `PARAM_*` keys in the `params` dict, passed in via the constructure or set via `set_user_params()`

## References

- Home Assistant Pioneer integration: [https://www.home-assistant.io/integrations/pioneer/](https://www.home-assistant.io/integrations/pioneer/)
- Pioneer commands references: [https://github.com/rwifall/pioneer-receiver-notes](https://github.com/rwifall/pioneer-receiver-notes)
- Another asyncio Pioneer HA component: [https://github.com/realthk/asyncpioneer](https://github.com/realthk/asyncpioneer)
- Pioneer IP and serial IO control documentation: [https://www.pioneerelectronics.com/PUSA/Support/Home-Entertainment-Custom-Install/RS-232+&+IP+Codes/A+V+Receivers](https://www.pioneerelectronics.com/PUSA/Support/Home-Entertainment-Custom-Install/RS-232+&+IP+Codes/A+V+Receivers)
  - This library supports many of the commands listed in the **2015 Pioneer & Elite AVR External Command*- document
