"""aiopioneer response parsers for DSP functions. Most responses are only valid for Zone 1."""

from aiopioneer.const import (DSP_DIGITAL_DIALOG_ENHANCEMENT,
                              DSP_DIGITAL_FILTER,
                              DSP_DRC,
                              DSP_DUAL_MONO,
                              DSP_HEIGHT_GAIN,
                              DSP_PHASE_CONTROL,
                              DSP_SIGNAL_SELECT,
                              DSP_VIRTUAL_DEPTH,
                              Zones)
from .response import Response

class DspParsers():
    """DSP Response parsers."""

    @staticmethod
    def mcacc_setting(raw: str, _param: dict) -> list:
        """Response parser for MCACC setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="MC",
                            base_property="dsp",
                            property_name="mcacc_memory_set",
                            zone=Zones.Z1,
                            value=int(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def phasecontrol(raw: str, _param: dict) -> list:
        """Response parser for phase control setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="IS",
                            base_property="dsp",
                            property_name="phase_control",
                            zone=Zones.Z1,
                            value=DSP_PHASE_CONTROL.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def virtual_speakers(raw: str, _param: dict) -> list:
        """Response parser for virtual speakers setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VSP",
                            base_property="dsp",
                            property_name="virtual_speakers",
                            zone=Zones.Z1,
                            value=raw,
                            queue_commands=None))

        return parsed
        
    @staticmethod
    def virtual_soundback(raw: str, _param: dict) -> list:
        """Response parser for virtual sound-back setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VSB",
                            base_property="dsp",
                            property_name="virtual_sb",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def virtual_height(raw: str, _param: dict) -> list:
        """Response parser for virtual height setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VHT",
                            base_property="dsp",
                            property_name="virtual_height",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def sound_retriever(raw: str, _param: dict) -> list:
        """Response parser for sound retreiver setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATA",
                            base_property="dsp",
                            property_name="sound_retriever",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def signal_select(raw: str, _param: dict) -> list:
        """Response parser for signal select setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="SDA",
                            base_property="dsp",
                            property_name="signal_select",
                            zone=Zones.Z1,
                            value=DSP_SIGNAL_SELECT.get(raw),
                            queue_commands=None))

        return parsed
    
    @staticmethod
    def input_att(raw: str, _param: dict) -> list:
        """Response parser for input attenuation setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="SDB",
                            base_property="dsp",
                            property_name="analog_input_att",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def equalizer(raw: str, _param: dict) -> list:
        """Response parser for equalizer setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATC",
                            base_property="dsp",
                            property_name="eq",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def standing_wave(raw: str, _param: dict) -> list:
        """Response parser for standing wave setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATD",
                            base_property="dsp",
                            property_name="standing_wave",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def phase_control_plus(raw: str, _param: dict) -> list:
        """Response parser for phase control plus setting"""
        value = int(raw)
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATE",
                            base_property="dsp",
                            property_name="phase_control_plus",
                            zone=Zones.Z1,
                            value="auto" if value == 97 else value,
                            queue_commands=None))

        return parsed

    @staticmethod
    def sound_delay(raw: str, _param: dict) -> list:
        """Response parser for sound delay setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATF",
                            base_property="dsp",
                            property_name="sound_delay",
                            zone=Zones.Z1,
                            value=float(raw) / 10,
                            queue_commands=None))

        return parsed

    @staticmethod
    def digital_noise_reduction(raw: str, _param: dict) -> list:
        """Response parser for digital noise reduction setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATG",
                            base_property="dsp",
                            property_name="digital_noise_reduction",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def dialog_enhancement(raw: str, _param: dict) -> list:
        """Response parser for dialog enhancement setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATH",
                            base_property="dsp",
                            property_name="dialog_enchancement",
                            zone=Zones.Z1,
                            value=DSP_DIGITAL_DIALOG_ENHANCEMENT.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def audio_scaler(raw: str, _param: dict) -> list:
        """Response parser for Audio Scaler setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATY",
                            base_property="dsp",
                            property_name="audio_scaler",
                            zone=Zones.Z1,
                            value= "auto" if int(raw) == "0" else "manual",
                            queue_commands=None))

        return parsed

    @staticmethod
    def hi_bit(raw: str, _param: dict) -> list:
        """Response parser for Hi-BIT setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATI",
                            base_property="dsp",
                            property_name="hi_bit",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def up_sampling(raw: str, _param: dict) -> list:
        """Response parser for up sampling setting"""
        raw = int(raw)

        if raw == 0:
            raw = "off"
        elif raw == 1:
            raw = "2 times"
        elif raw == 2:
            raw = "4 times"

        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATZ",
                            base_property="dsp",
                            property_name="up_sampling",
                            zone=Zones.Z1,
                            value=raw,
                            queue_commands=None))

        return parsed

    @staticmethod
    def dual_mono(raw: str, _param: dict) -> list:
        """Response parser for dual mono setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATJ",
                            base_property="dsp",
                            property_name="dual_mono",
                            zone=Zones.Z1,
                            value=DSP_DUAL_MONO.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def fixed_pcm(raw: str, _param: dict) -> list:
        """Response parser for fixed PCM setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATK",
                            base_property="dsp",
                            property_name="fixed_pcm",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def dynamic_range_control(raw: str, _param: dict) -> list:
        """Response parser for dynamic range control setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATL",
                            base_property="dsp",
                            property_name="dynamic_range_control",
                            zone=Zones.Z1,
                            value=DSP_DRC.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def lfe_attenuator(raw: str, _param: dict) -> list:
        """Response parser for LFE attenuator setting"""
        value = int(raw) * -5
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATM",
                            base_property="dsp",
                            property_name="lfe_attenuator",
                            zone=Zones.Z1,
                            value="off" if value < -20 else value,
                            queue_commands=None))

        return parsed

    @staticmethod
    def sacd_gain(raw: str, _param: dict) -> list:
        """Response parser for SACD gain setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATN",
                            base_property="dsp",
                            property_name="sacd_gain",
                            zone=Zones.Z1,
                            value=6 if bool(raw) else 0,
                            queue_commands=None))

        return parsed

    @staticmethod
    def auto_delay(raw: str, _param: dict) -> list:
        """Response parser for auto delay setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATO",
                            base_property="dsp",
                            property_name="auto_delay",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def center_width(raw: str, _param: dict) -> list:
        """Response parser for center width setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATP",
                            base_property="dsp",
                            property_name="center_width",
                            zone=Zones.Z1,
                            value=int(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def panorama(raw: str, _param: dict) -> list:
        """Response parser for panorama setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATQ",
                            base_property="dsp",
                            property_name="panorama",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def dimension(raw: str, _param: dict) -> list:
        """Response parser for dimension setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATR",
                            base_property="dsp",
                            property_name="dimension",
                            zone=Zones.Z1,
                            value=int(raw) - 50,
                            queue_commands=None))

        return parsed

    @staticmethod
    def center_image(raw: str, _param: dict) -> list:
        """Response parser for center image setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATS",
                            base_property="dsp",
                            property_name="center_image",
                            zone=Zones.Z1,
                            value=float(raw) / 10,
                            queue_commands=None))

        return parsed

    @staticmethod
    def effect(raw: str, _param: dict) -> list:
        """Response parser for effect setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ATT",
                            base_property="dsp",
                            property_name="effect",
                            zone=Zones.Z1,
                            value=int(raw) * 10,
                            queue_commands=None))

        return parsed

    @staticmethod
    def height_gain(raw: str, _param: dict) -> list:
        """Response parser for height gain setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="atu",
                            base_property="dsp",
                            property_name="height_gain",
                            zone=Zones.Z1,
                            value=DSP_HEIGHT_GAIN.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def digital_filter(raw: str, _param: dict) -> list:
        """Response parser for digital filter setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="atv",
                            base_property="dsp",
                            property_name="digital_filter",
                            zone=Zones.Z1,
                            value=DSP_DIGITAL_FILTER.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def loudness_management(raw: str, _param: dict) -> list:
        """Response parser for loudness management setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="atw",
                            base_property="dsp",
                            property_name="loudness_management",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def center_spread(raw: str, _param: dict) -> list:
        """Response parser for center spread setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ARA",
                            base_property="dsp",
                            property_name="center_spread",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def rendering_mode(raw: str, _param: dict) -> list:
        """Response parser for rendering mode setting (Dolby Atmos only)"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="ARB",
                            base_property="dsp",
                            property_name="rendering_mode",
                            zone=Zones.Z1,
                            value="object base" if int(raw) == 0 else "channel base",
                            queue_commands=None))

        return parsed

    @staticmethod
    def virtual_depth(raw: str, _param: dict) -> list:
        """Response parser for virtual depth setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VDP",
                            base_property="dsp",
                            property_name="virtual_depth",
                            zone=Zones.Z1,
                            value=DSP_VIRTUAL_DEPTH.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def virtual_wide(raw: str, _param: dict) -> list:
        """Response parser for virtual wide setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command="VWD",
                            base_property="dsp",
                            property_name="virtual_wide",
                            zone=Zones.Z1,
                            value=bool(raw),
                            queue_commands=None))

        return parsed
