"""aiopioneer response decoder."""

import logging

from .const import Zone
from .decoders.code_map import CodeMapBase
from .decoders.response import Response
from .exceptions import AVRResponseDecodeError
from .params import AVRParams
from .properties import AVRProperties
from .property_registry import PROPERTY_REGISTRY

_LOGGER = logging.getLogger(__name__)


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
        if not (match_resp := PROPERTY_REGISTRY.match_response(raw_resp=raw_resp)):
            ## No error handling as not all responses have been captured by aiopioneer.
            if not (raw_resp.startswith("E") or raw_resp == "B00"):
                _LOGGER.debug("undecoded response: %s", raw_resp)
            return []

        response_cmd, code_map, response_zone = match_resp
        code = raw_resp[len(response_cmd) :]
        if not issubclass(code_map, CodeMapBase):
            raise RuntimeError(f"invalid decoder {code_map} for response: {code}")
        responses = code_map.decode_response(
            response=Response(
                properties=properties,
                code=code,
                response_command=response_cmd,
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
