import os 
from NSEDownload import stocks
from NSEDownload import indices
import pandas as pd
import math
import sys
pd.set_option('display.float_format', '{:.10f}'.format)

class DataFetcher:
    
    def __init__(self,symbols,start_date,end_date,temp_data_path):
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.path_to_store = temp_data_path
        self.indice = "NIFTY 50"
    
    def raw_fetcher(self,symbol):
        df = stocks.get_data(stockSymbol = symbol, 
                            start_date = self.start_date,
                            end_date = self.end_date)

        df.reset_index(inplace=True)
        return df
    
    def data_indice(self):
        ref_data = indices.get_data(indexName = self.indice,start_date=self.start_date,end_date=self.end_date)
        ref_data.reset_index(inplace=True)
        ref_date = pd.to_datetime(ref_data['Date'])
        ref_data.to_csv(f"{self.path_to_store}/{self.indice}.csv",index=False)

        return ref_date


    def data_validator(self,df,ref_date):
        temp = pd.merge(df,ref_date,how='right',left_on='Date',right_on ='Date')
        temp.fillna(method="bfill",inplace=True)
        temp.fillna(method="ffill",inplace=True)
        return temp

    def preprocess(self):
        _dict = {}

        for symbol in self.symbols:

            path = os.path.join(self.path_to_store,str(symbol)+".csv")
            df = pd.read_csv(path)

            # Daily return values
            daily_rt = (df['Close Price']/df['Prev Close'] -1 )*100

            # Variance  Formula - (daily returns - Avg Daily return)**2 / No. of Days
            variance = sum((daily_rt - daily_rt.mean())**2 ) /df.shape[0]
            std_deviation = math.sqrt(variance)
            avg_daily_rt = daily_rt - daily_rt.mean() 

            _dict[symbol] = {
                        'avg_daily_rt':list(avg_daily_rt),
                        'daily_rt':list(daily_rt),
                        'dates':df.Date,
                        'close_price':df['Close Price'],
                        'variance':variance,
                        'std_deviation':std_deviation }

        return _dict


    def fetcher(self):
        ref_date = self.data_indice()
        result_dict = {}
        issue_sysmbol = []
        for sym in self.symbols:
            try:
                df = self.raw_fetcher(sym)
                df = self.data_validator(df, ref_date)
                # Gets data without adjustment for events
                df.to_csv(f"{self.path_to_store}/{sym}.csv",index=False)
            except:
                print("Got error on following Company -> ",sym)
                issue_sysmbol.append(sym)
        if len(issue_sysmbol) != 0:
            print(f'\n\n Please manually put the following instruments in temp_data folder {issue_sysmbol}')

            flag = input(f'Please download the CSV file from - https://www.nseindia.com/get-quotes/equity?symbol=JSWENERGY website, from {self.start_date} to {self.end_date} \n Once done please continue or exit -> y/n \t')

            if flag=='y':
                symbols = [x for x in issue_sysmbol if str(x) != 'nan']
                for sym in symbols:

                    path = os.path.join(self.path_to_store,sym+".csv")
                    df = pd.read_csv(path)
                    df.rename(columns={'Date ':'Date','close ':'Close Price',
                                        'PREV. CLOSE ':'Prev Close'},inplace=True)

                    df = self.raw_fetcher(sym)
                    df = self.data_validator(df, ref_date)
                    df.to_csv(f"{self.path_to_store}/{sym}.csv",index=False)

            else:
                sys.exit()







