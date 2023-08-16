import numpy as np
import pandas as pd
import nltk
import os, re, sys, json, csv, string, os, math
import scipy
import scipy.stats as stats
from tqdm import tqdm

def ellipse_distance(a, b, x, y):
    """[summary]

    Args:
        a ([type]): [description]
        b ([type]): [description]
        x ([type]): [description]
        y ([type]): [description]

    Returns:
        [type]: [description]
    """
    px = abs(x)
    py = abs(y)
    t = math.pi/4

    for _ in range(4):
        x = a*math.cos(t)
        y = b*math.sin(t)
        ex = ((a*a - b*b)*(math.cos(t)**3))/a 
        ey = (b*b - a*a)*(math.sin(t)**3)/b
        rx = x-ex
        ry = y-ey
        qx = px-ex
        qy = py-ey
        r = math.sqrt(ry**2 + rx**2)
        q = math.sqrt(qy**2 + qx**2)

        delta_c = r*math.asin((rx*qy - ry*qx)/(r*q))
        delta_t = delta_c/math.sqrt(a**2 + b**2 - x**2 - y**2)
        t = t + delta_t
        t = min(math.pi/2, max(0, t))

    x = abs(x) * np.sign(px)
    y = abs(y) * np.sign(py)
    dist = math.sqrt((py-y)**2 + (px-x)**2)
    return dist

def in_ellipse(sdf, emoCols, level=0.68):
    x = sdf[emoCols[0]].tolist()
    y = sdf[emoCols[1]].tolist()
    
    mat = np.column_stack([x, y])
    mus = np.mean(mat, axis=0)
    sigma = np.cov(mat, rowvar=False)

    eg_val, eg_vec = np.linalg.eig(sigma)

    theta = scipy.stats.chi2.ppf(level, df=2) #why 2? == number of dimensions?

    a = math.sqrt(theta * eg_val[0])
    b = math.sqrt(theta * eg_val[1])
    angle = math.atan(eg_vec[1,0]/eg_vec[0,0])
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)

    #check if points are in the ellipse
    in_bases = [False for _ in range(len(x))]
    distances = [0 for _ in range(len(x))]

    for i in range(len(x)):
        dist = (((cos_theta*(x[i] - mus[0]) + sin_theta*(y[i]-mus[1]))**2)/a**2) +\
            (((sin_theta*(x[i] - mus[0]) - cos_theta*(y[i]-mus[1]))**2)/b**2)

        if dist<=1:
            in_bases[i] = True 
            distances[i] = 0
        
        else:
            in_bases[i] = False 
            distances[i] = ellipse_distance(a*cos_theta, b*sin_theta, x[i]-mus[0], y[i]-mus[1])
    
    sdf['in_home_base'] = in_bases
    sdf['dist_home_base'] = distances
    
    return sdf

def in_range(sdf, emoCol, level=0.68):

    in_bases = [False for _ in range(len(sdf))]
    distances = [0 for _ in range(len(sdf))]
    low_high = ['HOME' for _ in range(len(sdf))]

    x = sdf[emoCol].tolist()
    num_points = len(x)

    mult_val = abs(stats.t.ppf(q=(1-level)/2, df=num_points-1))

    xmean = np.nanmean(x)
    xstd = np.nanstd(x)

    band_low = xmean - (mult_val * xstd)
    band_high = xmean + (mult_val * xstd)

    for i in range(len(x)):
        if x[i]<=band_high and x[i]>=band_low:
            in_bases[i] = True 

        elif x[i] > band_high:
            distances[i] = x[i]-band_high
            low_high[i] = 'HIGH' 
        else:
            distances[i] = band_low-x[i]
            low_high[i] = 'LOW'

    sdf['in_home_base'] = in_bases
    sdf['dist_home_base'] = distances

    sdf['state'] = low_high
    return sdf

def displacement_number(sdf):
    x = sdf['in_home_base'].tolist()
    y = sdf['state'].tolist()
    low_disp_count = 1
    high_disp_count = 1
    disp_count = 1
    disp_nums = [0 for _ in range(len(x))]
    for i in range(len(x)):
        if x[i]:
            disp_nums[i] = None
        else:
            if i == len(x)-1:
                disp_nums[i]  = disp_count
            else:
                disp_nums[i] = disp_count
                if x[i]!=x[i+1]:
                    disp_count += 1
                    if y[i] == 'LOW':
                        low_disp_count += 1
                    if y[i] == 'HIGH':
                        high_disp_count += 1
    sdf['disp_num'] = disp_nums
    sdf['disp_count'] = disp_count   #len(set(disp_nums))
    sdf['low_disp_count'] = low_disp_count
    sdf['high_disp_count'] = high_disp_count
    return sdf

def displacement_distance(sdf):
    x = sdf['in_home_base'].tolist()
    indices = sdf['is_peak'].tolist()
    
    disp_count = 0
    disp_dists = [0 for _ in range(len(x))]
    indices =  [i for i in range(len(indices)) if indices[i]==True]

    for i in range(len(x)):
        if x[i]:
            disp_dists[i] = None
        else:
            disp_dists[i] = i-indices[disp_count]

        if i==len(x)-1:
            disp_count = disp_count
        elif ((not x[i]) and (x[i+1])):
            disp_count += 1
    
    sdf['disp_dist'] = disp_dists
    
    return sdf