# -*- coding: utf-8 -*-
from Analyze import DataProcess as DP
import tushare as ts
import pandas as pd
import numpy as np


def vectorized_forward_return(df,cycle):
    forperiods = [1, 3, 5, 10, 15]
    for i in range(len(df)):
        code = DP.codeType(df.loc[i,'code'])
        curclose = df.loc[i,'curclose']
        startdate = df.loc[i,'time']
        tradata = ts.get_k_data(code,start=startdate,ktype=cycle)

        tradata = pd.DataFrame(tradata.values,columns=tradata.columns)

        closes = tradata['close']

        for period in forperiods:

            if (period < len(closes)):
                forclose = closes[period]
                forreturn = (forclose - curclose) * 100 / curclose
            else:
                forclose = None
                forreturn = None
            df.loc[i,'close'+str(period)] = forclose
            df.loc[i, 'return' + str(period)] = forreturn
    return df

def smaexit(df,smaperiod,cycle):
    for i in range(len(df)):
        code = DP.codeType(df.loc[i, 'code'])
        curclose = df.loc[i, 'curclose']
        startdate = df.loc[i, 'time']
        tradata = ts.get_k_data(code, ktype=cycle)

        tradata = pd.DataFrame(tradata.values, columns=tradata.columns)

        posindex =list(tradata['date']).index(startdate)
        closes = tradata['close']
        posindex += 1
        while(posindex < len(closes)):
            posclose = tradata.loc[posindex,'close']
            possmaprice = sum(closes[posindex-smaperiod+1:posindex+1])/smaperiod
            if(posclose < possmaprice):
                exitprice = posclose
                exitdate = tradata.loc[posindex, 'date']
                exitreturn = (exitprice - curclose) * 100 / curclose
                break
            posindex += 1
        if(posindex == len(closes)):
            exitprice = posclose
            exitdate = tradata.loc[posindex-1, 'date']
            exitreturn = (exitprice - curclose) * 100 / curclose
        df.loc[i,'exitdate']  = exitdate
        df.loc[i,'exitprice'] = exitprice
        df.loc[i,'exitreturn'] = exitreturn
    return df
