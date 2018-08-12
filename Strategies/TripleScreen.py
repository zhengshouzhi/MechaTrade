# -*- coding: utf-8 -*-
import DataInter as DI
import Config
import os
from Analyze import DataProcess as DP
import tushare as ts
from Analyze import Technical as ta
from pandas import DataFrame, Series

def GetPrimaryCycle(tradeCycle = 'D'):
    '''
    :param tradeCycle: 交易周期
    :return: 上一周期
    '''
    if(tradeCycle == 'D'):
        primaryCyele = 'W'
    elif(tradeCycle in['30','60','15']):
        primaryCyele = 'D'
    elif(tradeCycle=='5'):
        primaryCyele = '30'
    if(tradeCycle =='W'):
        primaryCyele = 'D'
    if(tradeCycle =='5'):
        primaryCyele='30'

    return primaryCyele

def GetSubCycle(tradeCycle = 'D'):
    '''
    :param tradeCycle: 交易周期
    :return: 上一周期
    '''
    if(tradeCycle == 'D'):
        subCyele = '30'

    elif(tradeCycle=='W'):
        primaryCyele = 'D'

    return primaryCyele


def ImpluseLight(MADir,MACDDir):
    if(MADir == 'up' and (MACDDir =='belowup' or MACDDir =='aboveup' or MACDDir =='upcross')):
        LightColor = 'Green'
    elif(MADir =='down' and (MACDDir =='belowdown' or MACDDir == 'abovedown' or MACDDir =='downcross')):
        LightColor = 'Red'
    else:
        LightColor = 'Blue'
    return LightColor





def triplescreen(dataset = 'sz50',tradeCycle = 'D'):
    curdatestr = Config.curdatestr

    codelist = DI.get_stockcode_list(dataset)

    RootDir = os.path.join(os.pardir, 'data',curdatestr)
    DP.mkdir(RootDir)

    primaryCycle = GetPrimaryCycle(tradeCycle)

    dfScreen = codelist[['code','name']]


    for Cycle in [primaryCycle, tradeCycle]:
        totalrows = len(dfScreen)
        for i in range(totalrows):
            code = dfScreen.loc[i,'code']
            print(code)
            df = ts.get_k_data(code, ktype=Cycle)

            dates = df['date'].values
            closes = df['close'].values
            lows = df['low'].values
            highs = df['high'].values

            smadir = ta.SMA_Direction(dates, closes)
            macddir = ta.MACD_Direction(dates, closes)
            lightcolor = ImpluseLight(smadir, macddir)
            if(lightcolor == 'Red'):
                #dfScreen = dfScreen.drop(i)
                break
            rsi = ta.get_cur_rsi(dates, closes)

            uppenetrationCounter, downpenetrationCounter, bandratio, upband, lowband \
                = ta.envelop_ratio(dates, highs, lows, closes)
            value_re = ta.SMAValueZone_GX(dates, closes)


            dfScreen.loc[i,Cycle + '-smadir'] = smadir
            dfScreen.loc[i, Cycle + '-macddir'] = macddir
            dfScreen.loc[i, Cycle + '-light'] = lightcolor

            dfScreen.loc[i, Cycle + '-bandratio'] = round(bandratio,2)
            dfScreen.loc[i, Cycle + '-upband'] = round(upband,2)
            dfScreen.loc[i, Cycle + '-lowband'] = round(lowband,2)
            dfScreen.loc[i, Cycle + '-valuerel'] = value_re
            dfScreen.loc[i, Cycle + '-rsi'] = round(rsi,0)

        dfScreen = DataFrame(dfScreen.values,columns=dfScreen.columns)


    filename = dataset + '-'+ curdatestr + '-' + primaryCycle + '-' + tradeCycle
    filepath = os.path.join(RootDir,filename+'.csv')
    dfScreen.to_csv(filepath)

def main():
    dataset = 'sz50'
    tradeCycle = 'D'
    triplescreen(dataset,tradeCycle)








if __name__ == "__main__":
    main()



