import os, re, csv, json, sys, string
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import gzip
from tqdm import tqdm
import logging
from twTokenizer import twokenize
import pickle as pkl


CITIES = ['Winnipeg', 'SanFrancisco', 'Memphis', 'Hamilton', 'Okanagan', 'Dallas', 'Surrey', 'Boston', 'Seattle', 'Victoria', 'Jacksonville', 'NewYork', \
    'Etobicoke', 'Phoenix', 'Brampton', 'Laval', 'Washington', 'SanJose', 'SanDiego', 'Philadelphia', 'Houston', 'NorthYork', 'LosAngeles', 'Columbus', \
        'Quebec', 'ElPaso', 'FortWorth', 'Denver', 'Charlotte', 'Detroit', 'SanAntonio', 'Vancouver', 'Mississauga', 'London', 'Windsor', 'Austin', 'Edmonton', \
            'Nashville', 'Calgary', 'Montreal', 'Ottawa', 'Halifax', 'Toronto', 'Indianapolis', 'Scarborough', 'Chicago']

COUNTRIES = ['CA', 'US']

def get_day_date_month_year(ts):
    
    day, month, date, time, offset, year = ts.split(" ")
    
    return day, date, month , year

def tokenize_tweet(tweetText):
    return " ".join(twokenize.tokenizeRawTweetText(tweetText))

def get_urls(tokenizedTweet):
    urls = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", tweet)
    if len(urls) == 0:
        return False
    return True

def count_words(tokenizedTweet):
    count = 0
    for t in tokenizedTweet.split(" "):
        if t.replace('\'', '').isalpha():
            count += 1
            if count ==3:
                return True
    
    if count < 3:
        return False
