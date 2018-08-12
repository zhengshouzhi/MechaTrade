# -*- coding: utf-8 -*-
from Analyze import DataProcess as DP
import pandas as pd
import DataInter as DI

def batch_etf(etflist,cyclelist):
    stragegyname = 'etfMonitor'
    dataset = 'etfs'
    tradeCycle = ''
    filepath = DP.get_stragegy_filepath(stragegyname,dataset,tradeCycle)

    colNames = ['code', 'tradeCycle', 'curclose', 'sma', 'ATR', 'ATRRatio', 'ATRWZ',
                'ImpLight', 'upchannel', 'downchannel', 'valueWZ', 'rewardratio']
    df = pd.DataFrame([],columns=colNames)
    for etf in etflist:
        for cycle in cyclelist:
            s = DP.get_common_parameters(etf,cycle)
            df = df.append(s,ignore_index=True)
    DI.Write_DF_T0_Excel(filepath,df,'etf')
    return df


def main():
    etflist = ['510050', '510300', '510500', '159915']
    cyclelist = ['W', 'D', '60', '15']
    df = batch_etf(etflist,cyclelist)

if __name__ == "__main__":
    main()

