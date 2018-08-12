# -*- coding: utf-8 -*-
import DataInter as DI
from Analyze import Statistical
import tushare as ts
import Analyze.DataProcess as DP
import Config
import os
import pandas as pd
from Analyze import Technical as ta
from Strategies import TripleScreen as Triple
import numpy as np


def get_stock_basic_parameters(code,Cycle = 'D',period = 480):
    '''
    :param code:股票代码
    :param Cycle: 分析周期
    :param period: 分析的时间周期
    :return:返回指标列表：
    ['EMADir','SMADir','MACDDir','SMALight','EMALight','valuerel','ATRWz','ATRRatio',
    'oneATR','twoATR','threeATR','moneATR','mtwoATR','mthreeATR','position','curup',
    'curdown']
    '''
    code = DP.codeType(code)
    print(code)
    dfdata = ts.get_k_data(code, ktype=Cycle)
    if (len(dfdata) < 60):
        return None
    closes = dfdata['close'].values
    dates = dfdata['date'].values
    EMADir = ta.EMA_Direction(dates, closes)
    SMADir = ta.SMA_Direction(dates, closes)
    MACDDir = ta.MACD_Direction(dates, closes)
    SMALight = Triple.ImpluseLight(SMADir, MACDDir)
    EMALight = Triple.ImpluseLight(EMADir, MACDDir)

    valuerel = ta.SMAValueZone_GX(dates, closes)

    highs = dfdata['high'].values
    lows = dfdata['low'].values
    curatr = ta.last_atr(dates, closes, highs, lows)
    absdis, perdis, maprice = ta.curdistosma(closes, 20)
    ATRWz = absdis / curatr
    ATRRatio = absdis / maprice
    oneATR = maprice + curatr
    twoATR = maprice + 2 * curatr
    threeATR = maprice + 3 * curatr
    moneATR = maprice - curatr
    mtwoATR = maprice - 2 * curatr
    mthreeATR = maprice - 3 * curatr

    if (len(closes) > period):
        closes = closes[-period:]
    position, curup, curdown = Statistical.position_in_period(closes)

    valuelist = [EMADir,SMADir,MACDDir,SMALight,EMALight,valuerel,ATRWz,ATRRatio,oneATR,twoATR,
                threeATR,moneATR,mtwoATR,mthreeATR,position,curup,curdown]
    namelist = ['EMADir','SMADir','MACDDir','SMALight','EMALight','valuerel','ATRWz','ATRRatio',
                'oneATR','twoATR','threeATR','moneATR','mtwoATR','mthreeATR','position','curup',
                'curdown']
    colnames =[]
    for ele in namelist:
        name = Cycle + '-' + ele
        colnames.append(name)
    s = pd.Series(valuelist,index=colnames)
    return s

def get_stockset_basic_position(stockset = 'sz50'):
    '''
    :param stockset:目前的属性为批数
    :return:将股票指数内各成分股的属性返回。
    '''
    stocksetname = stockset
    rootdir = Config.dataDir
    fileroot = os.path.join(rootdir, 'Applets', 'Index')
    filename = 'basic-position ' + stocksetname
    filepath = os.path.join(fileroot, filename + '.csv')
    if (os.path.exists(filepath)):
        dfstockset = pd.read_csv(filepath, encoding='gbk')
        return dfstockset
    codelist = DI.get_stockcode_list(stockset)

    dfstockset = DI.get_stockset_basics(codelist['code'].values)
    Cycles = ['W','D']
    for Cycle in Cycles:
        for i in range(len(dfstockset)):
            code = dfstockset.loc[i,'code']
            s = get_stock_basic_parameters(code,Cycle)
            if(s is None):
                continue
            for key in s.index:
                dfstockset.loc[i,key] = s[key]
    print(dfstockset)
    dfstockset.to_csv(filepath)
    return dfstockset

def get_indus_basic_position(industry = '铝'):
    '''
    :param industry:行业属性
    :return: 将行业内各成分股的属性返回。
    '''
    print(industry)
    industryprefix = 'ind'

    industryname = industryprefix + '-'+ str(industry)
    rootdir = Config.dataDir
    fileroot = os.path.join(rootdir, 'Applets', 'YouSheLV')
    filename = 'basic-position '+industryname
    filepath = os.path.join(fileroot, filename + '.csv')
    if(os.path.exists(filepath)):
        dfindustry = pd.read_csv(filepath, encoding='gbk')
        return dfindustry

    basics = ['code', 'name', 'industry', 'pe', 'pb']
    industrylist = []
    industrylist.append(industry)
    dfindustry = DI.get_industry_stocks(industrylist=industrylist, keylist=basics)

    period = 480
    Cycles = ['W', 'D']
    for Cycle in Cycles:
        for i in range(len(dfindustry)):
            code = dfindustry.loc[i, 'code']
            s = get_stock_basic_parameters(code, Cycle)
            if (s is None):
                continue
            for key in s.index:
                dfindustry.loc[i, key] = s[key]
    print(dfindustry)

    dfindustry.to_csv(filepath)

    return dfindustry

def basic_pos_statistics(dfindusbasic,feature):
    '''
    :param dfindusbasic:带有股票集内各成分股基本面和技术面信息的DataFrame
    :param feature: 对于股票集的特征
    :return:带有股票集统计描述的Series,特征如colName描述
    '''

    colNames = ['feature','avgPE','avgPB','WRed','WBlue','WGreen','WAbove','WIn','WBelow','DRed', 'DBlue',
                'DGreen', 'DAbove', 'DIn', 'DBelow', 'Wonetwotwo','Wtwotothree','Wzerotoone',
                'Wabovethree','Wmzerotoone','Wmabovethree','Wmonetotwo','Wmtwotothree',
                'DonetDotDo', 'DtDotothree', 'Dzerotoone', 'Dabovethree', 'Dmzerotoone',
                'Dmabovethree', 'DmonetotDo','DmtDotothree','WPosition','DPosition']

    s = dfindusbasic['pe']
    avgpe = sum(s)/sum(s!=0)
    avgpe = avgpe.round(2)
    s = dfindusbasic['pb']
    for key in s.index:
        if(s[key]<=0):
            s[key] = 0
    avgpb = sum(s)/sum(s>0)
    avgpb = avgpb.round(2)

    s = dfindusbasic['W-SMALight']
    WRed = int(sum(s=='Red'))
    WBlue = int(sum(s=='Blue'))
    WGreen = int(sum(s=='Green'))

    s = dfindusbasic['W-valuerel']
    WAbove = int(sum(s=='above'))
    WBelow = int(sum(s=='below'))
    WIn = int(sum(s=='in'))

    s = dfindusbasic['D-SMALight']
    DRed = int(sum(s == 'Red'))
    DBlue = int(sum(s == 'Blue'))
    DGreen = int(sum(s == 'Green'))

    s = dfindusbasic['D-valuerel']
    DAbove = int(sum(s == 'above'))
    DBelow = int(sum(s == 'below'))
    DIn = int(sum(s == 'in'))

    s = dfindusbasic['W-ATRWz']
    WATRCounter = ta.ATRCounter(s)
    Wonetwotwo = int(WATRCounter['onetotwo'])
    Wtwotothree = int(WATRCounter['twotothree'])
    Wzerotoone = int(WATRCounter['zerotoone'])
    Wabovethree = int(WATRCounter['abovethree'])
    Wmzerotoone = int(WATRCounter['mzerotoone'])
    Wmabovethree = int(WATRCounter['mabovethree'])
    Wmonetotwo = int(WATRCounter['monetotwo'])
    Wmtwotothree = int(WATRCounter['mtwotothree'])

    s = dfindusbasic['D-ATRWz']
    DATRCounter = ta.ATRCounter(s)
    DonetDotDo = int(DATRCounter['onetotwo'])
    DtDotothree = int(DATRCounter['twotothree'])
    Dzerotoone = int(DATRCounter['zerotoone'])
    Dabovethree = int(DATRCounter['abovethree'])
    Dmzerotoone = int(DATRCounter['mzerotoone'])
    Dmabovethree = int(DATRCounter['mabovethree'])
    DmonetotDo = int(DATRCounter['monetotwo'])
    DmtDotothree = int(DATRCounter['mtwotothree'])


    s = dfindusbasic['W-position']
    s = s.replace(np.nan,0)

    WPosition = sum(s)/len(s)
    WPosition = WPosition.round(2)

    s = dfindusbasic['D-position']
    s = s.replace(np.nan, 0)
    DPosition = sum(s)/len(s)
    DPosition = DPosition.round(2)

    values = [feature,avgpe,avgpb,WRed,WBlue,WGreen,WAbove,WIn,WBelow,DRed,DBlue,DGreen,DAbove,DIn,DBelow,
              Wonetwotwo,Wtwotothree,Wzerotoone,Wabovethree,Wmzerotoone,Wmabovethree,Wmonetotwo,
              Wmtwotothree,DonetDotDo,DtDotothree,Dzerotoone ,Dabovethree,Dmzerotoone,Dmabovethree,
              DmonetotDo,DmtDotothree,WPosition,DPosition
              ]

    colNames = ['feature','avgPE','avgPB','WRed','WBlue','WGreen','WAbove','WIn','WBelow','DRed', 'DBlue',
                'DGreen', 'DAbove', 'DIn', 'DBelow', 'Wonetwotwo','Wtwotothree','Wzerotoone',
                'Wabovethree','Wmzerotoone','Wmabovethree','Wmonetotwo','Wmtwotothree',
                'DonetDotDo', 'DtDotothree', 'Dzerotoone', 'Dabovethree', 'Dmzerotoone',
                'Dmabovethree', 'DmonetotDo','DmtDotothree','WPosition','DPosition']

    s = pd.Series(values,index = colNames)
    print(s)
    return s

def batah_stockset_analyze():
    stocksets = ['sz50','hs300','zz500','cyb','zxb']
    dfstocksetbasic = get_stockset_basic_position('sz50')
    s  = basic_pos_statistics(dfstocksetbasic,'sz50')
    dfallstockset = pd.DataFrame([],columns=s.index)

    for stockset in stocksets:
        print(stockset)
        dfstocksetbasic = get_stockset_basic_position(stockset)

        s = basic_pos_statistics(dfstocksetbasic, stockset)
        dfallstockset = dfallstockset.append(s, ignore_index=True)
        print(s)

    dataDir = Config.dataDir
    rootDir = os.path.join(dataDir, 'BatchStatistic')
    filename = 'dfullstockset'
    filepath = os.path.join(rootDir, filename + '.csv')
    dfallstockset.to_csv(filepath)




def batch_industry_analyze():
    #
    #    dfindusbasic = get_indus_basic_position(industry)
    #s = get_stock_basic_parameters('600519',Cycle='W')
    #print(s)
    #get_stockset_basic_position()

    dfindusbasic = get_indus_basic_position('铝')
    #print(dfindusbasic)
    s = basic_pos_statistics(dfindusbasic, '铝')
    print(type(s))
    dfallindustry = pd.DataFrame([],columns=s.index)
    allindustry = DI.get_all_industry()
    for industry in allindustry:

        dfindusbasic = get_indus_basic_position(industry)
        s = basic_pos_statistics(dfindusbasic,industry)
        dfallindustry = dfallindustry.append(s,ignore_index=True)
        print(s)

    dataDir = Config.dataDir
    rootDir = os.path.join(dataDir, 'BatchStatistic')
    filename = 'allindustry'
    filepath = os.path.join(rootDir,filename+'.csv')
    dfallindustry.to_csv(filepath)


def batch_stockset_selection(stockset = 'hs300'):
    rootDir = os.path.join(Config.dataDir,'Applets','Index')
    filename = 'basic-position ' + stockset
    filepath = os.path.join(rootDir,filename+'.csv')
    dfwholeset = pd.read_csv(filepath,encoding='gbk')
    dfnotred = pd.DataFrame([],columns=dfwholeset.columns)
    dflightcontradict = pd.DataFrame([],columns=dfwholeset.columns)
    dfoversold = pd.DataFrame([],columns=dfwholeset.columns)

    for i in range(len(dfwholeset)):
        weeksimlight = dfwholeset.loc[i,'W-SMALight']
        weekemalight = dfwholeset.loc[i,'W-EMALight']
        daysimlight = dfwholeset.loc[i, 'D-SMALight']
        dayemalight = dfwholeset.loc[i, 'D-EMALight']
        DayATR = dfwholeset.loc[i,'D-ATRWz']
        WeekATR = dfwholeset.loc[i,'W-ATRWz']
        s = dfwholeset.ix[i]
        if(weekemalight != 'Red' and weeksimlight != 'Red'
           and dayemalight !='Red' and daysimlight!='Red'):
            dfnotred = dfnotred.append(s,ignore_index=True)
            if (DayATR < -2 or WeekATR < -2):
                dfoversold = dfoversold.append(s, ignore_index=True)
        elif(((weekemalight == 'Red' or weeksimlight=='Red')and (weekemalight != weeksimlight))
            or ((dayemalight == 'Red' or daysimlight == 'Red') and (dayemalight != daysimlight))):
            dflightcontradict = dflightcontradict.append(s,ignore_index=True)

    notredname = stockset + 'notred'
    contraname = stockset + 'contradict'
    oversoldname = stockset + 'oversold'

    notredfilepath = os.path.join(rootDir,notredname+'.xlsx')
    contrafilepath = os.path.join(rootDir,contraname+'.xlsx')
    oversoldfilepath = os.path.join(rootDir,oversoldname+'.xlsx')


    dfnotred = DP.rearrange(dfnotred,'D-position')
    dflightcontradict = DP.rearrange(dflightcontradict, 'D-position')
    dfoversold = DP.rearrange(dfoversold, 'D-position')

    DI.Write_DF_T0_Excel(notredfilepath,dfnotred)
    DI.Write_DF_T0_Excel(contrafilepath,dflightcontradict)
    DI.Write_DF_T0_Excel(oversoldfilepath,dfoversold)




def main():
    get_stockset_basic_position('longtou')
    '''
    batah_stockset_analyze()
    batch_industry_analyze()
    stocksets = ['sz50','hs300','zz500','zxb']
    for stockset in stocksets:
        batch_stockset_selection(stockset)
    '''

if __name__ == "__main__":
    main()
