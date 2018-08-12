# -*- coding: utf-8 -*-
import Analyze.Statistical as  sta
from pandas import DataFrame,Series
import tushare as ts
import Config
import os
import pandas as pd
import DataInter as DI
from Analyze import Statistical


def fallenangel(dfPosition,downthresh=90):
    dfPosition = dfPosition.sort_values(by='curdown', ascending=True)
    dfPosition = DataFrame(dfPosition.values, columns=dfPosition.columns)
    i = 0
    while i < len(dfPosition):
        curdown = dfPosition.loc[i, 'curdown']
        if (curdown < -downthresh):
            print(curdown,i,-downthresh)
            i = i+1
        else:
            break
    dfselected = dfPosition[0:i]
    return dfselected


def Stock_InRange_Selection(dfPosition,lowthresh=35,upthresh=55):
    for i in range(len(dfPosition)):
        position = dfPosition.loc[i,'position']
        if(position < lowthresh):
            i = i+1
        else:
            break
    for j in range(len(dfPosition)):
        position = dfPosition.loc[j, 'position']
        if (position < upthresh):
            j = j + 1
        else:
            break
    dfselected =dfPosition[i:j]
    return dfselected


def get_fallen_angels(dataset='Whole', Cycle='D', period=240,downthresh=90):
    from Analyze import StockSelectiion
    selectmethod = 'fallenangel'
    rootDir = Config.dataDir
    positionfilename = dataset + '-' + Cycle + '-' + str(period) + '-' + Config.curdatestr
    positionfilepath = os.path.join(rootDir, 'StockSelection', positionfilename + '.csv')

    if (os.path.exists(positionfilepath)):

        dfPosition = pd.read_csv(positionfilepath, encoding='gbk')
    else:
        codelist = DI.get_stockcode_list(dataset)
        dfPosition = Statistical.batch_position(codelist, period=period, value='curdown',Cycle=Cycle)
        dfPosition.to_csv(positionfilepath)
    dfSelected = StockSelectiion.fallenangel(dfPosition,downthresh=downthresh)
    selectedfilename = dataset + Config.curdatestr + selectmethod + str(period)

    selectedfilpath = os.path.join(rootDir, 'StockSelection', selectedfilename + '.csv')
    dfSelected.to_csv(selectedfilpath)
    return dfSelected



def fallenAngel():

    dataset = 'whole'
    period = 240
    downthresh = 70
    Cycle = 'W'
    get_fallen_angels(dataset=dataset, Cycle=Cycle, period=period, downthresh=downthresh)


