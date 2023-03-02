"""Pioneer AVR commands."""

PIONEER_COMMANDS = {
    "system_query_mac_addr": {"1": ["?SVB", "SVB"]},
    "system_query_software_version": {"1": ["?SSI", "SSI"]},
    "system_query_model": {"1": ["?RGD", "RGD"]},
    "turn_on": {
        "1": ["PO", "PWR"],
        "2": ["APO", "APR"],
        "3": ["BPO", "BPR"],
        "Z": ["ZEO", "ZEP"],
    },
    "turn_off": {
        "1": ["PF", "PWR"],
        "2": ["APF", "APR"],
        "3": ["BPF", "BPR"],
        "Z": ["ZEF", "ZEP"],
    },
    "select_source": {
        "1": ["FN", "FN"],
        "2": ["ZS", "Z2F"],
        "3": ["ZT", "Z3F"],
        "Z": ["ZEA", "ZEA"],
    },
    "volume_up": {
        "1": ["VU", "VOL"],
        "2": ["ZU", "ZV"],
        "3": ["YU", "YV"],
        "Z": ["HZU", "XV"],
    },
    "volume_down": {
        "1": ["VD", "VOL"],
        "2": ["ZD", "ZV"],
        "3": ["YD", "YV"],
        "Z": ["HZD", "XV"],
    },
    "set_volume_level": {
        "1": ["VL", "VOL"],
        "2": ["ZV", "ZV"],
        "3": ["YV", "YV"],
        "Z": ["HZV", "XV"],
    },
    "mute_on": {
        "1": ["MO", "MUT"],
        "2": ["Z2MO", "Z2MUT"],
        "3": ["Z3MO", "Z3MUT"],
        "Z": ["HZMO", "HZMUT"],
    },
    "mute_off": {
        "1": ["MF", "MUT"],
        "2": ["Z2MF", "Z2MUT"],
        "3": ["Z3MF", "Z3MUT"],
        "Z": ["HZMF", "HZMUT"],
    },
    "query_power": {
        "1": ["?P", "PWR"],
        "2": ["?AP", "APR"],
        "3": ["?BP", "BPR"],
        "Z": ["?ZEP", "ZEP"],
    },
    "query_volume": {
        "1": ["?V", "VOL"],
        "2": ["?ZV", "ZV"],
        "3": ["?YV", "YV"],
        "Z": ["?HZV", "XV"],
    },
    "query_mute": {
        "1": ["?M", "MUT"],
        "2": ["?Z2M", "Z2MUT"],
        "3": ["?Z3M", "Z3MUT"],
        "Z": ["?HZM", "HZMUT"],
    },
    "query_source_id": {
        "1": ["?F", "FN"],
        "2": ["?ZS", "Z2F"],
        "3": ["?ZT", "Z3F"],
        "Z": ["?ZEA", "ZEA"],
    },
    "query_listening_mode": {
        "1": ["?S", "SR"]
    },
    "set_listening_mode": {
        "1": ["SR", "SR"]
    },
    "query_tone_status": {
        "1": ["?TO", "TO"],
        "2": ["?ZGA", "ZGA"]
    },
    "query_tone_bass": {
        "1": ["?BA", "BA"],
        "2": ["?ZGB", "ZGB"]
    },
    "query_tone_treble": {
        "1": ["?TR", "TR"],
        "2": ["?ZGC", "ZGC"]
    },
    "set_tone_mode": {
        "1": ["TO", "TO"],
        "2": ["ZGA", "ZGA"],
    },
    "set_tone_bass": {
        "1": ["BA", "BA"],
        "2": ["ZGB", "ZGB"],
    },
    "set_tone_treble": {
        "1": ["TR", "TR"],
        "2": ["ZGC", "ZGC"],
    },
    "query_amp_speaker_status": {
        "1": ["?SPK", "SPK"]
    },
    "set_amp_speaker_status": {
        "1": ["SPK", "SPK"]
    },
    "query_amp_hdmi_out_status": {
        "1": ["?HO", "HO"]
    },
    "set_amp_hdmi_out_status": {
        "1": ["HO", "HO"]
    },
    "query_amp_hdmi_audio_status": {
        "1": ["?HA", "HA"]
    },
    "set_amp_hdmi_audio_status": {
        "1": ["HA", "HA"]
    },
    "query_amp_pqls_status": {
        "1": ["?PQ", "PQ"]
    },
    "set_amp_pqls_status": {
        "1": ["PQ", "PQ"]
    },
    "set_amp_dimmer": {
        "1": ["SAA", "SAA"]
    },
    "query_amp_sleep_remain_time": {
        "1": ["?SAB", "SAB"]
    },
    "set_amp_sleep_remain_time": {
        "1": ["SAB", "SAB"]
    },
    "query_tuner_frequency": {
        "1": ["?FR", "FR"]
    },
    "set_tuner_band_am": {
        "1": ["01TN", "FR"]
    },
    "set_tuner_band_fm": {
        "1": ["00TN", "FR"]
    },
    "increase_tuner_frequency": {
        "1": ["TFI", "FR"]
    },
    "decrease_tuner_frequency": {
        "1": ["TFD", "FR"]
    },
    "query_amp_panel_lock": {
        "1": ["?PKL", "PKL"]
    },
    "query_amp_remote_lock": {
        "1": ["?RML", "RML"]
    },
    "set_amp_panel_lock": {
        "1": ["PKL", "PKL"]
    },
    "set_amp_remote_lock": {
        "1": ["RML", "RML"]
    },
    "query_tuner_preset": {
        "1": ["?PR", "PR"]
    },
    "set_tuner_preset": {
        "1": ["PR", "PR"]
    },
    "increase_tuner_preset": {
        "1": ["TPI", "PR"]
    },
    "decrease_tuner_preset": {
        "1": ["TPD", "PR"]
    },
    "query_video_resolution": {
        "1": ["?VTC", "VTC"]
    },
    "set_video_resolution": {
        "1": ["VTC", "VTC"]
    },
    "query_video_converter": {
        "1": ["?VTB", "VTB"]
    },
    "set_video_converter": {
        "1": ["VTB", "VTB"]
    },
    "query_video_pure_cinema_status": {
        "1": ["?VTD", "VTD"]
    },
    "set_video_pure_cinema_status": {
        "1": ["VTD", "VTD"]
    },
    "query_video_prog_motion_status": {
        "1": ["?VTE", "VTE"]
    },
    "set_video_prog_motion_status": {
        "1": ["VTE", "VTE"]
    },
    "query_video_stream_smoother": {
        "1": ["?VTF", "VTF"]
    },
    "set_video_stream_smoother": {
        "1": ["VTF", "VTF"]
    },
    "query_video_advanced_video_adjust": {
        "1": ["?VTG", "VTG"]
    },
    "set_video_advanced_video_adjust": {
        "1": ["VTG", "VTG"]
    },
    "query_video_ynr": {
        "1": ["?VTH", "VTH"]
    },
    "set_video_ynr": {
        "1": ["VTH", "VTH"]
    },
    "query_video_cnr": {
        "1": ["?VTI", "VTI"]
    },
    "set_video_cnr": {
        "1": ["VTI", "VTI"]
    },
    "query_video_bnr": {
        "1": ["?VTJ", "VTJ"]
    },
    "set_video_bnr": {
        "1": ["VTJ", "VTJ"]
    },
    "query_video_mnr": {
        "1": ["?VTK", "VTK"]
    },
    "set_video_mnr": {
        "1": ["VTK", "VTK"]
    },
    "query_video_detail": {
        "1": ["?VTL", "VTL"]
    },
    "set_video_detail": {
        "1": ["VTL", "VTL"]
    },
    "query_video_sharpness": {
        "1": ["?VTM", "VTM"]
    },
    "set_video_sharpness": {
        "1": ["VTM", "VTM"]
    },
    "query_video_brightness": {
        "1": ["?VTN", "VTN"]
    },
    "set_video_brightness": {
        "1": ["VTN", "VTN"]
    },
    "query_video_contrast": {
        "1": ["?VTO", "VTO"]
    },
    "set_video_contrast": {
        "1": ["VTO", "VTO"]
    },
    "query_video_hue": {
        "1": ["?VTP", "VTP"]
    },
    "set_video_hue": {
        "1": ["VTP", "VTP"]
    },
    "query_video_chroma": {
        "1": ["?VTQ", "VTQ"]
    },
    "set_video_chroma": {
        "1": ["VTQ", "VTQ"]
    },
    "query_video_black_setup": {
        "1": ["?VTR", "VTR"]
    },
    "set_video_black_setup": {
        "1": ["VTR", "VTR"]
    },
    "query_video_aspect": {
        "1": ["?VTS", "VTS"]
    },
    "set_video_aspect": {
        "1": ["VTS", "VTS"]
    },
    "set_channel_levels": {
        "1": ["CLV", "CLV"],
        "2": ["ZGE", "ZGE"],
        "3": ["ZHE", "ZHE"]
    },
    "set_dsp_mcacc_memory_set": {
        "1": ["MC", "MC"]
    },
    "set_dsp_phase_control": {
        "1": ["IS", "IS"]
    },
    "set_dsp_virtual_sb": {
        "1": ["VSB", "VSB"]
    },
    "set_dsp_virtual_height": {
        "1": ["VHT", "VHT"]
    },
    "set_dsp_sound_retriever": {
        "1": ["ATA", "ATA"]
    },
    "set_dsp_signal_select": {
        "1": ["SDA", "SDA"]
    },
    "set_dsp_analog_input_att": {
        "1": ["SDB", "SDB"]
    },
    "set_dsp_eq": {
        "1": ["ATC", "ATC"]
    },
    "set_dsp_standing_wave": {
        "1": ["ATD", "ATD"]
    },
    "set_dsp_phase_control_plus": {
        "1": ["ATE", "ATE"]
    },
    "set_dsp_sound_delay": {
        "1": ["ATF", "ATF"]
    },
    "set_dsp_digital_noise_reduction": {
        "1": ["ATG", "ATG"]
    },
    "set_dsp_digital_dialog_enhancement": {
        "1": ["ATH", "ATH"]
    },
    "set_dsp_hi_bit": {
        "1": ["ATI", "ATI"]
    },
    "set_dsp_dual_mono": {
        "1": ["ATJ", "ATJ"]
    },
    "set_dsp_fixed_pcm": {
        "1": ["ATK", "ATK"]
    },
    "set_dsp_drc": {
        "1": ["ATL", "ATL"]
    },
    "set_dsp_lfe_att": {
        "1": ["ATM", "ATM"]
    },
    "set_dsp_sacd_gain": {
        "1": ["ATN", "ATN"]
    },
    "set_dsp_auto_delay": {
        "1": ["ATO", "ATO"]
    },
    "set_dsp_center_width": {
        "1": ["ATP", "ATP"]
    },
    "set_dsp_panorama": {
        "1": ["ATQ", "ATQ"]
    },
    "set_dsp_dimension": {
        "1": ["ATR", "ATR"]
    },
    "set_dsp_center_image": {
        "1": ["ATS", "ATS"]
    },
    "set_dsp_effect": {
        "1": ["ATT", "ATT"]
    },
    "set_dsp_height_gain": {
        "1": ["ATU", "ATU"]
    },
    "set_dsp_virtual_depth": {
        "1": ["VDP", "VDP"]
    },
    "set_dsp_digital_filter": {
        "1": ["ATV", "ATV"]
    },
    "set_dsp_loudness_management": {
        "1": ["ATW", "ATW"]
    },
    "set_dsp_virtual_wide": {
        "1": ["VWD", "VWD"]
    },
    "query_dsp_mcacc_memory_query": {
        "1": ["?MC", "MC"]
    },
    "query_dsp_phase_control": {
        "1": ["?IS", "IS"]
    },
    "query_dsp_virtual_sb": {
        "1": ["?VSB", "VSB"]
    },
    "query_dsp_virtual_height": {
        "1": ["?VHT", "VHT"]
    },
    "query_dsp_sound_retriever": {
        "1": ["?ATA", "ATA"]
    },
    "query_dsp_signal_select": {
        "1": ["?SDA", "SDA"]
    },
    "query_dsp_analog_input_att": {
        "1": ["?SDB", "SDB"]
    },
    "query_dsp_eq": {
        "1": ["?ATC", "ATC"]
    },
    "query_dsp_standing_wave": {
        "1": ["?ATD", "ATD"]
    },
    "query_dsp_phase_control_plus": {
        "1": ["?ATE", "ATE"]
    },
    "query_dsp_sound_delay": {
        "1": ["?ATF", "ATF"]
    },
    "query_dsp_digital_noise_reduction": {
        "1": ["?ATG", "ATG"]
    },
    "query_dsp_digital_dialog_enhancement": {
        "1": ["?ATH", "ATH"]
    },
    "query_dsp_hi_bit": {
        "1": ["?ATI", "ATI"]
    },
    "query_dsp_dual_mono": {
        "1": ["?ATJ", "ATJ"]
    },
    "query_dsp_fixed_pcm": {
        "1": ["?ATK", "ATK"]
    },
    "query_dsp_drc": {
        "1": ["?ATL", "ATL"]
    },
    "query_dsp_lfe_att": {
        "1": ["?ATM", "ATM"]
    },
    "query_dsp_sacd_gain": {
        "1": ["?ATN", "ATN"]
    },
    "query_dsp_auto_delay": {
        "1": ["?ATO", "ATO"]
    },
    "query_dsp_center_width": {
        "1": ["?ATP", "ATP"]
    },
    "query_dsp_panorama": {
        "1": ["?ATQ", "ATQ"]
    },
    "query_dsp_dimension": {
        "1": ["?ATR", "ATR"]
    },
    "query_dsp_center_image": {
        "1": ["?ATS", "ATS"]
    },
    "query_dsp_effect": {
        "1": ["?ATT", "ATT"]
    },
    "query_dsp_height_gain": {
        "1": ["?ATU", "ATU"]
    },
    "query_dsp_virtual_depth": {
        "1": ["?VDP", "VDP"]
    },
    "query_dsp_digital_filter": {
        "1": ["?ATV", "ATV"]
    },
    "query_dsp_loudness_management": {
        "1": ["?ATW", "ATW"]
    },
    "query_dsp_virtual_wide": {
        "1": ["?VWD", "VWD"]
    },
    "query_system_speaker_system": {
        "1": ["?SSF", "SSF"]
    },
    "set_system_speaker_system": {
        "1": ["?SSF", "SSF"]
    },
    "query_audio_information": {
        "1": ["?AST", "AST"]
    },
    "query_video_information": {
        "1": ["?VST", "VST"]
    },
    "operation_tuner_edit": {
        "1": "02TN"
    },
    "operation_tuner_enter": {
        "1": "03TN"
    },
    "operation_tuner_return": {
        "1": "04TN"
    },
    "operation_tuner_mpx_noise_cut": {
        "1": "05TN"
    },
    "operation_tuner_display": {
        "1": "06TN"
    },
    "operation_tuner_pty_search": {
        "1": "07TN"
    },
    "operation_ipod_play": {
        "1": "00IP"
    },
    "operation_ipod_pause": {
        "1": "01IP"
    },
    "operation_ipod_stop": {
        "1": "02IP"
    },
    "operation_ipod_previous": {
        "1": "03IP"
    },
    "operation_ipod_next": {
        "1": "04IP"
    },
    "operation_ipod_rewind": {
        "1": "05IP"
    },
    "operation_ipod_fastforward": {
        "1": "06IP"
    },
    "operation_ipod_repeat": {
        "1": "07IP"
    },
    "operation_ipod_shuffle": {
        "1": "08IP"
    },
    "operation_ipod_display": {
        "1": "09IP"
    },
    "operation_ipod_control": {
        "1": "10IP"
    },
    "operation_ipod_cursor_up": {
        "1": "13IP"
    },
    "operation_ipod_cursor_down": {
        "1": "14IP"
    },
    "operation_ipod_cursor_left": {
        "1": "16IP"
    },
    "operation_ipod_cursor_right": {
        "1": "15IP"
    },
    "operation_ipod_enter": {
        "1": "17IP"
    },
    "operation_ipod_return": {
        "1": "18IP"
    },
    "operation_ipod_top_menu": {
        "1": "19IP"
    },
    "operation_ipod_iphone_direct_control": {
        "1": "20IP"
    },
    "operation_network_play": {
        "1": "10NW"
    },
    "operation_network_pause": {
        "1": "11NW"
    },
    "operation_network_stop": {
        "1": "20NW"
    },
    "operation_network_fastforward": {
        "1": "15NW"
    },
    "operation_network_rewind": {
        "1": "14NW"
    },
    "operation_network_next": {
        "1": "13NW"
    },
    "operation_network_previous": {
        "1": "12NW"
    },
    "operation_network_repeat": {
        "1": "34NW"
    },
    "operation_network_random": {
        "1": "35NW"
    },
    "operation_adapaterport_play": {
        "1": "10BT"
    },
    "operation_adapaterport_pause": {
        "1": "11BT"
    },
    "operation_adapaterport_stop": {
        "1": "12BT"
    },
    "operation_adapaterport_previous": {
        "1": "13BT"
    },
    "operation_adapaterport_next": {
        "1": "14BT"
    },
    "operation_adapaterport_rewind": {
        "1": "15BT"
    },
    "operation_adapaterport_fastforward": {
        "1": "16BT"
    },
    "operation_adapaterport_repeat": {
        "1": "17BT"
    },
    "operation_adapaterport_random": {
        "1": "18BT"
    },
    "operation_mhl_play": {
        "1": "23MHL"
    },
    "operation_mhl_pause": {
        "1": "25MHL"
    },
    "operation_mhl_stop": {
        "1": "24MHL"
    },
    "operation_mhl_record": {
        "1": "26MHL"
    },
    "operation_mhl_rewind": {
        "1": "27MHL"
    },
    "operation_mhl_fastforward": {
        "1": "28MHL"
    },
    "operation_mhl_eject": {
        "1": "29MHL"
    },
    "operation_mhl_next": {
        "1": "30MHL"
    },
    "operation_mhl_previous": {
        "1": "31MHL"
    },
    "operation_amp_status_display": {
        "1": "STS"
    },
    "operation_amp_cursor_up": {
        "1": "CUP"
    },
    "operation_amp_cursor_down": {
        "1": "CDN"
    },
    "operation_amp_cursor_right": {
        "1": "CRI"
    },
    "operation_amp_cursor_left": {
        "1": "CLE"
    },
    "operation_amp_cursor_enter": {
        "1": "CEN"
    },
    "operation_amp_cursor_return": {
        "1": "CRT"
    },
    "operation_amp_audio_parameter": {
        "1": "ATA"
    },
    "operation_amp_output_parameter": {
        "1": "HPA"
    },
    "operation_amp_video_parameter": {
        "1": "VPA"
    },
    "operation_amp_channel_select": {
        "1": "CLC"
    },
    "operation_amp_home_menu": {
        "1": "HM"
    },
    "operation_amp_key_off": {
        "1": "KOF"
    }
}