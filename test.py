# -*- coding: utf-8 -*-
import tushare as ts
from Analyze import Technical as ta
from numpy import std
from pandas import DataFrame,Series
import DataInter as DI
import os
from Analyze import Vectorized
import pandas as pd
from Analyze import DataProcess as DP
from Analyze import Statistical
import Strategies.False_Breakout_Divergence as FBD
from BackTest import Performance
import datetime


def sz50Daily():
    codelist = DI.get_stockcode_list('sz50')
    colNames = ['stockcode','smadir','uppenetrationCounter', 'downpenetrationCounter'
        ,'macddir','bandratio','upband','lowband','value_re']
    filterdf = DataFrame([],columns=colNames)
    filepath = os.path.join(os.getcwd(),'data','list')

    for stockcode in codelist['code']:

        df = ts.get_k_data(stockcode, ktype='D')

        dates = df['date'].values
        closes = df['close'].values
        lows = df['low'].values
        highs = df['high'].values

        smadir = ta.SMA_Direction(dates,closes)

        macddir = ta.MACD_Direction(dates,closes)

        uppenetrationCounter, downpenetrationCounter, bandratio, upband, lowband\
            = ta.envelop_ratio(dates,highs,lows,closes)
        #print(stockcode,uppenetrationCounter, downpenetrationCounter, bandratio, upband, lowband)

        value_re = ta.SMAValueZone_GX(dates,closes)

        s = Series([stockcode,smadir,uppenetrationCounter, downpenetrationCounter,
                    macddir,bandratio,upband,lowband,value_re],index=colNames)
        filterdf = filterdf.append(s,ignore_index=True)


    filterdf.to_csv(filepath+'.csv')


def stockDaily():
    stockcode = '600000'
    df = ts.get_k_data(stockcode, ktype='D')

    #df = df[-100:]
    dates = df['date'].values
    closes = df['close'].values
    lows = df['low'].values
    highs = df['high'].values


    #uppenetrationCounter, downpenetrationCounter, bandratio, upband, lowband = \
    #    ta.envelop_ratio(dates, highs, lows,closes)
    #print(stockcode,uppenetrationCounter, downpenetrationCounter, bandratio, upband, lowband)




def main():
    start_date = datetime.datetime(2000, 1, 1)
    end_date = datetime.datetime(2014, 1, 1)
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]
    print(start_date,end_date)
    data = ts.get_k_data('510300', index=False, start=start_date, end=end_date)
    print(data.head())
    '''
    dataset = 'etf'
    tradeCycle = 'D'
    StrategyName = 'SMABreakDiv'

    RootDir = os.path.join(os.getcwd(), 'data', 'Vectorized', StrategyName)
    filename = dataset + 'whole' + StrategyName + '.xls'
    filepath = os.path.join(RootDir, filename)
    df = pd.read_excel(filepath,'selected')
    df = Performance.smaexit(df,20,'D')
    print(df)

    #sz50Daily()
    #stockDaily()
    #codelist = DI.get_stockcode_list('')
    from Analyze import StockSelectiion
    #DI.get_stock_basics()
    #DI.get_concept_classification()
    #codelist = DI.get_stockcode_list('zz500')
    #codelist = codelist['code'].values
    #setbasics = DI.get_stockset_basics(codelist)
    #print(setbasics)
    #codelist = DI.get_stockcode_list('longtou')
    #print(codelist)

    dfdata = ts.get_k_data(code = '002411')

    dates = dfdata['date'].values
    closes = dfdata['close'].values

    macddiclist = ta.cal_macd(dates, closes)

    macd, dif, dea = DP.get_macd_list(macddiclist)
    print(len(macd))
    peaktrough = ta.get_macdpeaktrough(dates,macd)
    print(peaktrough)
    
    codelist = DI.get_stockcode_list('longtou')


    totalrows = len(codelist)

    for i in range(totalrows):

        code = codelist.loc[i, 'code']
        print(code,type(code))
        code = DP.codeType(code)
        print(code)
        name = codelist.loc[i, 'name']
        print(name)
        if (DI.is_tingpai(code)):
            print(name +"is tingpai")
            continue
             code = '601336'
    tradeCycle = 'D'
    dfdata = ts.get_k_data(code, ktype=tradeCycle)


    dates = dfdata['date'].values
    closes = dfdata['close'].values
    highs = dfdata['high'].values
    lows = dfdata['low'].values

    macddiclist = ta.cal_macd(dates, closes)
    macd, dif, dea = DP.get_macd_list(macddiclist)
    macdpeaktrough = ta.get_macdpeaktrough(dates, macd,50)
    print(macdpeaktrough)

    
    data = ts.get_k_data('600111')
    closes = data['close']
    periods = [5,10,20,30,60]
    spear = ta.smaspearmanr(closes,periods)
    print(spear)
    '''
    # Create a Gometric Brownian Motion, Mean-Reverting and Trending Series




if __name__ == "__main__":
    main()
