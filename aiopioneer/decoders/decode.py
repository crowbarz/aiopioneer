"""aiopioneer response decoder."""

import logging

from ..const import Zone
from ..exceptions import AVRResponseDecodeError
from ..params import AVRParams
from ..properties import AVRProperties
from .audio import RESPONSE_DATA_AUDIO
from .code_map import (
    CodeMapBase,
    CodeBoolMap,
)
from .dsp import RESPONSE_DATA_DSP
from .information import AudioInformation, VideoInformation, DisplayText
from .response import Response
from .settings import RESPONSE_DATA_SYSTEM
from .amp import RESPONSE_DATA_AMP
from .tuner import FrequencyFM, FrequencyAM, Preset, FrequencyAMStep
from .video import (
    VideoInt08Map,
    VideoProgMotion,
    VideoInt66Map,
    VideoResolution,
    VideoPureCinema,
    VideoStreamSmoother,
    AdvancedVideoAdjust,
    VideoAspect,
    VideoSuperResolution,
)

_LOGGER = logging.getLogger(__name__)

RESPONSE_DATA = [
    *RESPONSE_DATA_AMP,
    *RESPONSE_DATA_SYSTEM,
    *RESPONSE_DATA_DSP,
    *RESPONSE_DATA_AUDIO,
    ## tuner
    ["FRF", FrequencyFM, Zone.ALL, "tuner", "frequency"],
    ["FRA", FrequencyAM, Zone.ALL, "tuner", "frequency"],
    ["PR", Preset, Zone.ALL, "tuner", "preset"],
    ["SUQ", FrequencyAMStep, Zone.ALL, "tuner", "am_frequency_step"],
    ## information
    ["AST", AudioInformation, Zone.ALL, "audio"],
    ["VST", VideoInformation, Zone.ALL, "video"],
    ["FL", DisplayText, Zone.ALL, "amp", "display"],
    ## video
    ["VTC", VideoResolution, Zone.Z1, "video", "resolution"],
    ["VTB", CodeBoolMap, Zone.Z1, "video", "converter"],
    ["VTD", VideoPureCinema, Zone.Z1, "video", "pure_cinema"],
    ["VTE", VideoProgMotion, Zone.Z1, "video", "prog_motion"],
    ["VTF", VideoStreamSmoother, Zone.Z1, "video", "stream_smoother"],
    ["VTG", AdvancedVideoAdjust, Zone.Z1, "video", "advanced_video_adjust"],
    ["VTH", VideoInt08Map, Zone.Z1, "video", "ynr"],
    ["VTI", VideoInt08Map, Zone.Z1, "video", "cnr"],
    ["VTJ", VideoInt08Map, Zone.Z1, "video", "bnr"],
    ["VTK", VideoInt08Map, Zone.Z1, "video", "mnr"],
    ["VTL", VideoInt08Map, Zone.Z1, "video", "detail"],
    ["VTM", VideoInt08Map, Zone.Z1, "video", "sharpness"],
    ["VTN", VideoInt66Map, Zone.Z1, "video", "brightness"],
    ["VTO", VideoInt66Map, Zone.Z1, "video", "contrast"],
    ["VTP", VideoInt66Map, Zone.Z1, "video", "hue"],
    ["VTQ", VideoInt66Map, Zone.Z1, "video", "chroma"],
    ["VTR", CodeBoolMap, Zone.Z1, "video", "black_setup"],
    ["VTS", VideoAspect, Zone.Z1, "video", "aspect"],
    ["VTT", VideoSuperResolution, Zone.Z1, "video", "super_resolution"],
]


def _commit_response(response: Response) -> None:
    """Commit a decoded response to properties."""
    current_base = current_value = None  #
    properties = response.properties

    if response.base_property is None:
        return

    current_base = current_value = getattr(properties, response.base_property)
    is_global = response.zone in [Zone.ALL, None]
    if response.property_name is None and not is_global:
        current_value = current_base.get(response.zone)
        if current_value != response.value:
            if response.value is not None:
                current_base[response.zone] = response.value
            else:
                del current_base[response.zone]
            setattr(properties, response.base_property, current_base)
            _LOGGER.info(
                "%s: %s: %s -> %s (%s)",
                response.zone.full_name,
                response.base_property,
                repr(current_value),
                repr(response.value),
                repr(response.code),
            )
    elif response.property_name is not None and not is_global:
        ## Default zone dict first, otherwise we hit an exception
        current_base.setdefault(response.zone, {})
        current_prop = current_base.get(response.zone)
        current_value = current_prop.get(response.property_name)
        if current_value != response.value:
            if response.value is not None:
                current_base[response.zone][response.property_name] = response.value
            else:
                del current_base[response.zone][response.property_name]
            setattr(properties, response.base_property, current_base)
            _LOGGER.info(
                "%s: %s.%s: %s -> %s (%s)",
                response.zone.full_name,
                response.base_property,
                response.property_name,
                repr(current_value),
                repr(response.value),
                repr(response.code),
            )
    elif response.property_name is None and is_global:
        if current_base != response.value:
            setattr(properties, response.base_property, response.value)
            _LOGGER.info(
                "Global: %s: %s -> %s (%s)",
                response.base_property,
                repr(current_base),
                repr(response.value),
                repr(response.code),
            )
    else:  # response.property_name is not None and is_global:
        current_value = current_base.get(response.property_name)
        if current_value != response.value:
            if response.value is not None:
                current_base[response.property_name] = response.value
            else:
                del current_base[response.property_name]
            setattr(properties, response.base_property, current_base)
            _LOGGER.info(
                "Global: %s.%s: %s -> %s (%s)",
                response.base_property,
                response.property_name,
                repr(current_value),
                repr(response.value),
                repr(response.code),
            )


def process_raw_response(
    raw_resp: str, params: AVRParams, properties: AVRProperties
) -> set[Zone]:
    """Processes a raw response, decode and apply to properties."""
    try:
        match_resp = next((r for r in RESPONSE_DATA if raw_resp.startswith(r[0])), None)
        if not match_resp:
            ## No error handling as not all responses have been captured by aiopioneer.
            if not raw_resp.startswith("E"):
                _LOGGER.debug("undecoded response: %s", raw_resp)
            return []

        response_cmd: str = match_resp[0]
        code_map = match_resp[1]
        response_zone: Zone = match_resp[2]
        code = raw_resp[len(response_cmd) :]

        if not issubclass(code_map, CodeMapBase):
            raise RuntimeError(f"invalid decoder {code_map} for response: {code}")
        responses = code_map.decode_response(
            response=Response(
                properties=properties,
                code=code,
                response_command=response_cmd,
                base_property=match_resp[3] if len(match_resp) >= 4 else None,
                property_name=match_resp[4] if len(match_resp) >= 5 else None,
                zone=response_zone,
            ),
            params=params,
        )
        if responses is None:
            raise RuntimeError(f"decoder {code_map} returned null response: {code}")

        ## Process responses and update properties
        updated_zones: set[Zone] = set()
        while responses:
            response = responses.pop(0)
            if response is None:
                raise RuntimeError("decoder returned null response")
            if response.callback:
                callback = response.callback
                response.callback = None
                callback_responses = callback(response)
                _LOGGER.debug(
                    "response callback: %s -> %s", callback.__name__, callback_responses
                )
                if callback_responses is None:
                    raise RuntimeError("decoder callback returned null response")
                callback_responses.extend(responses)  # prepend callback_responses
                responses = callback_responses
                continue  ## don't process original callback response
            _commit_response(response)
            if response.zone is not None:
                updated_zones.add(response.zone)
            if response.update_zones:
                updated_zones |= response.update_zones
            if response.queue_commands:
                properties.command_queue.extend(response.queue_commands)

    except Exception as exc:  # pylint: disable=broad-except
        raise AVRResponseDecodeError(response=raw_resp, exc=exc) from exc

    return updated_zones
