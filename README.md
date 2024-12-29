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
- Queries device information from the AVR: MAC address, software version, model
- Ability to set internal parameters to change the API functionality, eg. maximum volume, volume step change delta
- Defaults for internal parameters set via custom profiles based on AVR model
- Includes workaround for AVRs with an initial volume set on the Main Zone (eg. VSX-930)
- Supports AVRs that do not support setting the volume level by emulating using up/down commands (eg. VSX-S510)
- Command line client for sending commands and testing
- Supports all listening mode functions
- Supports all video related functions
- Supports panel and remote locking
- Supports most AMP related functions
- Supports all tone functions
- Supports most zone power functions
- Supports all zone input functions
- Supports all zone volumne and mute functions
- Supports setting of tuner band and preset
- Supports setting tuner frequency directly for AVRs that support this via the API, and also by stepping the frequency up/down

## Parameters

There are several types of parameters that modify the library's functionality. These are listed below in order of increasing priority:

- **Default parameters**: these are the defaults for all of the parameters
- **Model parameters**: these parameters are determined by the AVR model as detected by the library. Custom profiles for specific AVR models are defined in [`aiopioneer/param.py](https://github.com/crowbarz/aiopioneer/blob/main/aiopioneer/param.py)
- **User parameters**: these parameters are provided by the user at instantiation, and can also be updated via the `set_user_params` method
- **Run-time parameters**: these parameters are set by the library at run-time

Where a parameter is specified at more than one level, the higher priority parameter takes precedence. Thus, a user specified parameter will override any value that is determined by the AVR model.

> [!NOTE]
> YAML syntax is used to indicate values the table below. Use Python equivalents (`false` -> `False`, `true` -> `True`, `null` -> `None` etc.) when calling the Python API directly, and JSON syntax if specifying parameters manually via the Home Assistant integration.

| Name | Type | Default | Description
| ---- | ---- | ------- | -----------
| `ignored_zones` | list | `[]` | List of zones to ignore even if they are auto-discovered. Specify Zone IDs as strings: "1", "2", "3" and "Z"
| `command_delay` | float | `0.1` | Insert a delay between sequential commands that are sent to the AVR. This appears to make the AVR behave more reliably during status polls. Increase this value if debug logging shows that your AVR times out between commands
| `max_source_id` | int | `60` | Maximum source ID that the source discovery queries. Reduce this if your AVR returns errors
| `max_volume` | int | `185` | Maximum volume for the Main Zone
| `max_volume_zonex` | int | `185` | Maximum volume for zones other than the Main Zone
| `power_on_volume_bounce` | bool | `false` | On some AVRs (eg. VSX-930) where a power-on is set, the initial volume is not reported by the AVR correctly until a volume change is made. This option enables a workaround that sends a volume up and down command to the AVR on power-on to correct the reported volume without affecting the power-on volume
| `volume_step_only` | bool | `false` | On some AVRs (eg. VSX-S510), setting the volume level is not supported natively by the API. This option emulates setting the volume level using volume up and down commands.
| `ignore_volume_check` | bool | `false` | Don't check volume when determining whether a zone exists on the AVR. Useful for AVRs with an HDZone that passes through audio
| `zone_1_sources` | list | `[]` | (>0.4) Customises the available sources for use with Zone 1. Defaults to all available sources
| `zone_2_sources` | list | [see source](https://github.com/crowbarz/aiopioneer/blob/dev/aiopioneer/param.py#L61) | Customises the available sources for use with Zone 2 (some AVRs do not support all sources)
| `zone_3_sources` | list | [see source](https://github.com/crowbarz/aiopioneer/blob/dev/aiopioneer/param.py#L61) | Customises the available sources for use with Zone 3 (some AVRs do not support all sources)
| `hdzone_sources` | list | [see source](https://github.com/crowbarz/aiopioneer/blob/dev/aiopioneer/param.py#L61) | Customises the available sources for use with HDZone (some AVRs do not support all sources)
<!-- unimplemented
| `hdzone_volume_requirements` | list | `["13", "15", "05", "25"]` | A list of sources that HDZone must be set to for volume control, some AVRs do not support HDZone volume at all (see `ignore_volume_check` above) and some only allow control of certain sources -->
| `amp_speaker_system_modes` | dict | `....` | Customises the names of speaker system modes. Different generations of AVR will name zones slighty differently. For example, the SC-LX57 names speaker system mode `15` as `5.1ch Bi-Amp + ZONE2` however this can also be called `5.2ch Bi-Amp + HDZONE` on newer AVRs
| `extra_amp_listening_modes` | dict | [see source](https://github.com/crowbarz/aiopioneer/blob/dev/aiopioneer/const.py#L24) | (>0.5) Additional listening modes that are added to the list of all possible listening modes for the AVR. This list is used to decode the listening mode ID returned by the AVR. See the source for the format for listening mode definition
| `enabled_amp_listening_modes` | list | `[]` | (>0.5) A list of listening mode IDs to be made available for selection. If specified, then no listening mode IDs will be included by default. All enabled source names must be unique, and duplicated names are ignored. The additional listening modes must be actually supported by the AVR, and will return an error (usually `E02`) when an unsupported listening mode is selected. This list is predefined for some AVRs, and specifying this parameter manually will override the model specific default disable list
| `disabled_amp_listening_modes` | list | `[]` | A list of listening mode IDs to be disabled. Listening mode IDs that are also specified in `enabled_amp_listening_modes` will be disabled. This list is predefined for some AVRs, and specifying this parameter manually will override the model specific default disable list
| `video_resolution_modes` | list | `['0', '1', '3', '4', '5', '6', '7', '8', '9']` | Sets the available video resolutions. Not all AVRs support the same resolution settings. This defaults to all of the latest resolutions from FY16
| `mhl_source` | string | `null` | Sets the MHL source ID. This is used for media controls. This information cannot be queried automatically
| `enabled_functions` | list | `["basic", "audio", "amp", "dsp", "tone", "channels", "video", "tuner", "system", "display"]` | Change the functions that are enabled by the API, adding more functions will increase the amount of time it takes to complete a full init and update
| `disable_auto_query` | bool | `false` | Set to `true` to disable auto queries on first zone power on for all functions apart from core functionality (power, source, volume and mute)
| `am_frequency_step` | int | `null` | Optional setting to configure the tuner AM frequency step. If not specified, it will be queried from the AVR if supported by the AVR, otherwise it will be determined by stepping the frequency up and down when the AM tuner is first used
| `always_poll` | bool | `false` | Always poll the AVR every _scan_interval_. If set to `false`, out of band status responses from the AVR will reset the polling interval
| `debug_listener` | bool | `false` | Enables additional debug logging for the listener task
| `debug_responder` | bool | `false` | Enables additional debug logging for the responder task
| `debug_updater` | bool | `false` | Enables additional debug logging for the updater task
| `debug_command` | bool | `false` | Enables additional debug logging for commands sent and responses received
| `debug_command_queue` | bool | `false` | Enables additional debug logging for the command queue task

If your model of AVR always needs specific parameters to be set for the library to function properly, then please create a PR to add a custom profile for the AVR model.

## Python API

The library exposes a Python API through the **PioneerAVR** class. The class methods are listed below:

`PioneerAVR.__init__(`_host_, _port_ = DEFAULT_PORT, _timeout_: **float** = DEFAULT_TIMEOUT, _scan_interval_: **float** = DEFAULT_SCAN_INTERVAL, _params_: **dict[str, str]** = **None** `)`

Constructor for the **PioneerAVR** class. The connection parameters are used when `PioneerAVR.connect` is called. After connection is established, the AVR will be polled every _scan_interval_ seconds. If the `always_poll` parameter is set, the poll timer is reset when a response from the AVR is received. Optional user parameters are provided via _params_.

### Connection methods (inherited by `PioneerAVR`)

_awaitable_ `PioneerAVRConnection.connect(`_reconnect_: **bool** = True`)`

Establish a connection to the AVR. Set _reconnect_ to **True** to re-establish the connection if it is disconnected.

_awaitable_ `PioneerAVRConnection.disconnect(`_reconnect_: **bool**`)`

Disconnect from the AVR. Attempt to re-establish the connection if enabled at connect, or overridden by specifying _reconnect_.

_awaitable_ `PioneerAVRConnection.shutdown()`

Permanently disconnect from the AVR. Does not attempt reconnection.

_awaitable_ `PioneerAVRConnection.set_timeout(`_timeout_: **float**`)`

Set command and socket keepalive timeouts.

_property_ `available`: **bool**

Whether integration is connected to the AVR.

_property_ `scan_interval`: **float**

Number of seconds between polls for AVR full updates.

### Update methods

_awaitable_ `PioneerAVR.update(`_zones_: **list[Zone]** = **None**, _wait_: **bool** = **True**`)`

Update of the cached properties from the AVR via the command queue. <br/>
Refresh the AVR zones _zones_, or all AVR zones if not specified. <br/>
Wait for the update to be completed if _wait_ is **True**. <br/>

_awaitable_ `PioneerAVR.set_scan_interval(`_scan_interval_: **int**`)`

Set the scan interval to _scan_interval_ and restart the updater task.

### AVR system methods

_awaitable_ `PioneerAVR.turn_on(`_zone_: Zone = Zone.Z1`)`:

Turn on the Pioneer AVR zone.

_awaitable_ `PioneerAVR.turn_off(`_zone_: Zone = Zone.Z1`)`:

Turn off the Pioneer AVR zone.

_awaitable_ `PioneerAVR.query_device_model()`

Query the AVR for device model. Updates the model parameters if device model is changed.

_awaitable_ `PioneerAVR.query_device_info()`

Query the AVR for device information.

_awaitable_ `PioneerAVR.query_zones(`_force_update_: **bool** = **True**`)`

Query the AVR for available zones by querying the power status for each zone and checking if the AVR responds.
Ignores zones listed in the `ignored_zones` parameter. <br/>
If the `ignore_volume_check` parameter is not set, then additionally query the zone volume as well.

_awaitable_ `PioneerAVR.set_panel_lock(`_panel_lock_: **str**`)`:

Set the panel lock.

_awaitable_ `PioneerAVR.set_remote_lock(`_remote_lock_: **bool**`)`:

Set the remote lock.

_awaitable_ `PioneerAVR.set_dimmer(`_dimmer_: **str**, _zone_: Zone = Zone.Z1`)`:

Set the display dimmer.

### AVR source methods

_awaitable_ `PioneerAVR.select_source(`_source_: **str** = **None**, _source_id_: **str** = **None**, _zone_: Zone = Zone.Z1`)`:

Set the input source for _zone_ to name _source_name_ or ID _source_id_ (requires one argument.)

_awaitable_ `PioneerAVR.build_source_dict()`

Query the available sources names from the AVR. <br/>
Parameter `max_source_id` determines the highest source ID that is queried.

`PioneerAVRProperties.set_source_dict(`_sources_: **dict**[**str**, **str**]`)`

Manually set the available sources to the dict _sources_, where the keys are source IDs (padded to 2 chars) and the values are the corresponding source names.

`PioneerAVRProperties.get_source_list(`_zone_: Zone = Zone.Z1`)` -> **list**[**str**]

Return the set of currently available source names for _zone_. The source names can be used with the `select_source` method.

`PioneerAVRProperties.get_source_dict(`_zone_: Zone = **None**`)` -> **dict**[**str**, **str**]

Return a dict of currently available source names to source ID mappings for _zone_. <br/>
If _zone_ is **None**, then return the dict of all available source names to source ID mappings.

`PioneerAVRProperties.get_source_name(`_source_id_: **str**`)` -> **str**

Return the source name for _source_id_.

_awaitable_ `PioneerAVR.set_source_name(`_source_id_: **str**, _source_name_: **str** = "", _default_: **bool** = **False**`)` -> **bool**

Renames _source_id_ to _source_name_ on the AVR. <br/>
If _default_ is **True**, reset _source_id_ to the default source name.

`PioneerAVRProperties.clear_source_id(`_source_id_: **str**`)`

Clear the name mapping for _source_id_.

### Command queue

`PioneerAVR.queue_command(`_command_: **str** | **list**, _skip_if_queued_: **bool** = **True**, _insert_at_: **int** = -1`)` -> **None**

Add _command_ to the command queue, to to be sent in the background to the AVR or executed as a local command. Starts the command queue task if not already running. <br/>
_command_ may be specified as a **str**, or a **list** whose first element is a **str** that is used as the command to execute. The list form is used for local commands that support arguments of arbitrary type.
The following local commands are supported, these are mainly used by the command parsers for more complex actions:

- `_power_on`: execute initial refresh on zone power on
- `_full_refresh`: perform a full refresh on all AVR Zones
- \[ `_refresh_zone`, _zone_: **Zone** \]: perform a refresh on the specified zone
- \[ `_delayed_query_basic`, _delay_: **float** \]: schedule a basic AVR query if parameter `disable_auto_query` is not enabled
- `_query_basic`: perform a basic AVR query if parameter `disable_auto_query` is not enabled
- `_calculate_am_frequency_step`: calculate the tuner AM frequency step
- \[ `_sleep`, _delay_: **float** \]: sleep for _delay_ before executing the next command in the queue

If _skip_if_queued_ is **True** and _command_ is already present in the command queue, then the command is not queued again. Local command arguments are included in the match. <br\>
Insert the command at queue position _insert_at_ if specified. Inserts by default at end of the queue.

### Low level AVR command methods (inherited by `PioneerAVR`)

_awaitable_ `PioneerAVRConnection.send_command(`_command_: **str**, _zone_: Zone = Zone.Z1, _prefix_: **str** = "", _suffix_: **str** = "", _ignore_erro* = **None**, _rate_limit_: **bool** = **True**`)` -> **bool** | **None**

Send command _command_ for zone _zone_ to the AVR, prefixed with _prefix_ and/or suffixed with _suffix_ if specified. <br/>
If _command_ does not generate a response, then returns **True** if the command was successfully sent.
Otherwise, returns the response received from the AVR, **None** if timed out, or **False** if an error response was received. <br/>
If _ignore_error_ is **None** (default), then raise an exception on error. If _ignore_error_ is **True**, then log the error as level debug, otherwise log the error as level error. <br/>
Raises `AVRUnavailable` if the AVR is disconnected, `AVRResponseTimeoutError` on timeout, and `AVRCommandError` if the request returned an error.<br/>
If _rate_limit_ is **True**, then rate limit the commands sent to the AVR in accordance with the `command_delay` parameter.

_awaitable_ `PioneerAVRConnection.send_raw_command(`_command_: **str**, _rate_limit_: **bool** = True`)`

Send a raw command _command_ to the AVR.
If _rate_limit_ is **True**, then rate limit the commands sent to the AVR in accordance with the `command_delay` parameter. <br/>
Raises `AVRUnavailable` if the AVR is disconnected.

_awaitable_ `PioneerAVRConnection.send_raw_request(`_command_: **str**, _response_prefix_: **str**, _rate_limit_: **bool** = **True**`)` -> **str** | **bool** | **None**

Send a raw command _command_ to the AVR and wait for a response with prefix _response_prefix_.
Returns the response received from the AVR.<br/>
Raises `AVRUnavailable` if the AVR is disconnected, `AVRResponseTimeoutError` on timeout, and `AVRCommandError` if the request returned an error.<br/>
If _rate_limit_ is **True**, then rate limit the commands sent to the AVR in accordance with the `command_delay` parameter.

### AVR tuner methods

_awaitable_ `PioneerAVR.select_tuner_band(`_band_: TunerBand = TunerBand.FM`)` -> **bool**

Set the tuner band to _band_.

_awaitable_ `PioneerAVR.set_tuner_frequency(`_band_: TunerBand, _frequency_: **float** = **None**`)` -> **bool**

Set the tuner band to _band_ and tuner frequency to _frequency_.
Step the frequency up or down if it cannot be set directly.

_awaitable_ `PioneerAVR.select_tuner_preset(`_tuner_class_: **str**, _preset_: **int**`)` -> **bool**:

Select the tuner preset _preset_ in class _tuner_class_.

_awaitable_ `PioneerAVR.tuner_previous_preset()`

Select the previous tuner preset.

_awaitable_ `PioneerAVR.tuner_next_preset()`

Select the next tuner preset.

### AVR audio/video methods

_awaitable_ `PioneerAVR.select_listening_mode(`_mode_name_: **str** = **None**, _mode_id_: **str** = **None**`)` -> **bool**

Set the listening mode to name _mode_name_, or ID _mode_id_ (requires one argument.)
Must be a listening mode valid for the current sound input as returned by `get_listening_modes`.

`PioneerAVR.get_listening_modes()` -> **dict**[**str**, **str**] | **None**

Return dict of valid listening mode mapping to names for the AVR.

_awaitable_ `PioneerAVR.set_volume_level(`_target_volume_: **int**, zone: Zones = Zones.Z1`)`

Set the volume level for zone _zone_ to _target_volume_.
_target_volume_ must be between 0 and 185 inclusive for Zone 1, and between 0 and 81 inclusive for all  other zones.

_awaitable_ `PioneerAVR.mute_on(`_zone_: Zone = Zone.Z1`)` -> **bool**

Turn mute on for zone _zone_.

_awaitable_ `PioneerAVR.mute_off(`_zone_: Zone = Zone.Z1`)` -> **bool**

Turn mute off for zone _zone_.

_awaitable_ `PioneerAVR.set_tone_settings(`_tone_: **str** = **None**, _treble_: **int** = **None**, _bass_: **int** = **None**, _zone_: Zone = Zone.Z1 `)`*

Set the tone settings for zone _zone_ to _tone_. When _tone_ is set to `On`, _treble_ specifies the treble and _bass_ specifies the bass.

_awaitable_ `PioneerAVR.set_amp_settings(`_speaker_config_: **str** = **None**, _hdmi_out_: **str** = **None**, _hdmi_audio_output_: **bool** = **None**, _pqls_: **bool** = **None**, _amp_: **str** = **None**, _zone_: Zone = Zone.Z1`)` -> **bool**

Set amplifier function settings for zone _zone_.

`PioneerAVRProperties.get_supported_media_controls(`_zone_: Zone`)` -> **list**[**str**]

Return a list of all valid media control actions for a given zone. If the provided zone source is not currently compatible with media controls, **None** will be returned.

_property_ `PioneerAVRProperties.ipod_control_commands`: **list**[**str**]

Return a list of all valid iPod control modes.

_property_ `PioneerAVRProperties.tuner_control_commands`: **list**[**str**]

Return a list of all valid tuner control commands.

_awaitable_ `PioneerAVR.set_channel_levels(`_channel_: **str**, _level_: **float**, _zone_: Zone = Zone.Z1`)` -> **bool**

Set the level (gain) for amplifier channel in zone _zone_.

_awaitable_ `PioneerAVR.set_video_settings(`_zone_: Zone, **_arguments_`)` -> **bool**

Set video settings for zone _zone_.

_awaitable_ `PioneerAVR.set_dsp_settings(`_zone_: Zone, **_arguments_`)` -> **bool**

Set the DSP settings for the amplifier for zone _zone_.

_awaitable_ `PioneerAVR.media_control(`_action_: **str**, _zone_: Zone = Zone.Z1`)` -> **bool**

Perform media control activities such as play, pause, stop, fast forward or rewind.

### AVR zone callback methods

`PioneerAVR.set_zone_callback(`_zone_: Zone, _callback_: **Callable**[..., **None**]`)`

Register callback _callback_ for zone _zone_.

`PioneerAVR.clear_zone_callbacks()`

Clear callbacks for all zones.

### Parameter methods

`PioneerAVRParams.set_default_params_model(`_model_: **str**`)` -> **None**

Set default parameters based on device model.

`PioneerAVRParams.set_user_params(`_params_: **dict**[**str**, **Any**] = **None**`)` -> **None**

Set user parameters and update current parameters.

`PioneerAVRParams.set_user_param(`_param_: **str**, _value_: **Any**`)` -> **None**

Set a user parameter.

`PioneerAVRParams.set_runtime_param(`_param_: **str**, _value_: **Any**`)` -> **None**

Set a run-time parameter.

_property_ `PioneerAVRParams.zones_initial_refresh`: **set**[Zone]

Return set of zones that have completed an initial refresh.

_property_ `PioneerAVRParams.default_params`: **dict**[**str**, **Any**]

Get a copy of current default parameters.

_property_ `PioneerAVRParams.user_params`: **dict**[**str**, **Any**]

Get a copy of user parameters.

_property `PioneerAVRParams.params_all` -> **dict**[**str**, **Any**]

Get a copy of all current parameters.

`PioneerAVRParams.get_param(`_param_name_: **str**`)` -> **Any**

Get the value of the specified parameter.

`PioneerAVRParams.get_runtime_param(`_param_name_: **str**`)` -> **Any**

Get the value of the specified run-time parameter.

### AVR Properties

Listed below are the public attributes of a `PioneerAVRProperties` object that contains the current state of the AVR. Use a `Zone` enum to access zone specific attributes for those that are indexed by zone.

| Attribute | Type | Description
| --- | --- | ---
| `model` | **str** \| **None** | Model number returned by the AVR
| `software_version` | **str** \| **None** | Software version returned by the AVR
| `mac_addr` | **str** \| **None** | System MAC address returned by the AVR
| `zones` | **list**[Zone] | List of all zones detected on the AVR
| `power` | **dict**[Zone, **bool**] | Power status for each detected zone
| `volume` | **dict**[Zone, **int**] | Volume status for each detected zone
| `max_volume` | **dict**[Zone, **int**] | Maximum valid volume for each detected zone
| `mute` | **dict**[Zone, **bool**] | Mute status for each detected zone
| `source_id` | **dict**[Zone, **str**] | Active source ID for each detected zone
| `source_name` | **dict**[Zone, **str**] | Active source name for each detected zone
| `listening_mode` | **str** | Name of the currently active listening mode
| `listening_mode_raw` | **str** | ID of the currently active listening mode
| `media_control_mode` | **dict**[Zone, **str**] | Media control mode for each detected zone
| `tone` | **dict**[Zone, **dict**] | Tone attributes for each detected zone
| `amp` | **dict**[**str** \| Zone, **str**] | Current AVR amp attributes
| `tuner` | **dict**[**str** \| Zone, **str**] | Current AVR tuner attributes
| `dsp` | **dict**[**str** \| Zone, **str**] | Current AVR DSP attributes
| `video` | **dict**[**str** \| Zone, **str**] | Current AVR video parameters
| `audio` | **dict**[**str** \| Zone, **str**] | Current AVR audio parameters
| `system` | **dict**[**str** \| Zone, **str**]| AVR system attributes
| `channel_levels` | **dict**[**str**, **Any**] | Current AVR channel levels, indexed by channel name
| `ip_control_port_n` | **str** | IP control ports configured on the AVR (where `n` is the port index)

## Command line interface (CLI)

A very simple command line interface `aiopioneer` is available to connect to the AVR, send commands and receive responses. It can be used to test the capabilities of the library against your specific AVR.

On Home Assistant, you can run the CLI when the `pioneer_async` Home Assistant integration has been installed. On Home Assistant Supervised or Container, start the CLI from within the HA container: `docker exec -it homeassistant aiopioneer`.

Invoke the CLI with the following arguments:

| Argument | Default | Description
| --- | --- | ---
| hostname | required | hostname for AVR connection
| `-p`<br>`--port` | 8102 | port for AVR connection
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
| `get_zone_listening_modes` | | (>0.5) Return the current set of available listening modes.
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
| `debug_command_queue` | _state_ (bool) | Enable/disable the `debug_command_queue` parameter.
| `set_scan_interval` | _scan_interval_ (float) | Set the scan interval to _scan_interval_.
| `get_scan_interval` | | Return the current scan interval.
| `set_volume_level` | _volume_level_ (int) | Set the volume level for the current zone.
| `select_source` | _source_name_ | Set the input source for the current zone.
| `select_listening_mode` | _listening_mode_ | (>0.5) Set the listening mode to the specified mode.
| `set_tuner_frequency` | _band_ _frequency_ | Set the tuner band and (optionally) frequency.
| `tuner_previous_preset` | | Select the previous tuner preset
| `tuner_next_preset` | | Select the next tuner preset
| `send_raw_command` or `>` | _raw_command_ | Send the raw command _raw_command_ to the AVR.

**NOTE:** The CLI interface may change in the future, and should not be used in scripts. Use the Python API instead.

## Source list

The list below shows the source ID that corresponds to each AVR source:

| ID | Default Name
| -- | ---
| 25 | BD
| 04 | DVD
| 06 | SAT/CBL
| 10 | VIDEO
| 15 | DVR/BDR
| 19 | HDMI 1
| 20 | HDMI 2
| 21 | HDMI 3
| 22 | HDMI 4
| 23 | HDMI 5
| 24 | HDMI 6
| 34 | HDMI 7
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

### 0.8

- To enable params to be accessible from AVR response parsers and also to reduce the size of the main class, the `PioneerAVR` class has been split out to the classes listed below. References to parameter and properties methods and attributes will need to be updated to be accessed via the `params` and `properties` attributes of the `PioneerAVR` object. All other public attributes have moved to the new classes.
  - `PioneerAVRParams` contains the user and run-time parameter get/set methods. Some method names have changed, please consult the updated documentation for details
  - `PioneerAVRProperties` contains the cache of AVR properties collected from its responses
- The connection related methods have also been split out to the `PioneerAVRConnection` class, although `PioneerAVR` inherits from the new class so the connection methods are still accessible via the `PioneerAVR` class
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
- The `query_sources` method has been removed. `PioneerAVRParams.get_runtime_param(PARAM_QUERY_SOURCES)` should be used instead
- The `update_zones` method has been removed. Change the AVR zones by recreating the `PioneerAVR` object with the new zones
- The `PioneerAVR.initial_update` property has moved to run-time param `PARAM_ZONES_INITIAL_REFRESH` and is now a set of `Zone`. The `PioneerAVRParams.zones_initial_refresh` property is provided as a convenience to access this run-time parameter
- System parameters have been re-termed as run-time parameters to better reflect their function

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
  - This library supports many of the commands listed in the **2015 Pioneer & Elite AVR External Command** document
