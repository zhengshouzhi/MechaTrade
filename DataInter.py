# -*- coding: utf-8 -*-
import tushare as ts
import Config
import os
import pandas as pd
from pandas import ExcelWriter

rootDir = Config.dataDir

def get_stockcode_list(dataset = None,update = False):

    filepath = dataset + '.csv'
    codefilepath = os.path.join(rootDir,'codelist',filepath)

    if(os.path.exists(codefilepath) and update == False):
        codelist = pd.read_csv(codefilepath,encoding='gbk')
        return codelist

    if(dataset == 'zxb'):
        codelist = ts.get_sme_classified()
        codelist = codelist[['code', 'name']]
        codelist.to_csv(codefilepath)
        return codelist
    elif(dataset == 'cyb'):
        codelist = ts.get_gem_classified()
        codelist = codelist[['code', 'name']]
        codelist.to_csv(codefilepath)
        return codelist
    elif(dataset == 'hs300'):
        codelist = ts.get_hs300s()
        codelist = codelist[['code', 'name']]
        codelist.to_csv(codefilepath)
        return codelist
    elif(dataset == 'sz50'):
        codelist = ts.get_sz50s()
        codelist = codelist[['code', 'name']]
        codelist.to_csv(codefilepath)
        return codelist
    elif(dataset == 'zz500'):
        codelist = ts.get_zz500s()
        codelist = codelist[['code', 'name']]
        codelist.to_csv(codefilepath)
        return codelist
    elif(dataset =='whole'):
        codelist = ts.get_today_all()
        codelist = codelist[['code', 'name']]

        codelist.to_csv(codefilepath)

        return codelist


def is_tingpai(stockcode):

    dfindex = ts.get_k_data('510050', ktype='D')
    dfstock = ts.get_k_data(stockcode,ktype='D')
    if(dfindex.loc[len(dfindex) - 1, 'date'] == dfstock.loc[len(dfstock)-1,'date']):
        return False
    else:
        return True


def get_industry_classification():
    filename = 'industry_classification'
    filepath = os.path.join(rootDir,'StockBasis',filename+'.csv')
    if(os.path.exists(filepath)):
        data = pd.read_csv(filepath,encoding='gbk')
    else:
        data = ts.get_industry_classified()
        data.to_csv(filepath)
    return data

def get_concept_classification():
    filename = 'concept_classification'
    filepath = os.path.join(rootDir,'StockBasis',filename+'.csv')
    if(os.path.exists(filepath)):
        data = pd.read_csv(filepath,encoding='gbk')
    else:
        data = ts.get_concept_classified()
        data.to_csv(filepath)
    return data

def get_area_classification():
    filename = 'area_classification'
    filepath = os.path.join(rootDir,'StockBasis',filename+'.csv')
    if(os.path.exists(filepath)):
        data = pd.read_csv(filepath,encoding='gbk')
    else:
        data = ts.get_area_classified()
        data.to_csv(filepath)
    return data

def get_stock_basics(update = False):
    filename = 'stock_basics'
    filepath = os.path.join(rootDir, 'StockBasics', filename + '.csv')
    if (os.path.exists(filepath) and update == False):
        data = pd.read_csv(filepath, encoding='gbk')
    else:
        data = ts.get_stock_basics()
        data.to_csv(filepath)
    return data


def get_profit_data(year,quarter):
    filename = 'stock_profit'
    filepath = os.path.join(rootDir, 'StockBasis', filename + '.csv')
    if (os.path.exists(filepath)):
        data = pd.read_csv(filepath, encoding='gbk')
    else:
        data = ts.get_profit_data(year,quarter)
        data.to_csv(filepath)
    return data


def get_industry_stocks(industrylist,keylist):
    dfbasics = get_stock_basics()
    dfindustrystocks = pd.DataFrame([],columns=keylist)
    for i in range(len(dfbasics)):
        industry = dfbasics.loc[i,'industry']
        if(industry in industrylist):
            valuelist = []
            for key in keylist:
                valuelist.append(dfbasics.loc[i,key])
            s = pd.Series(valuelist,index = keylist)
            dfindustrystocks = dfindustrystocks.append(s,ignore_index=True)
    return dfindustrystocks

def get_stockset_basics(codelist,valuelist = ['code','name','pe','pb']):
    basics = get_stock_basics()[valuelist]
    setbasics = pd.DataFrame([],columns=valuelist)
    for i in range(len(basics)):
        code = basics.loc[i,'code']
        if(code in codelist):
            s = basics.ix[i]
            setbasics = setbasics.append(s,ignore_index=True)
    setbasics = pd.DataFrame(setbasics.values,columns=setbasics.columns)
    return setbasics

def get_stocknameset_basics(namelist,valuelist = ['code','name','pe','pb']):
    basics = get_stock_basics()[valuelist]
    setbasics = pd.DataFrame([], columns=valuelist)
    for i in range(len(basics)):
        name = basics.loc[i, 'name']
        if (name in namelist):
            s = basics.ix[i]
            setbasics = setbasics.append(s, ignore_index=True)
    setbasics = pd.DataFrame(setbasics.values, columns=setbasics.columns)
    return setbasics

#将DataFrame类型数据写入指定路径
def Write_DF_T0_Excel(FilePath,df_Data ,sheetname='stock'):
    writer = ExcelWriter(FilePath)
    df_Data.to_excel(writer,sheetname)
    writer.save()




def get_all_industry():
    dfbasics = get_stock_basics()
    allindstry = []
    for i in range(len(dfbasics)):
        industry = dfbasics.loc[i, 'industry']
        if(industry not in allindstry):
            allindstry.append(industry)
    return allindstry

def get_longtou_list():
    rootDir = os.path.join(os.getcwd(), 'Data')
    sourcefilepath = os.path.join(rootDir,'IndLongTou.xls')

    dflongtou = pd.read_excel(sourcefilepath)
    namelist = dflongtou['股票名称'].values
    longtoubasics = get_stocknameset_basics(namelist)
    longtoucodelist = longtoubasics[['code','name']]
    codeDir = os.path.join(rootDir,'codelist')
    codefilepath = os.path.join(codeDir,'longtou.csv')
    longtoucodelist.to_csv(codefilepath)

#从Excel读取数据
def Get_TrdData_FromExcel(FilePath= 'file.xlsx',Worksheet = 'sheetname'): #用Xlrd获取数据
    try:
       Trd_Data = pd.read_excel(io=FilePath,sheetname = Worksheet)
    except Exception as err:
        print (str(err))
    #Trd_Data = Trd_Data.sort_values(by = ColIndex,ascending =True )
    return Trd_Data