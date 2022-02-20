# from utils import 
import streamlit as st
import pandas as pd
import numpy as np
from utils import *
from datafetcher import DataFetcher
import datetime
# Gobal Variables
stock_path = "/home/leo/Learning/Portfolio/data/holdings.csv"
mf_path = "/home/leo/Learning/Portfolio/data/MF_Data.csv"
temp_data_path = "/home/leo/Learning/Portfolio/temp_data"


def StockMetrics(portfolio):
    col1, col2, col3, col4 = st.columns(4)
    profit_per = portfolio.pl.sum()/portfolio.t_value.sum() * 100
    col1.metric("Gain",f"+{round(profit_per,2)}%")
    col2.metric("P&L in ₹ ", f"₹ {round(portfolio.pl.sum(),2)}")
    col3.metric("Current value of portfolio ₹",f"₹ {round(portfolio.cu_t_value.sum(),2)}")
    col4.metric("Invested value of portfolio ₹",f"₹ {round(portfolio.t_value.sum(),2)}")

def Overall_view():
    col1, col2,col3 = st.columns(3)

    equity_portfolio = portFolioFetcher(stock_path)
    in_debt,cu_debt,p_debt,p_debt_pert,in_equity,cur_equity,p_equity,p_equity_pert =mutual_fund(mf_path)
    
    total_invested  = in_debt +in_equity +equity_portfolio.t_value.sum()
    total_current = cu_debt +cur_equity +equity_portfolio.cu_t_value.sum()
    total_profit = total_current - total_invested
    total_profit_pert = total_profit / total_invested *100

    col1.metric("P&L in ₹ ", f"₹ {round(total_profit,2)}",delta=f"{round(total_profit_pert,2)} %")
    col2.metric("Total Current Value of Portfolio ₹",f"{round(total_current,2)}")
    col3.metric("Total Invested value of portfolio ₹",f"{round(total_invested,2)}")


    total_equity_invested = in_equity +equity_portfolio.t_value.sum()
    total_equity_current = cur_equity +equity_portfolio.cu_t_value.sum()
    total_non_equity_invested = in_debt
    total_non_equity_current = cu_debt

    ratio_invested_equity = total_equity_invested/total_invested *100
    ratio_current_equity = total_equity_current/total_current *100
    ratio_invested_debt = total_non_equity_invested/total_invested *100
    ratio_current_debt = total_non_equity_current/total_current *100

    d = {
        'Type':['Equity','Debt','Total'],
        'Invested':[total_equity_invested,total_non_equity_invested,total_invested],
        'Current':[total_equity_current,total_non_equity_current,total_current],
        'Ratio at Invested':[ratio_invested_equity,ratio_invested_debt,ratio_invested_equity+ratio_invested_debt],
        'Ratio at Current':[ratio_current_equity,ratio_current_debt,ratio_current_equity+ratio_current_debt],
    }
    
    result = pd.DataFrame(data=d)

    st.table(result)


# Layout of the Dashboard
if '__main__'==__name__:

    st.title("Portfolio Analysis 💰 !!")

    Overall_view()

    st.markdown(f'##### Mutual Fund Section')

    st.markdown(f'##### Equity Stock Market Section')
    equity_portfolio = portFolioFetcher(stock_path)

    StockMetrics(equity_portfolio)

    # Calculate the date
    start_date = (datetime.date.today() - datetime.timedelta(days = 90)).strftime('%d-%m-%Y')
    end_date = datetime.date.today().strftime('%d-%m-%Y')

    dataFetcher_obj = DataFetcher(equity_portfolio.symbols,start_date,end_date,temp_data_path)
    
    # dataFetcher_obj.fetcher() 
    result_dict = dataFetcher_obj.preprocess()

    # Chat of Equity Curve
    st.markdown(f"Analysis from the **{start_date}**  to **{end_date}** and variance {portfolio_variance(result_dict,equity_portfolio)}")

    quitycurve_df = equityCurve(result_dict,equity_portfolio)

    st.line_chart(data=quitycurve_df,height=400)



