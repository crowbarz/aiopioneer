"""aiopioneer response parsers for DSP functions."""

from aiopioneer.const import (DSP_DIGITAL_DIALOG_ENHANCEMENT,
                              DSP_DIGITAL_FILTER,
                              DSP_DRC,
                              DSP_DUAL_MONO,
                              DSP_HEIGHT_GAIN,
                              DSP_PHASE_CONTROL,
                              DSP_SIGNAL_SELECT,
                              DSP_VIRTUAL_DEPTH)
from .const import Response

def mc(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="mc",
                         base_property="dsp",
                         property_name="mcacc_memory_set",
                         zone="1",
                         value=int(raw),
                         queue_commands=None))

    return parsed

def is_phasecontrol(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="is",
                         base_property="dsp",
                         property_name="phase_control",
                         zone="1",
                         value=DSP_PHASE_CONTROL.get(raw),
                         queue_commands=None))

    return parsed

def vsp(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vsp",
                         base_property="dsp",
                         property_name="virtual_speakers",
                         zone="1",
                         value=raw,
                         queue_commands=None))

    return parsed
    
def vsb(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vsb",
                         base_property="dsp",
                         property_name="virtual_sb",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def vht(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vht",
                         base_property="dsp",
                         property_name="virtual_height",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def ata(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ata",
                         base_property="dsp",
                         property_name="sound_retriever",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def sda(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="sda",
                         base_property="dsp",
                         property_name="signal_select",
                         zone="1",
                         value=DSP_SIGNAL_SELECT.get(raw),
                         queue_commands=None))

    return parsed

def sdb(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="sdb",
                         base_property="dsp",
                         property_name="analog_input_att",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def atc(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atc",
                         base_property="dsp",
                         property_name="eq",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def atd(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atd",
                         base_property="dsp",
                         property_name="standing_wave",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def ate(raw: str, _param: dict) -> list:
    value = int(raw)
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ate",
                         base_property="dsp",
                         property_name="phase_control_plus",
                         zone="1",
                         value="auto" if value == 97 else value,
                         queue_commands=None))

    return parsed

def atf(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atf",
                         base_property="dsp",
                         property_name="sound_delay",
                         zone="1",
                         value=float(raw) / 10,
                         queue_commands=None))

    return parsed

def atg(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atg",
                         base_property="dsp",
                         property_name="digital_noise_reduction",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def ath(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ath",
                         base_property="dsp",
                         property_name="digital_noise_reduction",
                         zone="1",
                         value=DSP_DIGITAL_DIALOG_ENHANCEMENT.get(raw),
                         queue_commands=None))

    return parsed

def aty(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="aty",
                         base_property="dsp",
                         property_name="digital_noise_reduction",
                         zone="1",
                         value= "off" if int(raw) == "0" else "on",
                         queue_commands=None))

    return parsed

def ati(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ati",
                         base_property="dsp",
                         property_name="hi_bit",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def atz(raw: str, _param: dict) -> list:

    raw = int(raw)

    if raw == 0:
        raw = "off"
    elif raw == 1:
        raw = "2 times"
    elif raw == 2:
        raw = "4 times"

    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atz",
                         base_property="dsp",
                         property_name="up_sampling",
                         zone="1",
                         value=raw,
                         queue_commands=None))

    return parsed

def atj(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atj",
                         base_property="dsp",
                         property_name="dual_mono",
                         zone="1",
                         value=DSP_DUAL_MONO.get(raw),
                         queue_commands=None))

    return parsed

def atk(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atk",
                         base_property="dsp",
                         property_name="fixed_pcm",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def atl(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atj",
                         base_property="dsp",
                         property_name="drc",
                         zone="1",
                         value=DSP_DRC.get(raw),
                         queue_commands=None))

    return parsed

def atm(raw: str, _param: dict) -> list:

    value = int(raw) * -5
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atm",
                         base_property="dsp",
                         property_name="lfe_att",
                         zone="1",
                         value="off" if value < -20 else value,
                         queue_commands=None))

    return parsed

def atn(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atm",
                         base_property="dsp",
                         property_name="sacd_gain",
                         zone="1",
                         value=6 if bool(raw) else 0,
                         queue_commands=None))

    return parsed

def ato(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ato",
                         base_property="dsp",
                         property_name="auto_delay",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def atp(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atp",
                         base_property="dsp",
                         property_name="center_width",
                         zone="1",
                         value=int(raw),
                         queue_commands=None))

    return parsed

def atq(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atq",
                         base_property="dsp",
                         property_name="panorama",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def atr(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atr",
                         base_property="dsp",
                         property_name="dimension",
                         zone="1",
                         value=int(raw) - 50,
                         queue_commands=None))

    return parsed

def ats(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ats",
                         base_property="dsp",
                         property_name="center_image",
                         zone="1",
                         value=float(raw) / 10,
                         queue_commands=None))

    return parsed

def att(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atr",
                         base_property="dsp",
                         property_name="effect",
                         zone="1",
                         value=int(raw) * 10,
                         queue_commands=None))

    return parsed

def atu(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atu",
                         base_property="dsp",
                         property_name="height_gain",
                         zone="1",
                         value=DSP_HEIGHT_GAIN.get(raw),
                         queue_commands=None))

    return parsed

def atv(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atv",
                         base_property="dsp",
                         property_name="digital_filter",
                         zone="1",
                         value=DSP_DIGITAL_FILTER.get(raw),
                         queue_commands=None))

    return parsed

def atw(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="atw",
                         base_property="dsp",
                         property_name="loudness_management",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def ara(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="ara",
                         base_property="dsp",
                         property_name="center_spread",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed

def arb(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="arb",
                         base_property="dsp",
                         property_name="rendering_mode",
                         zone="1",
                         value="object base" if int(raw) == 0 else "channel base",
                         queue_commands=None))

    return parsed

def vdp(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vdp",
                         base_property="dsp",
                         property_name="virtual_depth",
                         zone="1",
                         value=DSP_VIRTUAL_DEPTH.get(raw),
                         queue_commands=None))

    return parsed

def vwd(raw: str, _param: dict) -> list:
    parsed = []
    parsed.append(Response(raw=raw,
                         response_command="vwd",
                         base_property="dsp",
                         property_name="virtual_wide",
                         zone="1",
                         value=bool(raw),
                         queue_commands=None))

    return parsed
