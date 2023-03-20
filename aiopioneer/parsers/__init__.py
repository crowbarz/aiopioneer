"""aiopioneer response parsers."""

from .system import *
from .audio import *
from .tuner import *
from .video import *
from .dsp import *
from .information import *
from .const import Response

def process_raw(raw: str, _param: dict) -> list:
    """Handler to pass the raw response to the correct parser."""
    if raw.startswith("pwr"):
        return pwr(raw[3:], _param)
    if raw.startswith("apr"):
        return apr(raw[3:], _param)
    if raw.startswith("bpr"):
        return bpr(raw[3:], _param)
    if raw.startswith("zep"):
        return zep(raw[3:], _param)
    if raw.startswith("fn"):
        return fn(raw[2:], _param)
    if raw.startswith("z2f"):
        return z2f(raw[3:], _param)
    if raw.startswith("z3f"):
        return z3f(raw[3:], _param)
    if raw.startswith("zea"):
        return zea(raw[3:], _param)
    if raw.startswith("vol"):
        return vol(raw[3:], _param)
    if raw.startswith("zv"):
        return zv(raw[2:], _param)
    if raw.startswith("yv"):
        return yv(raw[2:], _param)
    if raw.startswith("xv"):
        return xv(raw[2:], _param)
    if raw.startswith("mut"):
        return mut(raw[3:], _param)
    if raw.startswith("z2mut"):
        return z2mut(raw[5:], _param)
    if raw.startswith("z3mut"):
        return z3mut(raw[5:], _param)
    if raw.startswith("HZMUT"):
        return hzmut(raw[5:], _param)
    if raw.startswith("SR"):
        return listening_mode(raw[2:], _param)
    if raw.startswith("TO"):
        return tone(raw[2:], _param)
    if raw.startswith("BA"):
        return tone_bass(raw[2:], _param)
    if raw.startswith("TR"):
        return tone_treble(raw[2:], _param)
    if raw.startswith("ZGA"):
        return tone(raw[3:], _param, "2", "ZGA")
    if raw.startswith("ZGB"):
        return tone_bass(raw[3:], _param, "2", "ZGB")
    if raw.startswith("ZGC"):
        return tone_treble(raw[3:], _param, "2", "ZGC")
    if raw.startswith("spk"):
        return spk(raw[3:], _param)
    if raw.startswith("ho"):
        return ho(raw[2:], _param)
    if raw.startswith("ha"):
        return ha(raw[2:], _param)
    if raw.startswith("pq"):
        return pq(raw[2:], _param)
    if raw.startswith("saa"):
        return saa(raw[3:], _param)
    if raw.startswith("sab"):
        return sab(raw[3:], _param)
    if raw.startswith("sac"):
        return sac(raw[3:], _param)
    if raw.startswith("pkl"):
        return pkl(raw[3:], _param)
    if raw.startswith("rml"):
        return rml(raw[3:], _param)
    if raw.startswith("frf"):
        return frf(raw[3:], _param)
    if raw.startswith("fra"):
        return fra(raw[3:], _param)
    if raw.startswith("pr"):
        return pr(raw[2:], _param)
    if raw.startswith("CLV"):
        return channel_levels(raw[3:], _param)
    if raw.startswith("ZGE"):
        return channel_levels(raw[3:], _param, "2", "ZGE")
    if raw.startswith("ZHE"):
        return channel_levels(raw[3:], _param, "3", "ZHE")
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
