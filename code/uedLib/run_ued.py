import os, re, sys, json, csv, string
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import argparse

import lib.ued as ued

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, required=True, help='path to config file')
parser.add_argument('--preprocess', type=str, required=False, default='true', help='preprocess data')
parser.add_argument('--postprocess', type=str, required=False, default='true', help='post-process results')

if __name__=='__main__':
    args = parser.parse_args()

    config_path = args.config
    postp = args.postprocess
    prep = args.preprocess

    ued.main(config_path, postp, prep)