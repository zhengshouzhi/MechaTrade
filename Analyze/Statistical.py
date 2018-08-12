# -*- coding: utf-8 -*-
import scipy.stats as scs  # 科学计算
import numpy as np
import matplotlib.pyplot as plt  # 绘图
import DataInter as DI
from Analyze import DataProcess as DP
import tushare as ts
from pandas import DataFrame,Series
# Import the Time Series library
from statsmodels.tsa import stattools
from numpy import cumsum, log, polyfit, sqrt, std, subtract
from numpy.random import randn
import statsmodels.api as sm
import pandas as pd


#用上述结果进行正式的正态性检验

def normality_tests(arr):
    '''
    Tests for normality distribution of given data set.
    normality_tests函数组合了3中不同的统计学测试：
    偏斜度测试（Skewtest）
    测试样本数据的偏斜度是否“正态”（也就是值足够接近0）
    峰度测试（kurtosistest）与上一种测试类似，测试样本数据的峰度是否“正态”（同样是值足够接近0）
    正态性测试（normaltest）
    组合其他两种测试方法，检验正态性
    '''
    print("Skew of data set  %14.3f" % scs.skew(arr))
    print("Skew test p-value %14.3f" % scs.skewtest(arr)[1])
    print("Kurt of data set  %14.3f" % scs.kurtosis(arr))
    print("Kurt test p-value %14.3f" % scs.kurtosistest(arr)[1])
    print("Norm test p-value %14.3f" % scs.normaltest(arr)[1])

def print_statistics(array):
    sta = scs.describe(array)
    print("%14s %15s" % ('statistic', 'value'))
    print(30 * "-")
    print("%14s %15.5f" % ('size', sta[0]))
    print("%14s %15.5f" % ('min', sta[1][0]))
    print("%14s %15.5f" % ('max', sta[1][1]))
    print("%14s %15.5f" % ('mean', sta[2]))
    print("%14s %15.5f" % ('std', np.sqrt(sta[3])))
    print("%14s %15.5f" % ('skew', sta[4]))
    print("%14s %15.5f" % ('kurtosis', sta[5]))

def netvalue_plot(dfport):
    (dfport / dfport.ix[0] * 100).plot(figsize=(8, 6))
    plt.show()

def position_in_period(closes):
    maxprice = max(closes)
    minprice = min(closes)
    curprice = closes[-1]
    position = (curprice-minprice)*100/(maxprice-minprice)
    position = position.round(2)
    curup = (curprice-minprice)*100/minprice
    curup = curup.round(2)
    curdown = (curprice-maxprice)*100/maxprice
    curdown = curdown.round(2)
    return (position,curup,curdown)

def batch_position(codelist,period = 240,value = 'position',Cycle = 'D'):
    colNames = ['code','name','position','curup','curdown']
    dfPosition = DataFrame([],columns=colNames)
    index_date = DP.get_last_trade_time()

    for code,name in zip(codelist['code'],codelist['name']):
        code = DP.codeType(code)
        print(code)
        if(DI.is_tingpai(code)):
            continue
        df = ts.get_k_data(code,ktype=Cycle)
        if(len(df)== 0):
            continue
        closes = df['close'].values
        last_date = df.loc[len(df) - 1, 'date']
        if(len(df)<period or last_date != index_date):
            continue

        closes = closes[-period:]

        position, curup, curdown = position_in_period(closes)
        s = Series([code,name,position,curup,curdown],index=colNames)
        dfPosition = dfPosition.append(s,ignore_index=True)
    dfPosition = dfPosition.sort_values(by=value,ascending=True)
    dfPosition = DataFrame(dfPosition.values,columns=dfPosition.columns)
    return dfPosition

def adftest(stockcode,begdate,enddate):
    '''
    example result (0.049177575166452235,
    0.96241494632563063,
    1,
    3771,
    {’1%’: -3.4320852842548395,
    ’10%’: -2.5671781529820348,
    ’5%’: -2.8623067530084247},
    19576.116041473877)
    Since the calculated value of the test statistic is larger than any of the critical values at the 1,
    5 or 10 percent levels, we cannot reject the null hypothesis of
     = 0 and thus we are unlikely to
    have found a mean reverting time series. This is in line with our tuition as most equities behave
    akin to Geometric Brownian Motion (GBM), i.e. a random walk.
    :param stockcode:
    :return:
    '''
    data = ts.get_k_data(stockcode,start=begdate,end=enddate)
    ret = DP.closetoret(data['close'])
    resultret = stattools.adfuller(ret)
    resultclose = stattools.adfuller(data['close'])
    print('return',resultret)
    print('close',resultclose)
    return resultret,resultclose


def hurst(ts):
    '''
    # Create a Gometric Brownian Motion, Mean-Reverting and Trending Series
    gbm = log(cumsum(randn(100000)) + 1000)
    mr = log(randn(100000) + 1000)
    tr = log(cumsum(randn(100000) + 1) + 1000)

    # Output the Hurst Exponent for each of the above series
    # and the price of Amazon (the Adjusted Close price) for
    # the ADF test given above in the article
    print("Hurst(GBM): %s" % hurst(gbm))
    print("Hurst(MR): %s" % hurst(mr))
    print("Hurst(TR): %s" % hurst(tr))
    MaoTai = ts.get_k_data('600519')
    # Assuming you have run the above code to obtain ’amzn’!
    print("Hurst(MaoTai): %s" % hurst(MaoTai['close']))

    '''

    """Returns the Hurst Exponent of the time series vector ts"""
    # Create the range of lag values
    lags = range(2, 100)
    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)
    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0


def olsfit(ticker,bench,begdate,enddate):
    tickerdata = ts.get_k_data(ticker,start=begdate,end=enddate)
    benchdata = ts.get_k_data(bench,start=begdate,end=enddate)

    y = DP.closetoret(tickerdata['close'])
    x = DP.closetoret(benchdata['close'])

    x = sm.add_constant(x)
    model = sm.OLS(y,x)
    results = model.fit()
    return results.summary()

def rollingbeta(ticker,bench,begdate,enddate,window =252):
    tickerdata = ts.get_k_data(ticker, start=begdate, end=enddate)
    benchdata = ts.get_k_data(bench, start=begdate, end=enddate)

    y0 = DP.closetoret(tickerdata['close'])
    x0 = DP.closetoret(benchdata['close'])
    y0 = pd.Series(y0)
    x0 = pd.Series(x0)
    model = pd.ols(y=y0,x=x0,window = window)
    model.beta.plot()
    plt.show()


def Var(ticker,begdate,enddate,nshares,ndays):
    x = ts.get_k_data(ticker,start=begdate,end=enddate)
    ret = DP.closetoret(x)
    position = nshares*x['close'][-1]
    VaR = position*std(ret)*sqrt(ndays)
    print("Holding=", position, "VaR=", round(VaR, 4), "in ", ndays, "Days")
    return VaR

def hurst(ts):
    '''
        # Create a Gometric Brownian Motion, Mean-Reverting and Trending Series
    gbm = log(cumsum(randn(100000)) + 1000)
    mr = log(randn(100000) + 1000)
    tr = log(cumsum(randn(100000) + 1) + 1000)

    # Output the Hurst Exponent for each of the above series
    # and the price of Amazon (the Adjusted Close price) for
    # the ADF test given above in the article
    print("Hurst(GBM): %s" % hurst(gbm))
    print("Hurst(MR): %s" % hurst(mr))
    print("Hurst(TR): %s" % hurst(tr))
    H < 0:5 - The time series is mean reverting
  H = 0:5 - The time series is a Geometric Brownian Motion
  H > 0:5 - The time series is trending
    maotai = ts.get_k_data('600519',start=begdate,end=enddate)
    # Assuming you have run the above code to obtain ’amzn’!
    print("Hurst(MaoTai): %s" % hurst(maotai['close']))
    tianshili = ts.get_k_data('600535',start=begdate,end=enddate)
    print("Hurst(TianShiLi): %s" % hurst(tianshili['close']))
    '''
    
    """Returns the Hurst Exponent of the time series vector ts"""
    # Create the range of lag values
    lags = range(2, 100)
    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)
    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0


def cadf_test(tickdict1,tickdict2,begdate,enddate):
    import datetime
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import pandas as pd

    import pprint
    import statsmodels.tsa.stattools as sts
    from pandas.stats.api import ols
    import tushare as ts
    print(begdate,enddate)
    ticker1 = tickdict1['code']
    ticker2 = tickdict2['code']
    symbol1 = tickdict1['symbo']
    symbol2 = tickdict2['symbo']
    print(ticker1,ticker2)
    df1 = ts.get_k_data(ticker1, start=begdate, end=enddate)
    df2 = ts.get_k_data(ticker2, start=begdate, end=enddate)
    df1.index = df1['date']
    df2.index = df2['date']
    df = pd.DataFrame(index=df1['date'])
    df[symbol1] = df1["close"]
    df[symbol2] = df2["close"]

    # Plot the two time series
    # plot_scatter_series(df, "sz50", "hs300")

    # Calculate optimal hedge ratio "beta"
    res = ols(y=df[symbol2], x=df[symbol1])
    beta_hr = res.beta.x
    # Calculate the residuals of the linear combination
    df["res"] = df[symbol2] - beta_hr * df[symbol1]
    # Plot the residuals
    # plot_residuals(df)
    # Calculate and output the CADF test on the residuals
    cadf = sts.adfuller(df["res"])
    pprint.pprint(cadf)
    return cadf

if __name__ == "__main__":
    begdate = '2013-01-01'
    enddate = '2017-11-30'
    #res = rollingbeta('159915','510050',begdate,enddate)
    tickdict1 = {}
    tickdict2 = {}
    tickdict1['code']  = '510050'
    tickdict1['symbo']  = 'sz50'
    tickdict2['code'] = '510300'
    tickdict2['symbo'] = 'hs300'
    cadf_test(tickdict1,tickdict2,begdate,enddate)













