# -*- coding: utf-8 -*-
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

import pprint
import statsmodels.tsa.stattools as sts
from pandas.stats.api import ols
import tushare as ts

def plot_price_series(df, ts1, ts2):
    months = mdates.MonthLocator() # every month

    fig, ax = plt.subplots()
    ax.plot(df.index, df[ts1], label=ts1)
    ax.plot(df.index, df[ts2], label=ts2)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime.datetime(2013, 1, 1), datetime.datetime(2017, 11, 30))
    ax.grid(True)
    fig.autofmt_xdate()
    plt.xlabel('Month/Year')
    plt.ylabel('Price ($)')
    plt.title('%s and %s Daily Prices' % (ts1, ts2))
    plt.legend()
    plt.show()

def plot_scatter_series(df, ts1, ts2):
    plt.xlabel('%s Price ($)' % ts1)
    plt.ylabel('%s Price ($)' % ts2)
    plt.title('%s and %s Price Scatterplot' % (ts1, ts2))
    plt.scatter(df[ts1], df[ts2])
    plt.show()

def plot_residuals(df):
    months = mdates.MonthLocator() # every month
    fig, ax = plt.subplots()
    ax.plot(df.index, df["res"], label="Residuals")
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1))
    ax.grid(True)
    fig.autofmt_xdate()
    plt.xlabel('Month/Year')
    plt.ylabel('Price ($)')
    plt.title('Residual Plot')
    plt.legend()
    plt.plot(df["res"])
    plt.show()

if __name__ == "__main__":
    begdate = '2013-01-01'
    enddate = '2017-11-30'
    ticker1 = '510050'
    ticker2 = 'hs300'
    sz50 = ts.get_k_data(ticker1,start=begdate,end=enddate)
    hs300 = ts.get_k_data(ticker2,start=begdate,end=enddate)
    sz50.index = sz50['date']
    hs300.index = hs300['date']
    df = pd.DataFrame(index=sz50['date'])
    df["sz50"] = sz50["close"]
    df["hs300"] = hs300["close"]

    # Plot the two time series
    #plot_scatter_series(df, "sz50", "hs300")

    # Calculate optimal hedge ratio "beta"
    res = ols(y=df['hs300'], x = df["sz50"])
    beta_hr = res.beta.x
    # Calculate the residuals of the linear combination
    df["res"] = df["hs300"] - beta_hr * df["sz50"]
    # Plot the residuals
    #plot_residuals(df)
    # Calculate and output the CADF test on the residuals
    cadf = sts.adfuller(df["res"])
    pprint.pprint(cadf)