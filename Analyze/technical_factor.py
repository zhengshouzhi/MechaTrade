# -*- coding: utf-8 -*-
#import urllib2
import numpy as np


################################################################################
#######  ji shu yin zi
################################################################################
def cal_kdj(dates, opens, highs, lows, closes, volumes, k_period=9, d_period=3, slowing=3):

    kdj_list = []
    prior_k_value, prior_d_value = 0, 0
    index = 0
    for date, open, high, low, close in zip(dates, opens, highs, lows, closes):
        index += 1

        if index >= max(k_period, d_period, slowing):
            maxer = max(highs[index - k_period: index])
            miner = min(lows[index - k_period: index])
            rsv = (close - miner) / (maxer - miner)
            if index == max(k_period, d_period, slowing):
                prior_k_value, prior_d_value = 50, 50

            k_value = (d_period - 1.0) / d_period * prior_k_value + 1.0 / d_period * rsv
            d_value = (d_period - 1.0) / slowing * prior_d_value + 1.0 / slowing * k_value
            j_value = 3 * k_value - 2 * d_value
            prior_k_value, prior_d_value = k_value, d_value
            kdj_dic = {}
            kdj_dic['date'] = date
            kdj_dic['k'] = k_value
            kdj_dic['d'] = d_value
            kdj_dic['j'] = j_value
            kdj_list.append(kdj_dic)

    return kdj_list


def cal_ma(dates, opens, highs, lows, closes, volumes, period=5):

    ma_list = []
    ma_str = 'ma' + str(period)
    index = 0
    for date, open, high, low, close in zip(dates, opens, highs, lows, closes):
        index += 1

        if index >= period:
            ma = sum(closes[index - period: index]) / period
            ma_dic = {}
            ma_dic['date'] = date
            ma_dic[ma_str] = ma

            ma_list.append(ma_dic)

    return ma_list


def cal_cci(dates, opens, highs, lows, closes, volumes, period=14, constant=0.015):

    cci_list = []
    cci_str = 'cci' + str(period)
    index = 0
    md_list = []
    for date, open, high, low, close in zip(dates, opens, highs, lows, closes):
        index += 1

        if index >= period:
            ma = sum(closes[index - period: index]) / period
            md_list.append((ma, close))
        if len(md_list) >= period:
            tp = (high + low + close) / 3.0
            ma = md_list[-1][0]
            md = sum([x[0] - x[1] for x in md_list[-period:]]) / period
            cci = (tp - ma) / md / constant
            cci_dic = {}
            cci_dic['date'] = date
            cci_dic[cci_str] = cci

            cci_list.append(cci_dic)

    return cci_list


def cal_bais(dates, opens, highs, lows, closes, volumes, period=10):

    bais_list = []
    bais_str = 'bais' + str(period)
    index = 0
    for date, open, high, low, close in zip(dates, opens, highs, lows, closes):
        index += 1

        if index >= period:
            ma = sum(closes[index - period: index]) / period
            bais = (close - ma) / ma
            bais_dic = {}
            bais_dic['date'] = date
            bais_dic[bais_str] = bais

            bais_list.append(bais_dic)

    return bais_list


def cal_mfi(dates, opens, highs, lows, closes, volumes, period=14):

    mfi_list = []
    mfi_str = 'mfi' + str(period)
    index = 0
    temp_list = []
    for date, open, high, low, close, volume in zip(dates, opens, highs, lows, closes, volumes):
        index += 1

        if index >= period:
            tp = (high + low + close) / 3.0
            period_volumes = sum(volumes[index - period: index])
            if len(temp_list) == 0:
                temp_list.append((tp, period_volumes, 0))
            elif tp > temp_list[-1][0]:
                temp_list.append((tp, period_volumes, 1))
            elif tp < temp_list[-1][0]:
                temp_list.append((tp, period_volumes, -1))
            else:
                temp_list.append((tp, period_volumes, 0))

        if len(temp_list) > period:
            pmf = sum([x[1] for x in temp_list[-period:] if x[2] == 1])
            nmf = sum([x[1] for x in temp_list[-period:] if x[2] == -1])
            mfi = 100 - (100 / (1 + pmf / nmf))

            mfi_dic = {}
            mfi_dic['date'] = date
            mfi_dic[mfi_str] = mfi

            mfi_list.append(mfi_dic)

    return mfi_list


def cal_mtm(dates, opens, highs, lows, closes, volumes, period=12):

    mtm_list = []
    mtm_str = 'mtm' + str(period)
    index = 0
    for date, open, high, low, close in zip(dates, opens, highs, lows, closes):
        index += 1

        if index > period:
            mtm = close - closes[index - period - 1]
            mtm_dic = {}
            mtm_dic['date'] = date
            mtm_dic[mtm_str] = mtm

            mtm_list.append(mtm_dic)

    return mtm_list


def cal_mtmma(dates, opens, highs, lows, closes, volumes, prior_period=12, m_period=6):

    mtmma_list = []
    mtmma_str = 'mtmma' + str(m_period)
    mtm_list = cal_mtm(dates, opens, highs, lows, closes, volumes, prior_period)
    index = 0
    for mtm in mtm_list:
        index += 1
        if index >= m_period:
            mtmma = sum(x['mtm' + str(prior_period)] for x in mtm_list[index - m_period: index]) / m_period
            mtmma_dic = {}
            mtmma_dic['date'] = mtm['date']
            mtmma_dic[mtmma_str] = mtmma

            mtmma_list.append(mtmma_dic)

    return mtmma_list

'''
相对强弱指数(Relative Strength Index，简称RSI)是韦达(J.Welles WilderJr.)所设计的摆荡指标，几乎任何技术分析软体都提供这种指标。RSI是根据收盘价的变动，衡量趋势的强度，它可能是领先或同时指标，绝对不会是落后指标。
RSI=100-(100/(1+RS))
RS＝某特定期间内上涨收盘价的差价平均值÷某特定期间内下跌收盘价的差价平均值
RSI峰位与谷底的形态，并不会随着期间长度而变化。就视觉上来说，短期RSI（例如：7天或9天）的讯号比较明显。大多数交易者都是透过电脑来计算与绘制RSI。
让我们以7天期RSI为例，说明计算的步骤。
1． 取最近7天的收盘价。
2． 在这7天之中，标示所有收盘价较前一天上涨者，加总全部的上涨差价，将总和除以7,结果是7天期上涨收盘价的差价平均值。
3． 在这7天之中，标示所有收盘价较前一天下跌者，加总全部的下跌差价，将总和除以7,结果是7天期下跌收盘价的差价平均值。
4． 将“上涨收盘价的差价平均值”除以“下跌收盘价的差价平均值”，结果是“相对强弱值”(Relative Strength,简称RS)，将RS代入上述公式中，即可以取得RSI。
5． 每天重复前述的程序（参考图31－1的工作底稿）。
图 《交易为生》P90
'''
def cal_rsi(dates, opens, highs, lows, closes, volumes, period=6):

    rsi_list = []
    rsi_str = 'rsi' + str(period)
    index = 0
    for date, open, high, low, close in zip(dates, opens, highs, lows, closes):
        index += 1
        if index > period:
            p_sum, n_sum = 0, 0
            for i in range(index - period, index):
                if closes[i] - closes[i - 1] > 0:
                    p_sum += closes[i] - closes[i - 1]
                if closes[i] - closes[i - 1] < 0:
                    n_sum += closes[i] - closes[i - 1]
            rsi = p_sum / (p_sum + abs(n_sum)) * 100
            rsi_dic = {}
            rsi_dic['date'] = date
            rsi_dic[rsi_str] = rsi

            rsi_list.append(rsi_dic)

    return rsi_list


def cal_emv(dates, opens, highs, lows, closes, volumes, period=6):
    
    emv_list = []
    emv_str = 'emv' + str(period)
    em_list = []
    index = 0
    for date, open, high, low, close, volume in zip(dates, opens, highs, lows, closes, volumes):
        index += 1
        if index > 1:
            pr = 0.5 * (highs[index - 1] + lows[index - 1]) - 0.5 * (highs[index - 2] + lows[index - 2])
            em = (high - low) * pr / volume
            em_list.append(em)
        if len(em_list) >= period:
            emv_dic = {}
            emv_dic['date'] = date
            emv_dic[emv_str] = sum(em_list[-period:])

            emv_list.append(emv_dic)

    return emv_list

'''
EMA技术分析软体可以让你随意选择EMA的长度，只要按几个键就可以了。如果你希望透过手工计算，请遵循下列步骤：
1．选择EMA的长度（参考下文），假定你希望计算10天期的EMA。
2．计算长度系统K（参考上文）。以10天期EMA为例，K是(2/10+1)，相当于是0.18。
3．计算最初10天的简单移动平均----将收盘价加总，除以10。
4．在第11天，以当天的收盘价乘以K，并将前一天的移动平均乘以(1-K)，将这两个数值加总，结果就是第11天的10天期EMA。（译按：就第11天而言，“前一天的移动平均”是指最初10天的简单移动平均。就第X天而言(X≥12)，“前一天的移动平均”是指“第(x-1)天的10天期EMA”）。
5．每天都重复第4步骤，藉以计算最近的EMA（参考图25－1的工作底稿）。
'''

def cal_ema(dates, opens, highs, lows, closes, volumes, period=10):
    ema_list = []
    ema_str = 'ema' + str(period)
    index = 0
    for date, open, high, low, close, volume in zip(dates, opens, highs, lows, closes, volumes):

        if index == 0:#period:
            ema = close #sum(closes[index - period: index]) / period
            ema_dic = {}
            ema_dic['date'] = date
            ema_dic[ema_str] = ema
            ema_list.append(ema_dic)
        else: #if index > period:
            ema = (2 * close + (period - 1) * ema_list[-1][ema_str]) / (period + 1)
            ema_dic = {}
            ema_dic['date'] = date
            ema_dic[ema_str] = ema
            ema_list.append(ema_dic)

        index += 1
    return ema_list


def cal_macd(dates, opens, highs, lows, closes, volumes, s_period=12, l_period=26, m_period=9):
    
    macd_list = []
    macd_str = 'macd'
    s_emas = cal_ema(dates, opens, highs, lows, closes, volumes, s_period)
    l_emas = cal_ema(dates, opens, highs, lows, closes, volumes, l_period)

    dif_list = []
    for s_ema, l_ema in zip(s_emas, l_emas):#[l_period - s_period:]
        dif = s_ema['ema' + str(s_period)] - l_ema['ema' + str(l_period)]
        dif_dic = {}
        dif_dic['date'] = l_ema['date']
        dif_dic['dif'] = dif.round(3)
        dif_list.append(dif_dic)

    if len(dif_list) >= m_period:
        dif_value_list = [x['dif'] for x in dif_list]
        dea_list = cal_ema(dates,opens,highs,lows,dif_value_list,volumes,m_period)

        dea_value_list = [x['ema' + str(m_period)] for x in dea_list]
        for date, dif, dea in zip(dates, dif_value_list, dea_value_list):
            macd = 2 * (dif - dea)
            macd_dic = {}
            macd_dic['date'] = date
            macd_dic['diff'] = dif.round(3)

            macd_dic['dea'] = dea.round(3)
            macd_dic[macd_str] = macd.round(3)

            macd_list.append(macd_dic)

    return macd_list


def cal_trix(dates, opens, highs, lows, closes, volumes, period=10):
    
    trix_list = []
    trix_str = 'trix' + str(period)
    first_ema = cal_ema(dates, opens, highs, lows, closes, volumes, period)
    first_ema_value = [x['ema' + str(period)] for x in first_ema]
    second_ema = cal_ema(dates[period - 1:], opens[period - 1:], highs[period - 1:], lows[period - 1:],
                         first_ema_value, volumes[period - 1:], period)
    second_ema_value = [x['ema' + str(period)] for x in second_ema]
    third_ema = cal_ema(dates[2 * period - 2:], opens[2 * period - 2:], highs[2 * period - 2:], lows[2 * period - 2:],
                        second_ema_value, volumes[2 * period - 2:], period)

    third_ema_dates = [x['date'] for x in third_ema]
    third_ema_values = [x['ema' + str(period)] for x in third_ema]
    index, prior_value = 0, 0
    for date, value in zip(third_ema_dates, third_ema_values):
        index += 1
        if index == 1:
            prior_value = value
        if index > 1:
            trix = (value - prior_value) / prior_value * 100
            prior_value = value
            trix_dic = {}
            trix_dic['date'] = date
            trix_dic[trix_str] = trix

            trix_list.append(trix_dic)

    return trix_list


def cal_ad(dates, opens, highs, lows, closes, volumes, period=6):

    ad_values = []
    for high, low, close, volume in zip(highs, lows, closes, volumes):
        ad = 0
        if (high - low) < 0.00001:
            ad = volume
        else:
            ad = ((close - low) - (high - close)) / (high - low) * volume
        ad_values.append(ad)

    ad_list = []
    ad_str = 'ad' + str(period)
    index = 0
    for date, ad_value in zip(dates, ad_values):
        index += 1
        if index >= period:
            ad_sum = sum(ad_values[index - period: index])
            ad_dic = {}
            ad_dic['date'] = date
            ad_dic[ad_str] = ad_sum

            ad_list.append(ad_dic)

    return ad_list


def cal_ar(dates, opens, highs, lows, closes, volumes, period=5):

    ar_list = []
    ar_str = 'ar' + str(period)
    index = 0
    for date, high, low, open in zip(dates, highs, lows, opens):
        index += 1
        if index >= period:
            ar_ho = sum([x - y for x, y in zip(highs[index - period: index], opens[index - period: index])])
            ar_ol = sum([x - y for x, y in zip(opens[index - period: index], lows[index - period: index])])
            if ar_ol < 0.00001:
                ar = 1000
            else:
                ar = ar_ho / ar_ol * 100
            ar_dic = {}
            ar_dic['date'] = date
            ar_dic[ar_str] = ar

            ar_list.append(ar_dic)

    return ar_list


def cal_br(dates, opens, highs, lows, closes, volumes, period=5):

    br_list = []
    br_str = 'br' + str(period)
    index = 0
    for date, high, low, open in zip(dates, highs, lows, opens):
        index += 1
        if index > period:
            br_hc = sum([x - y for x, y in zip(highs[index - period: index], closes[index - period - 1: index - 1])])
            br_cl = sum([x - y for x, y in zip(closes[index - period - 1: index - 1], lows[index - period: index])])
            if br_cl < 0.00001:
                br = 1000
            else:
                br = br_hc / br_cl * 100
            br_dic = {}
            br_dic['date'] = date
            br_dic[br_str] = br

            br_list.append(br_dic)

    return br_list


def cal_arbr(dates, opens, highs, lows, closes, volumes, period=5):

    ars = cal_ar(dates, opens, highs, lows, closes, volumes, period=5)
    brs = cal_br(dates, opens, highs, lows, closes, volumes, period=5)

    arbr_list = []
    arbr_str = 'arbr' + str(period)
    for ar, br in zip(ars[1:], brs):
        arbr_dic = {}
        arbr_dic['date'] = ar['date']
        arbr_dic[arbr_str] = ar['ar' + str(period)] - br['br' + str(period)]

        arbr_list.append(arbr_dic)

    return arbr_list


def cal_bbi(dates, opens, highs, lows, closes, volumes, f_period=3, s_period=6, t_period=12, fourth_period=24):

    f_mas = cal_ma(dates, opens, highs, lows, closes, volumes, period=f_period)
    s_mas = cal_ma(dates, opens, highs, lows, closes, volumes, period=s_period)
    t_mas = cal_ma(dates, opens, highs, lows, closes, volumes, period=t_period)
    fourth_mas = cal_ma(dates, opens, highs, lows, closes, volumes, period=fourth_period)

    bbi_list = []
    bbi_str = 'bbi'
    for f_ma, s_ma, t_ma, fourth_ma in zip(f_mas[fourth_period - f_period:], s_mas[fourth_period - s_period:], t_mas[fourth_period - t_period:], fourth_mas):
        bbi = (f_ma['ma' + str(f_period)] + s_ma['ma' + str(s_period)] + t_ma['ma' + str(t_period)] + fourth_ma['ma' + str(fourth_period)]) / 4
        bbi_dic = {}
        bbi_dic['date'] = fourth_ma['date']
        bbi_dic[bbi_str] = bbi

        bbi_list.append(bbi_dic)

    return bbi_list


def cal_obv(dates, opens, highs, lows, closes, volumes):

    obv_list = []
    obv_str = 'obv'
    index = 0
    prior_obv = 0
    for date, open, close, volume in zip(dates, opens, closes, volumes):
        index += 1
        obv_dic = {}
        obv_dic['date'] = date
        if index == 1:
            if abs(close - open) < 0.00001:
                obv_dic[obv_str] = 0
            elif close > open:
                obv_dic[obv_str] = volume
            else:
                obv_dic[obv_str] = -volume
        else:
            if abs(close - closes[index - 2]) < 0.00001:
                obv_dic[obv_str] = prior_obv
            elif close > closes[index - 2]:
                obv_dic[obv_str] = prior_obv + volume
            else:
                obv_dic[obv_str] = prior_obv - volume
        prior_obv = obv_dic[obv_str]

        obv_list.append(obv_dic)

    return obv_list


def cal_vr(dates, opens, highs, lows, closes, volumes, period=26):

    vr_list = []
    vr_str = 'vr' + str(period)
    index = 0
    for date, close, volume in zip(dates, closes, volumes):
        index += 1

        if index > period:
            avs, bvs, cvs = 0, 0, 0
            for i in range(-period, 0):
                if abs(closes[index + i] - closes[index + i - 1]) < 0.00001:
                    cvs += volumes[index + i]
                elif closes[index + i] > closes[index + i - 1]:
                    avs += volumes[index + i]
                else:
                    bvs += volumes[index + i]
            vr = (avs + 0.5 * cvs) / (bvs + 0.5 * cvs)
            vr_dic = {}
            vr_dic['date'] = date
            vr_dic[vr_str] = vr

            vr_list.append(vr_dic)

    return vr_list


def cal_roc(dates, opens, highs, lows, closes, volumes, period=12):

    roc_list = []
    roc_str = 'roc' + str(period)
    index = 0
    for date, close in zip(dates, closes):
        index += 1

        if index > period:
            roc = (close - closes[index - period - 1]) / closes[index - period - 1]
            roc_dic = {}
            roc_dic['date'] = date
            roc_dic[roc_str] = roc

            roc_list.append(roc_dic)

    return roc_list


def cal_vema(dates, opens, highs, lows, closes, volumes, period=10):
    
    vema_list = []
    vema_str = 'vema' + str(period)
    index = 0
    for date, open, high, low, close, volume in zip(dates, opens, highs, lows, closes, volumes):
        index += 1
        if index == period:
            vema = sum(volumes[index - period: index]) / period
            vema_dic = {}
            vema_dic['date'] = date
            vema_dic[vema_str] = vema
            vema_list.append(vema_dic)
        if index > period:
            vema = (2 * volume + (period - 1) * vema_list[-1][vema_str]) / (period + 1)
            vema_dic = {}
            vema_dic['date'] = date
            vema_dic[vema_str] = vema

            vema_list.append(vema_dic)

    return vema_list


def cal_vmacd(dates, opens, highs, lows, closes, volumes, s_period=12, l_period=26, m_period=9):
    
    vmacd_list = []
    vmacd_str = 'vmacd'
    s_vemas = cal_vema(dates, opens, highs, lows, closes, volumes, s_period)
    l_vemas = cal_vema(dates, opens, highs, lows, closes, volumes, l_period)

    dif_list = []
    for s_vema, l_vema in zip(s_vemas[l_period - s_period:], l_vemas):
        dif = s_vema['vema' + str(s_period)] - l_vema['vema' + str(l_period)]
        dif_dic = {}
        dif_dic['date'] = l_vema['date']
        dif_dic['dif'] = dif
        dif_list.append(dif_dic)

    if len(dif_list) >= m_period:
        dif_value_list = [x['dif'] for x in dif_list]
        dea_list = cal_vema(dates[l_period - 1:], opens[l_period - 1:], highs[l_period - 1:],
                           lows[l_period - 1:], dif_value_list, volumes[l_period - 1:], m_period)

        dea_value_list = [x['vema' + str(m_period)] for x in dea_list]
        for date, dif, dea in zip(dates[l_period + m_period - 2:], dif_value_list[m_period - 1:], dea_value_list):
            vmacd = 2 * (dif - dea)
            vmacd_dic = {}
            vmacd_dic['date'] = date
            vmacd_dic[vmacd_str] = vmacd

            vmacd_list.append(vmacd_dic)

    return vmacd_list


################################################################################
#######  bo dong lv yin zi
################################################################################
def cal_high_low_ratio(dates, opens, highs, lows, closes, volumes, period=20):
    
    high_low_ratio_list = []
    high_low_ratio_str = 'high_low_ratio' + str(period)
    index = 0
    for date, high, low in zip(dates, highs, lows):
        index += 1

        if index >= period:
            highest = max(highs[index - period: index])
            lowest = min(lows[index - period: index])
            high_low_ratio = highest / lowest
            high_low_ratio_dic = {}
            high_low_ratio_dic['date'] = date
            high_low_ratio_dic[high_low_ratio_str] = high_low_ratio

            high_low_ratio_list.append(high_low_ratio_dic)

    return high_low_ratio_list


def cal_std_return_rate(dates, opens, highs, lows, closes, volumes, period=20):
    
    std_return_rate_list = []
    std_return_rate_str = 'std_return_rate' + str(period)
    return_rate_list = []
    for i, value in enumerate(closes):
        if i == 0:
            return_rate_list.append(0.0)
        else:
            return_rate_list.append((value - closes[i - 1]) / closes[i - 1])
    index = 0
    for date, return_rate in zip(dates, return_rate_list):
        index += 1

        if index >= period:
            std_return_rate = np.std(return_rate_list[index - period: index])
            std_return_rate_dic = {}
            std_return_rate_dic['date'] = date
            std_return_rate_dic[std_return_rate_str] = std_return_rate

            std_return_rate_list.append(std_return_rate_dic)

    return std_return_rate_list


def cal_force_index(dates, opens, highs, lows, closes, volumes, period=1):
    
    force_index_list = []
    force_index_str = 'force_index'

    index = 0
    for date, close, volume in zip(dates, closes, volumes):
        index += 1

        if index > period:
            force_index = volume * (close - closes[index - 2])
            force_index_dic = {}
            force_index_dic['date'] = date
            force_index_dic[force_index_str] = force_index

            force_index_list.append(force_index_dic)
    return force_index_list


def cal_force_index_ema(dates, opens, highs, lows, closes, volumes, period=2):

    force_index_ema_list = []
    force_index_ema_str = 'force_index_ema' + str(period)

    force_index_list = cal_force_index(dates, opens, highs, lows, closes, volumes)

    #print(force_index_list)

    force_index_value_list = [x['force_index'] for x in force_index_list]


    force_index_emas = cal_ema(dates[1:], opens[1:], highs[1:], lows[1:], force_index_value_list, volumes[1:], period)

    for force_index_ema in force_index_emas:
        force_index_dic = {}
        force_index_dic['date'] = force_index_ema['date']
        force_index_dic[force_index_ema_str] = force_index_ema['ema' + str(period)]
        force_index_ema_list.append(force_index_dic)

    return force_index_ema_list





################################################################################
#######  EnvelopRatio
################################################################################
def envelop_ratio(dates, opens, highs, lows, closes, volumes, period=100,lowthresh = 0.9,highthersh=0.95):
    bandratio = 0.03
    step = 0.05

    min_penetration = period * (1-highthersh)
    max_penetration = period * (1-lowthresh)

    closes = closes[period:len(closes)]
    iCounter = 0

    while(True ):
        iCounter += 1
        if(iCounter > 50):
            return None
        for index in range(len(closes)):
            upperband = closes[index] * (1+bandratio)
            lowerband = closes[index] * (1-bandratio)
            penetrationCounter = 0
            while(True):
                if(highs[index] > upperband):
                    penetrationCounter += 1
                if(lows[index] < lowerband):
                    penetrationCounter += 1
                if(penetrationCounter > max_penetration):
                    break

        if(penetrationCounter > max_penetration):
            bandratio = bandratio + step
        elif(penetrationCounter < min_penetration):
            bandratio = bandratio - step
        elif(min_penetration < penetrationCounter < max_penetration):
            return bandratio



#MACD指标处理，用于补充力度计算的不足
def Data_MACD_BAR(Trd_Data = 'Trd_Data'):
    Trd_Data['EMA12'] = None
    Trd_Data['EMA26'] = None
    Trd_Data['DIF'] = None
    Trd_Data['DEA'] = None
    Trd_Data['BAR'] = None
    totalrows = len(Trd_Data)
    irows = 0
    Trd_Data.loc[irows,'EMA12'] = Trd_Data.loc[irows,'close']
    Trd_Data.loc[irows,'EMA26'] = Trd_Data.loc[irows,'close']
    Trd_Data.loc[irows,'DIF'] = 0
    Trd_Data.loc[irows,'DEA'] = 0
    Trd_Data.loc[irows,'BAR'] = 0
    irows = irows + 1
    while (irows < totalrows):
        preEMA12 = Trd_Data.loc[irows-1,'EMA12']
        preEMA26 = Trd_Data.loc[irows-1,'EMA26']
        curClose = Trd_Data.loc[irows,'close']
        Trd_Data.loc[irows,'EMA12'] = preEMA12*11/13 +curClose*2/13
        Trd_Data.loc[irows,'EMA26'] = preEMA26*25/27 +curClose*2/27
        curEMA12 = Trd_Data.loc[irows,'EMA12']
        curEMA26 = Trd_Data.loc[irows,'EMA26']
        Trd_Data.loc[irows,'DIF'] = (curEMA12 -curEMA26).round(3)
        preDEA = Trd_Data.loc[irows-1,'DEA']
        curDIF =  Trd_Data.loc[irows,'DIF']
        Trd_Data.loc[irows,'DEA'] = (preDEA * 0.8 + curDIF * 0.2).round(3)
        curDEA = Trd_Data.loc[irows,'DEA']
        Trd_Data.loc[irows,'BAR'] = (2*(curDIF - curDEA)).round(3)
        irows = irows + 1
    return Trd_Data

def cal_ema_wz(dates, opens, highs, lows, closes, volumes, emaperiod = 20,timespan = 60):
    emas = cal_ema(dates, opens, highs, lows, closes, volumes, emaperiod)

    emawz_list = []
    ema_str = 'ema' + str(emaperiod)
    upcounter = 0
    downcounter = 0

    totalrows = len(closes)
    index = totalrows -1

    while(index >=0):
        emawz_dic = {}
        if(index < timespan):
            emawz_dic['wz'] 


    for date,close,ema_dic in zip(closes,emas):
        emawz_dic = {}
        emawz_dic['date'] = date
        emawz_dic[ema_str] = ema_dic[ema_str]
        emawz_dic['close'] = close

        if(ema_dic[ema_str]) > close:
            upcounter += 1
            emawz_dic['wz'] = 'up'

        if(ema_dic[ema_str]) < close:
            downcounter += 1
            emawz_dic['wz'] = 'down'

        emawz_list.append(emawz_dic)

    return emawz_list,upcounter,downcounter


def isBelowSMA(dates, opens, highs, lows, closes, volumes,period):
    close_list = []
    for date, close in zip(dates,closes):
        close_dic = {}
        close_dic['date'] = date
        close_dic['close'] = close
        close_list.append(close_dic)

    sma_list = cal_ma(dates, opens, highs, lows, closes, volumes,period)

    initialdate = max(close_list[0]['date'],sma_list[0]['date'])

    close_list = GP.date_clip(close_list,initialdate)
    sma_list = GP.date_clip(sma_list,initialdate)

    isbelow_sma_list = []

    for close_dic,sma_dic in zip(close_list,sma_list):
        isbelow_sma_dic = {}
        isbelow_sma_dic['date'] = close_dic['date']
        if(close_dic['close'] < sma_dic['ma'+str(period)]):
            isbelow_sma_dic['belowsma'] = True

        else:
            isbelow_sma_dic['belowsma'] = False
        isbelow_sma_list.append(isbelow_sma_dic)

    return isbelow_sma_list



def isBelowEMA(dates, opens, highs, lows, closes, volumes,period):
    close_list = []
    for date, close in zip(dates,closes):
        close_dic = {}
        close_dic['date'] = date
        close_dic['close'] = close
        close_list.append(close_dic)

    ema_list = cal_ema(dates, opens, highs, lows, closes, volumes,period)

    initialdate = max(close_list[0]['date'],ema_list[0]['date'])

    close_list = GP.date_clip(close_list,initialdate)
    ema_list = GP.date_clip(ema_list,initialdate)

    isbelow_ema_list = []

    for close_dic,sma_dic in zip(close_list,ema_list):
        isbelow_ema_dic = {}
        isbelow_ema_dic['date'] = close_dic['date']
        if(close_dic['close'] < sma_dic['ema'+str(period)]):
            isbelow_ema_dic['belowema'] = True

        else:
            isbelow_ema_dic['belowema'] = False

        isbelow_ema_list.append(isbelow_ema_dic)

    return isbelow_ema_list


def isnewlow(diclist,indicatorname,position,period=15):
    if(position < period):
        return None
    newlow = True
    index = 1
    while(index <period):
        if(diclist[position][indicatorname] > diclist[position-index][indicatorname]):
            newlow = False
            break
        index += 1
    return newlow








