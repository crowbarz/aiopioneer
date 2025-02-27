"""aiopioneer response decoders for core system responses."""

import logging
import re

from ..const import MEDIA_CONTROL_SOURCES, Zone
from ..params import (
    AVRParams,
    PARAM_MHL_SOURCE,
    PARAM_SPEAKER_SYSTEM_MODES,
    PARAM_POWER_ON_VOLUME_BOUNCE,
)
from .code_map import (
    CodeMapBase,
    CodeBoolMap,
    CodeStrMap,
    CodeInverseBoolMap,
    CodeDictStrMap,
    CodeIntMap,
)
from .response import Response

_LOGGER = logging.getLogger(__name__)


class Power(CodeInverseBoolMap):
    """Zone power status."""

    friendly_name = "zone power"

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for zone power status."""

        def check_power_on(response: Response) -> list[Response]:
            """Check for power on."""
            zone = response.zone
            properties = response.properties
            if properties.power.get(zone):  ## zone is already on
                return []

            queue_commands = [
                ["_oob", "_sleep", 2],
                ["_oob", "_delayed_query_basic", 2],
            ]
            if zone not in properties.zones_initial_refresh:
                ## TODO: skip if updating to replace _oob
                _LOGGER.info("queueing initial refresh for %s", zone.full_name)
                queue_commands = [
                    [False, 0, "_oob", "_sleep", 2],
                    [False, 1, "_oob", "_refresh_zone", zone],
                ]

            if zone is Zone.Z1 and params.get_param(PARAM_POWER_ON_VOLUME_BOUNCE):
                _LOGGER.info("queueing volume workaround for Main Zone")
                ## NOTE: volume bounce queues before refresh
                queue_commands.extend(
                    [[False, 0, "volume_up"], [False, 1, "volume_down"]]
                )

            response.update(queue_commands=queue_commands)
            return [response]

        super().decode_response(response, params)
        if response.value:
            response.update(callback=check_power_on)
        else:
            response.update(queue_commands=[["_oob", "_delayed_query_basic", 2]])
        response.update(update_zones={Zone.ALL})
        return [response]


class InputSource(CodeMapBase):
    """Zone input source."""

    friendly_name = "zone input source"

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for zone input source."""
        super().decode_response(response, params)
        source = response.value
        queue_commands = []
        if source == SOURCE_TUNER:
            queue_commands.extend(["query_tuner_frequency", "query_tuner_preset"])
        queue_commands.append(["_oob", "_delayed_query_basic", 2])
        if source in MEDIA_CONTROL_SOURCES:
            media_control_mode = MEDIA_CONTROL_SOURCES.get(source)
        elif source == params.get_param(PARAM_MHL_SOURCE):
            media_control_mode = "MHL"
        else:
            media_control_mode = None

        return [
            response.clone(
                base_property="source_name",
                value=response.properties.get_source_name(response.value),
                update_zones={Zone.ALL},
                queue_commands=queue_commands,
            ),
            response,
            response.clone(
                base_property="media_control_mode",
                inherit_value=False,
                value=media_control_mode,
            ),
        ]


class SpeakerMode(CodeDictStrMap):
    """Speaker mode."""

    friendly_name = "speaker mode"

    code_map = {"0": "off", "1": "A", "2": "B", "3": "A+B"}


class HdmiOut(CodeDictStrMap):
    """HDMI out."""

    friendly_name = "HDMI out"

    code_map = {"0": "all", "1": "HDMI 1", "2": "HDMI 2"}


class Hdmi3Out(CodeBoolMap):
    """HDMI3 out."""

    friendly_name = "HDMI3 out"

    code_true = "1"
    code_false = "3"


class HdmiAudio(CodeDictStrMap):
    """HDMI audio."""

    friendly_name = "HDMI audio"

    code_map = {"0": "amp", "1": "passthrough"}


class Pqls(CodeDictStrMap):
    """PQLS."""

    friendly_name = "PQLS"

    code_map = {"0": "off", "1": "auto"}


class Dimmer(CodeDictStrMap):
    """Dimmer."""

    friendly_name = "dimmer"

    code_map = {
        "0": "brightest",
        "1": "bright",
        "2": "dark",
        "3": "off",
    }


class SleepTime(CodeIntMap):
    """Sleep time remaining."""

    friendly_name = "sleep time"

    value_min = 0
    value_max = 90
    value_step = 30
    code_zfill = 3


class AmpMode(CodeDictStrMap):
    """AMP status."""

    friendly_name = "AMP status"

    code_map = {
        "0": "amp on",
        "1": "amp front off",
        "2": "amp front & center off",
        "3": "amp off",
    }


class PanelLock(CodeDictStrMap):
    """Panel lock."""

    friendly_name = "panel lock"

    code_map = {"0": "off", "1": "panel only", "2": "panel + volume"}


class SpeakerSystem(CodeDictStrMap):
    """Speaker system."""

    friendly_name = "speaker system"

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for speaker system."""
        cls.code_map = params.get_param(PARAM_SPEAKER_SYSTEM_MODES, {})
        super().decode_response(response, params)
        return [
            response,
            response.clone(property_name="speaker_system_raw", value=response.code),
        ]


class InputName(CodeMapBase):
    """Input name."""

    friendly_name = "input name"

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,
    ) -> list[Response]:
        """Response decoder for input name."""

        if not response.properties.query_sources:
            ## Only update AVR source mappings if AVR sources are being queried
            return []

        def clear_source_id(response: Response) -> list[Response]:
            """Clear source ID before applying new source ID mapping."""
            properties = response.properties
            source_name = None
            if (source_id := response.value) in properties.source_id_to_name:
                source_name = properties.source_id_to_name[source_id]
                properties.source_id_to_name.pop(source_id)
            if source_name in properties.source_name_to_id:
                properties.source_name_to_id.pop(source_name)

        super().decode_response(response, params)
        source_id, source_name = response.value
        return [
            response.clone(callback=clear_source_id, value=source_id),
            response.clone(
                base_property="source_name_to_id",
                property_name=source_name,
                value=source_id,
            ),
            response.clone(
                base_property="source_id_to_name",
                property_name=source_id,
                value=source_name,
            ),
        ]

    @classmethod
    def code_to_value(cls, code: str) -> tuple[str, str]:
        return code[:2], code[3:]


class SystemMacAddress(CodeStrMap):
    """System MAC address."""

    ## NOTE: value_to_code not implemented

    @classmethod
    def code_to_value(cls, code: str) -> str:
        return ":".join([code[i : i + 2] for i in range(0, len(code), 2)])


class SystemAvrModel(CodeStrMap):
    """System AVR model."""

    ## NOTE: value_to_code not implemented

    @classmethod
    def code_to_value(cls, code: str) -> str:
        value = "unknown"
        if matches := re.search(r"<([^>/]{5,})(/.[^>]*)?>", code):
            value = matches.group(1)
        return value


class SystemSoftwareVesion(CodeStrMap):
    """System software version."""

    ## NOTE: value_to_code not implemented

    @classmethod
    def code_to_value(cls, code: str) -> str:
        value = "unknown"
        if matches := re.search(r'"([^)]*)"', code):
            value = matches.group(1)
        return value


class AudioParameterProhibition(CodeMapBase):
    """Audio parameter prohibition."""

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for audio parameter prohibition."""
        response.update(queue_commands=[["_delayed_query_basic", 2]])
        return [response]


class AudioParameterWorking(CodeMapBase):
    """Audio parameter working."""

    @classmethod
    def decode_response(
        cls,
        response: Response,
        params: AVRParams,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response decoder for audio parameter working."""
        response.update(queue_commands=[["_delayed_query_basic", 2]])
        return [response]
