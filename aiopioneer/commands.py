"""Pioneer AVR commands."""

from .const import Zones

PIONEER_COMMANDS = {
    "system_query_mac_addr": {Zones.Z1: ["?SVB", "SVB"]},
    "system_query_software_version": {Zones.Z1: ["?SSI", "SSI"]},
    "system_query_model": {Zones.Z1: ["?RGD", "RGD"]},
    "turn_on": {
        Zones.Z1: ["PO", "PWR"],
        Zones.Z2: ["APO", "APR"],
        Zones.Z3: ["BPO", "BPR"],
        Zones.HDZ: ["ZEO", "ZEP"],
    },
    "turn_off": {
        Zones.Z1: ["PF", "PWR"],
        Zones.Z2: ["APF", "APR"],
        Zones.Z3: ["BPF", "BPR"],
        Zones.HDZ: ["ZEF", "ZEP"],
    },
    "select_source": {
        Zones.Z1: ["FN", "FN"],
        Zones.Z2: ["ZS", "Z2F"],
        Zones.Z3: ["ZT", "Z3F"],
        Zones.HDZ: ["ZEA", "ZEA"],
    },
    "volume_up": {
        Zones.Z1: ["VU", "VOL"],
        Zones.Z2: ["ZU", "ZV"],
        Zones.Z3: ["YU", "YV"],
        Zones.HDZ: ["HZU", "XV"],
    },
    "volume_down": {
        Zones.Z1: ["VD", "VOL"],
        Zones.Z2: ["ZD", "ZV"],
        Zones.Z3: ["YD", "YV"],
        Zones.HDZ: ["HZD", "XV"],
    },
    "set_volume_level": {
        Zones.Z1: ["VL", "VOL"],
        Zones.Z2: ["ZV", "ZV"],
        Zones.Z3: ["YV", "YV"],
        Zones.HDZ: ["HZV", "XV"],
    },
    "mute_on": {
        Zones.Z1: ["MO", "MUT"],
        Zones.Z2: ["Z2MO", "Z2MUT"],
        Zones.Z3: ["Z3MO", "Z3MUT"],
        Zones.HDZ: ["HZMO", "HZMUT"],
    },
    "mute_off": {
        Zones.Z1: ["MF", "MUT"],
        Zones.Z2: ["Z2MF", "Z2MUT"],
        Zones.Z3: ["Z3MF", "Z3MUT"],
        Zones.HDZ: ["HZMF", "HZMUT"],
    },
    "query_power": {
        Zones.Z1: ["?P", "PWR"],
        Zones.Z2: ["?AP", "APR"],
        Zones.Z3: ["?BP", "BPR"],
        Zones.HDZ: ["?ZEP", "ZEP"],
    },
    "query_volume": {
        Zones.Z1: ["?V", "VOL"],
        Zones.Z2: ["?ZV", "ZV"],
        Zones.Z3: ["?YV", "YV"],
        Zones.HDZ: ["?HZV", "XV"],
    },
    "query_mute": {
        Zones.Z1: ["?M", "MUT"],
        Zones.Z2: ["?Z2M", "Z2MUT"],
        Zones.Z3: ["?Z3M", "Z3MUT"],
        Zones.HDZ: ["?HZM", "HZMUT"],
    },
    "query_source_id": {
        Zones.Z1: ["?F", "FN"],
        Zones.Z2: ["?ZS", "Z2F"],
        Zones.Z3: ["?ZT", "Z3F"],
        Zones.HDZ: ["?ZEA", "ZEA"],
    },
    "query_listening_mode": {Zones.Z1: ["?S", "SR"]},
    "set_listening_mode": {Zones.Z1: ["SR", "SR"]},
    "query_tone_status": {Zones.Z1: ["?TO", "TO"], Zones.Z2: ["?ZGA", "ZGA"]},
    "query_tone_bass": {Zones.Z1: ["?BA", "BA"], Zones.Z2: ["?ZGB", "ZGB"]},
    "query_tone_treble": {Zones.Z1: ["?TR", "TR"], Zones.Z2: ["?ZGC", "ZGC"]},
    "set_tone_mode": {
        Zones.Z1: ["TO", "TO"],
        Zones.Z2: ["ZGA", "ZGA"],
    },
    "set_tone_bass": {
        Zones.Z1: ["BA", "BA"],
        Zones.Z2: ["ZGB", "ZGB"],
    },
    "set_tone_treble": {
        Zones.Z1: ["TR", "TR"],
        Zones.Z2: ["ZGC", "ZGC"],
    },
    "query_amp_speaker_status": {Zones.Z1: ["?SPK", "SPK"]},
    "set_amp_speaker_status": {Zones.Z1: ["SPK", "SPK"]},
    "query_amp_hdmi_out_status": {Zones.Z1: ["?HO", "HO"]},
    "set_amp_hdmi_out_status": {Zones.Z1: ["HO", "HO"]},
    "query_amp_hdmi_audio_status": {Zones.Z1: ["?HA", "HA"]},
    "set_amp_hdmi_audio_status": {Zones.Z1: ["HA", "HA"]},
    "query_amp_pqls_status": {Zones.Z1: ["?PQ", "PQ"]},
    "set_amp_pqls_status": {Zones.Z1: ["PQ", "PQ"]},
    "set_amp_dimmer": {Zones.Z1: ["SAA", "SAA"]},  ## no query command
    "query_amp_sleep_remain_time": {Zones.Z1: ["?SAB", "SAB"]},
    "set_amp_sleep_remain_time": {Zones.Z1: ["SAB", "SAB"]},
    "query_amp_panel_lock": {Zones.Z1: ["?PKL", "PKL"]},
    "query_amp_remote_lock": {Zones.Z1: ["?RML", "RML"]},
    "set_amp_panel_lock": {Zones.Z1: ["PKL", "PKL"]},
    "set_amp_remote_lock": {Zones.Z1: ["RML", "RML"]},
    "query_tuner_preset": {Zones.Z1: ["?PR", "PR"]},
    "query_tuner_am_step": {Zones.Z1: ["?SUQ", "SUQ"]},
    "select_tuner_preset": {Zones.Z1: ["PR", "PR"]},
    "increase_tuner_preset": {Zones.Z1: ["TPI", "PR"]},
    "decrease_tuner_preset": {Zones.Z1: ["TPD", "PR"]},
    "query_tuner_frequency": {Zones.Z1: ["?FR", "FR"]},
    "set_tuner_band_am": {Zones.Z1: ["01TN", "FR"]},
    "set_tuner_band_fm": {Zones.Z1: ["00TN", "FR"]},
    "increase_tuner_frequency": {Zones.Z1: ["TFI", "FR"]},
    "decrease_tuner_frequency": {Zones.Z1: ["TFD", "FR"]},
    "query_video_resolution": {Zones.Z1: ["?VTC", "VTC"]},
    "set_video_resolution": {Zones.Z1: ["VTC", "VTC"]},
    "query_video_converter": {Zones.Z1: ["?VTB", "VTB"]},
    "set_video_converter": {Zones.Z1: ["VTB", "VTB"]},
    "query_video_pure_cinema": {Zones.Z1: ["?VTD", "VTD"]},
    "set_video_pure_cinema": {Zones.Z1: ["VTD", "VTD"]},
    "query_video_prog_motion": {Zones.Z1: ["?VTE", "VTE"]},
    "set_video_prog_motion": {Zones.Z1: ["VTE", "VTE"]},
    "query_video_stream_smoother": {Zones.Z1: ["?VTF", "VTF"]},
    "set_video_stream_smoother": {Zones.Z1: ["VTF", "VTF"]},
    "query_video_advanced_video_adjust": {Zones.Z1: ["?VTG", "VTG"]},
    "set_video_advanced_video_adjust": {Zones.Z1: ["VTG", "VTG"]},
    "query_video_ynr": {Zones.Z1: ["?VTH", "VTH"]},
    "set_video_ynr": {Zones.Z1: ["VTH", "VTH"]},
    "query_video_cnr": {Zones.Z1: ["?VTI", "VTI"]},
    "set_video_cnr": {Zones.Z1: ["VTI", "VTI"]},
    "query_video_bnr": {Zones.Z1: ["?VTJ", "VTJ"]},
    "set_video_bnr": {Zones.Z1: ["VTJ", "VTJ"]},
    "query_video_mnr": {Zones.Z1: ["?VTK", "VTK"]},
    "set_video_mnr": {Zones.Z1: ["VTK", "VTK"]},
    "query_video_detail": {Zones.Z1: ["?VTL", "VTL"]},
    "set_video_detail": {Zones.Z1: ["VTL", "VTL"]},
    "query_video_sharpness": {Zones.Z1: ["?VTM", "VTM"]},
    "set_video_sharpness": {Zones.Z1: ["VTM", "VTM"]},
    "query_video_brightness": {Zones.Z1: ["?VTN", "VTN"]},
    "set_video_brightness": {Zones.Z1: ["VTN", "VTN"]},
    "query_video_contrast": {Zones.Z1: ["?VTO", "VTO"]},
    "set_video_contrast": {Zones.Z1: ["VTO", "VTO"]},
    "query_video_hue": {Zones.Z1: ["?VTP", "VTP"]},
    "set_video_hue": {Zones.Z1: ["VTP", "VTP"]},
    "query_video_chroma": {Zones.Z1: ["?VTQ", "VTQ"]},
    "set_video_chroma": {Zones.Z1: ["VTQ", "VTQ"]},
    "query_video_black_setup": {Zones.Z1: ["?VTR", "VTR"]},
    "set_video_black_setup": {Zones.Z1: ["VTR", "VTR"]},
    "query_video_aspect": {Zones.Z1: ["?VTS", "VTS"]},
    "set_video_aspect": {Zones.Z1: ["VTS", "VTS"]},
    "set_channel_levels": {
        Zones.Z1: ["CLV", "CLV"],
        Zones.Z2: ["ZGE", "ZGE"],
        Zones.Z3: ["ZHE", "ZHE"],
    },
    "set_dsp_mcacc_memory_set": {Zones.Z1: ["MC", "MC"]},
    "set_dsp_phase_control": {Zones.Z1: ["IS", "IS"]},
    "set_dsp_virtual_sb": {Zones.Z1: ["VSB", "VSB"]},
    "set_dsp_virtual_height": {Zones.Z1: ["VHT", "VHT"]},
    "set_dsp_sound_retriever": {Zones.Z1: ["ATA", "ATA"]},
    "set_dsp_signal_select": {Zones.Z1: ["SDA", "SDA"]},
    "set_dsp_analog_input_att": {Zones.Z1: ["SDB", "SDB"]},
    "set_dsp_eq": {Zones.Z1: ["ATC", "ATC"]},
    "set_dsp_standing_wave": {Zones.Z1: ["ATD", "ATD"]},
    "set_dsp_phase_control_plus": {Zones.Z1: ["ATE", "ATE"]},
    "set_dsp_sound_delay": {Zones.Z1: ["ATF", "ATF"]},
    "set_dsp_digital_noise_reduction": {Zones.Z1: ["ATG", "ATG"]},
    "set_dsp_digital_dialog_enhancement": {Zones.Z1: ["ATH", "ATH"]},
    "set_dsp_hi_bit": {Zones.Z1: ["ATI", "ATI"]},
    "set_dsp_dual_mono": {Zones.Z1: ["ATJ", "ATJ"]},
    "set_dsp_fixed_pcm": {Zones.Z1: ["ATK", "ATK"]},
    "set_dsp_drc": {Zones.Z1: ["ATL", "ATL"]},
    "set_dsp_lfe_att": {Zones.Z1: ["ATM", "ATM"]},
    "set_dsp_sacd_gain": {Zones.Z1: ["ATN", "ATN"]},
    "set_dsp_auto_delay": {Zones.Z1: ["ATO", "ATO"]},
    "set_dsp_center_width": {Zones.Z1: ["ATP", "ATP"]},
    "set_dsp_panorama": {Zones.Z1: ["ATQ", "ATQ"]},
    "set_dsp_dimension": {Zones.Z1: ["ATR", "ATR"]},
    "set_dsp_center_image": {Zones.Z1: ["ATS", "ATS"]},
    "set_dsp_effect": {Zones.Z1: ["ATT", "ATT"]},
    "set_dsp_height_gain": {Zones.Z1: ["ATU", "ATU"]},
    "set_dsp_virtual_depth": {Zones.Z1: ["VDP", "VDP"]},
    "set_dsp_digital_filter": {Zones.Z1: ["ATV", "ATV"]},
    "set_dsp_loudness_management": {Zones.Z1: ["ATW", "ATW"]},
    "set_dsp_virtual_wide": {Zones.Z1: ["VWD", "VWD"]},
    "query_dsp_mcacc_memory_query": {Zones.Z1: ["?MC", "MC"]},
    "query_dsp_phase_control": {Zones.Z1: ["?IS", "IS"]},
    "query_dsp_virtual_sb": {Zones.Z1: ["?VSB", "VSB"]},
    "query_dsp_virtual_height": {Zones.Z1: ["?VHT", "VHT"]},
    "query_dsp_sound_retriever": {Zones.Z1: ["?ATA", "ATA"]},
    "query_dsp_signal_select": {Zones.Z1: ["?SDA", "SDA"]},
    "query_dsp_analog_input_att": {Zones.Z1: ["?SDB", "SDB"]},
    "query_dsp_eq": {Zones.Z1: ["?ATC", "ATC"]},
    "query_dsp_standing_wave": {Zones.Z1: ["?ATD", "ATD"]},
    "query_dsp_phase_control_plus": {Zones.Z1: ["?ATE", "ATE"]},
    "query_dsp_sound_delay": {Zones.Z1: ["?ATF", "ATF"]},
    "query_dsp_digital_noise_reduction": {Zones.Z1: ["?ATG", "ATG"]},
    "query_dsp_digital_dialog_enhancement": {Zones.Z1: ["?ATH", "ATH"]},
    "query_dsp_hi_bit": {Zones.Z1: ["?ATI", "ATI"]},
    "query_dsp_dual_mono": {Zones.Z1: ["?ATJ", "ATJ"]},
    "query_dsp_fixed_pcm": {Zones.Z1: ["?ATK", "ATK"]},
    "query_dsp_drc": {Zones.Z1: ["?ATL", "ATL"]},
    "query_dsp_lfe_att": {Zones.Z1: ["?ATM", "ATM"]},
    "query_dsp_sacd_gain": {Zones.Z1: ["?ATN", "ATN"]},
    "query_dsp_auto_delay": {Zones.Z1: ["?ATO", "ATO"]},
    "query_dsp_center_width": {Zones.Z1: ["?ATP", "ATP"]},
    "query_dsp_panorama": {Zones.Z1: ["?ATQ", "ATQ"]},
    "query_dsp_dimension": {Zones.Z1: ["?ATR", "ATR"]},
    "query_dsp_center_image": {Zones.Z1: ["?ATS", "ATS"]},
    "query_dsp_effect": {Zones.Z1: ["?ATT", "ATT"]},
    "query_dsp_height_gain": {Zones.Z1: ["?ATU", "ATU"]},
    "query_dsp_virtual_depth": {Zones.Z1: ["?VDP", "VDP"]},
    "query_dsp_digital_filter": {Zones.Z1: ["?ATV", "ATV"]},
    "query_dsp_loudness_management": {Zones.Z1: ["?ATW", "ATW"]},
    "query_dsp_virtual_wide": {Zones.Z1: ["?VWD", "VWD"]},
    "query_system_speaker_system": {Zones.Z1: ["?SSF", "SSF"]},
    "set_system_speaker_system": {Zones.Z1: ["?SSF", "SSF"]},
    "query_display_information": {Zones.Z1: ["?FL", "FL"]},
    "query_audio_information": {Zones.Z1: ["?AST", "AST"]},
    "query_video_information": {Zones.Z1: ["?VST", "VST"]},
    "operation_direct_access": {Zones.Z1: ["TAC", "TAC"]},
    "operation_tuner_digit": {Zones.Z1: ["TP", "TP"]},
    "operation_tuner_edit": {Zones.Z1: "02TN"},
    "operation_tuner_enter": {Zones.Z1: "03TN"},
    "operation_tuner_return": {Zones.Z1: "04TN"},
    "operation_tuner_mpx_noise_cut": {Zones.Z1: "05TN"},
    "operation_tuner_display": {Zones.Z1: "06TN"},
    "operation_tuner_pty_search": {Zones.Z1: "07TN"},
    "operation_ipod_play": {Zones.Z1: "00IP"},
    "operation_ipod_pause": {Zones.Z1: "01IP"},
    "operation_ipod_stop": {Zones.Z1: "02IP"},
    "operation_ipod_previous": {Zones.Z1: "03IP"},
    "operation_ipod_next": {Zones.Z1: "04IP"},
    "operation_ipod_rewind": {Zones.Z1: "05IP"},
    "operation_ipod_fastforward": {Zones.Z1: "06IP"},
    "operation_ipod_repeat": {Zones.Z1: "07IP"},
    "operation_ipod_shuffle": {Zones.Z1: "08IP"},
    "operation_ipod_display": {Zones.Z1: "09IP"},
    "operation_ipod_control": {Zones.Z1: "10IP"},
    "operation_ipod_cursor_up": {Zones.Z1: "13IP"},
    "operation_ipod_cursor_down": {Zones.Z1: "14IP"},
    "operation_ipod_cursor_left": {Zones.Z1: "16IP"},
    "operation_ipod_cursor_right": {Zones.Z1: "15IP"},
    "operation_ipod_enter": {Zones.Z1: "17IP"},
    "operation_ipod_return": {Zones.Z1: "18IP"},
    "operation_ipod_top_menu": {Zones.Z1: "19IP"},
    "operation_ipod_iphone_direct_control": {Zones.Z1: "20IP"},
    "operation_network_play": {Zones.Z1: "10NW"},
    "operation_network_pause": {Zones.Z1: "11NW"},
    "operation_network_stop": {Zones.Z1: "20NW"},
    "operation_network_fastforward": {Zones.Z1: "15NW"},
    "operation_network_rewind": {Zones.Z1: "14NW"},
    "operation_network_next": {Zones.Z1: "13NW"},
    "operation_network_previous": {Zones.Z1: "12NW"},
    "operation_network_repeat": {Zones.Z1: "34NW"},
    "operation_network_random": {Zones.Z1: "35NW"},
    "operation_adapaterport_play": {Zones.Z1: "10BT"},
    "operation_adapaterport_pause": {Zones.Z1: "11BT"},
    "operation_adapaterport_stop": {Zones.Z1: "12BT"},
    "operation_adapaterport_previous": {Zones.Z1: "13BT"},
    "operation_adapaterport_next": {Zones.Z1: "14BT"},
    "operation_adapaterport_rewind": {Zones.Z1: "15BT"},
    "operation_adapaterport_fastforward": {Zones.Z1: "16BT"},
    "operation_adapaterport_repeat": {Zones.Z1: "17BT"},
    "operation_adapaterport_random": {Zones.Z1: "18BT"},
    "operation_mhl_play": {Zones.Z1: "23MHL"},
    "operation_mhl_pause": {Zones.Z1: "25MHL"},
    "operation_mhl_stop": {Zones.Z1: "24MHL"},
    "operation_mhl_record": {Zones.Z1: "26MHL"},
    "operation_mhl_rewind": {Zones.Z1: "27MHL"},
    "operation_mhl_fastforward": {Zones.Z1: "28MHL"},
    "operation_mhl_eject": {Zones.Z1: "29MHL"},
    "operation_mhl_next": {Zones.Z1: "30MHL"},
    "operation_mhl_previous": {Zones.Z1: "31MHL"},
    "operation_amp_status_display": {Zones.Z1: "STS"},
    "operation_amp_cursor_up": {Zones.Z1: "CUP"},
    "operation_amp_cursor_down": {Zones.Z1: "CDN"},
    "operation_amp_cursor_right": {Zones.Z1: "CRI"},
    "operation_amp_cursor_left": {Zones.Z1: "CLE"},
    "operation_amp_cursor_enter": {Zones.Z1: "CEN"},
    "operation_amp_cursor_return": {Zones.Z1: "CRT"},
    "operation_amp_audio_parameter": {Zones.Z1: "ATA"},
    "operation_amp_output_parameter": {Zones.Z1: "HPA"},
    "operation_amp_video_parameter": {Zones.Z1: "VPA"},
    "operation_amp_channel_select": {Zones.Z1: "CLC"},
    "operation_amp_home_menu": {Zones.Z1: "HM"},
    "operation_amp_key_off": {Zones.Z1: "KOF"},
    "query_source_name": {Zones.Z1: ["?RGB", "RGB"]},
    "set_source_name": {Zones.Z1: ["1RGB", "RGB"]},
    "set_default_source_name": {Zones.Z1: ["0RGB", "RGB"]},
}
