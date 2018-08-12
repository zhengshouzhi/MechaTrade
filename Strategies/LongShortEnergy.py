# -*- coding: utf-8 -*-
import tushare as ts
from Analyze import Technical as ta
from pandas import Series,DataFrame
import numpy as np
import pandas as pd
import DataInter as DI
from Analyze import DataProcess as DP


primarycycle = 'W'
tradecycle = 'D'
dataset = 'hs300'
codelist = DI.get_stockcode_list(dataset)
#dfSelected = pd.DataFrame([],columns=colNames)
dfScreen = codelist[['code', 'name']]

def screener1():
    totalrows = len(dfScreen)
    for i in range(totalrows):

        code = dfScreen.loc[i,'code']
        code = DP.codeType(code)
        stockcode = code

        df_trade = ts.get_k_data(code = stockcode,ktype=tradecycle)


        totalrows = len(df_trade)
        dates = df_trade['date']
        closes = df_trade['close']
        lows = df_trade['low']

        sma5 = ta.cal_sma(dates,closes,5)
        sma5 = Series(sma5)

        macd = ta.cal_macd(dates,closes)
        macd = macd[len(macd)-len(sma5):]
        macd = Series(macd)

        sma5 = sma5[len(macd)-len(sma5):]
        sma5 = Series(sma5)

        df_trade = df_trade[len(df_trade)-len(sma5):]

        df_trade = DataFrame(df_trade.values,columns=df_trade.columns)
        df_trade['sma5'] = sma5
        df_trade['macd'] = macd

        totalrows = len(df_trade)
        i = 5
        while(i<totalrows):
            if(df_trade.loc[i,'close'] > df_trade.loc[i,'sma5']['sma5']
                and df_trade.loc[i-1,'close'] > df_trade.loc[i-1,'sma5']['sma5']
               and df_trade.loc[i-3,'close'] < df_trade.loc[i-3,'sma5']['sma5']
               and df_trade.loc[i,'macd']['macd'] > df_trade.loc[i-1,'macd']['macd']
               and df_trade.loc[i,'macd']['diff']<df_trade.loc[i,'macd']['dea']
               and df_trade.loc[i,'macd']['macd']>-0.003):
                date = df_trade.loc[i,'date'][:10]

                df_prim = ts.get_k_data(code=stockcode,ktype=primarycycle,start='2000-01-01',end=date)

                primcloses = df_prim['close'][-5:]

                primclose = primcloses.values[-1]
                primsma5 = np.average(primcloses)
                primdates = df_prim['date']
                primcloses = df_prim['close']
                primmacd = ta.cal_macd(dates,closes)
                primdiff = primmacd[len(primmacd)-1]['diff']
                primdea = primmacd[len(primmacd)-1]['dea']
                if(primclose>primsma5 and primdiff > primdea):
                    #print(df_trade.loc[i, 'date'])

                    curlows = lows[:i]
                    curdates = dates[:i]

                    difenxinglist = ta.get_pre_difenxing(curdates,curlows,4)
                    #print(difenxinglist)

                    if(len(difenxinglist)<4):
                        continue
                    # difenxinglist[0]['low'] < difenxinglist[1]['low'] and
                    else:
                        if(
                        difenxinglist[1]['low'] < difenxinglist[2]['low'] and
                         difenxinglist[2]['low'] < difenxinglist[3]['low']
                        ):
                            print(stockcode,df_trade.loc[i, 'date'])
            i += 1

def screener2 ():
    totalrows = len(dfScreen)
    for index in range(totalrows):

        code = dfScreen.loc[index,'code']
        code = DP.codeType(code)
        stockcode = code

        df_trade = ts.get_k_data(code = stockcode,ktype=tradecycle)

        dates = df_trade['date']
        closes = df_trade['close']
        lows = df_trade['low']

        sma5 = ta.cal_sma(dates,closes,5)
        sma5 = Series(sma5)

        macd = ta.cal_macd(dates,closes)
        macd = macd[len(macd)-len(sma5):]
        macd = Series(macd)

        sma5 = sma5[len(macd)-len(sma5):]
        sma5 = Series(sma5)

        df_trade = df_trade[len(df_trade)-len(sma5):]

        df_trade = DataFrame(df_trade.values,columns=df_trade.columns)
        df_trade['sma5'] = sma5
        df_trade['macd'] = macd

        totalrows = len(df_trade)
        i = 5
        while(i<totalrows):

            if(df_trade.loc[i,'close'] > df_trade.loc[i,'sma5']['sma5']
               and df_trade.loc[i-1,'close'] < df_trade.loc[i,'sma5']['sma5']

               and df_trade.loc[i,'macd']['diff']>df_trade.loc[i,'macd']['dea']
               ):
                j = i
                while(j>0):
                    if df_trade.loc[j,'macd']['diff']<df_trade.loc[j,'macd']['dea']:
                        break
                    j -= 1
                closesslice = closes[j:i]

                if(len(closesslice)<8):
                    i += 1
                    continue
                print(closesslice)
                k = np.argmax(closesslice)

                print('here')
                print(j,k,i)
                if(min(closesslice[j:k])<min(closesslice[k:i])):
                    date = df_trade.loc[i,'date'][:10]

                    df_prim = ts.get_k_data(code=stockcode,ktype=primarycycle,start='2000-01-01',end=date)

                    primcloses = df_prim['close'][-5:]

                    primclose = primcloses.values[-1]
                    primsma5 = np.average(primcloses)

                    primmacd = ta.cal_macd(dates,closes)
                    primdiff = primmacd[len(primmacd)-1]['diff']
                    primdea = primmacd[len(primmacd)-1]['dea']
                    if(primclose>primsma5 and primdiff > primdea):
                        #print(df_trade.loc[i, 'date'])

                        curlows = lows[:i]
                        curdates = dates[:i]

                        difenxinglist = ta.get_pre_difenxing(curdates,curlows,4)
                        #print(difenxinglist)

                        if(len(difenxinglist)<4):
                            continue
                        # difenxinglist[0]['low'] < difenxinglist[1]['low'] and
                        else:
                            if(
                            difenxinglist[1]['low'] < difenxinglist[2]['low'] and
                             difenxinglist[2]['low'] < difenxinglist[3]['low']
                            ):
                                print(stockcode,df_trade.loc[i, 'date'])
            i += 1

def main():
    screener2()

if __name__ == "__main__":

    main()






