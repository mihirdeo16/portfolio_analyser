import pandas as pd
import os
import math
import numpy as np

pd.set_option('display.float_format', '{:.2f}'.format)

import streamlit as st
@st.cache  # 👈 Added this
def portfolio_adj(df,x,split):

    new_total = df[df['Type']=='Total']['Current'].values + x

    new_equ = new_total * split
    new_debt = new_total - new_equ

    new_diff_equity = new_equ - df[df['Type']=='Equity']['Current'].values
    new_diff_debt = new_debt - df[df['Type']=='Debt']['Current'].values

    df['Current Value(New)'] =[float(new_equ),float(new_debt),float(new_total)]
    df['Investment Split '] =[float(new_diff_equity),float(new_diff_debt),float(new_diff_equity+new_diff_debt)]
    df['Ratio New(Current)'] =[float(new_equ/new_total *100),float(new_debt/new_total *100),float((new_equ/new_total *100)+(new_debt/new_total *100))] 
    df.drop(columns=['Investment','Current'],inplace=True)

    return df

def mutual_fund(mf_path):
    mf_df = pd.read_csv(mf_path)
    mf_debt = mf_df[mf_df['Type']=="Debt"]
    mf_equity = mf_df[mf_df['Type']=="Equity"]

    invested_debt = mf_debt.Invested.astype(int).sum()
    current_debt = mf_debt.Current_value.sum()
    profit_debt = current_debt - invested_debt
    profit_debt_pert = profit_debt / invested_debt*100

    invested_equity = mf_equity.Invested.sum()
    current_equity = mf_equity.Current_value.sum()
    profit_equity = current_equity - invested_equity  
    profit_equity_pert = profit_equity / invested_equity*100

    total_profit = mf_df.Current_value.sum() - mf_df.Invested.sum() 
    total_profit_pert = total_profit/ mf_df.Invested.sum() *100

    temp_d = {
        'Type':['Debt','Equity','Total'],
        'Invested':[invested_debt,invested_equity,mf_df.Current_value.sum()],
        "Current":[current_debt,current_equity,mf_df.Current_value.sum()],
        "Profit":[profit_debt,profit_equity,total_profit],
        "Profit in %":[profit_debt_pert,profit_equity_pert,total_profit_pert]
    }

    deb_equity_table = pd.DataFrame(data=temp_d)

    mf_metadate = {
        'mf_debt':mf_debt[['MF_NAME','Provider','Handler','Invested']],
        'invested_debt':invested_debt,
        'current_debt':current_debt,
        'profit_debt':profit_debt,
        'profit_debt_pert':profit_debt_pert,

        'mf_equity':mf_equity[['MF_NAME','Provider','Handler','Invested']],
        'invested_equity':invested_equity,
        'current_equity':current_equity,
        'profit_equity':profit_equity,
        'profit_equity_pert':profit_equity_pert,

        'total_profit':total_profit,
        'total_profit_pert':total_profit_pert,
        'deb_equity_table':deb_equity_table
    }

    return mf_metadate

def current_values(df,temp_data_path):

    current_value = []

    for symbol in df.symbols:
            path = os.path.join(temp_data_path,symbol+".csv")
            temp = pd.read_csv(path)
            current_value.append(temp['Close Price'].values[-1])

    return current_value

def symbol_extract(path_csv,symbols_to_igonre):

    portfolio = pd.read_csv(path_csv)
    portfolio = portfolio[~portfolio['Instrument'].isin(symbols_to_igonre)]

    symbols = portfolio.Instrument

    return symbols

def portFolioFetcher(path_csv,symbols_to_igonre,temp_data_path):
    portfolio = pd.read_csv(path_csv)
    portfolio = portfolio[~portfolio['Instrument'].isin(symbols_to_igonre)]
    result = pd.DataFrame()
    # Take the list of symbols
    result['symbols'] = portfolio['Instrument']
    result['quntity'] = portfolio['Qty.']
    result['avg_price'] = portfolio['Avg. cost']
    result['t_value'] = portfolio['Qty.'] * portfolio['Avg. cost']
    
    result['cu_t_value'] = current_values(result,temp_data_path) * portfolio['Qty.']

    result['pl'] = result['cu_t_value'] - result['t_value']

    result['wt'] = result['t_value']/result['t_value'].sum() *100

    return result

def equityCurve(result_dict,portfolio):
    data = dict()
    for symbols,values in result_dict.items():
        data[symbols] = (pd.Series(values['daily_rt']) +1)* portfolio.loc[portfolio['symbols'] == symbols]['wt'].values.astype(float)
    
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


def value_at_risk(df):
    daily_rt = df.Values.pct_change() * 100

    max_rt = daily_rt.max()
    min_rt = daily_rt.min()
    count = daily_rt.shape[0]

    print(max_rt,min_rt,count)

def overall_portfolio(equity_portfolio,mf_metadate):
    
    total_invested  = mf_metadate['invested_debt'] + mf_metadate['invested_equity'] +equity_portfolio.t_value.sum()
    total_current = mf_metadate['current_debt'] + mf_metadate['current_equity'] +equity_portfolio.cu_t_value.sum()
    total_profit = total_current - total_invested
    total_profit_pert = total_profit / total_invested *100

    total_equity_invested = mf_metadate['invested_equity'] +equity_portfolio.t_value.sum()
    total_equity_current = mf_metadate['current_equity'] +equity_portfolio.cu_t_value.sum()
    total_non_equity_invested = mf_metadate['invested_debt']
    total_non_equity_current = mf_metadate['current_debt']

    ratio_invested_equity = total_equity_invested/total_invested *100
    ratio_current_equity = total_equity_current/total_current *100
    ratio_invested_debt = total_non_equity_invested/total_invested *100
    ratio_current_debt = total_non_equity_current/total_current *100

    temp_d = {
        'Type':['Equity','Debt','Total'],
        'Investment':[total_equity_invested,total_non_equity_invested,total_invested],
        'Current':[total_equity_current,total_non_equity_current,total_current],
        'Ratio at Investment':[ratio_invested_equity,ratio_invested_debt,ratio_invested_equity+ratio_invested_debt],
        'Ratio at Current':[ratio_current_equity,ratio_current_debt,ratio_current_equity+ratio_current_debt],
    }
    
    portfolio_df = pd.DataFrame(data=temp_d)

    return {
        'total_profit':round(total_profit,2),
        'total_profit_pert':round(total_profit_pert,2),
        'total_current':total_current,
        'total_invested':round(total_invested,2),
        'portfolio_df':portfolio_df
    }
