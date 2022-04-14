# from utils import 
import streamlit as st
import pandas as pd
import numpy as np
from utils import *
from datafetcher import DataFetcher
import datetime
st.set_page_config(layout="wide")



def stockMetrics(portfolio):
    col1, col2, col3 = st.columns(3)
    profit_per = portfolio.pl.sum()/portfolio.t_value.sum() * 100
    col1.metric("P&L in ₹ ", f"₹ {round(portfolio.pl.sum(),2)}",delta =f"{round(profit_per,2)}%")
    col2.metric("Current value of portfolio ₹",f"{round(portfolio.cu_t_value.sum(),2)}")
    col3.metric("Invested value of portfolio ₹",f"{round(portfolio.t_value.sum(),2)}")

def overallView(comp_portfolio):
    col1, col2,col3 = st.columns(3)


    col1.metric("P&L in ₹ ", f"{comp_portfolio['total_profit']}",delta=f"{comp_portfolio['total_profit_pert']} %")
    col2.metric("Total Current Value of Portfolio ₹",f"{comp_portfolio['total_current']}")
    col3.metric("Total Invested value of portfolio ₹",f"{comp_portfolio['total_invested']}")
    st.table(comp_portfolio['portfolio_df'])

    with st.expander('Investment calculator :-'):
        col1, col2 = st.columns([4, 1])

        amount = col1.number_input("Amount to invest :-", min_value=100, max_value=None, value=10000, step=1000)
        ratio = col2.number_input("Ratio :-", min_value=0, max_value=100, value=85, step=5)/100
        new_results = portfolio_adj(comp_portfolio['portfolio_df'],amount,ratio)
        st.table(new_results)
    

def mfShow(mf_metadate):
    col1, col2 = st.columns([1, 3])

    col1.metric("P&L in ₹ ", f"{round(mf_metadate['total_profit'],2)}",delta=f"{round(mf_metadate['total_profit_pert'],2)} %")   
    col2.table(mf_metadate['deb_equity_table'])

    with st.expander('More details on MF:-'):
        col1, col2 = st.columns(2)

        col1.markdown('Equity MF')
        col1.table(mf_metadate['mf_equity'])

        col2.markdown('Debt MF')
        col2.table(mf_metadate['mf_debt'])

def FetchData(symbols,start_date,end_date,temp_data_path,isNew=False):
    dataFetcher_obj = DataFetcher(symbols.values,start_date,end_date,temp_data_path)
    if isNew:
        dataFetcher_obj.fetcher() 
    result_dict = dataFetcher_obj.preprocess()
    return result_dict


# Layout of the Dashboard
if '__main__'==__name__:

    # Gobal Variables
    stock_path = "/home/leo/FinTech/Portfolio/data/holdings.csv"
    mf_path = "/home/leo/FinTech/Portfolio/data/MF_Data.csv"
    temp_data_path = "/home/leo/FinTech/Portfolio/temp_data"
    symbols_to_igonre=['GOLDBEES', 'ICICIGOLD']
    isNew = False
    pd.set_option('display.float_format', '{:.2f}'.format)

    # Calculate the date
    start_date = (datetime.date.today() - datetime.timedelta(days = 365))
    end_date = datetime.date.today()

    # Take the Symbols
    symbols = symbol_extract(stock_path,symbols_to_igonre)
    result_dict = FetchData(symbols,start_date.strftime('%d-%m-%Y'),end_date.strftime('%d-%m-%Y'),temp_data_path,isNew=isNew)
    equity_portfolio = portFolioFetcher(stock_path,symbols_to_igonre,temp_data_path)
    mf_portfolio = mutual_fund(mf_path)
    comp_portfolio = overall_portfolio(equity_portfolio,mf_portfolio)


    st.title("Portfolio Analysis 💰 !!")
    st.subheader(datetime.date.today().strftime("%B %d, %Y"))
    overallView(comp_portfolio)

    st.markdown(f'##### Mutual Fund Section')
    mfShow(mf_portfolio)

    st.markdown(f'##### Equity Stock Market Section')
    stockMetrics(equity_portfolio)

    # Chat of Equity Curve
    st.markdown(f" #### Analysis from the *{start_date.strftime('%d %B, %Y')}*  to *{end_date.strftime('%d %B , %Y')}* and variance {portfolio_variance(result_dict,equity_portfolio)}")
    quitycurve_df = equityCurve(result_dict,equity_portfolio)
    st.line_chart(data=quitycurve_df,height=400)

    
    value_at_risk(quitycurve_df)


