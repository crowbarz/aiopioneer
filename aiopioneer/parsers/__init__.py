"""aiopioneer response parsers."""

from .system import *
from .audio import *
from .tuner import *
from .video import *
from .dsp import *
from .information import *
from .const import Zones

def process_raw(raw: str, _param: dict) -> list:
    """Handler to pass the raw response to the correct parser."""
    if raw.startswith("PWR"):
        return power(raw[3:], _param)
    if raw.startswith("APR"):
        return power(raw[3:], _param, Zones.Z2, "APR")
    if raw.startswith("BPR"):
        return power(raw[3:], _param, Zones.Z3, "BPR")
    if raw.startswith("ZEP"):
        return power(raw[3:], _param, Zones.HDZ, "ZEP")
    if raw.startswith("FN"):
        return input_source(raw[2:], _param)
    if raw.startswith("Z2F"):
        return input_source(raw[3:], _param, Zones.Z2, "Z2F")
    if raw.startswith("Z3F"):
        return input_source(raw[3:], _param, Zones.Z3, "Z3F")
    if raw.startswith("ZEA"):
        return input_source(raw[3:], _param, Zones.HDZ, "ZEA")
    if raw.startswith("VOL"):
        return volume(raw[3:], _param)
    if raw.startswith("ZV"):
        return volume(raw[2:], _param, Zones.Z2, "ZV")
    if raw.startswith("YV"):
        return volume(raw[2:], _param, Zones.Z3, "YV")
    if raw.startswith("XV"):
        return volume(raw[2:], _param, Zones.HDZ, "XV")
    if raw.startswith("MUT"):
        return mute(raw[3:], _param)
    if raw.startswith("Z2MUT"):
        return mute(raw[5:], _param, Zones.Z2, "Z2MUT")
    if raw.startswith("Z3MUT"):
        return mute(raw[5:], _param, Zones.Z3, "Z3MUT")
    if raw.startswith("HZMUT"):
        return mute(raw[5:], _param, Zones.HDZ, "HZMUT")
    if raw.startswith("SR"):
        return listening_mode(raw[2:], _param)
    if raw.startswith("TO"):
        return tone(raw[2:], _param)
    if raw.startswith("BA"):
        return tone_bass(raw[2:], _param)
    if raw.startswith("TR"):
        return tone_treble(raw[2:], _param)
    if raw.startswith("ZGA"):
        return tone(raw[3:], _param, Zones.Z2, "ZGA")
    if raw.startswith("ZGB"):
        return tone_bass(raw[3:], _param, Zones.Z2, "ZGB")
    if raw.startswith("ZGC"):
        return tone_treble(raw[3:], _param, Zones.Z2, "ZGC")
    if raw.startswith("SPK"):
        return speaker_modes(raw[3:], _param)
    if raw.startswith("HO"):
        return hdmi_out(raw[2:], _param)
    if raw.startswith("HA"):
        return hdmi_audio(raw[2:], _param)
    if raw.startswith("PQ"):
        return pqls(raw[2:], _param)
    if raw.startswith("SAA"):
        return dimmer(raw[3:], _param)
    if raw.startswith("SAB"):
        return sleep(raw[3:], _param)
    if raw.startswith("SAC"):
        return amp_status(raw[3:], _param)
    if raw.startswith("PKL"):
        return panel_lock(raw[3:], _param)
    if raw.startswith("RML"):
        return remote_lock(raw[3:], _param)
    if raw.startswith("SSF"):
        return speaker_system(raw[3:], _param)
    if raw.startswith("AUA"):
        return audio_parameter_prohibitation(raw[3:], _param)
    if raw.startswith("AUB"):
        return audio_parameter_working(raw[3:], _param)
    if raw.startswith("frf"):
        return frf(raw[3:], _param)
    if raw.startswith("fra"):
        return fra(raw[3:], _param)
    if raw.startswith("pr"):
        return pr(raw[2:], _param)
    if raw.startswith("CLV"):
        return channel_levels(raw[3:], _param)
    if raw.startswith("ZGE"):
        return channel_levels(raw[3:], _param, Zones.Z2, "ZGE")
    if raw.startswith("ZHE"):
        return channel_levels(raw[3:], _param, Zones.Z3, "ZHE")
    if raw.startswith("mc"):
        return mc(raw[2:], _param)
    if raw.startswith("is"):
        return is_phasecontrol(raw[2:], _param)
    if raw.startswith("vsp"):
        return vsp(raw[3:], _param)
    if raw.startswith("vsb"):
        return vsb(raw[3:], _param)
    if raw.startswith("vht"):
        return vht(raw[3:], _param)
    if raw.startswith("sda"):
        return sda(raw[3:], _param)
    if raw.startswith("sdb"):
        return sdb(raw[3:], _param)
    if raw.startswith("ata"):
        return ata(raw[3:], _param)
    if raw.startswith("atc"):
        return atc(raw[3:], _param)
    if raw.startswith("atd"):
        return atd(raw[3:], _param)
    if raw.startswith("ate"):
        return ate(raw[3:], _param)
    if raw.startswith("atf"):
        return atf(raw[3:], _param)
    if raw.startswith("atg"):
        return atg(raw[3:], _param)
    if raw.startswith("ath"):
        return ath(raw[3:], _param)
    if raw.startswith("ati"):
        return ati(raw[3:], _param)
    if raw.startswith("atj"):
        return atj(raw[3:], _param)
    if raw.startswith("atk"):
        return atk(raw[3:], _param)
    if raw.startswith("atl"):
        return atl(raw[3:], _param)
    if raw.startswith("atm"):
        return atm(raw[3:], _param)
    if raw.startswith("atn"):
        return atn(raw[3:], _param)
    if raw.startswith("ato"):
        return ato(raw[3:], _param)
    if raw.startswith("atp"):
        return atp(raw[3:], _param)
    if raw.startswith("atq"):
        return atq(raw[3:], _param)
    if raw.startswith("atr"):
        return atr(raw[3:], _param)
    if raw.startswith("ats"):
        return ats(raw[3:], _param)
    if raw.startswith("att"):
        return att(raw[3:], _param)
    if raw.startswith("atu"):
        return atu(raw[3:], _param)
    if raw.startswith("atv"):
        return atv(raw[3:], _param)
    if raw.startswith("atw"):
        return atw(raw[3:], _param)
    if raw.startswith("aty"):
        return aty(raw[3:], _param)
    if raw.startswith("atz"):
        return atz(raw[3:], _param)
    if raw.startswith("vdp"):
        return vdp(raw[3:], _param)
    if raw.startswith("vwd"):
        return vwd(raw[3:], _param)
    if raw.startswith("ara"):
        return ara(raw[3:], _param)
    if raw.startswith("arb"):
        return arb(raw[3:], _param)
    if raw.startswith("ast"):
        return ast(raw[3:], _param)
    if raw.startswith("vst"):
        return vst(raw[3:], _param)

    return None
