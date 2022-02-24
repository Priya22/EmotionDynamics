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

    print(common_group_cols, dispCols)
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
        print(dim, len(dispdf), dispdf.columns)

    dispdf = pd.concat(dispdfs)

    return dispdf


def get_dialogue_df(clean_ued, config):
    dialoguedf = clean_ued.groupby(list(set(['Identifier', config.idCol, config.textIdCol]))).agg({config.textCol: 'first'}).reset_index()
    return dialoguedf

def divvy_dfs(ued, summ, config):
    clean_ued = process_ued(ued, config)
    clean_summ = process_summ(summ, config)


    stepWiseCols = [
        'Identifier', config.idCol, config.textIdCol, 'rolling_window_step', 'narrative_time', 'speaker_dialogue_turn', 'speaker_word_turn', 'word',\
            'valence', 'valence_in_home_base', 'valence_disp_num', 'valence_dist_home_base', 'valence_is_peak', 'valence_disp_dist', 'valence_state',\
                # 'valence_peak_dist', 'valence_disp_length', 'valence_rise_rate', 'valence_recovery_rate',\
                'arousal', 'arousal_in_home_base', 'arousal_disp_num', 'arousal_dist_home_base', 'arousal_is_peak', 'arousal_disp_dist', 'arousal_state',\
                    # 'arousal_peak_dist', 'arousal_disp_length', 'arousal_rise_rate', 'arousal_recovery_rate',\
                    'dominance', 'dominance_in_home_base', 'dominance_disp_num', 'dominance_dist_home_base', 'dominance_is_peak', 'dominance_disp_dist', 'dominance_state'\
                        # 'dominance_peak_dist', 'dominance_disp_length', 'dominance_rise_rate', 'dominance_recovery_rate'
                    ]

    relStepCols = list(set([x for x in stepWiseCols if x in clean_ued]))

    dialoguedf = get_dialogue_df(clean_ued, config)
    narrdf = clean_ued[relStepCols]
    displacementdf = get_dispcurve_df(clean_ued, config)
    speakerdf = clean_summ

    return clean_ued, clean_summ, dialoguedf, narrdf, displacementdf, speakerdf