"""Pioneer AVR commands."""

from .const import Zone
from .parsers.code_map import CodeBoolMap
from .parsers.dsp import (
    DspMcaccMemorySet,
    DspPhaseControl,
    DspSignalSelect,
    DspPhaseControlPlus,
    DspVirtualSpeakers,
    DspSoundDelay,
    DspAudioScaler,
    DspDialogEnhancement,
    DspDualMono,
    DspDynamicRange,
    DspLfeAttenuator,
    DspSacdGain,
    DspCenterWidth,
    DspDimension,
    DspCenterImage,
    DspEffect,
    DspHeightGain,
    DspDigitalFilter,
    DspUpSampling,
    DspVirtualDepth,
    DspRenderingMode,
)
from .parsers.system import (
    SpeakerMode,
    HdmiOut,
    Hdmi3Out,
    HdmiAudio,
    Pqls,
    Dimmer,
    SleepTime,
    AmpMode,
    PanelLock,
)
from .parsers.video import (
    AdvancedVideoAdjust,
    VideoAspect,
    VideoInt08Map,
    VideoProgMotion,
    VideoInt66Map,
    VideoPureCinema,
    VideoResolution,
    VideoStreamSmoother,
    VideoSuperResolution,
)

PIONEER_COMMANDS = {
    "query_model": {Zone.Z1: ["?RGD", "RGD"]},
    "system_query_mac_addr": {Zone.Z1: ["?SVB", "SVB"]},
    "system_query_software_version": {Zone.Z1: ["?SSI", "SSI"]},
    "turn_on": {
        Zone.Z1: ["PO", "PWR"],
        Zone.Z2: ["APO", "APR"],
        Zone.Z3: ["BPO", "BPR"],
        Zone.HDZ: ["ZEO", "ZEP"],
    },
    "turn_off": {
        Zone.Z1: ["PF", "PWR"],
        Zone.Z2: ["APF", "APR"],
        Zone.Z3: ["BPF", "BPR"],
        Zone.HDZ: ["ZEF", "ZEP"],
    },
    "select_source": {
        Zone.Z1: ["FN", "FN"],
        Zone.Z2: ["ZS", "Z2F"],
        Zone.Z3: ["ZT", "Z3F"],
        Zone.HDZ: ["ZEA", "ZEA"],
    },
    "volume_up": {
        Zone.Z1: ["VU", "VOL"],
        Zone.Z2: ["ZU", "ZV"],
        Zone.Z3: ["YU", "YV"],
        Zone.HDZ: ["HZU", "XV"],
    },
    "volume_down": {
        Zone.Z1: ["VD", "VOL"],
        Zone.Z2: ["ZD", "ZV"],
        Zone.Z3: ["YD", "YV"],
        Zone.HDZ: ["HZD", "XV"],
    },
    "set_volume_level": {
        Zone.Z1: ["VL", "VOL"],
        Zone.Z2: ["ZV", "ZV"],
        Zone.Z3: ["YV", "YV"],
        Zone.HDZ: ["HZV", "XV"],
    },
    "mute_on": {
        Zone.Z1: ["MO", "MUT"],
        Zone.Z2: ["Z2MO", "Z2MUT"],
        Zone.Z3: ["Z3MO", "Z3MUT"],
        Zone.HDZ: ["HZMO", "HZMUT"],
    },
    "mute_off": {
        Zone.Z1: ["MF", "MUT"],
        Zone.Z2: ["Z2MF", "Z2MUT"],
        Zone.Z3: ["Z3MF", "Z3MUT"],
        Zone.HDZ: ["HZMF", "HZMUT"],
    },
    "query_power": {
        Zone.Z1: ["?P", "PWR"],
        Zone.Z2: ["?AP", "APR"],
        Zone.Z3: ["?BP", "BPR"],
        Zone.HDZ: ["?ZEP", "ZEP"],
    },
    "query_volume": {
        Zone.Z1: ["?V", "VOL"],
        Zone.Z2: ["?ZV", "ZV"],
        Zone.Z3: ["?YV", "YV"],
        Zone.HDZ: ["?HZV", "XV"],
    },
    "query_mute": {
        Zone.Z1: ["?M", "MUT"],
        Zone.Z2: ["?Z2M", "Z2MUT"],
        Zone.Z3: ["?Z3M", "Z3MUT"],
        Zone.HDZ: ["?HZM", "HZMUT"],
    },
    "query_source_id": {
        Zone.Z1: ["?F", "FN"],
        Zone.Z2: ["?ZS", "Z2F"],
        Zone.Z3: ["?ZT", "Z3F"],
        Zone.HDZ: ["?ZEA", "ZEA"],
    },
    "query_listening_mode": {Zone.Z1: ["?S", "SR"]},
    "set_listening_mode": {Zone.Z1: ["SR", "SR"]},
    ## basic
    "query_basic_audio_information": {Zone.Z1: ["?AST", "AST"]},
    "query_basic_video_information": {Zone.Z1: ["?VST", "VST"]},
    ## amp
    "query_amp_speaker_mode": {Zone.Z1: ["?SPK", "SPK"]},
    "set_amp_speaker_mode": {Zone.Z1: ["SPK", "SPK"], "args": [SpeakerMode]},
    "query_amp_hdmi_out": {Zone.Z1: ["?HO", "HO"]},
    "set_amp_hdmi_out": {Zone.Z1: ["HO", "HO"], "args": [HdmiOut]},
    "query_amp_hdmi3_out": {Zone.Z1: ["?HDO", "HDO"]},
    "set_amp_hdmi3_out": {Zone.Z1: ["HDO", "HDO"], "args": [Hdmi3Out]},
    "query_amp_hdmi_audio": {Zone.Z1: ["?HA", "HA"]},
    "set_amp_hdmi_audio": {Zone.Z1: ["HA", "HA"], "args": [HdmiAudio]},
    "query_amp_pqls": {Zone.Z1: ["?PQ", "PQ"]},
    "set_amp_pqls": {Zone.Z1: ["PQ", "PQ"], "args": [Pqls]},
    "set_amp_dimmer": {Zone.Z1: ["SAA", "SAA"], "args": [Dimmer]},
    ## NOTE: no amp dimmer query command
    "query_amp_sleep_time": {Zone.Z1: ["?SAB", "SAB"]},
    "set_amp_sleep_time": {Zone.Z1: ["SAB", "SAB"], "args": [SleepTime]},
    "query_amp_mode": {Zone.Z1: ["?SAC", "SAC"]},
    "set_amp_mode": {Zone.Z1: ["SAC", "SAC"], "args": [AmpMode]},
    "query_amp_panel_lock": {Zone.Z1: ["?PKL", "PKL"]},
    "set_amp_panel_lock": {Zone.Z1: ["PKL", "PKL"], "args": [PanelLock]},
    "query_amp_remote_lock": {Zone.Z1: ["?RML", "RML"]},
    "set_amp_remote_lock": {Zone.Z1: ["RML", "RML"], "args": [CodeBoolMap]},
    ## dsp
    "set_dsp_mcacc_memory_set": {Zone.Z1: ["MC", "MC"], "args": [DspMcaccMemorySet]},
    "set_dsp_phase_control": {Zone.Z1: ["IS", "IS"], "args": [DspPhaseControl]},
    "set_dsp_phase_control_plus": {
        Zone.Z1: ["ATE", "ATE"],
        "args": [DspPhaseControlPlus],
    },
    "set_dsp_virtual_speakers": {Zone.Z1: ["VSP", "VSP"], "args": [DspVirtualSpeakers]},
    "set_dsp_virtual_sb": {Zone.Z1: ["VSB", "VSB"], "args": [CodeBoolMap]},
    "set_dsp_virtual_height": {Zone.Z1: ["VHT", "VHT"], "args": [CodeBoolMap]},
    "set_dsp_virtual_wide": {Zone.Z1: ["VWD", "VWD"], "args": [CodeBoolMap]},
    "set_dsp_virtual_depth": {Zone.Z1: ["VDP", "VDP"], "args": [DspVirtualDepth]},
    "set_dsp_sound_retriever": {Zone.Z1: ["ATA", "ATA"], "args": [CodeBoolMap]},
    "set_dsp_signal_select": {Zone.Z1: ["SDA", "SDA"], "args": [DspSignalSelect]},
    "set_dsp_input_attenuator": {Zone.Z1: ["SDB", "SDB"], "args": [CodeBoolMap]},
    "set_dsp_eq": {Zone.Z1: ["ATC", "ATC"], "args": [CodeBoolMap]},
    "set_dsp_standing_wave": {Zone.Z1: ["ATD", "ATD"], "args": [CodeBoolMap]},
    "set_dsp_sound_delay": {Zone.Z1: ["ATF", "ATF"], "args": [DspSoundDelay]},
    "set_dsp_digital_noise_reduction": {
        Zone.Z1: ["ATG", "ATG"],
        "args": [CodeBoolMap],
    },
    "set_dsp_dialog_enhancement": {
        Zone.Z1: ["ATH", "ATH"],
        "args": [DspDialogEnhancement],
    },
    "set_dsp_audio_scaler": {Zone.Z1: ["ATY", "ATY"], "args": [DspAudioScaler]},
    "set_dsp_hi_bit": {Zone.Z1: ["ATI", "ATI"], "args": [CodeBoolMap]},
    "set_dsp_up_sampling": {Zone.Z1: ["ATZ", "ATZ"], "args": [DspUpSampling]},
    "set_dsp_digital_filter": {Zone.Z1: ["ATV", "ATV"], "args": [DspDigitalFilter]},
    "set_dsp_dual_mono": {Zone.Z1: ["ATJ", "ATJ"], "args": [DspDualMono]},
    "set_dsp_fixed_pcm": {Zone.Z1: ["ATK", "ATK"], "args": [CodeBoolMap]},
    "set_dsp_dynamic_range": {Zone.Z1: ["ATL", "ATL"], "args": [DspDynamicRange]},
    "set_dsp_lfe_attenuator": {Zone.Z1: ["ATM", "ATM"], "args": [DspLfeAttenuator]},
    "set_dsp_sacd_gain": {Zone.Z1: ["ATN", "ATN"], "args": [DspSacdGain]},
    "set_dsp_auto_delay": {Zone.Z1: ["ATO", "ATO"], "args": [CodeBoolMap]},
    "set_dsp_center_width": {Zone.Z1: ["ATP", "ATP"], "args": [DspCenterWidth]},
    "set_dsp_panorama": {Zone.Z1: ["ATQ", "ATQ"], "args": [CodeBoolMap]},
    "set_dsp_dimension": {Zone.Z1: ["ATR", "ATR"], "args": [DspDimension]},
    "set_dsp_center_image": {Zone.Z1: ["ATS", "ATS"], "args": [DspCenterImage]},
    "set_dsp_effect": {Zone.Z1: ["ATT", "ATT"], "args": [DspEffect]},
    "set_dsp_height_gain": {Zone.Z1: ["ATU", "ATU"], "args": [DspHeightGain]},
    "set_dsp_loudness_management": {Zone.Z1: ["ATW", "ATW"], "args": [CodeBoolMap]},
    "set_dsp_center_spread": {Zone.Z1: ["ARA", "ARA"], "args": [CodeBoolMap]},
    "set_dsp_rendering_mode": {Zone.Z1: ["ARB", "ARB"], "args": [DspRenderingMode]},
    "query_dsp_mcacc_memory_query": {Zone.Z1: ["?MC", "MC"]},
    "query_dsp_phase_control": {Zone.Z1: ["?IS", "IS"]},
    "query_dsp_virtual_speakers": {Zone.Z1: ["?VSP", "VSP"]},
    "query_dsp_virtual_sb": {Zone.Z1: ["?VSB", "VSB"]},
    "query_dsp_virtual_height": {Zone.Z1: ["?VHT", "VHT"]},
    "query_dsp_sound_retriever": {Zone.Z1: ["?ATA", "ATA"]},
    "query_dsp_signal_select": {Zone.Z1: ["?SDA", "SDA"]},
    "query_dsp_input_attenuator": {Zone.Z1: ["?SDB", "SDB"]},
    "query_dsp_eq": {Zone.Z1: ["?ATC", "ATC"]},
    "query_dsp_standing_wave": {Zone.Z1: ["?ATD", "ATD"]},
    "query_dsp_phase_control_plus": {Zone.Z1: ["?ATE", "ATE"]},
    "query_dsp_sound_delay": {Zone.Z1: ["?ATF", "ATF"]},
    "query_dsp_digital_noise_reduction": {Zone.Z1: ["?ATG", "ATG"]},
    "query_dsp_dialog_enhancement": {Zone.Z1: ["?ATH", "ATH"]},
    "query_dsp_audio_scaler": {Zone.Z1: ["?ATY", "ATY"]},
    "query_dsp_hi_bit": {Zone.Z1: ["?ATI", "ATI"]},
    "query_dsp_up_sampling": {Zone.Z1: ["?ATZ", "ATZ"]},
    "query_dsp_dual_mono": {Zone.Z1: ["?ATJ", "ATJ"]},
    "query_dsp_fixed_pcm": {Zone.Z1: ["?ATK", "ATK"]},
    "query_dsp_dynamic_range": {Zone.Z1: ["?ATL", "ATL"]},
    "query_dsp_lfe_attenuator": {Zone.Z1: ["?ATM", "ATM"]},
    "query_dsp_sacd_gain": {Zone.Z1: ["?ATN", "ATN"]},
    "query_dsp_auto_delay": {Zone.Z1: ["?ATO", "ATO"]},
    "query_dsp_center_width": {Zone.Z1: ["?ATP", "ATP"]},
    "query_dsp_panorama": {Zone.Z1: ["?ATQ", "ATQ"]},
    "query_dsp_dimension": {Zone.Z1: ["?ATR", "ATR"]},
    "query_dsp_center_image": {Zone.Z1: ["?ATS", "ATS"]},
    "query_dsp_effect": {Zone.Z1: ["?ATT", "ATT"]},
    "query_dsp_height_gain": {Zone.Z1: ["?ATU", "ATU"]},
    "query_dsp_virtual_depth": {Zone.Z1: ["?VDP", "VDP"]},
    "query_dsp_digital_filter": {Zone.Z1: ["?ATV", "ATV"]},
    "query_dsp_loudness_management": {Zone.Z1: ["?ATW", "ATW"]},
    "query_dsp_virtual_wide": {Zone.Z1: ["?VWD", "VWD"]},
    "query_center_spread": {Zone.Z1: ["?ARA", "ARA"]},
    "query_rendering_mode": {Zone.Z1: ["?ARB", "ARB"]},
    ## tone
    "query_tone_status": {Zone.Z1: ["?TO", "TO"], Zone.Z2: ["?ZGA", "ZGA"]},
    "query_tone_bass": {Zone.Z1: ["?BA", "BA"], Zone.Z2: ["?ZGB", "ZGB"]},
    "query_tone_treble": {Zone.Z1: ["?TR", "TR"], Zone.Z2: ["?ZGC", "ZGC"]},
    "set_tone_mode": {
        Zone.Z1: ["TO", "TO"],
        Zone.Z2: ["ZGA", "ZGA"],
    },
    "set_tone_bass": {
        Zone.Z1: ["BA", "BA"],
        Zone.Z2: ["ZGB", "ZGB"],
    },
    "set_tone_treble": {
        Zone.Z1: ["TR", "TR"],
        Zone.Z2: ["ZGC", "ZGC"],
    },
    ## channels
    "set_channel_levels": {
        Zone.Z1: ["CLV", "CLV"],
        Zone.Z2: ["ZGE", "ZGE"],
        Zone.Z3: ["ZHE", "ZHE"],
    },
    ## video
    "query_video_resolution": {Zone.Z1: ["?VTC", "VTC"]},
    "set_video_resolution": {Zone.Z1: ["VTC", "VTC"], "args": [VideoResolution]},
    "query_video_converter": {Zone.Z1: ["?VTB", "VTB"]},
    "set_video_converter": {Zone.Z1: ["VTB", "VTB"], "args": [CodeBoolMap]},
    "query_video_pure_cinema": {Zone.Z1: ["?VTD", "VTD"]},
    "set_video_pure_cinema": {Zone.Z1: ["VTD", "VTD"], "args": [VideoPureCinema]},
    "query_video_prog_motion": {Zone.Z1: ["?VTE", "VTE"]},
    "set_video_prog_motion": {Zone.Z1: ["VTE", "VTE"], "args": [VideoProgMotion]},
    "query_video_stream_smoother": {Zone.Z1: ["?VTF", "VTF"]},
    "set_video_stream_smoother": {
        Zone.Z1: ["VTF", "VTF"],
        "args": [VideoStreamSmoother],
    },
    "query_video_advanced_video_adjust": {Zone.Z1: ["?VTG", "VTG"]},
    "set_video_advanced_video_adjust": {
        Zone.Z1: ["VTG", "VTG"],
        "args": [AdvancedVideoAdjust],
    },
    "query_video_ynr": {Zone.Z1: ["?VTH", "VTH"]},
    "set_video_ynr": {Zone.Z1: ["VTH", "VTH"], "args": [VideoInt08Map]},
    "query_video_cnr": {Zone.Z1: ["?VTI", "VTI"]},
    "set_video_cnr": {Zone.Z1: ["VTI", "VTI"], "args": [VideoInt08Map]},
    "query_video_bnr": {Zone.Z1: ["?VTJ", "VTJ"]},
    "set_video_bnr": {Zone.Z1: ["VTJ", "VTJ"], "args": [VideoInt08Map]},
    "query_video_mnr": {Zone.Z1: ["?VTK", "VTK"]},
    "set_video_mnr": {Zone.Z1: ["VTK", "VTK"], "args": [VideoInt08Map]},
    "query_video_detail": {Zone.Z1: ["?VTL", "VTL"]},
    "set_video_detail": {Zone.Z1: ["VTL", "VTL"], "args": [VideoInt08Map]},
    "query_video_sharpness": {Zone.Z1: ["?VTM", "VTM"]},
    "set_video_sharpness": {Zone.Z1: ["VTM", "VTM"], "args": [VideoInt08Map]},
    "query_video_brightness": {Zone.Z1: ["?VTN", "VTN"]},
    "set_video_brightness": {Zone.Z1: ["VTN", "VTN"], "args": [VideoInt66Map]},
    "query_video_contrast": {Zone.Z1: ["?VTO", "VTO"]},
    "set_video_contrast": {Zone.Z1: ["VTO", "VTO"], "args": [VideoInt66Map]},
    "query_video_hue": {Zone.Z1: ["?VTP", "VTP"]},
    "set_video_hue": {Zone.Z1: ["VTP", "VTP"], "args": [VideoInt66Map]},
    "query_video_chroma": {Zone.Z1: ["?VTQ", "VTQ"]},
    "set_video_chroma": {Zone.Z1: ["VTQ", "VTQ"], "args": [VideoInt66Map]},
    "query_video_black_setup": {Zone.Z1: ["?VTR", "VTR"]},
    "set_video_black_setup": {Zone.Z1: ["VTR", "VTR"], "args": [CodeBoolMap]},
    "query_video_aspect": {Zone.Z1: ["?VTS", "VTS"]},
    "set_video_aspect": {Zone.Z1: ["VTS", "VTS"], "args": [VideoAspect]},
    "query_video_super_resolution": {Zone.Z1: ["?VTT", "VTT"]},
    "set_video_super_resolution": {
        Zone.Z1: ["VTT", "VTT"],
        "args": [VideoSuperResolution],
    },
    ## operation
    "operation_direct_access": {Zone.Z1: ["TAC", "TAC"]},
    "operation_tuner_digit": {Zone.Z1: ["TP", "TP"]},
    "operation_tuner_edit": {Zone.Z1: "02TN"},
    "operation_tuner_enter": {Zone.Z1: "03TN"},
    "operation_tuner_return": {Zone.Z1: "04TN"},
    "operation_tuner_mpx_noise_cut": {Zone.Z1: "05TN"},
    "operation_tuner_display": {Zone.Z1: "06TN"},
    "operation_tuner_pty_search": {Zone.Z1: "07TN"},
    "operation_ipod_play": {Zone.Z1: "00IP"},
    "operation_ipod_pause": {Zone.Z1: "01IP"},
    "operation_ipod_stop": {Zone.Z1: "02IP"},
    "operation_ipod_previous": {Zone.Z1: "03IP"},
    "operation_ipod_next": {Zone.Z1: "04IP"},
    "operation_ipod_rewind": {Zone.Z1: "05IP"},
    "operation_ipod_fastforward": {Zone.Z1: "06IP"},
    "operation_ipod_repeat": {Zone.Z1: "07IP"},
    "operation_ipod_shuffle": {Zone.Z1: "08IP"},
    "operation_ipod_display": {Zone.Z1: "09IP"},
    "operation_ipod_control": {Zone.Z1: "10IP"},
    "operation_ipod_cursor_up": {Zone.Z1: "13IP"},
    "operation_ipod_cursor_down": {Zone.Z1: "14IP"},
    "operation_ipod_cursor_left": {Zone.Z1: "16IP"},
    "operation_ipod_cursor_right": {Zone.Z1: "15IP"},
    "operation_ipod_enter": {Zone.Z1: "17IP"},
    "operation_ipod_return": {Zone.Z1: "18IP"},
    "operation_ipod_top_menu": {Zone.Z1: "19IP"},
    "operation_ipod_iphone_direct_control": {Zone.Z1: "20IP"},
    "operation_network_play": {Zone.Z1: "10NW"},
    "operation_network_pause": {Zone.Z1: "11NW"},
    "operation_network_stop": {Zone.Z1: "20NW"},
    "operation_network_fastforward": {Zone.Z1: "15NW"},
    "operation_network_rewind": {Zone.Z1: "14NW"},
    "operation_network_next": {Zone.Z1: "13NW"},
    "operation_network_previous": {Zone.Z1: "12NW"},
    "operation_network_repeat": {Zone.Z1: "34NW"},
    "operation_network_random": {Zone.Z1: "35NW"},
    "operation_adapaterport_play": {Zone.Z1: "10BT"},
    "operation_adapaterport_pause": {Zone.Z1: "11BT"},
    "operation_adapaterport_stop": {Zone.Z1: "12BT"},
    "operation_adapaterport_previous": {Zone.Z1: "13BT"},
    "operation_adapaterport_next": {Zone.Z1: "14BT"},
    "operation_adapaterport_rewind": {Zone.Z1: "15BT"},
    "operation_adapaterport_fastforward": {Zone.Z1: "16BT"},
    "operation_adapaterport_repeat": {Zone.Z1: "17BT"},
    "operation_adapaterport_random": {Zone.Z1: "18BT"},
    "operation_mhl_play": {Zone.Z1: "23MHL"},
    "operation_mhl_pause": {Zone.Z1: "25MHL"},
    "operation_mhl_stop": {Zone.Z1: "24MHL"},
    "operation_mhl_record": {Zone.Z1: "26MHL"},
    "operation_mhl_rewind": {Zone.Z1: "27MHL"},
    "operation_mhl_fastforward": {Zone.Z1: "28MHL"},
    "operation_mhl_eject": {Zone.Z1: "29MHL"},
    "operation_mhl_next": {Zone.Z1: "30MHL"},
    "operation_mhl_previous": {Zone.Z1: "31MHL"},
    "operation_amp_status_display": {Zone.Z1: "STS"},
    "operation_amp_cursor_up": {Zone.Z1: "CUP"},
    "operation_amp_cursor_down": {Zone.Z1: "CDN"},
    "operation_amp_cursor_right": {Zone.Z1: "CRI"},
    "operation_amp_cursor_left": {Zone.Z1: "CLE"},
    "operation_amp_cursor_enter": {Zone.Z1: "CEN"},
    "operation_amp_cursor_return": {Zone.Z1: "CRT"},
    "operation_amp_audio_parameter": {Zone.Z1: "ATA"},
    "operation_amp_output_parameter": {Zone.Z1: "HPA"},
    "operation_amp_video_parameter": {Zone.Z1: "VPA"},
    "operation_amp_channel_select": {Zone.Z1: "CLC"},
    "operation_amp_home_menu": {Zone.Z1: "HM"},
    "operation_amp_key_off": {Zone.Z1: "KOF"},
    ## tuner
    "query_tuner_preset": {Zone.Z1: ["?PR", "PR"]},
    "query_tuner_am_step": {Zone.Z1: ["?SUQ", "SUQ"]},
    "select_tuner_preset": {Zone.Z1: ["PR", "PR"]},
    "increase_tuner_preset": {Zone.Z1: ["TPI", "PR"]},
    "decrease_tuner_preset": {Zone.Z1: ["TPD", "PR"]},
    "query_tuner_frequency": {Zone.Z1: ["?FR", "FR"]},
    "set_tuner_band_am": {Zone.Z1: ["01TN", "FR"]},
    "set_tuner_band_fm": {Zone.Z1: ["00TN", "FR"]},
    "increase_tuner_frequency": {Zone.Z1: ["TFI", "FR"]},
    "decrease_tuner_frequency": {Zone.Z1: ["TFD", "FR"]},
    ## system
    "query_system_speaker_system": {Zone.Z1: ["?SSF", "SSF"]},
    "set_system_speaker_system": {Zone.Z1: ["?SSF", "SSF"]},
    "query_source_name": {Zone.Z1: ["?RGB", "RGB"]},
    "set_source_name": {Zone.Z1: ["1RGB", "RGB"]},
    "set_default_source_name": {Zone.Z1: ["0RGB", "RGB"]},
    ## display
    "query_display_information": {Zone.Z1: ["?FL", "FL"]},
}
