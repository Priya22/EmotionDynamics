import os, re, csv, json, sys, string
import numpy as np
import pandas as pd
from collections import defaultdict, Counter

import gzip

from tqdm import tqdm

import pickle as pkl
from argparse import ArgumentParser
import logging

tqdm.pandas()

parser = ArgumentParser()
parser.add_argument('--dataPath', help='path to CSV data file with texts')
parser.add_argument('--lexPath', help='path to lexicon. CSV with columns word, val')
parser.add_argument('--lexName', help='Name of the lexicon')
parser.add_argument('--savePath', help='path to save folder')

def read_lexicon(path):
    df = pd.read_csv(path)
    df = df[~df['word'].isna()]
    df = df[~df['val'].isna()]
    df.drop_duplicates(subset=['word'], keep='first', inplace=True)
    df['word'] = [x.lower() for x in df['word']]
    df['val'] = [float(x) for x in df['val']]
    df.set_index('word', inplace=True)
    return df

def get_alpha(token):
    return token.isalpha()


def get_vals(twt):
    tt = twt.lower().split(" ")
    at = [w for w in tt if w.isalpha()]

    pw = [x for x in tt if x in LEXICON.index]
    pv = [LEXICON.loc[w]['val'] for w in pw]

    numTokens = len(at)
    numLexTokens = len(pw)
    
    avgLexVal = np.mean(pv)  #nan for 0 tokens

    return [numTokens, numLexTokens, avgLexVal]


def process_df(df):
    logging.info("Number of rows: " + str(len(df)))

    resrows = [get_vals(x) for x in df['text']]

    resdf = pd.DataFrame(resrows, columns=['numTokens', 'numLexTokens', 'avgLexVal'])
    resdf = resdf[resdf['numLexTokens']>=1]
    
    resdf['lexRatio'] = resdf['numLexTokens']/resdf['numTokens']
    return resdf

def main(args):
    

    save_file = args.savePath
    os.makedirs(save_file, exist_ok=True)

    logfile = os.path.join(save_file, LEXNAME+'_log.txt')

    logging.basicConfig(filename=logfile, format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
    
    logging.info("Lexicon length: " + str(len(LEXICON)) + " " + LEXNAME)

    df = pd.read_csv(args.dataPath)
    resdf = process_df(df)

    resdf.to_csv(os.path.join(save_file, LEXNAME+'.csv'), index=False)

if __name__=='__main__':
    args = parser.parse_args()
    lexPath = args.lexPath
    LEXICON = read_lexicon(lexPath)

    LEXNAME = args.lexName
    main(args)