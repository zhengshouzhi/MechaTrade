# -*- coding: utf-8 -*-
import numpy as np
from Analyze import DataProcess as DP

def roll_spread(closes):
    p = closes
    d = np.diff(p)
    cov_ = np.cov(d[1:], d[:-1])
    if cov_[0,1]<0:
        rollspread = round(2*np.sqrt(-cov_[0,1]),3)
    else:
        rollspread = None
    return rollspread

def AminudIlliq(closes,volume):
    p = closes
    dollar_vol = np.array(volume * p)
    ret = np.array(DP.closetoret(closes))
    illiq = np.mean(np.divide(abs(ret), dollar_vol[1:]))
    return illiq

