"""Main aiopioneer parsing classes and functions"""

from aiopioneer.const import Zones
from .system import SystemParsers
from .audio import AudioParsers
from .tuner import TunerParsers
from .dsp import DspParsers
from .information import InformationParsers


def process_raw(raw: str, _param: dict) -> list:
    """Handler to pass the raw response to the correct parser."""
    if raw.startswith("PWR"):
        return SystemParsers.power(raw[3:], _param)
    if raw.startswith("APR"):
        return SystemParsers.power(raw[3:], _param, Zones.Z2, "APR")
    if raw.startswith("BPR"):
        return SystemParsers.power(raw[3:], _param, Zones.Z3, "BPR")
    if raw.startswith("ZEP"):
        return SystemParsers.power(raw[3:], _param, Zones.HDZ, "ZEP")
    if raw.startswith("FN"):
        return SystemParsers.input_source(raw[2:], _param)
    if raw.startswith("Z2F"):
        return SystemParsers.input_source(raw[3:], _param, Zones.Z2, "Z2F")
    if raw.startswith("Z3F"):
        return SystemParsers.input_source(raw[3:], _param, Zones.Z3, "Z3F")
    if raw.startswith("ZEA"):
        return SystemParsers.input_source(raw[3:], _param, Zones.HDZ, "ZEA")
    if raw.startswith("VOL"):
        return SystemParsers.volume(raw[3:], _param)
    if raw.startswith("ZV"):
        return SystemParsers.volume(raw[2:], _param, Zones.Z2, "ZV")
    if raw.startswith("YV"):
        return SystemParsers.volume(raw[2:], _param, Zones.Z3, "YV")
    if raw.startswith("XV"):
        return SystemParsers.volume(raw[2:], _param, Zones.HDZ, "XV")
    if raw.startswith("MUT"):
        return SystemParsers.mute(raw[3:], _param)
    if raw.startswith("Z2MUT"):
        return SystemParsers.mute(raw[5:], _param, Zones.Z2, "Z2MUT")
    if raw.startswith("Z3MUT"):
        return SystemParsers.mute(raw[5:], _param, Zones.Z3, "Z3MUT")
    if raw.startswith("HZMUT"):
        return SystemParsers.mute(raw[5:], _param, Zones.HDZ, "HZMUT")
    if raw.startswith("SR"):
        return AudioParsers.listening_mode(raw[2:], _param)
    if raw.startswith("TO"):
        return AudioParsers.tone(raw[2:], _param)
    if raw.startswith("BA"):
        return AudioParsers.tone_bass(raw[2:], _param)
    if raw.startswith("TR"):
        return AudioParsers.tone_treble(raw[2:], _param)
    if raw.startswith("ZGA"):
        return AudioParsers.tone(raw[3:], _param, Zones.Z2, "ZGA")
    if raw.startswith("ZGB"):
        return AudioParsers.tone_bass(raw[3:], _param, Zones.Z2, "ZGB")
    if raw.startswith("ZGC"):
        return AudioParsers.tone_treble(raw[3:], _param, Zones.Z2, "ZGC")
    if raw.startswith("SPK"):
        return SystemParsers.speaker_modes(raw[3:], _param)
    if raw.startswith("HO"):
        return SystemParsers.hdmi_out(raw[2:], _param)
    if raw.startswith("HA"):
        return SystemParsers.hdmi_audio(raw[2:], _param)
    if raw.startswith("PQ"):
        return SystemParsers.pqls(raw[2:], _param)
    if raw.startswith("SAA"):
        return SystemParsers.dimmer(raw[3:], _param)
    if raw.startswith("SAB"):
        return SystemParsers.sleep(raw[3:], _param)
    if raw.startswith("SAC"):
        return SystemParsers.amp_status(raw[3:], _param)
    if raw.startswith("PKL"):
        return SystemParsers.panel_lock(raw[3:], _param)
    if raw.startswith("RML"):
        return SystemParsers.remote_lock(raw[3:], _param)
    if raw.startswith("SSF"):
        return SystemParsers.speaker_system(raw[3:], _param)
    if raw.startswith("AUA"):
        return SystemParsers.audio_parameter_prohibitation(raw[3:], _param)
    if raw.startswith("AUB"):
        return SystemParsers.audio_parameter_working(raw[3:], _param)
    if raw.startswith("FRF"):
        return TunerParsers.frequency_fm(raw[3:], _param)
    if raw.startswith("FRA"):
        return TunerParsers.frequency_am(raw[3:], _param)
    if raw.startswith("PR"):
        return TunerParsers.preset(raw[2:], _param)
    if raw.startswith("CLV"):
        return AudioParsers.channel_levels(raw[3:], _param)
    if raw.startswith("ZGE"):
        return AudioParsers.channel_levels(raw[3:], _param, Zones.Z2, "ZGE")
    if raw.startswith("ZHE"):
        return AudioParsers.channel_levels(raw[3:], _param, Zones.Z3, "ZHE")
    if raw.startswith("MC"):
        return DspParsers.mcacc_setting(raw[2:], _param)
    if raw.startswith("IS"):
        return DspParsers.phasecontrol(raw[2:], _param)
    if raw.startswith("VSP"):
        return DspParsers.virtual_speakers(raw[3:], _param)
    if raw.startswith("VSB"):
        return DspParsers.virtual_soundback(raw[3:], _param)
    if raw.startswith("VHT"):
        return DspParsers.virtual_height(raw[3:], _param)
    if raw.startswith("SDA"):
        return DspParsers.signal_select(raw[3:], _param)
    if raw.startswith("SDB"):
        return DspParsers.input_att(raw[3:], _param)
    if raw.startswith("ATA"):
        return DspParsers.sound_retriever(raw[3:], _param)
    if raw.startswith("ATC"):
        return DspParsers.equalizer(raw[3:], _param)
    if raw.startswith("ATD"):
        return DspParsers.standing_wave(raw[3:], _param)
    if raw.startswith("ATE"):
        return DspParsers.phase_control_plus(raw[3:], _param)
    if raw.startswith("ATF"):
        return DspParsers.sound_delay(raw[3:], _param)
    if raw.startswith("ATG"):
        return DspParsers.digital_noise_reduction(raw[3:], _param)
    if raw.startswith("ATH"):
        return DspParsers.dialog_enhancement(raw[3:], _param)
    if raw.startswith("ATI"):
        return DspParsers.hi_bit(raw[3:], _param)
    if raw.startswith("ATJ"):
        return DspParsers.dual_mono(raw[3:], _param)
    if raw.startswith("ATK"):
        return DspParsers.fixed_pcm(raw[3:], _param)
    if raw.startswith("atl"):
        return DspParsers.atl(raw[3:], _param)
    if raw.startswith("atm"):
        return DspParsers.atm(raw[3:], _param)
    if raw.startswith("atn"):
        return DspParsers.atn(raw[3:], _param)
    if raw.startswith("ato"):
        return DspParsers.ato(raw[3:], _param)
    if raw.startswith("atp"):
        return DspParsers.atp(raw[3:], _param)
    if raw.startswith("atq"):
        return DspParsers.atq(raw[3:], _param)
    if raw.startswith("atr"):
        return DspParsers.atr(raw[3:], _param)
    if raw.startswith("ats"):
        return DspParsers.ats(raw[3:], _param)
    if raw.startswith("att"):
        return DspParsers.att(raw[3:], _param)
    if raw.startswith("atu"):
        return DspParsers.atu(raw[3:], _param)
    if raw.startswith("atv"):
        return DspParsers.atv(raw[3:], _param)
    if raw.startswith("atw"):
        return DspParsers.atw(raw[3:], _param)
    if raw.startswith("aty"):
        return DspParsers.aty(raw[3:], _param)
    if raw.startswith("atz"):
        return DspParsers.atz(raw[3:], _param)
    if raw.startswith("vdp"):
        return DspParsers.vdp(raw[3:], _param)
    if raw.startswith("vwd"):
        return DspParsers.vwd(raw[3:], _param)
    if raw.startswith("ara"):
        return DspParsers.ara(raw[3:], _param)
    if raw.startswith("arb"):
        return DspParsers.arb(raw[3:], _param)
    if raw.startswith("ast"):
        return InformationParsers.ast(raw[3:], _param)
    if raw.startswith("vst"):
        return InformationParsers.vst(raw[3:], _param)

    return None



class Response():
    """Model defining a parsed response for dynamic parsing into aiopioneer properties."""

    def __init__(
            self,
            raw: str,
            response_command: str,
            base_property: str,
            property_name: str,
            zone: str,
            value,
            queue_commands: list
        ):
        self.raw = raw
        self.response_command =  response_command
        self.base_property = base_property
        self.property_name = property_name
        self.zone = zone
        self.value = value
        self.command_queue = queue_commands
