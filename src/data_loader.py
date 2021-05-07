import pandas as pd
import streamlit as st
import traceback
import datetime
import logging
import numpy as np


class DataCaseOverall:
    def __init__(self, path_data):
        try:
            self.path_data = path_data
            self.data = pd.read_csv(path_data)
            self.data['date'] = self.data['Date_YMD'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
            self.data['date_str'] = self.data['date'].apply(lambda x: x.strftime("%d-%m-%Y"))

        except:
            st.error("Deployment in Progress! Please try again after sometimes.")
            error = st.beta_expander("Error Details")
            error.error(traceback.format_exc())
            st.stop()
    # @st.cache
    def preprocess(self):
        n = len(self.data)
        self.data = self.data[self.data['Total Confirmed'] > 1000]
        self.data['daily_confirmed'] = self.data['Daily Confirmed']
        self.data['total_active'] = self.data['Total Confirmed'] - self.data['Daily Recovered'] - self.data['Total Deceased']
        self.data['daily_recovered'] = self.data['Daily Recovered']

    # @st.cache
    def process(self, path_data):
        # Preprocessing dataset
        self.preprocess()
        

class DataCaseState:
    def __init__(self, path_data):
        try:
            self.path_data = path_data
            self.data = pd.read_csv(path_data)
            self.data['date'] = self.data['Date'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
            self.data['date_str'] = self.data['date'].apply(lambda x: x.strftime("%d-%m-%Y"))

        except:
            st.error("Deployment in Progress! Please try again after sometimes.")
            error = st.beta_expander("Error Details")
            error.error(traceback.format_exc())
            st.stop()

    # @st.cache
    def preprocess(self):
        self.data = self.data.sort_values(by=['State', 'date'])
        n = len(self.data)

        self.data['daily_recovered'] = self.data['Recovered']
        total_case = self.data['Confirmed'].values
        total_recover = self.data['Recovered'].values
        total_death = self.data['Deceased'].values
        total_tested = self.data['Tested'].values

        states = self.data['State'].values

        daily_case = [total_case[0]]
        daily_recovery = [total_recover[0]]
        daily_death = [total_death[0]]
        daily_test = [total_tested[0]]

        for i in range(1, n):
            if states[i] == states[i-1]:
                daily_case.append(total_case[i] - total_case[i-1])
                daily_recovery.append(total_recover[i] - total_recover[i-1])
                daily_death.append(total_death[i] - total_death[i-1])
                daily_test.append(total_tested[i] - total_tested[i-1])

            else:
                daily_case.append(total_case[i])
                daily_recovery.append(total_recover[i])
                daily_death.append(total_death[i])
                daily_test.append(total_tested[i])

            
        self.data['daily_recovery'] = daily_recovery
        self.data['daily_confirmed'] = daily_case
        self.data['daily_deceased'] = daily_death
        self.data['daily_test'] = daily_test
        
        self.data['daily_active'] = self.data['daily_confirmed'] - self.data['daily_recovery'] -self.data['daily_deceased']
        self.data['total_active'] = (self.data[f'Confirmed'] - self.data['Recovered']) -self.data['Deceased']
        # Growth data    
        self.data['percent_growth_active_case'] = np.round(self.data[f'daily_active']/self.data['total_active'], 4)

    # @st.cache
    def process(self):
        # Preprocessing dataset
        self.preprocess()
        


class DataTestState:
    def __init__(self, path_data):
        try:
            self.path_data = path_data
            self.data = pd.read_csv(path_data)

            n = len(self.data)
            self.data = self.data.dropna(subset=['Updated On'])
            n2 = len(self.data)
            logging.info(f'Number of NaNs in state wise testing on Updated on column: {n2-n}')

            self.data['date'] = self.data['Updated On'].apply(lambda x: datetime.datetime.strptime(x, "%d/%m/%Y"))
            self.data['date_str'] = self.data['date'].apply(lambda x: x.strftime("%d-%m-%Y"))

        except:
            st.error("Deployment in Progress! Please try again after sometimes.")
            error = st.beta_expander("Error Details")
            error.error(traceback.format_exc())
            st.stop()

    # @st.cache
    def preprocess(self):
        self.data['Total Tested'] = self.data['Total Tested'].fillna(0)
        n = len(self.data)
        self.data = self.data.sort_values(by=['State', 'date'])

        total_test = self.data['Total Tested'].values
        states = self.data['State'].values

        daily_test = [total_test[0]]

        for i in range(1, n):
            if states[i] == states[i-1]:
                daily_test.append(total_test[i] - total_test[i-1])
            else:
                daily_test.append(total_test[i])
            
        self.data['daily_test'] = daily_test
    
    # @st.cache
    def process(self):
        # Preprocessing dataset
        self.preprocess()
        

class DataTestOverall:
    def __init__(self, path_data):
        try:
            self.path_data = path_data
            self.data = pd.read_csv(path_data)
            n1 = len(self.data)
            self.data = self.data.dropna(subset=['Tested As Of'])
            n2 = len(self.data)
            logging.info(f'Number of NaNs removed in Overall Test Data on Tested As Of : {n2-n1}')

            self.data['Date'] = self.data['Tested As Of'].apply(lambda x: datetime.datetime.strptime(x, "%d/%m/%Y"))
            self.data['date_str'] = self.data['Date'].apply(lambda x: x.strftime("%d-%m-%Y"))

        except Exception as e:
            st.error("Deployment in Progress! Please try again after sometimes.")
            error = st.beta_expander(f"Error Details, Error: {e}")
            error.error(traceback.format_exc())
            st.stop()

    # @st.cache
    def preprocess(self):
        self.data['daily_test'] = self.data['Sample Reported today']
    
    # @st.cache
    def process(self):
        # Preprocessing dataset
        self.preprocess()
        