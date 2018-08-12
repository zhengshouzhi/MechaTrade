# -*- coding: utf-8 -*-
import datetime
import tushare as ts
import pandas as pd
import os
import numpy as np

def GetDateIndex(df,date):
    totalrows = len(df)
    for i in range(totalrows-1):
        curdate = df.loc[i,'date']
        nxtdate = df.loc[i+1,'date']
        if(curdate == date):
            return i
        if(curdate < date and nxtdate > date):
            return i
        elif(nxtdate < date):
            continue
        elif(curdate > date):
            return None
    if(i == totalrows-2):
        curdate = df.loc[i+1, 'date']
        if(curdate == date):
            return i
        else:
            return None



#获得当前时间的str,格式为："%Y-%m-%d %H:%M:%S"
def getcurrenttimestr():
    # 获得当前时间
    now = datetime.datetime.now()
    # 转换为指定的格式:
    timestr = now.strftime("%Y-%m-%d %H:%M:%S")
    return timestr


#新建文件夹的函数
def mkdir(path):
    # 引入模块
    import os
    #
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        print (path+' 创建成功')
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        #print (path+' 目录已存在')
        return False

# 将任何类型的股票代码转换成本程序通用的代码，只是针对遇到的情况，未来要根据数据源升级
def codeType(stockcode='sh'):
    import numpy

    if (isinstance(stockcode, (float))):
        stockcode = str(stockcode)

        if len(stockcode) == 8:
            stockcode = stockcode[0:6]
        elif len(stockcode) == 9:
            stockcode = stockcode[2:8]
        elif len(stockcode) == 6:
            stockcode = stockcode[0:4]
            stockcode = stockcode.zfill(6)
        elif len(stockcode) == 5:
            stockcode = stockcode[0:3]
            stockcode = stockcode.zfill(6)
        if (len(stockcode) < 5):

            stockcode = stockcode.zfill(6)


    elif (isinstance(stockcode, (numpy.int64))):
        stockcode = str(stockcode)
        stockcode = stockcode.zfill(6)

    elif(isinstance(stockcode,(str))):
        if(len(stockcode) == 3):
            stockcode = '000' +stockcode
        elif(len(stockcode) == 4):
            stockcode = '00' + stockcode
        elif(len(stockcode)==2):
            stockcode = '0000'+stockcode

    stockcode = str(stockcode)

    return stockcode

def get_last_trade_time(Cycle = 'D'):
    df = ts.get_k_data('510050',ktype=Cycle)
    return df.loc[len(df)-1,'date']

def get_pre_low(highs,lows):
    maxvalue = max(highs)
    highlist = []
    for high in highs:
        highlist.append(high)
    maxindex = highlist.index(maxvalue)

    if(maxindex == 0 or maxindex == len(lows)-1):
        return None
    leftlist = lows[0:maxindex]
    return(min(leftlist))

def rearrange(df,key):
    df = df.sort_values(by = key,ascending = True)
    df = pd.DataFrame(df.values,columns=df.columns)
    return df


def get_macd_list(macddiclist):
    macdlist = []
    diflist = []
    dealist = []
    for ele in macddiclist:
        macdlist.append(ele['macd'])
        diflist.append(ele['diff'])
        dealist.append(ele['dea'])
    return macdlist,diflist,dealist


def get_stragegy_filepath(StrategyName,dataset,tradeCycle):

    lasttradetimestr = get_last_trade_time('D')
    filename = StrategyName + lasttradetimestr + '-' + dataset + '-' + tradeCycle
    RootDir = os.path.join(os.pardir, 'data', lasttradetimestr)
    mkdir(RootDir)
    filepath = os.path.join(RootDir, filename + '.xls')
    return filepath


def get_common_parameters(code,tradeCycle):
    from Analyze import Technical as ta
    from Strategies import False_Breakout_Divergence as FB
    smaperiod = 20
    colNames = ['code', 'tradeCycle', 'curclose', 'sma', 'ATR', 'ATRRatio', 'ATRWZ',
                'ImpLight','upchannel','downchannel','valueWZ','rewardratio']
    dfdata = ts.get_k_data(code, ktype=tradeCycle)
    if (len(dfdata) < 120):  # 剔除交易时间少于120天的个股
        print('No Enough Trading Days')
    dates = dfdata['date'].values
    closes = dfdata['close'].values
    highs = dfdata['high'].values
    lows = dfdata['low'].values
    macddiclist = ta.cal_macd(dates, closes)

    macd, dif, dea =get_macd_list(macddiclist)

    absdis, perdis, maprice = ta.curdistosma(closes, smaperiod)
    curATR = ta.last_atr(dates, closes, highs, lows)
    upchannel = maprice + 2 * curATR
    downchannel = maprice - 2 * curATR

    curClose = closes[-1]
    ATRRatio = curATR / curClose
    ATRWZ = absdis / curATR

    smadir = ta.SMA_Direction(dates, closes)
    macddir = ta.MACD_Direction(dates, closes)
    ImpLight = FB.ImpluseLight(smadir, macddir)

    rewardratio = (upchannel-curClose)*100/curClose
    value_re = ta.SMAValueZone_GX(dates, closes)

    curATR = round(curATR, 2)
    ATRRatio = round(ATRRatio * 100, 2)
    rewardratio = round(rewardratio, 2)
    ATRWZ = round(ATRWZ, 2)
    maprice = round(maprice, 2)
    upchannel = round(upchannel,2)
    downchannel = round(downchannel,2)
    s = pd.Series([code, tradeCycle, curClose, maprice, curATR, ATRRatio, ATRWZ,ImpLight,
                   upchannel,downchannel,value_re,rewardratio], index=colNames)

    return s

def closetoret(closes):
    ret = []
    for curclose,preclose in zip(closes[1:],closes[:-1]):

        ret.append(curclose/preclose-1)
    return ret

def closetologret(closes):
    logret = []
    for curclose,preclose in zip(closes[1:],closes[:-1]):
        logret.append(np.log(curclose/preclose))
    return logret

def dailyret_to_monthly(df):
    logret = closetologret(df['close'])
    dates = df['date']
    yyyymm = []
    for i in range(0, len(logret)):
        yyyymm.append(dates[i][0:4] + dates[i][5:7])
    y = pd.DataFrame(logret, yyyymm, columns=['ret_monthly'])
    ret_monthly = y.groupby(y.index).sum()
    return ret_monthly

def dailyret_to_annual(df):
    logret = closetologret(df['close'])
    dates = df['date']
    yyyy = []
    for i in range(0, len(logret)):
        yyyy.append(dates[i][0:4])
    y = pd.DataFrame(logret, yyyy, columns=['ret_annual'])
    ret_annual = np.exp(y.groupby(y.index).sum()) - 1
    return ret_annual