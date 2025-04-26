<!-- markdownlint-disable no-inline-html -->
# Python API

The library exposes a Python API through the **PioneerAVR** class. The class methods are listed below:

`PioneerAVR.__init__(`_host_: **str**, _port_ = DEFAULT_PORT, _timeout_: **float** = DEFAULT_TIMEOUT, _scan_interval_: **float** = DEFAULT_SCAN_INTERVAL, _params_: **dict[str, str]** = **None** `)`

Constructor for the **PioneerAVR** class. The connection parameters are used when `PioneerAVR.connect` is called. After connection is established, the AVR will be polled every _scan_interval_ seconds. If the `always_poll` parameter is set, the poll timer is reset when a response from the AVR is received. Optional user parameters are provided via _params_.

## Connection methods (inherited by `PioneerAVR`)

_awaitable_ `AVRConnection.connect(`_reconnect_: **bool** = True`)`

Establish a connection to the AVR, and query the AVR device model if parameter `model` is not set. Set _reconnect_ to **True** to re-establish the connection if it is disconnected.

Raises `AVRConnectionError` on connection errors, with `err` indicating the connection error.

_awaitable_ `AVRConnection.disconnect(`_reconnect_: **bool**`)`

Disconnect from the AVR. Attempt to re-establish the connection if enabled at connect, or overridden by specifying _reconnect_.

_awaitable_ `AVRConnection.shutdown()`

Permanently disconnect from the AVR. Does not attempt reconnection.

_awaitable_ `AVRConnection.set_timeout(`_timeout_: **float**`)`

Set command and socket keepalive timeouts.

_property_ `available`: **bool**

Whether integration is connected to the AVR.

_property_ `scan_interval`: **float**

Number of seconds between polls for AVR full updates.

## Update methods

_awaitable_ `PioneerAVR.refresh(`_zones_: **list[Zone]** = **None**, _wait_: **bool** = **True**`)`

Refresh the cached properties from the AVR via the command queue. <br/>
Refresh the AVR zones _zones_, or all AVR zones if not specified. <br/>
Wait for the update to be completed if _wait_ is **True**. <br/>

_awaitable_ `PioneerAVR.set_scan_interval(`_scan_interval_: **int**`)`

Set the scan interval to _scan_interval_ and restart the updater task.

## AVR system methods

_awaitable_ `PioneerAVR.turn_on(`_zone_: Zone = Zone.Z1`)`:

Turn on the Pioneer AVR zone.

_awaitable_ `PioneerAVR.turn_off(`_zone_: Zone = Zone.Z1`)`:

Turn off the Pioneer AVR zone.

_awaitable_ `PioneerAVR.query_device_model()` -> **bool** | **None** (**deprecated**)

Query the AVR for device model. Updates the model parameters if device model is changed.
Returns **True** if the AVR responds with its model, **False** if the AVR responds with an error, and **None** otherwise.

> [!CAUTION]
> As of 0.8.2, it is no longer required to call this function after connecting to the AVR. This method is deprecated and will be removed in a future version.

_awaitable_ `PioneerAVR.query_device_info()`

Query the AVR for device information.

_awaitable_ `PioneerAVR.query_zones(`_force_update_: **bool** = **True**`)`

Query the AVR for available zones by querying the power status for each zone and checking if the AVR responds.
Ignores zones listed in the `ignored_zones` parameter. <br/>
If the `ignore_volume_check` parameter is not set, then additionally query the zone volume as well.

_awaitable_ `PioneerAVR.set_amp_settings(`_**kwargs_`)` -> **None**

Set amplifier settings. Any `set_amp` command can be sent by specifying the command as an argument. **TODO**

## AVR source methods

_awaitable_ `PioneerAVR.select_source(`_source_: **str** | **int**, _zone_: Zone = Zone.Z1`)`:

Set the input source for _zone_ to _source_, which can be an integer source ID or a source name.

_awaitable_ `PioneerAVR.build_source_dict()`

Query the available sources names from the AVR. <br/>
Parameter `max_source_id` determines the highest source ID that is queried.

`AVRProperties.set_source_dict(`_sources_: **dict**[**int**, **str**]`)`

Manually set the available sources to the dict _sources_, where the keys are integer source IDs and the values are the corresponding source names.

`AVRProperties.get_source_list(`_zone_: Zone = Zone.Z1`)` -> **list**[**str**]

Return the set of currently available source names for _zone_. The source names can be used with the `select_source` method.

`AVRProperties.get_source_dict(`_zone_: Zone = **None**`)` -> **dict**[**int**, **str**]

Return a dict of currently available source ID to source name mappings for _zone_. <br/>
If _zone_ is **None**, then return the dict of all available source ID to source name mappings for the AVR.

`AVRProperties.get_source_name(`_source_id_: **str**`)` -> **str**

Return the source name for _source_id_.

_awaitable_ `PioneerAVR.set_source_name(`_source_id_: **str**, _source_name_: **str** = **None**`)` -> **bool**

Renames _source_id_ to _source_name_ on the AVR. <br/>
If _source_name_ is **None**, reset source name to default.

## Command queue methods

`CommandQueue.enqueue(`_item_: **ComandItem**, _queue_id_: **int** = **None**, _skip_if_startup_: **bool** = **None**, _skip_if_queued_: **bool** = **None**, _skip_if_refreshing_: **bool** = **None**, _insert_at_: **int** = -1, _start_executing_: **bool** = **True**`)` -> **None**

Add _item_ to the command queue, to be sent in the background to the AVR or executed as a local command. <br/>
Use the queue _queue_id_ if specified, otherwise use the default queue. <br/>
Insert at position _insert_at_ in the queue. If _insert_at_ is negative, then calculate the position relative to the end of the queue. If not specified, use the value specified in _item_. <br/>
If _skip_if_startup_, _skip_if_queued_ and/or _skip_if_refreshing_ are provided, then override the values specified in _item_. <br/>
If _skip_if_startup_ is **True**, then the command is not queued if the module is still connecting to the AVR. <br/>
If _skip_if_queued_ is **True** and _item_ is already present in the command queue, then the command is not queued again. <br/>
If _skip_if_refreshing_ is **True**, then the command is not queued if the zone is scheduled for a refresh. <br/>
If _start_executing_ is **True**, then starts the command queue task if it is not already running. <br/>

The following local commands are supported, these are mainly used by the command decoders for more complex actions:

- `_full_refresh`: perform a full refresh on all AVR Zones
- `_refresh_zone`(_zone_: **Zone**): perform a refresh on the specified zone
- `_delayed_refresh_zone`(_zone_: **Zone**): perform a refresh on the specified zone after a 2.5s delay
- `_delayed_query_basic`(_delay_: **float**): schedule a basic AVR query after waiting _delay_, if parameter `disable_auto_query` is not enabled
- `_update_listening_modes`: recalculate the available listening modes
- `_calculate_am_frequency_step`: calculate the tuner AM frequency step
- `_sleep`(_delay_: **float**): sleep for _delay_ before executing the next command in the queue

`CommandQueue.extend(`_items_: **list**\[**ComandItem**\]`)` -> **None**

Add _items_ to the queue using the properties for each **CommandItem**. Start executing the commands if not already started.

`CommandQueue.purge()` -> **None**

Purge the command queues.

`CommandQueue.active_queue()` -> **int** | **None**

Return the ID of the currently active command queue.

`CommandQueue.peek(`_queue_id: **int** = **None**, _queue_pos_: **int** = 0`)` -> **tuple**[**int**, **CommandItem**] | **None**

Peek at the next item in the command queue. <br/>
If _queue_id_ is specified, peek at the specified command queue. Otherwise, peek at the first non-empty command queue. <br/>
If _queue_pos_ is specified, peek at the specified position in the command queue. Otherwise, peek at the first position. <br/>

`CommandQueue.pop(`_queue_id: **int** = **None**, _queue_pos_: **int** = 0`)` -> **CommandItem** | **None**

Pop the first item in the command queue. <br/>
If _queue_id_ is specified, pop from the specified command queue. Otherwise, pop from the first non-empty command queue. <br/>

`CommandQueue.schedule()` -> **int** | **None**

Schedule the command queue task.

`CommandQueue.cancel()` -> **int** | **None**

Cancel the command queue task and purge the command queue.

`CommandQueue.wait()` -> **int** | **None**

Wait until command queue has finished executing.

`CommandQueue.commands` -> **list**\[**str**\]

Return a list of the queued command names.

## Low level AVR command methods (inherited by `PioneerAVR`)

_awaitable_ `AVRConnection.send_command(`_command_: **str**, _zone_: Zone = Zone.Z1, _prefix_: **str** = "", _suffix_: **str** = "", _ignore_erro* = **None**, _rate_limit_: **bool** = **True**`)` -> **bool** | **None**

Send command _command_ for zone _zone_ to the AVR, prefixed with _prefix_ and/or suffixed with _suffix_ if specified. <br/>
If _command_ does not generate a response, then returns **True** if the command was successfully sent.
Otherwise, returns the response received from the AVR, **None** if timed out, or **False** if an error response was received. <br/>
If _ignore_error_ is **None** (default), then raise an exception on error. If _ignore_error_ is **True**, then log the error as level debug, otherwise log the error as level error. <br/>
Raises `AVRUnavailable` if the AVR is disconnected, `AVRResponseTimeoutError` on timeout, and `AVRCommandError` if the request returned an error.<br/>
If _rate_limit_ is **True**, then rate limit the commands sent to the AVR in accordance with the `command_delay` parameter.

_awaitable_ `AVRConnection.send_raw_command(`_command_: **str**, _rate_limit_: **bool** = True`)`

Send a raw command _command_ to the AVR.
If _rate_limit_ is **True**, then rate limit the commands sent to the AVR in accordance with the `command_delay` parameter. <br/>
Raises `AVRUnavailable` if the AVR is disconnected.

_awaitable_ `AVRConnection.send_raw_request(`_command_: **str**, _response_prefix_: **str**, _rate_limit_: **bool** = **True**`)` -> **str** | **bool** | **None**

Send a raw command _command_ to the AVR and wait for a response with prefix _response_prefix_.
Returns the response received from the AVR.<br/>
Raises `AVRUnavailable` if the AVR is disconnected, `AVRResponseTimeoutError` on timeout, and `AVRCommandError` if the request returned an error.<br/>
If _rate_limit_ is **True**, then rate limit the commands sent to the AVR in accordance with the `command_delay` parameter.

## AVR tuner methods

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

## AVR audio/video methods

_awaitable_ `PioneerAVR.select_listening_mode(`_mode_name_: **str** = **None**, _mode_id_: **str** = **None**`)` -> **bool**

Set the listening mode to name _mode_name_, or ID _mode_id_ (requires one argument.)
Must be a listening mode valid for the current sound input as returned by `get_listening_modes`.

`PioneerAVR.get_listening_modes()` -> **list**[**str**] | **None**

Return list of valid listening mode names for the AVR.

_awaitable_ `PioneerAVR.set_volume_level(`_target_volume_: **int**, zone: Zones = Zones.Z1`)`

Set the volume level for zone _zone_ to _target_volume_.
_target_volume_ must be between 0 and 185 inclusive for Zone 1, and between 0 and 81 inclusive for all  other zones.

_awaitable_ `PioneerAVR.mute_on(`_zone_: Zone = Zone.Z1`)` -> **bool**

Turn mute on for zone _zone_.

_awaitable_ `PioneerAVR.mute_off(`_zone_: Zone = Zone.Z1`)` -> **bool**

Turn mute off for zone _zone_.

_awaitable_ `PioneerAVR.set_tone_settings(`_tone_: **str** = **None**, _treble_: **int** = **None**, _bass_: **int** = **None**, _zone_: Zone = Zone.Z1 `)`*

Set the tone settings for zone _zone_ to _tone_. When _tone_ is set to `On`, _treble_ specifies the treble and _bass_ specifies the bass.

`AVRProperties.get_supported_media_controls(`_zone_: Zone`)` -> **list**[**str**]

Return a list of all valid media control actions for a given zone. If the provided zone source is not currently compatible with media controls, **None** will be returned.

_awaitable_ `PioneerAVR.set_channel_levels(`_channel_: **str**, _level_: **float**, _zone_: Zone = Zone.Z1`)` -> **bool**

Set the level (gain) for amplifier channel in zone _zone_.

_awaitable_ `PioneerAVR.set_video_settings(`_zone_: Zone, **_arguments_`)` -> **bool**

Set video settings for zone _zone_.

_awaitable_ `PioneerAVR.set_dsp_settings(`_zone_: Zone, **_arguments_`)` -> **bool**

Set the DSP settings for the amplifier for zone _zone_.

_awaitable_ `PioneerAVR.media_control(`_action_: **str**, _zone_: Zone = Zone.Z1`)` -> **bool**

Perform media control activities such as play, pause, stop, fast forward or rewind.

## AVR zone callback methods

`PioneerAVR.set_zone_callback(`_zone_: Zone, _callback_: **Callable**[..., **None**]`)`

Register callback _callback_ for zone _zone_.

`PioneerAVR.clear_zone_callbacks()`

Clear callbacks for all zones.

## Parameter methods

`AVRParams.set_default_params_model(`_model_: **str**`)` -> **None**

Set default parameters based on device model.

`AVRParams.set_user_params(`_params_: **dict**[**str**, **Any**] = **None**`)` -> **None**

Set user parameters and update current parameters.

`AVRParams.set_user_param(`_param_: **str**, _value_: **Any**`)` -> **None**

Set a user parameter.

_property_ `AVRParams.zones_initial_refresh`: **set**[Zone]

Return set of zones that have completed an initial refresh.

_property_ `AVRParams.default_params`: **dict**[**str**, **Any**]

Get a copy of current default parameters.

_property_ `AVRParams.user_params`: **dict**[**str**, **Any**]

Get a copy of user parameters.

_property `AVRParams.params_all` -> **dict**[**str**, **Any**]

Get a copy of all current parameters.

`AVRParams.get_param(`_param_name_: **str**`)` -> **Any**

Get the value of the specified parameter.
