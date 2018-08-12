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
from BackTest import Performance
import time
import numpy as np

StrategyName = 'FalseBreakDiv'




def reachNewLow(pricelist,recent=3,period=60,cycle = 'D'):
    '''
    :param pricelist:价格list
    :param recent:近recent天
    :param period:时间段
    :return: 近recent天是否达到period天的最低点
    '''
    if(cycle in ['30','15','60']):
        thresh = 0.005
    elif(cycle in ['D']):
        thresh = 0.015
    elif(cycle in ['W']):
        thresh = 0.03
    recentlow = min(pricelist[-recent:])
    periodlow = min(pricelist[-period:])

    if(recentlow == periodlow or recentlow < periodlow * (1+thresh)):
        return True
    else:
        return False






def isPriceNewLow(lows,recent =3,period = 20,cycle = 'D'):
    '''
    :param lows:每日价格低点的list
    :param recent:
    :param period:
    :return:
    '''
    ispricenewLow = reachNewLow(pricelist=lows, recent=recent, period=period,cycle = cycle)
    if (not ispricenewLow):
        return False
    else:
        return True


def ImpluseScore(dates,closes):
    '''
    :param dates:日期
    :param closes: 收盘价
    :return: 脉冲评分：红0分，绿1分，蓝2分
    '''
    smadir = ta.SMA_Direction(dates, closes)
    macddir = ta.MACD_Direction(dates, closes)
    lightcolor = ImpluseLight(smadir, macddir)
    if (lightcolor == 'Red'):
        score = 0
    elif(lightcolor == 'green'):
        score = 1
    else:
        score = 2
    return score

def value_score(dates,closes):
    '''
    :param dates: 价值评分
    :param closes:
    :return: 在价值区域上0分，中1分，下两分
    '''
    value_re = ta.SMAValueZone_GX(dates, closes)
    if(value_re == 'in'):
        score = 1
    elif(value_re == 'above'):
        score = 0
    else:
        score = 2
    return score


def isfalsebreakout(closes,lows,highs,period=30):
    '''
    :param dates:
    :param closes:
    :param lows:
    :param highs:
    :param recent:
    :param period:
    :return:是否falsbreak,也即当前close是否已经收复前低。
    '''
    highs = highs[-period:]
    lows = lows[-period:]

    prelow = DP.get_pre_low(highs, lows)
    if(prelow is None):
        return False
    curclose = closes[-1]
    curhigh = highs[-1]
    if(curclose > prelow):
        return True
    else:
        return False

def is_above_daysma(code,period=60):
    data = ts.get_k_data(code,ktype='D')
    closes = data['close'].values
    sma = sum(closes[-period:])/period
    if(closes[-1] > sma):
        return True
    else:
        return False


def batch_falsebreakout_divergence(dataset ='hs300',tradeCycle = 'D',recent = 3):
    lasttradetimestr = DP.get_last_trade_time('D')
    '''
    colNames = ['code', 'time', 'period', 'curclose', 'sma', 'ATR', 'ATRRatio', 'rewardratio',
                'riskratio', 'targetprice', 'cutshort', 'ATRWZ', 'rewardrisk', 'primImpScore',
                'tradeImpScore', 'valuescore', 'primdivscore', 'divscore', 'difdeascore', 'macdscore',
                'totalscore','targetprice1','targetprice2']
    '''
    colNames = ['code', 'name', 'time', 'period', 'curclose', 'sma', 'ATR', 'ATRRatio', 'rewardratio',
                'riskratio', 'targetprice', 'cutshort', 'ATRWZ', 'rewardrisk', 'primImpScore',
                'tradeImpScore', 'valuescore', 'primdivscore', 'divscore', 'difdeascore', 'macdscore',
                'totalscore', 'targetprice2', 'targetprice3']
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

        macddiclist = ta.cal_macd(dates,closes)
        macd,dif,dea = DP.get_macd_list(macddiclist)

        if(not(macd[-2]<0 and macd[-2]<macd[-1] and macd[-2]<macd[-3])):
            continue

        if(code in dfSelected['code'].values):
            continue

        divStatus = ta.macd_in_bulldivergence_signal(dates,macd)

        divscore = divStatus['div']
        macdscore = divStatus['macd']
        period = divStatus['period']

        if(divscore != 0 and isPriceNewLow(lows,recent,period)):


            absdis, perdis, maprice = ta.curdistosma(closes,20)
            curATR = ta.last_atr(dates, closes, highs,lows)
            targetprice = maprice + 2*curATR
            prelow = min(lows[-recent:])  #因此此处要求近recent天创period天新低

            ATRWZ = absdis/curATR
            curClose = closes[-1]
            #cutshort = min(prelow, curClose - curATR)
            cutshort = prelow
            ATRRatio = curATR /curClose
            #rewardratio = (targetprice-curClose)*100/curClose
            riskratio = (curClose-cutshort)*100/curClose
            #rewardrisk = (targetprice-curClose)/(curClose-cutshort)

            primCycle = GetPrimaryCycle(tradeCycle)
            dataprimCycle = ts.get_k_data(code,ktype=primCycle)
            primCloses = dataprimCycle['close'].values
            primdates = dataprimCycle['date'].values
            primlows = dataprimCycle['low'].values

            primImpScore = ImpluseScore(primdates,primCloses)
            tradeImpScore = ImpluseScore(dates,closes)
            valuescore = value_score(dates,closes)

            primmacd = pd.Series(ta.cal_macd(primdates, primCloses))
            primmacd,primdif,primdea = DP.get_macd_list(primmacd)

            isPrimNewLow = isPriceNewLow(primlows,recent,30)

            primdivStatus = ta.macd_in_bulldivergence_signal(primdates,primmacd)

            primdivscore = primdivStatus['div']

            if(primdivscore != 0 and isPrimNewLow != 0):
                primdivscore = 2
            elif(primdivscore != 0):
                primdivscore = 1

            difdeadivscore = 0
            if(ta.in_loose_bulldivergence(dif,period)):
                difdeadivscore += 1
            if(ta.in_loose_bulldivergence(dea,period)):
                difdeadivscore += 1

            totalscore = primImpScore + tradeImpScore + valuescore + primdivscore+divscore+difdeadivscore+macdscore

            curATR = round(curATR,4)
            targetprice2 = curClose + 2 * curATR
            targetprice3 = np.max(closes[-period:])

            target = np.min([float(targetprice),float(targetprice2),float(targetprice3)])
            rewardratio = (target - curClose) * 100 / curClose

            rewardrisk = (target - curClose) / (curClose - cutshort)

            ATRRatio = round(ATRRatio*100,3)
            rewardratio = round(rewardratio,3)
            riskratio = round(riskratio,3)
            ATRWZ = round(ATRWZ,3)
            rewardrisk = round(rewardrisk,3)
            targetprice = round(targetprice,3)
            maprice = round(maprice,3)
            cutshort = round(cutshort,3)
            import datetime
            curtime = datetime.datetime.now()

            selectedcolNames = ['ATR', 'ATRRatio', 'code', 'name', 'time', 'curclose', 'cutshort', 'rewardratio',
                                'riskratio', 'rewardrisk','sma', 'targetprice', 'targetprice2', 'targetprice3']

            print(curATR,ATRRatio,code,tradeCycle,name,curtime,curClose,cutshort,rewardratio,riskratio,rewardrisk,maprice,
                  targetprice,targetprice2,targetprice3)

            s = Series([code,name,curtime,period,curClose,maprice,curATR,ATRRatio,rewardratio,riskratio,
                        targetprice,cutshort,ATRWZ,rewardrisk,primImpScore,tradeImpScore,
                        valuescore,primdivscore,divscore,difdeadivscore,macdscore,totalscore,targetprice2,targetprice3],index=colNames)
            dfSelected = dfSelected.append(s,ignore_index=True)
            dfSelected = dfSelected[selectedcolNames]
    dfSelected = dfSelected.sort_values(by='time',ascending=False)
    dfSelected = pd.DataFrame(dfSelected.values,columns=dfSelected.columns)

    if(not os.path.exists(filepath)):
        DI.Write_DF_T0_Excel(filepath, dfSelected, 'selected')
    else:
        dftotal = DI.Get_TrdData_FromExcel(filepath,'selected')
        dftotal = pd.concat([dftotal,dfSelected])
        DI.Write_DF_T0_Excel(filepath,dftotal,'selected')


def vectorized_falsebreakout_divergence(code ='510300',tradeCycle = 'D',recent = 5):
    colNames = ['code', 'time', 'period', 'curclose', 'sma', 'ATR', 'ATRRatio', 'rewardratio',
                'riskratio', 'targetprice', 'cutshort', 'ATRWZ', 'rewardrisk', 'primImpScore',
                'tradeImpScore', 'valuescore', 'primdivscore', 'divscore', 'difdeascore', 'macdscore',
                'totalscore','targetprice1','targetprice2']

    filename = StrategyName +  '-' + code + '-' + tradeCycle
    dfSelected = pd.DataFrame([], columns=colNames)
    RootDir = os.path.join(os.pardir, 'data', 'Vectorized')
    DP.mkdir(RootDir)
    filepath = os.path.join(RootDir,filename+'.xls')

    code = DP.codeType(code)

    dfdata = ts.get_k_data(code,start = '2000-01-01',ktype=tradeCycle)#start = '2016-01-01',
    if(len(dfdata)<120):#剔除交易时间少于120天的个股
        print('Not Enough data for decision making.')

    totaldates = dfdata['date'].values
    totalcloses = dfdata['close'].values
    totalhighs = dfdata['high'].values
    totallows = dfdata['low'].values

    macddiclist = ta.cal_macd(totaldates,totalcloses)
    totalmacd,totaldif,totaldea = DP.get_macd_list(macddiclist)
    i = 120


    while i < len(totalcloses):
        closes = totalcloses[:i]
        highs = totalhighs[:i]
        lows = totallows[:i]
        macd = totalmacd[:i]
        dif = totaldif[:i]
        dea = totaldea[:i]

        dates = totaldates[:i]

        if( macd[-1] < macd[-2] or macd[-3] < macd[-2]):#macd[-1]> 0 这个条件由于without right shoulder删除
            i = i + 1
            continue

        divStatus = ta.macd_in_bulldivergence_signal(dates, macd)

        divscore = divStatus['div']
        macdscore = divStatus['macd']
        period = divStatus['period']

        if (divscore != 0 and isPriceNewLow(lows, recent, period,tradeCycle)):
            date = dates[-1]

            absdis, perdis, maprice = ta.curdistosma(closes, 20)
            curATR = ta.last_atr(dates, closes, highs, lows)
            targetprice = maprice + 2 * curATR  #应该是前高更合理

            prelow = min(lows[-recent:])  # 因此此处要求近recent天创period天新低
            cutshort = prelow
            ATRWZ = absdis / curATR
            curClose = closes[-1]
            targetprice2 = curClose + 2 * curATR
            targetprice3 = np.max(closes[-period:])
            ATRRatio = curATR / curClose
            rewardratio = (targetprice - curClose) * 100 / curClose
            riskratio = (curClose - cutshort) * 100 / curClose
            rewardrisk = (targetprice - curClose) / (curClose - cutshort)

            primCycle = GetPrimaryCycle(tradeCycle)
            dataprimCycle = ts.get_k_data(code, ktype=primCycle)
            primCloses = dataprimCycle['close'].values
            primdates = dataprimCycle['date'].values
            primlows = dataprimCycle['low'].values

            primImpScore = ImpluseScore(primdates, primCloses)
            tradeImpScore = ImpluseScore(dates, closes)
            valuescore = value_score(dates, closes)

            primmacd = pd.Series(ta.cal_macd(primdates, primCloses))
            primmacd, primdif, primdea = DP.get_macd_list(primmacd)

            isPrimNewLow = isPriceNewLow(primlows, recent, 30)

            primdivStatus = ta.macd_in_bulldivergence_signal(primdates, primmacd)

            primdivscore = primdivStatus['div']

            if (primdivscore != 0 and isPrimNewLow != 0):
                primdivscore = 2
            elif (primdivscore != 0):
                primdivscore = 1

            difdeadivscore = 0
            if (ta.in_loose_bulldivergence(dif, period)):
                difdeadivscore += 1
            if (ta.in_loose_bulldivergence(dea, period)):
                difdeadivscore += 1

            totalscore = primImpScore + tradeImpScore + valuescore + primdivscore + divscore + difdeadivscore + macdscore

            curATR = round(curATR,2)
            ATRRatio = round(ATRRatio*100,2)
            rewardratio = round(rewardratio,2)
            riskratio = round(riskratio,2)
            ATRWZ = round(ATRWZ,2)
            rewardrisk = round(rewardrisk,2)
            targetprice = round(targetprice,2)
            maprice = round(maprice,2)
            s = Series([code,date,period,curClose,maprice,curATR,ATRRatio,rewardratio,riskratio,
                        targetprice,cutshort,ATRWZ,rewardrisk,primImpScore,tradeImpScore,
                        valuescore,primdivscore,divscore,difdeadivscore,macdscore,totalscore,targetprice2,targetprice3],index=colNames)

            dfSelected = dfSelected.append(s,ignore_index=True)

        i += 1

    #dfSelected = dfSelected.sort_values(by='totalscore',ascending=False)
    dfSelected = pd.DataFrame(dfSelected.values,columns=dfSelected.columns)
    #dfSelected.to_csv(filepath)
    DI.Write_DF_T0_Excel(filepath,dfSelected,'selected')
    return dfSelected


def batch_vectorized_divergence(dataset = 'hs300',cycle = 'D'):
    colNames = ['code', 'time', 'period', 'curclose', 'sma', 'ATR', 'ATRRatio', 'rewardratio',
                'riskratio', 'targetprice', 'cutshort', 'ATRWZ', 'rewardrisk', 'primImpScore',
                'tradeImpScore', 'valuescore', 'primdivscore', 'divscore', 'difdeascore', 'macdscore',
                'totalscore','targetprice1','targetprice2']
    codelist = DI.get_stockcode_list(dataset)

    dfScreen = codelist[['code', 'name']]
    totalrows = len(dfScreen)
    dftotal = DataFrame([],columns=colNames)
    for i in range(totalrows):
        code = dfScreen.loc[i, 'code']
        print(code)
        code = DP.codeType(code)
        
        name = dfScreen.loc[i,'name']
        dfsub = vectorized_falsebreakout_divergence(code,cycle)
        dfsub['name'] = name
        dftotal = pd.concat([dftotal,dfsub])
    RootDir = os.path.join(os.pardir, 'data', 'Vectorized',StrategyName)
    if(not os.path.exists(RootDir)):
        DP.mkdir(RootDir)
    filename = dataset + 'whole'+cycle+'.xls'
    filepath = os.path.join(RootDir,filename)
    dftotal = dftotal.sort_values(by='time')
    dftotal = DataFrame(dftotal.values,columns=dftotal.columns)
    dftotal = Performance.vectorized_forward_return(dftotal,cycle)
    DI.Write_DF_T0_Excel(filepath, dftotal, 'selected')

def etffalsebreakmonitor():

    dataset = 'etf'
    for tradeCycle in ['D','60','30','W']:
        print('current Cycle is:'+ tradeCycle)
        batch_falsebreakout_divergence(dataset, tradeCycle)


def hs300falsebreakmonitor():

    dataset = 'hs300'
    for tradeCycle in ['D','W']:#'W', 'D', '60', '30','15'
        batch_falsebreakout_divergence(dataset, tradeCycle)


def Zz500falsebreakmonitor():
    dataset = 'zz500'
    for tradeCycle in ['W', 'D', '60', '30']:
        batch_falsebreakout_divergence(dataset, tradeCycle)

def false_break_divergence_execution():
    dataset = 'hs300'
    tradeCycle = 'D'
    batch_falsebreakout_divergence(dataset, tradeCycle)

def batch_vecttorized_divergence_execution():
    dataset = 'hs300'
    tradeCycle = 'D'
    batch_vectorized_divergence(dataset=dataset,cycle=tradeCycle)

def main():
    vectorized_falsebreakout_divergence(code='600688', tradeCycle='D')
    batch_vecttorized_divergence_execution()

    #etffalsebreakmonitor()
    #etffalsebreakmonitor()

    #false_break_divergence_execution()

    #stockcodelist = DI.get_stockcode_list(dataset=dataset,update=True)




    #
    #stockcode = '600111'
    #inDivergenceZone(stockcode,tradeCycle)
    #for cycle in ['W','D']:#,'30','15','5'
    #    vectorized_falsebreakout_divergence('510050',cycle)


if __name__ == "__main__":
    main()