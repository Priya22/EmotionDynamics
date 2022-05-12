import string, os, re, sys, json, csv
import numpy as np
from numpy.lib.npyio import save
import pandas as pd
from collections import Counter, defaultdict

# def prep(df):
#     df.drop_duplicates(subset=df.columns, inplace=True)
#     df = df[df['URL']==False]
#     df['createdAt'] = df['createdAt'].astype('datetime64[ns]')
#     df = df.sort_values(by='createdAt')
#     df['Turn'] = np.arange(len(df))
#     return df

def get_df(folder):
    
    if os.path.isfile(folder):
        df = pd.read_csv(folder)
        return df

    merged_df = None
    for file in os.scandir(folder):
        
        if os.path.isfile(file.path):
            print("Loading file: ", file.path)
            #assume dataframe
            try:
                df = pd.read_csv(file.path)

                if merged_df is None:
                    merged_df = df.copy()
                
                else:
                    merged_df = pd.concat([merged_df, df])
            except Exception as e:
                print("Failed to load: ", file.path)
        
        # elif os.path.isdir(file):
        #     print("Loading folder: ", file.path)
        #     for subf in os.scandir(file):
        #         if os.path.isfile(subf.path):
        #             print("Loading file: ", subf.path)
        #             #assume dataframe
        #             try:
        #                 df = pd.read_csv(subf.path)
        #                 if merged_df is None:
        #                     merged_df = df.copy()
                        
        #                 else:
        #                     merged_df = pd.concat([merged_df, df])
        #             except Exception as e:
        #                 print("Failed to load: ", subf.path)
    return merged_df

def prep(df, config):
   
    df = df.sort_values(by=config.timeCol)
    df['Turn'] = np.arange(len(df))
    config.timeCol = 'Turn'
    if isinstance(config.idCol, list): #and len(config.idCol) > 1:
        for idc in config.idCol:
            df[idc] = df[idc].astype('str')
        df['idCol'] = df[config.idCol].agg('-'.join, axis=1)
    
    else:
        df['idCol'] = df[config.idCol]

    if 'textIdCol' not in config:
        config.textIdCol = 'utteranceId'
    if config.textIdCol not in df.columns:
        df[config.textIdCol] = np.arange(len(df))
    config.idCol = 'idCol'
    return df, config