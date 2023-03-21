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
    def mcacc_setting(raw: str, _param: dict, zone = Zones.Z1, command = "MC") -> list:
        """Response parser for MCACC setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="mcacc_memory_set",
                            zone=zone,
                            value=int(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def phasecontrol(raw: str, _param: dict, zone = Zones.Z1, command = "IS") -> list:
        """Response parser for phase control setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="phase_control",
                            zone=zone,
                            value=DSP_PHASE_CONTROL.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def virtual_speakers(raw: str, _param: dict, zone = Zones.Z1, command = "VSP") -> list:
        """Response parser for virtual speakers setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="virtual_speakers",
                            zone=zone,
                            value=raw,
                            queue_commands=None))

        return parsed
        
    @staticmethod
    def virtual_soundback(raw: str, _param: dict, zone = Zones.Z1, command = "VSB") -> list:
        """Response parser for virtual sound-back setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="virtual_sb",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def virtual_height(raw: str, _param: dict, zone = Zones.Z1, command = "VHT") -> list:
        """Response parser for virtual height setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="virtual_height",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def sound_retriever(raw: str, _param: dict, zone = Zones.Z1, command = "ATA") -> list:
        """Response parser for sound retreiver setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="sound_retriever",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def signal_select(raw: str, _param: dict, zone = Zones.Z1, command = "SDA") -> list:
        """Response parser for signal select setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="signal_select",
                            zone=zone,
                            value=DSP_SIGNAL_SELECT.get(raw),
                            queue_commands=None))

        return parsed
    
    @staticmethod
    def input_att(raw: str, _param: dict, zone = Zones.Z1, command = "SDB") -> list:
        """Response parser for input attenuation setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="analog_input_att",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def equalizer(raw: str, _param: dict, zone = Zones.Z1, command = "ATC") -> list:
        """Response parser for equalizer setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="eq",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def standing_wave(raw: str, _param: dict, zone = Zones.Z1, command = "ATD") -> list:
        """Response parser for standing wave setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="standing_wave",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def phase_control_plus(raw: str, _param: dict, zone = Zones.Z1, command = "ATE") -> list:
        """Response parser for phase control plus setting"""
        value = int(raw)
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="phase_control_plus",
                            zone=zone,
                            value="auto" if value == 97 else value,
                            queue_commands=None))

        return parsed

    @staticmethod
    def sound_delay(raw: str, _param: dict, zone = Zones.Z1, command = "ATF") -> list:
        """Response parser for sound delay setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="sound_delay",
                            zone=zone,
                            value=float(raw) / 10,
                            queue_commands=None))

        return parsed

    @staticmethod
    def digital_noise_reduction(raw: str, _param: dict, zone = Zones.Z1, command = "ATG") -> list:
        """Response parser for digital noise reduction setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="digital_noise_reduction",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def dialog_enhancement(raw: str, _param: dict, zone = Zones.Z1, command = "ATH") -> list:
        """Response parser for dialog enhancement setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="dialog_enchancement",
                            zone=zone,
                            value=DSP_DIGITAL_DIALOG_ENHANCEMENT.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def audio_scaler(raw: str, _param: dict, zone = Zones.Z1, command = "ATY") -> list:
        """Response parser for Audio Scaler setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="audio_scaler",
                            zone=zone,
                            value= "auto" if int(raw) == "0" else "manual",
                            queue_commands=None))

        return parsed

    @staticmethod
    def hi_bit(raw: str, _param: dict, zone = Zones.Z1, command = "ATI") -> list:
        """Response parser for Hi-BIT setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="hi_bit",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def up_sampling(raw: str, _param: dict, zone = Zones.Z1, command = "ATZ") -> list:
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
                            response_command=command,
                            base_property="dsp",
                            property_name="up_sampling",
                            zone=zone,
                            value=raw,
                            queue_commands=None))

        return parsed

    @staticmethod
    def dual_mono(raw: str, _param: dict, zone = Zones.Z1, command = "ATJ") -> list:
        """Response parser for dual mono setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="dual_mono",
                            zone=zone,
                            value=DSP_DUAL_MONO.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def fixed_pcm(raw: str, _param: dict, zone = Zones.Z1, command = "ATK") -> list:
        """Response parser for fixed PCM setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="fixed_pcm",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def dynamic_range_control(raw: str, _param: dict, zone = Zones.Z1, command = "ATL") -> list:
        """Response parser for dynamic range control setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="dynamic_range_control",
                            zone=zone,
                            value=DSP_DRC.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def lfe_attenuator(raw: str, _param: dict, zone = Zones.Z1, command = "ATM") -> list:
        """Response parser for LFE attenuator setting"""
        value = int(raw) * -5
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="lfe_attenuator",
                            zone=zone,
                            value="off" if value < -20 else value,
                            queue_commands=None))

        return parsed

    @staticmethod
    def sacd_gain(raw: str, _param: dict, zone = Zones.Z1, command = "ATN") -> list:
        """Response parser for SACD gain setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="sacd_gain",
                            zone=zone,
                            value=6 if bool(raw) else 0,
                            queue_commands=None))

        return parsed

    @staticmethod
    def auto_delay(raw: str, _param: dict, zone = Zones.Z1, command = "ATO") -> list:
        """Response parser for auto delay setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="auto_delay",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def center_width(raw: str, _param: dict, zone = Zones.Z1, command = "ATP") -> list:
        """Response parser for center width setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="center_width",
                            zone=zone,
                            value=int(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def panorama(raw: str, _param: dict, zone = Zones.Z1, command = "ATQ") -> list:
        """Response parser for panorama setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="panorama",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def dimension(raw: str, _param: dict, zone = Zones.Z1, command = "ATR") -> list:
        """Response parser for dimension setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="dimension",
                            zone=zone,
                            value=int(raw) - 50,
                            queue_commands=None))

        return parsed

    @staticmethod
    def center_image(raw: str, _param: dict, zone = Zones.Z1, command = "ATS") -> list:
        """Response parser for center image setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="center_image",
                            zone=zone,
                            value=float(raw) / 10,
                            queue_commands=None))

        return parsed

    @staticmethod
    def effect(raw: str, _param: dict, zone = Zones.Z1, command = "ATT") -> list:
        """Response parser for effect setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="effect",
                            zone=zone,
                            value=int(raw) * 10,
                            queue_commands=None))

        return parsed

    @staticmethod
    def height_gain(raw: str, _param: dict, zone = Zones.Z1, command = "ATU") -> list:
        """Response parser for height gain setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="height_gain",
                            zone=zone,
                            value=DSP_HEIGHT_GAIN.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def digital_filter(raw: str, _param: dict, zone = Zones.Z1, command = "ATV") -> list:
        """Response parser for digital filter setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="digital_filter",
                            zone=zone,
                            value=DSP_DIGITAL_FILTER.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def loudness_management(raw: str, _param: dict, zone = Zones.Z1, command = "ATW") -> list:
        """Response parser for loudness management setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="loudness_management",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def center_spread(raw: str, _param: dict, zone = Zones.Z1, command = "ARA") -> list:
        """Response parser for center spread setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="center_spread",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def rendering_mode(raw: str, _param: dict, zone = Zones.Z1, command = "ARB") -> list:
        """Response parser for rendering mode setting (Dolby Atmos only)"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="rendering_mode",
                            zone=zone,
                            value="object base" if int(raw) == 0 else "channel base",
                            queue_commands=None))

        return parsed

    @staticmethod
    def virtual_depth(raw: str, _param: dict, zone = Zones.Z1, command = "VDP") -> list:
        """Response parser for virtual depth setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="virtual_depth",
                            zone=zone,
                            value=DSP_VIRTUAL_DEPTH.get(raw),
                            queue_commands=None))

        return parsed

    @staticmethod
    def virtual_wide(raw: str, _param: dict, zone = Zones.Z1, command = "VWD") -> list:
        """Response parser for virtual wide setting"""
        parsed = []
        parsed.append(Response(raw=raw,
                            response_command=command,
                            base_property="dsp",
                            property_name="virtual_wide",
                            zone=zone,
                            value=bool(raw),
                            queue_commands=None))

        return parsed
