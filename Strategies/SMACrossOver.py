# -*- coding: utf-8 -*-
import DataInter as DI
import Config
import os
from Analyze import DataProcess as DP
import tushare as ts
from Analyze import Technical as ta
from pandas import DataFrame, Series
import pandas as pd
from Strategies.TripleScreen import ImpluseLight,GetPrimaryCycle
from Analyze import Statistical as sta
from Strategies import False_Breakout_Divergence as FBD
from BackTest import Performance
import time

StrategyName = 'SMABreakDiv'

def stock_in_divergece(code,tradeCycle='W',startdate = '',enddate=''):

    dfdata = ts.get_k_data(code, ktype=tradeCycle,start=startdate,end=enddate)
    if (len(dfdata) < 120):  # 剔除交易时间少于120天的个股
        return False
    dates = dfdata['date'].values
    closes = dfdata['close'].values
    highs = dfdata['high'].values
    lows = dfdata['low'].values

    macddiclist = ta.cal_macd(dates, closes)
    macd, dif, dea = DP.get_macd_list(macddiclist)

    divstatus = ta.macd_in_bulldivergence(dates,macd)
    divstatus['div']
    if(divstatus['div'] != 0):

        return True
    else:

        return False

def vectorized_smabreak_divergence(code='510300', tradeCycle='D'):
    colNames = ['time','code', 'curclose', 'sma', 'ATR', 'ATRRatio', 'ATRWZ', 'tradeImpScore',
                'primImpScore']

    filename = StrategyName + '-' + code + '-' + tradeCycle
    dfSelected = pd.DataFrame([], columns=colNames)
    RootDir = os.path.join(os.pardir, 'data', 'Vectorized')

    filepath = os.path.join(RootDir, filename + '.xls')

    code = DP.codeType(code)
    startdate = '2000-01-01'
    dfdata = ts.get_k_data(code,start=startdate,end='', ktype=tradeCycle)
    if (len(dfdata) < 120):  # 剔除交易时间少于120天的个股
        print('Not Enough data for decision making.')

    totaldates = dfdata['date'].values
    totalcloses = dfdata['close'].values
    totalhighs = dfdata['high'].values
    totallows = dfdata['low'].values

    macddiclist = ta.cal_macd(totaldates, totalcloses)
    totalmacd, totaldif, totaldea = DP.get_macd_list(macddiclist)
    i = 120

    while i < len(totalcloses):

        closes = totalcloses[:i]
        highs = totalhighs[:i]
        lows = totallows[:i]
        dates = totaldates[:i]
        if (not ta.smaupcrosssignal(closes, 20)):
            i += 1
            continue
        primCycle =  GetPrimaryCycle(tradeCycle)
        if(stock_in_divergece(code,primCycle,startdate=startdate,enddate=dates[-1])):

            absdis, perdis, maprice = ta.curdistosma(closes, 20)
            curATR = ta.last_atr(dates, closes, highs, lows)

            ATRWZ = absdis / curATR
            curClose = closes[-1]
            ATRRatio = curATR / curClose

            tradeImpScore = FBD.ImpluseScore(dates, closes)

            curATR = round(curATR, 2)
            ATRRatio = round(ATRRatio * 100, 2)

            ATRWZ = round(ATRWZ, 2)

            maprice = round(maprice, 2)


            dataprimCycle = ts.get_k_data(code, ktype=primCycle)
            primCloses = dataprimCycle['close'].values
            primdates = dataprimCycle['date'].values

            primImpScore = FBD.ImpluseScore(primdates, primCloses)


            s = Series([dates[-1],code,  curClose, maprice, curATR, ATRRatio, ATRWZ, tradeImpScore,primImpScore], index=colNames)

            dfSelected = dfSelected.append(s, ignore_index=True)
        else:

            pass
        i += 1
    # dfSelected = dfSelected.sort_values(by='totalscore',ascending=False)
    dfSelected = pd.DataFrame(dfSelected.values, columns=dfSelected.columns)
    # dfSelected.to_csv(filepath)
    DI.Write_DF_T0_Excel(filepath, dfSelected, 'selected')
    return dfSelected


def batch_vectorized_smabreak_divergence(dataset='hs300', cycle='D'):
    colNames = ['time','code','name', 'curclose', 'sma', 'ATR', 'ATRRatio', 'ATRWZ', 'tradeImpScore','primImpScore']
    codelist = DI.get_stockcode_list(dataset)

    dfScreen = codelist[['code', 'name']]
    totalrows = len(dfScreen)
    dftotal = DataFrame([], columns=colNames)
    for i in range(totalrows):
        code = dfScreen.loc[i, 'code']
        print(code)
        code = DP.codeType(code)

        name = dfScreen.loc[i, 'name']
        dfsub = vectorized_smabreak_divergence(code, cycle)
        dfsub['name'] = name
        dftotal = pd.concat([dftotal, dfsub])
    RootDir = os.path.join(os.pardir, 'data', 'Vectorized',StrategyName)
    if(not os.path.exists(RootDir)):
        DP.mkdir(RootDir)
    filename = dataset + 'whole' +StrategyName+'-'+cycle+'.xls'
    filepath = os.path.join(RootDir, filename)
    dftotal = dftotal.sort_values(by='time')
    dftotal = DataFrame(dftotal.values, columns=dftotal.columns)
    dftotal = Performance.vectorized_forward_return(dftotal,cycle)
    dftotal = Performance.smaexit(dftotal,20,cycle)
    DI.Write_DF_T0_Excel(filepath, dftotal, 'selected')


def batch_upcrossafter_divergence(dataset ='hs300',tradeCycle = 'D'):
    lasttradetimestr = DP.get_last_trade_time('D')

    colNames = ['code', 'name', 'period', 'curclose', 'sma', 'ATR', 'ATRRatio', 'rewardrisk', 'primImpScore',
     'tradeImpScore', 'primdivscore', 'divscore','difdeascore', 'macdscore','totalscore']

    filename = StrategyName + lasttradetimestr + '-' + dataset + '-' + tradeCycle

    RootDir = os.path.join(os.pardir, 'data', lasttradetimestr)
    DP.mkdir(RootDir)
    filepath = os.path.join(RootDir,filename+'.xls')

    codelist = DI.get_stockcode_list(dataset)

    dfSelected = pd.DataFrame([],columns=colNames)
    dfScreen = codelist[['code', 'name']]
    totalrows = len(dfScreen)
    for i in range(totalrows):
        code = dfScreen.loc[i,'code']
        code = DP.codeType(code)

        name = dfScreen.loc[i,'name']

        if(DI.is_tingpai(code)):
            continue

        dfdata = ts.get_k_data(code,ktype=tradeCycle)
        if(len(dfdata)<120):#剔除交易时间少于120天的个股
            continue

        dates = dfdata['date'].values
        closes = dfdata['close'].values
        highs = dfdata['high'].values
        lows = dfdata['low'].values
        if(not ta.smaupcrosssignal(closes,20)):

            continue

        print(name)
        macddiclist = ta.cal_macd(dates,closes)
        macd,dif,dea = DP.get_macd_list(macddiclist)

        if(min(macd[-3:])>0):
            continue

        primCycle = GetPrimaryCycle(tradeCycle)
        dataprimCycle = ts.get_k_data(code, ktype=primCycle)
        primCloses = dataprimCycle['close'].values
        primdates = dataprimCycle['date'].values
        primlows = dataprimCycle['low'].values

        primmacd = pd.Series(ta.cal_macd(primdates, primCloses))
        primmacd, primdif, primdea = DP.get_macd_list(primmacd)

        divStatus = ta.macd_in_bulldivergence(dates,primmacd)

        divscore = divStatus['div']
        macdscore = divStatus['macd']
        period = divStatus['period']

        if(divscore != 0):

            print(code, name,divscore,macdscore,period)
            absdis, perdis, maprice = ta.curdistosma(closes,20)
            curATR = ta.last_atr(dates, closes, highs,lows)

            ATRWZ = absdis/curATR
            curClose = closes[-1]
            ATRRatio = curATR /curClose

            primImpScore = FBD.ImpluseScore(primdates, primCloses)
            tradeImpScore = FBD.ImpluseScore(dates, closes)
            primdivStatus = ta.macd_in_bulldivergence_signal(primdates,primmacd)

            primdivscore = primdivStatus['div']

            if(primdivscore != 0):
                primdivscore = 1

            difdeadivscore = 0
            if(ta.in_loose_bulldivergence(dif,period)):
                difdeadivscore += 1
            if(ta.in_loose_bulldivergence(dea,period)):
                difdeadivscore += 1

            totalscore = primImpScore + tradeImpScore + primdivscore+divscore+difdeadivscore+macdscore

            curATR = round(curATR,2)
            ATRRatio = round(ATRRatio*100,2)


            ATRWZ = round(ATRWZ,2)


            maprice = round(maprice,2)
            colNames = ['code', 'name', 'period', 'curclose', 'sma', 'ATR', 'ATRRatio', 'ATRWZ','primImpScore',
                        'tradeImpScore', 'primdivscore', 'divscore', 'difdeascore', 'macdscore', 'totalscore']
            s = Series([code,name,period,curClose,maprice,curATR,ATRRatio,ATRWZ,primImpScore,tradeImpScore,
                        primdivscore,divscore,difdeadivscore,macdscore,totalscore],index=colNames)

            dfSelected = dfSelected.append(s,ignore_index=True)
    dfSelected = dfSelected.sort_values(by='totalscore',ascending=False)
    dfSelected = pd.DataFrame(dfSelected.values,columns=dfSelected.columns)

    DI.Write_DF_T0_Excel(filepath,dfSelected,'selected')

def main():
    while(True):
        dataset = 'etf'

        tradeCycle ='D'

        #batch_vectorized_smabreak_divergence(dataset,tradeCycle)
        batch_upcrossafter_divergence(dataset, tradeCycle)
        time.sleep(300)

if __name__ == "__main__":
    main()