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
    if raw.lower().startswith("pwr"):
        return pwr(raw[3:], _param)
    if raw.lower().startswith("apr"):
        return apr(raw[3:], _param)
    if raw.lower().startswith("bpr"):
        return bpr(raw[3:], _param)
    if raw.lower().startswith("zep"):
        return zep(raw[3:], _param)
    if raw.lower().startswith("fn"):
        return fn(raw[2:], _param)
    if raw.lower().startswith("z2f"):
        return z2f(raw[3:], _param)
    if raw.lower().startswith("z3f"):
        return z3f(raw[3:], _param)
    if raw.lower().startswith("zea"):
        return zea(raw[3:], _param)
    if raw.lower().startswith("vol"):
        return vol(raw[3:], _param)
    if raw.lower().startswith("zv"):
        return zv(raw[2:], _param)
    if raw.lower().startswith("yv"):
        return yv(raw[2:], _param)
    if raw.lower().startswith("xv"):
        return xv(raw[2:], _param)
    if raw.lower().startswith("mut"):
        return mut(raw[3:], _param)
    if raw.lower().startswith("z2mut"):
        return z2mut(raw[5:], _param)
    if raw.lower().startswith("z3mut"):
        return z3mut(raw[5:], _param)
    if raw.lower().startswith("hzmut"):
        return hzmut(raw[5:], _param)
    if raw.lower().startswith("spk"):
        return spk(raw[3:], _param)
    if raw.lower().startswith("ho"):
        return ho(raw[2:], _param)
    if raw.lower().startswith("ha"):
        return ha(raw[2:], _param)
    if raw.lower().startswith("pq"):
        return pq(raw[2:], _param)
    if raw.lower().startswith("saa"):
        return saa(raw[3:], _param)
    if raw.lower().startswith("sab"):
        return sab(raw[3:], _param)
    if raw.lower().startswith("sac"):
        return sac(raw[3:], _param)
    if raw.lower().startswith("pkl"):
        return pkl(raw[3:], _param)
    if raw.lower().startswith("rml"):
        return rml(raw[3:], _param)
    if raw.lower().startswith("frf"):
        return frf(raw[3:], _param)
    if raw.lower().startswith("fra"):
        return fra(raw[3:], _param)
    if raw.lower().startswith("pr"):
        return pr(raw[2:], _param)
    if raw.lower().startswith("clv"):
        return clv(raw[3:], _param)
    if raw.lower().startswith("zge"):
        return zge(raw[3:], _param)
    if raw.lower().startswith("zhe"):
        return zhe(raw[3:], _param)
    if raw.lower().startswith("mc"):
        return mc(raw[2:], _param)
    if raw.lower().startswith("is"):
        return is_phasecontrol(raw[2:], _param)
    if raw.lower().startswith("vsp"):
        return vsp(raw[3:], _param)
    if raw.lower().startswith("vsb"):
        return vsb(raw[3:], _param)
    if raw.lower().startswith("vht"):
        return vht(raw[3:], _param)
    if raw.lower().startswith("sda"):
        return sda(raw[3:], _param)
    if raw.lower().startswith("sdb"):
        return sdb(raw[3:], _param)
    if raw.lower().startswith("ata"):
        return ata(raw[3:], _param)
    if raw.lower().startswith("atc"):
        return atc(raw[3:], _param)
    if raw.lower().startswith("atd"):
        return atd(raw[3:], _param)
    if raw.lower().startswith("ate"):
        return ate(raw[3:], _param)
    if raw.lower().startswith("atf"):
        return atf(raw[3:], _param)
    if raw.lower().startswith("atg"):
        return atg(raw[3:], _param)
    if raw.lower().startswith("ath"):
        return ath(raw[3:], _param)
    if raw.lower().startswith("ati"):
        return ati(raw[3:], _param)
    if raw.lower().startswith("atj"):
        return atj(raw[3:], _param)
    if raw.lower().startswith("atk"):
        return atk(raw[3:], _param)
    if raw.lower().startswith("atl"):
        return atl(raw[3:], _param)
    if raw.lower().startswith("atm"):
        return atm(raw[3:], _param)
    if raw.lower().startswith("atn"):
        return atn(raw[3:], _param)
    if raw.lower().startswith("ato"):
        return ato(raw[3:], _param)
    if raw.lower().startswith("atp"):
        return atp(raw[3:], _param)
    if raw.lower().startswith("atq"):
        return atq(raw[3:], _param)
    if raw.lower().startswith("atr"):
        return atr(raw[3:], _param)
    if raw.lower().startswith("ats"):
        return ats(raw[3:], _param)
    if raw.lower().startswith("att"):
        return att(raw[3:], _param)
    if raw.lower().startswith("atu"):
        return atu(raw[3:], _param)
    if raw.lower().startswith("atv"):
        return atv(raw[3:], _param)
    if raw.lower().startswith("atw"):
        return atw(raw[3:], _param)
    if raw.lower().startswith("aty"):
        return aty(raw[3:], _param)
    if raw.lower().startswith("atz"):
        return atz(raw[3:], _param)
    if raw.lower().startswith("vdp"):
        return vdp(raw[3:], _param)
    if raw.lower().startswith("vwd"):
        return vwd(raw[3:], _param)
    if raw.lower().startswith("ara"):
        return ara(raw[3:], _param)
    if raw.lower().startswith("arb"):
        return arb(raw[3:], _param)
    if raw.lower().startswith("ast"):
        return ast(raw[3:], _param)
    if raw.lower().startswith("vst"):
        return vst(raw[3:], _param)

    return None
