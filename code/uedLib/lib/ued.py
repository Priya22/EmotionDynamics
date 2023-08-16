import numpy as np
from numpy.lib.npyio import save
import pandas as pd
import nltk
import os, re, sys, json, csv, string, os, math
import scipy 
from tqdm import tqdm
import argparse
import yaml
from box import Box
import logging
import time
try:
    import lib.utils as utils
except ModuleNotFoundError:
    import utils

try:
    import lib.pre_process as pre_process
except ModuleNotFoundError:
    import pre_process as pre_process

try:
    import lib.post_process as post_process
except ModuleNotFoundError:
    import post_process

parser = argparse.ArgumentParser(description="Run emotion dynamics")
parser.add_argument('--config', metavar='FILE', help='path to the config file')
parser.add_argument('--pre_process', type=str, help='Apply pre-processing to input [True, False]', default='True', required=False)
parser.add_argument('--post_process', type=str, help='Apply post-processing to outputs [True, False]', default='True', required=False)

tqdm.pandas()

# TOKENIZER = nltk.word_tokenize
def split_tokens(s):
    return s.split(" ")

TOKENIZER = split_tokens

def default_hb(data, config, edim):
    data[edim+'_emo_std'] = data.groupby(config.idCol)[edim].transform(np.nanstd)
    data[edim + '_emo_mean'] = data.groupby(config.idCol)[edim].transform(np.nanmean) #replace with rmssd

    return data

def get_tenp_hb(sdf, config, edim):
    numTurns = sdf['NumTurns'].unique().tolist()
    assert len(numTurns) == 1
    numTurns = numTurns[0]

    tenp = 0.1*numTurns
    tenp = max(5, math.ceil(tenp))

    dnums = sdf[config.textIdCol].unique().tolist()[:tenp]

    tdf = sdf[sdf[config.textIdCol].isin(dnums)].sort_values(by='time_num')
    sdf[edim+'_emo_mean'] = np.nanmean(tdf[edim])
    sdf[edim+'_emo_std'] = np.nanstd(tdf[edim])

    return sdf

def tenp_hb(data, config, edim):
    data = data.groupby(config.idCol).apply(get_tenp_hb, config=config, edim=edim)
    return data

HB_DEFS = {
    'SPK100': default_hb,
    'SPK10': tenp_hb,
}

def read_config(config_file):
    config = Box.from_yaml(filename=config_file, Loader=yaml.FullLoader)
    return config

def get_tokenized_df(df, textCol):
    tok_rows = []
    for _, row in tqdm(df.iterrows()):
        tokens = TOKENIZER(row[textCol])

        comm_vals = [val for key, val in row.items()]
        for t in tokens:
            tok_rows.append(comm_vals + [t.lower()])
        
   
    tdf = pd.DataFrame(tok_rows, columns=[key for key in df.columns]+['word'])
    
    return tdf


def read_stopwords(path):
    with open(path,'r') as f:
        swords = f.readlines()
    swords = [x.strip().lower() for x in swords]
    stopdf = pd.DataFrame(swords, columns=['word'])
    return stopdf


def ued(config, df):

    textCol = config.textCol
    idCol = config.idCol
    timeCol = config.timeCol
    emoCols = config.emoCols

    logging.info("Number of speakers: " + str(len(df[idCol].unique())))


    assert textCol in df.columns, logging.info(textCol + " not found in data!")
    assert timeCol in df.columns, logging.info(timeCol + ' not found in data')

    #add count columns
    df['NumTurns'] = df.groupby(idCol)[timeCol].transform('nunique')

    # lex = pd.read_csv(config.lex_path, sep='\t', header=None, names=['word', 'valence', 'arousal', 'dominance'])
    lex = pd.read_csv(config.lex_path)
    
    lex.dropna(inplace=True)
    lex['word'] = lex['word'].astype('str')
    
    lex = lex[['word']+emoCols]


    for col in emoCols:
        assert col in lex.columns, logging.info(col + " not found in lexicon.")

    if isinstance(config.min_turns, int):
        # min_turns = int(config.min_turns)
        df = df[df['NumTurns']>=config.min_turns]

    df.sort_values(by=[config.idCol, config.timeCol], inplace=True)
    tdf = get_tokenized_df(df, textCol)

    stopdf = read_stopwords(config.stopword_path)

    tdf = tdf[~tdf['word'].isin(stopdf['word'])]

    tdf['row_num'] = [i for i in range(len(tdf))]

    res_dict = {}

    for edim in emoCols:
        logging.info("Computing metrics for dimension: {}".format(edim))
        emoverbose, emosummary = process_dimension(tdf, lex, edim, config)
        res_dict[edim] = [emoverbose, emosummary]

    return res_dict


def process_dimension(tdf, lex, edim, config):
    start_time = time.time()
    logging.info("Step 1: Generating sequence of emotion states")

    lexdf = lex[['word', edim]]

    if str(config.filter).lower() == 'true':
        lexdf = lexdf[(lexdf[edim]>=0.67) | (lexdf[edim]<=0.33)]

    
    ldf = tdf.merge(lexdf, on='word', how='inner', sort=False).sort_values(by='row_num')

    if isinstance(config.min_tokens, int):
        ldf = ldf.groupby(config.idCol).filter(lambda x: len(x)>=config.min_tokens)

    logging.info("Filtered to {} unique speakers".format(len(tdf[config.idCol].unique())))

    ldf['number_emo_words'] = ldf.groupby(by=config.idCol)['row_num'].transform('nunique')

    ldf = ldf.sort_values(by=[config.idCol, config.timeCol, 'row_num'])

    data_roll = ldf #.copy() #remove unnecessary copy
    data_roll['NumTurns'] = data_roll.groupby(config.idCol)[config.textIdCol].transform('nunique')


    data_roll[edim+'_straight_mean'] = data_roll.groupby(config.idCol)[edim].transform(np.nanmean) ##CHECK

    data_roll[edim] = data_roll.groupby(config.idCol)[edim].rolling(window=config.rollingWindow).mean().reset_index(0,drop=True)

    data_roll = data_roll.groupby(config.idCol).apply(lambda group: group.iloc[config.rollingWindow-1:]).reset_index(0, drop=True)

    data_roll['time_num'] = data_roll.groupby(config.idCol).cumcount()+1
    data_roll['time_prep'] = data_roll.groupby(config.idCol)['time_num'].transform('max')
    data_roll['time_prep'] = data_roll['time_num']/data_roll['time_prep']

    timeCol = 'time_num'
    level = config.level

    data = data_roll #.copy()  #remove unnecessary copy
    data = data.sort_values([config.idCol, timeCol])

    # for col in emoCols:
    # data[edim+'_emo_std'] = data.groupby(config.idCol)[edim].transform(np.std)
    # data[edim + '_emo_mean'] = data.groupby(config.idCol)[edim].transform(np.mean) 
    hb_func = HB_DEFS[config.hb_type]
    data = hb_func(data, config, edim)

    emoData = data.groupby(config.idCol).apply(utils.in_range, emoCol=edim, level=level)
    logging.info("Done in {} seconds".format(time.time()-start_time))
    emoverbose, emosummary = line_analysis(emoData, config, edim)

    return emoverbose, emosummary

 
def line_analysis(data, config, emoCol):
    # print(emoCol)
    logging.info("Step 2: computing UED metrics")
    start = time.time()

    idCol = config.idCol

    disp_length_min = config.disp_length_min 


    data = data.groupby(idCol).apply(utils.displacement_number)

    #peak dist
    data['peak_dist'] = data.groupby(by=[idCol, 'disp_num'])['dist_home_base'].transform(max)
    data['peak_dist'] = data['peak_dist'].fillna(0.)

    #is peak
    data['is_peak'] = np.where(data['in_home_base'] == True, np.nan, np.where(data['dist_home_base'] == data['peak_dist'], True, False)).astype(bool)
    data['is_peak'] = data['is_peak'].astype('bool')
    data['is_peak'] = np.where(data['in_home_base'] == True, np.nan, data['is_peak'])
    
    #displacement distance
    data['disp_num'] = data['disp_num'].fillna(-1)
    data = data.groupby([idCol, 'disp_num']).apply(utils.displacement_distance)
    data['disp_dist'] = np.where(data['disp_num']==-1, np.nan, data['disp_dist'])
    data['disp_num'] = np.where(data['disp_num']==-1, np.nan, data['disp_num'])

    #disp length
    data['disp_length'] = np.where(data['in_home_base']==True, np.nan, data.groupby([idCol, 'disp_num'])['disp_dist'].transform('count'))



    #rise recovery
    data['temp_rr'] = np.where(data['disp_dist'] < 0, 'rise_rate', np.nan)
    data['temp_rr'] = np.where(data['disp_dist'] > 0, 'recovery_rate', data['temp_rr'])
    # data['temp_rr'] = np.where(data['disp_dist'] == 0, np.nan, data['temp_rr'])
    data['temp_rr'] = np.where(np.isin(data['disp_length'],range(1, disp_length_min)), np.nan, data['temp_rr'])

    data.rename({
    'temp_rr': 'rise_recovery'
        }, inplace=True, axis=1)

    data['rise_recovery'].replace('nan', np.nan, inplace=True)

    #rate of rise/recovery
    data['tmp_count'] = data.groupby(by=[idCol, 'disp_num', 'rise_recovery'])[idCol].transform('size')
    data['disp_length'] = np.where(data['disp_length']>=disp_length_min, data['disp_length'], np.nan)

    data['state_rate'] = np.where(data['rise_recovery'].isin(['rise_rate', 'recovery_rate']), data['peak_dist']/data['tmp_count'], np.nan)

    data['rise_rate'] = np.where(data['rise_recovery']=='rise_rate', data['state_rate'], np.nan)
    
    data['recovery_rate'] = np.where(data['rise_recovery']=='recovery_rate', data['state_rate'], np.nan)

    data['low_rise_rate'] = np.where(data['state']=='LOW', data['rise_rate'], np.nan)
    data['low_recovery_rate'] = np.where(data['state']=='LOW', data['recovery_rate'], np.nan)
    data['high_rise_rate'] = np.where(data['state']=='HIGH', data['rise_rate'], np.nan)
    data['high_recovery_rate'] = np.where(data['state']=='HIGH', data['recovery_rate'], np.nan)

    #delete tmp
    data.drop([ 'rise_recovery', 'tmp_count', 'state_rate'], axis=1, inplace=True)
    

    data['n_words'] = data.groupby(idCol)['word'].transform('size')


    cols = []
    agg_cols = {}
    for col in [emoCol]:
        cols.append(col + '_emo_std')
        cols.append(col + '_emo_mean')
        cols.append(col+'_straight_mean')



    cols.extend(['in_home_base' , 'dist_home_base', \
        'disp_num', 'disp_dist', 'peak_dist', 'is_peak', 'disp_length', 'rise_rate',\
            'recovery_rate', 'low_rise_rate', 'low_recovery_rate', 'high_rise_rate', 'high_recovery_rate',\
                'disp_count', 'low_disp_count', 'high_disp_count'])

    cols  = [x for x in cols if x in data.columns]
    for col in cols:
        agg_cols[col] = np.nanmean
        data[col] = data[col].astype('float')


    for col in data.columns:

        if col != idCol and '_emo_mean' not in col and 'emo_std' not in col and '_straight_mean' not in col:
            if (data.groupby(idCol)[col].nunique() == 1).all():
                cols.append(col)
            
                if col not in agg_cols:
                    agg_cols[col] = 'first'

    cols = list(set(cols))


    op = data.groupby(idCol).agg(agg_cols).reset_index()
    op.drop(columns=['disp_num', 'is_peak', 'disp_dist'], inplace=True)


    common_cols = ['in_home_base', 'dist_home_base',
       'disp_num', 'disp_count', 'peak_dist', 'is_peak', 'disp_dist',
       'disp_length', 'rise_rate', 'recovery_rate', 'state', \
           'low_rise_rate', 'low_recovery_rate', 'high_rise_rate', 'high_recovery_rate',\
               'low_disp_count', 'high_disp_count']

    for col in common_cols:
        nc = emoCol + '_' + col
        data.rename({col: nc}, axis='columns', inplace=True)

    
    common_cols = ['in_home_base', 'dist_home_base',
       'disp_dist', 'peak_dist', 'disp_count', 'disp_length', 'rise_rate', 'recovery_rate', \
        'low_rise_rate', 'low_recovery_rate', 'high_rise_rate', 'high_recovery_rate', 'low_disp_count', 'high_disp_count']

    for col in common_cols:
        nc = emoCol + '_' + col 
        op.rename({col: nc}, axis='columns', inplace=True)

    logging.info("Done in {} seconds ".format(time.time()-start))
    print()

    return data, op
    
def main(config_path, post_p, pre_p):


    config = read_config(config_path)
    pp = False
    if post_p.lower() == 'true':
        pp = True
    prep = False 
    if pre_p.lower() == 'true':
        prep = True

    save_dir = config.save_dir
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir, exist_ok=True)

    logfile = os.path.join(save_dir, 'log.txt')

    logging.basicConfig(filename=logfile, format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='w',
                    level=logging.INFO)

    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    df = pre_process.get_df(config.data_path)
    
    if len(df) == 0:
        return

    if prep:
        df, config = pre_process.prep(df, config)

    config.to_yaml(os.path.join(save_dir, 'config.yaml'))

    res_dict = ued(config, df)

    for edim in res_dict:
        data, summary = res_dict[edim]

        if pp:
            clean_ued, clean_summ, dialoguedf, narrdf, displacementdf, speakerdf = post_process.divvy_dfs(data, summary, config, edim)
            
            edim_save_path = os.path.join(save_dir, edim)
            os.makedirs(edim_save_path, exist_ok=True)

            for df, name in zip([clean_ued, clean_summ, dialoguedf, narrdf, displacementdf, speakerdf], \
                ['ued_all', 'summ_all', 'utterance_info', 'narrative_info', 'displacement_info', 'overall_speaker_info']):
                if str(config.compress).lower() == 'true':
                    df.to_csv(os.path.join(edim_save_path, name+'.csv.gzip'), compression='gzip')
                else:
                    df.to_csv(os.path.join(edim_save_path, name+'.csv'), index=False)

    logging.info("Outputs written to " + str(save_dir))
    # print("Outputs written to " + str(save_dir))

if __name__ == '__main__':
    args = parser.parse_args()

    main(args.config, args.post_process, args.pre_process)