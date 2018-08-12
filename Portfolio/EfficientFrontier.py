# -*- coding: utf-8 -*-
import sys
import tushare as ts
import pandas as pd
import numpy as np
import statsmodels.api as sm  # 统计运算
import scipy.stats as scs  # 科学计算
import matplotlib.pyplot as plt  # 绘图
from Analyze import Statistical as stc

#最优化投资组合的推导是一个约束最优化问题
import scipy.optimize as sco


                #50etf, 创业板etf,纳指etf,  德国30,   标普500， 300ETF,  500ETF,  159922,   H股ETF,   黄金ETF， 国债ETF
stock_set = ['510050','159915','513100','513030']#,'513500','159919','510500','159922','510900','518880','511010']



def getportdata():
    start_date = '2017-01-01'
    end_date = '2017-09-22'
    dfport = pd.DataFrame([],columns=stock_set)
    for code in stock_set:
        df = ts.get_k_data(code, start=start_date, end=end_date)
        data = df['close']
        dfport[code] = data
    dfport.index = df['date']
    ##回报率

    return dfport


##投资组合优化1——sharpe最大


def statistic_plot(log_returns,stock_set):
    for sym in stock_set:
        print("\nResults for symbol %s" % sym)
        print(30 * "-")
        log_data = np.array(log_returns[sym].dropna())
        stc.print_statistics(log_data)

    # 通过qq图检查代码的数据

        # 下面是HS300 对数收益率 分位数-分位数图

        sm.qqplot(log_returns[sym].dropna(), line='s')
        plt.title(sym+'qqplot')
        plt.grid(True)
        plt.xlabel('theoretical quantiles')
        plt.ylabel('sample quantiles')

def main():
    dfport = getportdata()

    #print(dfport.info())
    #print(dfport.tail())

    #(dfport / dfport.ix[0] * 100).plot(figsize=(8, 6))


    log_returns = np.log(dfport / dfport.shift(1))
    #returns = returns[1:]
    #print(log_returns.head())
    log_returns.hist(bins=50, figsize=(9, 6))

    ##年化收益率
    annual_return = log_returns.mean() * 252
    ##计算协方差矩阵
    covmatrix = log_returns.cov() * 252
    ##计算股票个数
    noa = len(stock_set)





    ##随机生成初始化权重
    weights = np.random.random(noa)
    ##计算百分比
    weights /= np.sum(weights)

    ##下面通过一次蒙特卡洛模拟，产生大量随机的权重向量，并记录随机组合的预期收益和方差。
    port_returns = []

    port_variance = []

    for p in range(4000):
        weights = np.random.random(noa)
        weights /= np.sum(weights)
        port_returns.append(np.sum(log_returns.mean() * 252 * weights))
        port_variance.append(np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 252, weights))))

    ##因为要开更号，所以乘两次weight
    ##dot就是点乘
    port_returns = np.array(port_returns)
    port_variance = np.array(port_variance)

    # 无风险利率设定为4%
    risk_free = 0.04
    plt.figure(figsize=(8, 4))
    plt.scatter(port_variance, port_returns, c=(port_returns - risk_free) / port_variance, marker='o')
    plt.grid(True)
    plt.xlabel('excepted volatility')
    plt.ylabel('expected return')
    plt.colorbar(label='Sharpe ratio')

    def statistics(weights):
        weights = np.array(weights)
        port_returns = np.sum(log_returns.mean() * weights) * 252
        port_variance = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 252, weights)))
        return np.array([port_returns, port_variance, port_returns / port_variance])

    # 最小化夏普指数的负值
    def min_sharpe(weights):
        return -statistics(weights)[2]

    # 约束是所有参数(权重)的总和为1。这可以用minimize函数的约定表达如下
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})


    #我们还将参数值(权重)限制在0和1之间。这些值以多个元组组成的一个元组形式提供给最小化函数
    bnds = tuple((0,1) for x in range(noa))


    opts = sco.minimize(min_sharpe, noa * [1./noa, ], method='SLSQP', bounds=bnds, constraints=cons)

    ##sharpe最大的组合3个统计数据分别为：
    # 预期收益率、预期波动率、最优夏普指数

    statistics(opts['x']).round(3)

    ##通过方差最小来选出最优投资组合。


    def min_variance(weights):
        return statistics(weights)[1]

    # 得到的预期收益率、波动率和夏普指数
    optv = sco.minimize(min_variance, noa * [1. / noa, ], method='SLSQP', bounds=bnds, constraints=cons)

    ##方差最小的最优组合权重向量及组合的统计数据分别为：
    optv['x'].round(3)
    x = statistics(optv['x']).round(3)

    #投资组合的有效边界（前沿）：优化时两个约束条件:1.给定目标收益率，2.投资组合权重和为1。
    # 在不同目标收益率水平（target_returns）循环时，最小化的一个约束条件会变化。
    target_returns = np.linspace(0.0, 0.5, 50)
    target_variance = []
    for tar in target_returns:
        cons = ({'type': 'eq', 'fun': lambda x: statistics(x)[0] - tar}, {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        res = sco.minimize(min_variance, noa * [1. / noa, ], method='SLSQP', bounds=bnds, constraints=cons)
        target_variance.append(res['fun'])
    target_variance = np.array(target_variance)

    #下面是最优化结果的展示。
    #叉号：构成的曲线是有效前沿（目标收益率下最优的投资组合）
    #红星：sharpe最大的投资组合
    #黄星：方差最小的投资组合
    plt.figure(figsize=(8, 4))
    # 圆圈：蒙特卡洛随机产生的组合分布
    plt.scatter(port_variance, port_returns, c=port_returns / port_variance, marker='o')
    # 叉号：有效前沿
    plt.scatter(target_variance, target_returns, c=target_returns / target_variance, marker='x')
    # 红星：标记最高sharpe组合
    plt.plot(statistics(opts['x'])[1], statistics(opts['x'])[0], 'r*', markersize=15.0)
    # 黄星：标记最小方差组合
    plt.plot(statistics(optv['x'])[1], statistics(optv['x'])[0], 'y*', markersize=15.0)
    plt.grid(True)
    plt.xlabel('expected volatility')
    plt.ylabel('expected return')
    plt.colorbar(label='Sharpe ratio')

    plt.show()

if __name__ == "__main__":
    main()
