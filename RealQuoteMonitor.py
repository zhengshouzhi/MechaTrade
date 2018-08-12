# -*- coding: utf-8 -*-
from Strategies import False_Breakout_Divergence as FBD
import multiprocessing
import time
import datetime
import multiprocessing

def currenttradestatus():
    '''
    prestart = '09:00:00'
    morningstart = '09:30:00'
    morningend = '11:30:00'
    afternoonstart = '13:00:00'
    afternoonend  = '15:00:00'
    :return: tradestatus 根据时间返回的当下交易状态
    pre:开盘前
    pretrade:盘前
    morningtrade:早盘
    noonbreak：中午休息
    afternoontrade：下午盘
    post:收盘后
    dataready:数据准备好
    '''
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute

    if(hour < 9 and hour >= 0):
        tradestatus = 'pre'
    elif(hour==9 and minute < 30):
        tradestatus = 'pretrade'
    elif(hour==9 and minute >= 30):
        tradestatus = 'morningtrade'
    elif(hour > 9 and hour < 11):
        tradestatus = 'morningtrade'
    elif(hour == 11 and minute < 30):
        tradestatus = 'morningtrade'
    elif(hour < 13):
        tradestatus = 'noonbreak'
    elif(hour >= 13 and hour < 15):
        tradestatus = 'afternoontrade'
    elif(hour >= 15 and hour<=24):
        tradestatus = 'post'



    return tradestatus


def currentupdatestatus():
    '''
    10:00-10:05
    10:30-10:35
    11:00-11:05
    11:30--11:35

    13:30-13:35
    14:00-14:05
    14:30-14:35
    14:50--14:55
    15:00--15:05
    '''
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    updatestatus = False
    if(hour in [10,11,14]):
        if((minute <=5) or (minute>=25 and minute <=35 )):
            updatestatus = True
    if(hour == 13):
        if(minute>=25 and minute <=35 ):
            updatestatus = True
    if(hour ==14):
        if(minute>=45 and minute<=50):
            updatestatus = True
    if(hour == 15):
        if (minute <= 5):
            updatestatus = True
    return updatestatus



    return updatestatus

selectedcolNames = ['ATR', 'ATRRatio', 'code', 'tradeCycle', 'name', 'time', 'curclose', 'cutshort', 'rewardratio',
                        'riskratio', 'rewardrisk', 'targetprice1', 'targetprice2', 'targetprice3']
def ETFFalseBreakMonitor():
    while (True):
        tradestatus = currenttradestatus()
        if (tradestatus == 'post'):
            print(selectedcolNames)
            FBD.etffalsebreakmonitor()
            break

        updatestatus = currentupdatestatus()
        if (updatestatus):
            print(selectedcolNames)
            print('--' * 20)
            FBD.etffalsebreakmonitor()
            time.sleep(300)


def Hs300FalseBreakMonitor():
    while(True):
        tradestatus = currenttradestatus()
        if (tradestatus == 'post'):

            FBD.hs300falsebreakmonitor()
            break

        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        if(hour == 14 and minute > 30):

            FBD.hs300falsebreakmonitor()
            time.sleep(600)
            break


def Zz500FalseBreakMonitor():

    FBD.Zz500falsebreakmonitor()


def main():
    p1 = multiprocessing.Process(target= ETFFalseBreakMonitor)
    p2 = multiprocessing.Process(target=Hs300FalseBreakMonitor)
    p1.start()
    p2.start()

    #Hs300FalseBreakMonitor()
    #Zz500FalseBreakMonitor()


    #p1 = multiprocessing.Process(target=ETFFalseBreakMonitor())
    #p2 = multiprocessing.Process(target=Hs300FalseBreakMonitor())
    #p3 = multiprocessing.Process(target=Zz500FalseBreakMonitor())

    #p1.start()
    #p2.start()
    #p3.start()




if __name__ == "__main__":

    main()