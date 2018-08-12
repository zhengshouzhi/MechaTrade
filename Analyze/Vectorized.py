# -*- coding: utf-8 -*-
import os
import tushare as ts
from Analyze import Technical as ta
from Strategies import TripleScreen as trpscr
from pandas import DataFrame,Series
from Analyze import DataProcess as DP



DataRoot = os.path.join(os.pardir,'Data','Vectorized')
smaperiod = 20


def VecCycleIndicators(stockcode = None,Cycle = 'D'):
    dftotal = ts.get_k_data(stockcode, ktype=Cycle)
    totalrows = len(dftotal)
    if(totalrows <100):
        print('Insufficiennt Data for Analyze'
        )
        return None
    startIndex = 0

    colNames = ['date',Cycle+'-smadir',Cycle+'-macddir',Cycle+'-light',Cycle+'-bandratio',
                Cycle+'-upband',Cycle+'-lowband',Cycle+'-valuerel',Cycle+'-rsi']
    dfIndicator = DataFrame([],columns=colNames)

    while(startIndex + 100 <= totalrows):
        print(startIndex)
        df = dftotal[:startIndex + 100]
        dates = df['date'].values
        closes = df['close'].values
        lows = df['low'].values
        highs = df['high'].values

        date = dates[-1]

        smadir = ta.SMA_Direction(dates, closes)
        macddir = ta.MACD_Direction(dates, closes)
        lightcolor = trpscr.ImpluseLight(smadir,macddir)
        rsi = ta.get_cur_rsi(dates,closes)

        uppenetrationCounter, downpenetrationCounter, bandratio, upband, lowband \
            = ta.envelop_ratio(dates, highs, lows, closes)
        value_re = ta.SMAValueZone_GX(dates, closes)

        s = Series([date,smadir,macddir,lightcolor,bandratio,upband,lowband,value_re,rsi],index = colNames)
        dfIndicator = dfIndicator.append(s,ignore_index=True)
        startIndex += 1

    FileName = stockcode + Cycle +'.csv'
    FilePath = os.path.join(DataRoot,FileName)
    dfIndicator.to_csv(FilePath)
    return dfIndicator




def TripleScreenAnalyze(stockcode = None,tradeCycle = 'D'):

    dftrade = VecCycleIndicators(stockcode,tradeCycle)
    primaryCycle = trpscr.GetPrimaryCycle(tradeCycle)
    dfprimary = VecCycleIndicators(stockcode,primaryCycle)

    colNames = [ primaryCycle + '-smadir', primaryCycle + '-macddir', primaryCycle + '-light',
                primaryCycle + '-bandratio', primaryCycle + '-upband', primaryCycle + '-lowband',
                primaryCycle + '-valuerel',primaryCycle +'-rsi']

    for i in range(len(dftrade)):
        date = dftrade.loc[i,'date']
        priIndex = DP.GetDateIndex(dfprimary,date)
        if(priIndex is None):
            break
        for colName in colNames:
            dftrade.loc[i,colName]  = dfprimary.loc[priIndex,colName]
        #dftrade.loc[i,'w-date']  = dfprimary.loc[priIndex,'date']

    FileName = stockcode + tradeCycle + primaryCycle + '.csv'
    FilePath = os.path.join(DataRoot, FileName)
    dftrade.to_csv(FilePath)


def main():
    stockcode = '510050'
    tradeCycle = 'D'
    TripleScreenAnalyze(stockcode,tradeCycle)







if __name__ == "__main__":
    main()











