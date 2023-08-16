import string, os, re, sys, json, csv
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
# import matplotlib.pyplot as plt

def get_clean_ued(ued, config):
    clean_ued = ued.sort_values(by='row_num')
    clean_ued['rolling_window_step'] = [i for i in range(len(clean_ued))]

    clean_ued['dialogue_turn'] = clean_ued.groupby(config.timeCol).ngroup() + 1

    clean_ued.rename({'time_num': 'speaker_word_turn'}, axis='columns', inplace=True)

    clean_ued['speaker_dialogue_turn'] = clean_ued.groupby([config.idCol, 'dialogue_turn']).ngroup() 

    clean_ued['speaker_dialogue_turn'] = clean_ued.groupby(config.idCol)['speaker_dialogue_turn'].transform(lambda x: x - x.min() + 1)

    rename_map = {'n_words': 'speaker_num_steps'}
    rename_map = {k:v for k,v in rename_map.items() if k in clean_ued}
    clean_ued.rename(rename_map, axis='columns', inplace=True)

    return clean_ued


def process_ued(ued, config):
    clean_ued = get_clean_ued(ued, config)
    
    try:
        clean_ued['Identifier'] = config.iden
    except:
        clean_ued['Identifier'] = 'UNK'
    return clean_ued

def process_summ(summ, config):
    clean_summ = summ.copy()

    try:
        clean_summ['Identifier'] = config.iden

    except:
        clean_summ['Identifier'] = 'UNK'
       
    clean_summ.rename({'n_words': 'speaker_num_steps'}, axis='columns', inplace=True)

    return clean_summ

def get_dispcurve_df(clean_ued, config):
    common_group_cols = ['Identifier', config.idCol]
    common_group_cols = list(set([x for x in common_group_cols if x in clean_ued]))

    disp_curve_cols = [
        'peak_dist', 'disp_length', 'rise_rate', 'recovery_rate', 'state', 'low_rise_rate', \
            'low_recovery_rate', 'high_rise_rate', 'high_recovery_rate']

    emoDims = config.emoCols
    dispCols = common_group_cols+['emotion', 'disp_num', 'peak_dist', 'disp_length', 'rise_rate', 'recovery_rate', 'state',\
        'low_rise_rate', 'low_recovery_rate', 'high_rise_rate', 'high_recovery_rate']

    # print(common_group_cols, dispCols)
    dispdfs = []
    for dim in emoDims:
        if dim not in clean_ued:
            continue 

        group_cols = list(set(common_group_cols + [dim+'_disp_num']))
        dimCols = [dim+'_'+c for c in disp_curve_cols]
        
        dimued = clean_ued.dropna(subset=[dim+'_disp_num', dim+'_disp_length'], axis=0)
        
        aggf = {c:np.nanmean for c in dimCols}
        aggf[dim + '_state'] = 'first'
        
        dispdf = dimued.groupby(group_cols).agg(aggf).reset_index()
        
        dispdf['emotion'] = dim
        
        rename_f = {dim+'_'+c:c for c in ['disp_num', 'peak_dist', 'disp_length', 'rise_rate', 'recovery_rate',\
            'state', 'low_rise_rate', 'low_recovery_rate', 'high_rise_rate', 'high_recovery_rate']}
        dispdf.rename(rename_f, axis='columns', inplace=True)
        
        dispdf = dispdf[dispCols]
        
        dispdfs.append(dispdf)
        # print(dim, len(dispdf), dispdf.columns)

    dispdf = pd.concat(dispdfs)

    return dispdf


def get_dialogue_df(clean_ued, config):
    dialoguedf = clean_ued.groupby(list(set(['Identifier', config.idCol, config.textIdCol]))).agg({config.textCol: 'first', config.timeCol: 'first'}).reset_index()
    rename_func = {
        'idCol': 'speaker_id',
        config.textIdCol: 'global_utterance_index',
        'text': 'utterance_text'
    }
    # dialoguedf.rename({'dialogueTurn': 'dialogue_turn'}, axis='columns', inplace=True)
    dialoguedf.rename(rename_func, inplace=True, axis='columns')
    # print(dialoguedf.columns)
    return dialoguedf

def prep_narr_df(clean_ued, config, emoDim):
    # print("Columns: ", clean_ued.columns)
    # print(emoDim)
    rename_func = {
        'idCol': 'speaker_id',
        'speaker_dialogue_turn': 'speaker_utterance_index',
        config.textIdCol: 'global_utterance_index',
        'speaker_word_turn': 'speaker_word_index',
        'word': 'speaker_word',
        'rolling_window_step': 'speaker_rolling_window_index',
    }
    post_rename_func = {
        'speaker_emo_disp_num': 'speaker_emo_displacement_number',
        'speaker_emo_disp_dist': 'speaker_emo_displacement_counter',
        'speaker_emo_is_peak': 'speaker_emo_state_is_peak',
        'speaker_emo_dist_home_base': 'speaker_emo_distance_home_base',
        'speaker_emo_state':  'speaker_emo_state_position'
    }
    for col in clean_ued.columns:
        first, second = col.split("_")[0], col.split("_")[1:]
        if first == emoDim:
            # eDim = col.split("_")[0]
            # eDim = emoDim
            # print(col)
            if len(second)>0:
                nn = "_".join(['speaker_emo']+second)
                
            else:
                # print("Single val: ", col)
                nn = "speaker_emo_state_value"
            rename_func[col] = nn
    # rename_func['dialogueTurn'] = 'dialogue_turn'
    # rename_func['speaker_emo_in_']
    ndf = clean_ued.rename(rename_func, axis='columns')
    # print(ndf.columns)
    ndf.rename(post_rename_func, axis='columns', inplace=True)
    ndf['emotion'] = emoDim
    # del ndf['speaker_emo_state_value.1']

    ndf = ndf[['Identifier', 'speaker_id', 'emotion', 'speaker_utterance_index', 'global_utterance_index', 'speaker_rolling_window_index',\
        'speaker_word_index', 'speaker_word', 'speaker_emo_state_position', 'speaker_emo_state_is_peak', 'speaker_emo_displacement_counter',\
            'speaker_emo_displacement_number', 'speaker_emo_state_value', 'speaker_emo_in_home_base', 'speaker_emo_distance_home_base']]
    return ndf

def prep_sum_df(summdf, eDim):
    assert 'idCol' in summdf
    # print(eDim)
    post_rename_func = {
        'idCol': 'speaker_id',
        'NumTurns': 'number_emo_utterances',
        'speaker_num_steps': 'num_window_steps',
        'emo_straight_mean': 'emo_lexical_mean',
        'emo_dist_home_base': 'emo_avg_dist_home_base',
        'emo_peak_dist': 'emo_avg_peak_dist',
        'emo_disp_length': 'emo_avg_disp_length',
        'emo_rise_rate': 'emo_avg_rise_rate',
        'emo_recovery_rate': 'emo_avg_recovery_rate',
        'emo_low_rise_rate': 'emo_avg_home-to-low_rate',
        'emo_low_recovery_rate': 'emo_avg_low-to-home_rate',
        'emo_high_rise_rate': 'emo_avg_home-to-high_rate',
        'emo_high_recovery_rate': 'emo_avg_high-to-home_rate',
        'emo_disp_count': 'emo_number_displacements',
        'emo_low_disp_count': 'emo_number_low_displacements',
        'emo_high_disp_count': 'emo_number_high_displacements',
        'emo_emo_mean': 'emo_mean',
        'emo_emo_std': 'emo_std'
    }

    rename_func = {}

    # eDim = ''
    for col in summdf.columns:
        first, second = col.split("_")[0], col.split("_")[1:]
        # print(first, second)
        if first == eDim:
            # print(col)
            # eDim = first
            if len(second) > 0:
                rename_func[col] = "_".join(['emo']+second)
            else:
                rename_func[col] = 'speaker_emotion_value'

    # print(rename_func)
    sdf = summdf.rename(rename_func, axis='columns', inplace=False)

    sdf['emotion'] = eDim
    sdf.rename(post_rename_func, axis='columns', inplace=True)
    # print("Modified output columns: ", sdf.columns)
    return sdf

def prep_disp_df(displacementdf, eDim):
    rename_func = {
        'idCol': 'speaker_id',
        'disp_num': 'speaker_emo_displacement_number',
        'peak_dist': 'displacement_peak_dist',
        'disp_length': 'displacment_length',
        'rise_rate': 'displacement_rise_rate',
        'recovery_rate': 'displacement_recovery_rate',
        'state': 'displacement_position',
        'low_rise_rate': 'displacement_home-to-low_rate',
        'low_recovery_rate': 'displacement_low-to-home_rate',
        'high_rise_rate': 'displacement_home-to-high_rate',
        'high_recovery_rate': 'displacement_high-to-home_rate'
    }

    displacementdf.rename(rename_func, axis='columns', inplace=True)
    return displacementdf


def divvy_dfs(ued, summ, config, eDim):
    clean_ued = process_ued(ued, config)
    clean_summ = process_summ(summ, config)

    # emoDims = config.emoCols

    otherStepCols = ['in_home_base', 'disp_num', 'dist_home_base', 'is_peak', 'disp_dist', 'state']

    stepWiseCols = ['Identifier', config.idCol, config.textIdCol, 'rolling_window_step', 'narrative_time', 'speaker_dialogue_turn', 'speaker_word_turn', 'word']
    
    # for eDim in emoDims:
    stepWiseCols.append(eDim)
    for other in otherStepCols:
        stepWiseCols.append(eDim + '_' + other)
        
            # 'valence', 'valence_in_home_base', 'valence_disp_num', 'valence_dist_home_base', 'valence_is_peak', 'valence_disp_dist', 'valence_state',\
            #     # 'valence_peak_dist', 'valence_disp_length', 'valence_rise_rate', 'valence_recovery_rate',\
            #     'arousal', 'arousal_in_home_base', 'arousal_disp_num', 'arousal_dist_home_base', 'arousal_is_peak', 'arousal_disp_dist', 'arousal_state',\
            #         # 'arousal_peak_dist', 'arousal_disp_length', 'arousal_rise_rate', 'arousal_recovery_rate',\
            #         'dominance', 'dominance_in_home_base', 'dominance_disp_num', 'dominance_dist_home_base', 'dominance_is_peak', 'dominance_disp_dist', 'dominance_state'\
                        # 'dominance_peak_dist', 'dominance_disp_length', 'dominance_rise_rate', 'dominance_recovery_rate'
                    # ]

    relStepCols = list(set([x for x in stepWiseCols if x in clean_ued]))

    dialoguedf = get_dialogue_df(clean_ued, config)


    narrdf = prep_narr_df(clean_ued[relStepCols], config, eDim)
    
    displacementdf = get_dispcurve_df(clean_ued, config)
    displacementdf = prep_disp_df(displacementdf, eDim)

    speakerdf = prep_sum_df(clean_summ, eDim)

    return clean_ued, clean_summ, dialoguedf, narrdf, displacementdf, speakerdf