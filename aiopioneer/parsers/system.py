"""aiopioneer response parsers for core system responses."""

import re

from ..const import (
    SOURCE_TUNER,
    MEDIA_CONTROL_SOURCES,
    Zone,
)
from ..params import (
    PioneerAVRParams,
    PARAM_MHL_SOURCE,
    PARAM_SPEAKER_SYSTEM_MODES,
)
from ..properties import PioneerAVRProperties
from .code_map import (
    CodeMapBase,
    CodeBoolMap,
    CodeStrMap,
    CodeInverseBoolMap,
    CodeDictStrMap,
    CodeIntMap,
)
from .response import Response


class Power(CodeInverseBoolMap):
    """Zone power status."""

    @classmethod
    def parse_response(
        cls,
        response: Response,
        params: PioneerAVRParams,
        properties: PioneerAVRProperties,
    ) -> list[Response]:
        """Response parser for zone power status."""
        super().parse_response(response, params, properties)
        queue_commands = []
        if response.value:
            queue_commands.append(["_oob", "_power_on", response.zone])
        else:
            queue_commands.append(["_oob", "_delayed_query_basic", 2])

        response.update(update_zones={Zone.ALL}, queue_commands=queue_commands)
        return [response]


class InputSource(CodeMapBase):
    """Zone input source."""

    @classmethod
    def parse_response(
        cls,
        response: Response,
        params: PioneerAVRParams,
        properties: PioneerAVRProperties,
    ) -> list[Response]:
        """Response parser for zone input source."""
        super().parse_response(response, params, properties)
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
                value=properties.get_source_name(response.value),
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

    code_map = {"0": "off", "1": "A", "2": "B", "3": "A+B"}


class HdmiOut(CodeDictStrMap):
    """HDMI out."""

    code_map = {"0": "all", "1": "HDMI 1", "2": "HDMI 2"}


class Hdmi3Out(CodeBoolMap):
    """HDMI3 out."""

    code_true = "1"
    code_false = "3"


class HdmiAudio(CodeDictStrMap):
    """HDMI audio."""

    code_map = {"0": "amp", "1": "passthrough"}


class Pqls(CodeDictStrMap):
    """PQLS."""

    code_map = {"0": "off", "1": "auto"}


class Dimmer(CodeDictStrMap):
    """Dimmer."""

    code_map = {
        "0": "brightest",
        "1": "bright",
        "2": "dark",
        "3": "off",
    }


class SleepTime(CodeIntMap):
    """Sleep time remaining."""

    value_min = 0
    value_max = 90
    value_step = 30
    code_zfill = 3


class AmpMode(CodeDictStrMap):
    """AMP status."""

    code_map = {
        "0": "amp on",
        "1": "amp front off",
        "2": "amp front & center off",
        "3": "amp off",
    }


class PanelLock(CodeDictStrMap):
    """Panel lock."""

    code_map = {"0": "off", "1": "panel only", "2": "panel + volume"}


class SpeakerSystem(CodeDictStrMap):
    """Speaker system."""

    @classmethod
    def parse_response(
        cls,
        response: Response,
        params: PioneerAVRParams,
        properties: PioneerAVRProperties,
    ) -> list[Response]:
        """Response parser for speaker system."""
        cls.code_map = params.get_param(PARAM_SPEAKER_SYSTEM_MODES, {})
        super().parse_response(response, params, properties)
        return [
            response,
            response.clone(property_name="speaker_system_raw", value=response.code),
        ]


class InputName(CodeMapBase):
    """Input name."""

    @classmethod
    def parse_response(
        cls,
        response: Response,
        params: PioneerAVRParams,  # pylint: disable=unused-argument
        properties: PioneerAVRProperties,
    ) -> list[Response]:
        """Response parser for input name."""

        if not properties.query_sources:
            ## Only update AVR source mappings if AVR sources are being queried
            return []

        source_id = response.code[:2]
        source_name = response.code[3:]
        properties.clear_source_id(source_id)
        return [
            ## Clear source ID when Response is applied to avoid race condition
            response.clone(base_property="_clear_source_id", value=source_id),
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
    def parse_response(
        cls,
        response: Response,
        params: PioneerAVRParams,  # pylint: disable=unused-argument
        properties: PioneerAVRProperties,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response parser for audio parameter prohibition."""
        response.update(queue_commands=[["_delayed_query_basic", 2]])
        return [response]


class AudioParameterWorking(CodeMapBase):
    """Audio parameter working."""

    @classmethod
    def parse_response(
        cls,
        response: Response,
        params: PioneerAVRParams,  # pylint: disable=unused-argument
        properties: PioneerAVRProperties,  # pylint: disable=unused-argument
    ) -> list[Response]:
        """Response parser for audio parameter working."""
        response.update(queue_commands=[["_delayed_query_basic", 2]])
        return [response]
