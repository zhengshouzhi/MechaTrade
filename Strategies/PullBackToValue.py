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


StrategyName = 'InValueZoneDiv'
import time




def batch_invaluezone_divergence(dataset ='hs300',tradeCycle = 'D',recent = 5):
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
        if(not ta.invaluezone(closes,10,20)):
            continue


        macddiclist = ta.cal_macd(dates,closes)
        macd,dif,dea = DP.get_macd_list(macddiclist)

        if(min(macd[-3:])>0):
            continue

        divStatus = ta.macd_in_bulldivergence(dates,macd)

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


            primCycle = GetPrimaryCycle(tradeCycle)
            dataprimCycle = ts.get_k_data(code,ktype=primCycle)
            primCloses = dataprimCycle['close'].values
            primdates = dataprimCycle['date'].values
            primlows = dataprimCycle['low'].values

            primImpScore = FBD.ImpluseScore(primdates,primCloses)
            tradeImpScore = FBD.ImpluseScore(dates,closes)


            primmacd = pd.Series(ta.cal_macd(primdates, primCloses))
            primmacd,primdif,primdea = DP.get_macd_list(primmacd)



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

        batch_invaluezone_divergence(dataset, tradeCycle)

        time.sleep(300)


if __name__ == "__main__":
    main()