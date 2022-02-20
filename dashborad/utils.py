import pandas as pd
import os
import math
import numpy as np

def mutual_fund(mf_path):
    mf_df = pd.read_csv(mf_path)
    mf_debt = mf_df[mf_df['Type']=="Debt"]
    mf_equity = mf_df[mf_df['Type']=="Equity"]

    invested_debt = mf_debt.Invested.astype(int).sum()
    current_debt = mf_debt.Current_value.sum()
    profit_debt = current_debt - invested_debt
    profit_debt_pert = current_debt - invested_debt / invested_debt*100

    invested_equity = mf_equity.Invested.sum()
    current_equity = mf_equity.Current_value.sum()
    profit_equity = current_equity - invested_equity  
    profit_equity_pert = invested_equity - current_equity / invested_equity*100

    return invested_debt,current_debt,profit_debt,profit_debt_pert,invested_equity,current_equity,profit_equity,profit_equity_pert

def portFolioFetcher(path_csv):
    portfolio = pd.read_csv(path_csv)
    result = pd.DataFrame()
    # Take the list of symbols
    result['symbols'] = portfolio['Instrument']
    result['quntity'] = portfolio['Qty.']
    result['avg_price'] = portfolio['Avg. cost']
    result['t_value'] = portfolio['Qty.'] * portfolio['Avg. cost']
    result['cu_t_value'] = portfolio['LTP'] * portfolio['Qty.']
    result['pl'] = portfolio['P&L']
    result['wt'] = result['t_value']/result['t_value'].sum() *100
    return result

def equityCurve(result_dict,portfolio):
    data = dict()
    for symbols,values in result_dict.items():
        data[symbols] = values['daily_rt']+ portfolio.loc[portfolio['symbols'] == symbols]['wt'].values.astype(float)
    
    stock_normalize = pd.DataFrame(data)
    portfolio_normalize = stock_normalize.sum(axis=1)
    dates = pd.to_datetime(result_dict['ADANIGREEN']['dates'])
    portfolio_normalize = pd.concat([portfolio_normalize, dates], axis=1)
    portfolio_normalize.rename( columns={0:'Values'}, inplace=True )
    portfolio_normalize.set_index('Date',inplace=True)
    return portfolio_normalize


def portfolio_variance(result_dict,portfolio):
    wt_sd = {}
    corr = {}
    for symbols,values in result_dict.items():
        wt_sd[symbols] = values['variance']* portfolio.loc[portfolio['symbols'] == symbols]['wt'].values.astype(float)
        corr[symbols] = values['avg_daily_rt']
    corr = pd.DataFrame(corr)
    corr  = corr.corr()

    wt_sd = pd.DataFrame(wt_sd)

    portfolio_variance = np.round(np.squeeze(np.sqrt(np.dot(wt_sd.values,np.dot(corr,wt_sd.values.T)))),2)

    return portfolio_variance