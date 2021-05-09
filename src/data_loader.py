import traceback
import datetime
import logging

import numpy as np
import pandas as pd
import streamlit as st

import config


class DataCaseOverall:
    def __init__(self, path_data):
        try:
            self.path_data = path_data
            self.data = self.load_data(path_data)
            self.data['date'] = self.data['Date_YMD'].apply(
                lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").astimezone(config.tzinfo))
            self.data['date_str'] = self.data['date'].apply(
                lambda x: x.strftime("%d-%m-%Y"))

        except:
            st.error("Deployment in Progress! Please try again after sometimes.")
            error = st.beta_expander("Error Details")
            error.error(traceback.format_exc())
            st.stop()

    # @st.cache(ttl=60*60*24, allow_output_mutation=True)
    def load_data(self, path_data):
        return pd.read_csv(path_data)

    # @st.cache
    def preprocess(self):
        n = len(self.data)
        self.data = self.data[self.data['Total Confirmed'] > 1000]
        self.data['daily_confirmed'] = self.data['Daily Confirmed']
        self.data['total_active'] = self.data['Total Confirmed'] - \
            self.data['Daily Recovered'] - self.data['Total Deceased']
        self.data['daily_recovered'] = self.data['Daily Recovered']

    # @st.cache
    def process(self):
        # Preprocessing dataset
        self.preprocess()


class DataCaseState:
    def __init__(self, path_data):
        try:
            self.path_data = path_data
            self.data = self.load_data(path_data)
            self.data['date'] = self.data['Date'].apply(
                lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").astimezone(config.tzinfo))
            self.data['date_str'] = self.data['date'].apply(
                lambda x: x.strftime("%d-%m-%Y"))

        except:
            st.error("Deployment in Progress! Please try again after sometimes.")
            error = st.beta_expander("Error Details")
            error.error(traceback.format_exc())
            st.stop()

    # @st.cache(ttl=60*60*24, allow_output_mutation=True)
    def load_data(self, path_data):
        return pd.read_csv(path_data)

    # @st.cache
    def preprocess(self):
        self.data.sort_values(by=['State', 'date'], inplace=True)
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

        self.data['daily_active'] = self.data['daily_confirmed'] - \
            self.data['daily_recovery'] - self.data['daily_deceased']
        self.data['total_active'] = (
            self.data[f'Confirmed'] - self.data['Recovered']) - self.data['Deceased']
        # Growth data
        self.data['percent_growth_active_case'] = np.round(
            self.data[f'daily_active']/self.data['total_active'], 4)

    # @st.cache
    def process(self):
        # Preprocessing dataset
        self.preprocess()


class DataTestState:
    def __init__(self, path_data):
        try:
            self.path_data = path_data
            self.data = self.load_data(path_data)

            n = len(self.data)
            self.data = self.data.dropna(subset=['Updated On'])
            n2 = len(self.data)
            self.data.fillna(0, inplace=True)

            logging.info(
                f'Number of NaNs in state wise testing on Updated on column: {n-n2}')

            self.data['date'] = self.data['Updated On'].apply(
                lambda x: datetime.datetime.strptime(x, "%d/%m/%Y").astimezone(config.tzinfo))
            self.data['date_str'] = self.data['date'].apply(
                lambda x: x.strftime("%d-%m-%Y"))

        except:
            st.error("Deployment in Progress! Please try again after sometimes.")
            error = st.beta_expander("Error Details")
            error.error(traceback.format_exc())
            st.stop()

    # @st.cache(ttl=60*60*24, allow_output_mutation=True)
    def load_data(self, path_data):
        return pd.read_csv(path_data)

    # @st.cache
    def preprocess(self):
        self.data['Total Tested'] = self.data['Total Tested'].fillna(0)
        n = len(self.data)
        self.data.sort_values(by=['State', 'date'], inplace=True)

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
            self.data = self.load_data(path_data)
            n1 = len(self.data)
            self.data = self.data.dropna(subset=['Tested As Of'])
            self.data.fillna(0, inplace=True)
            n2 = len(self.data)
            logging.info(
                f'Number of NaNs removed in Overall Test Data on Tested As Of : {n1-n2}')

            self.data['date'] = self.data['Tested As Of'].apply(
                lambda x: datetime.datetime.strptime(x, "%d/%m/%Y").astimezone(config.tzinfo))
            self.data['date_str'] = self.data['date'].apply(
                lambda x: x.strftime("%d-%m-%Y"))

        except Exception as e:
            st.error("Deployment in Progress! Please try again after sometimes.")
            error = st.beta_expander(f"Error Details, Error: {e}")
            error.error(traceback.format_exc())
            st.stop()

    # @st.cache(ttl=60*60*24, allow_output_mutation=True)
    def load_data(self, path_data):
        return pd.read_csv(path_data)

    # @st.cache
    def preprocess(self):
        self.data['daily_test'] = self.data['Sample Reported today']

    # @st.cache
    def process(self):
        # Preprocessing dataset
        self.preprocess()


class DataVaccineState:
    def __init__(self, path_data):
        try:
            self.path_data = path_data
            self.data = self.load_data(path_data)

            n1 = len(self.data)
            self.data = self.data.dropna(subset=['Updated On'])
            n2 = len(self.data)
            logging.info(
                f'Number of NaNs removed in Overall Vaccine Data on Tested As Of : {n2-n1}')

            self.data['date'] = self.data['Updated On'].apply(
                lambda x: datetime.datetime.strptime(x, "%d/%m/%Y").astimezone(config.tzinfo))
            self.data['date_str'] = self.data['date'].apply(
                lambda x: x.strftime("%d-%m-%Y"))

            self.data.fillna(0, inplace=True)
            # self.data['date'] = self.data['Date_YMD'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
            # self.data['date_str'] = self.data['date'].apply(lambda x: x.strftime("%d-%m-%Y"))

        except:
            st.error("Deployment in Progress! Please try again after sometimes.")
            error = st.beta_expander("Error Details")
            error.error(traceback.format_exc())
            st.stop()

    # @st.cache(ttl=60*60*24, allow_output_mutation=True)
    def load_data(self, path_data):
        return pd.read_csv(path_data)

    # @st.cache
    def preprocess(self):
        self.data.sort_values(by=['State', 'date'], inplace=True)
        n = len(self.data)

        total_vaccine = self.data['Total Doses Administered'].values
        total_covaxin = self.data['Total Covaxin Administered'].values
        total_covidshield = self.data['Total Covaxin Administered'].values

        total_18_30 = self.data['18-30 years (Age)'].values
        total_30_45 = self.data['30-45 years (Age)'].values
        total_45_60 = self.data['45-60 years (Age)'].values
        total_60_100 = self.data['60+ years (Age)'].values

        total_male = self.data['Male(Individuals Vaccinated)'].values
        total_female = self.data['Female(Individuals Vaccinated)'].values
        total_trans = self.data['Transgender(Individuals Vaccinated)'].values

        total_first = self.data['First Dose Administered'].values
        total_second = self.data['Second Dose Administered'].values

        total_sites = self.data['Total Sites '].values

        states = self.data['State'].values

        daily_vaccine = [total_vaccine[0]]
        daily_covaxin = [total_covaxin[0]]
        daily_covidshield = [total_covidshield[0]]

        daily_18_30 = [total_18_30[0]]
        daily_30_45 = [total_30_45[0]]
        daily_45_60 = [total_45_60[0]]
        daily_60_100 = [total_60_100[0]]

        daily_male = [total_male[0]]
        daily_female = [total_female[0]]
        daily_trans = [total_trans[0]]

        daily_first = [total_first[0]]
        daily_second = [total_second[0]]

        daily_sites = [total_sites[0]]

        for i in range(1, n):
            if states[i] == states[i-1]:
                daily_vaccine.append(max(total_vaccine[i] - total_vaccine[i-1], 0))
                daily_covaxin.append(max(total_covaxin[i] - total_covaxin[i-1], 0))
                daily_covidshield.append(max(
                    total_covidshield[i] - total_covidshield[i-1], 0))

                daily_18_30.append(max(total_18_30[i] - total_18_30[i-1], 0))
                daily_30_45.append(max(total_30_45[i] - total_30_45[i-1], 0))
                daily_45_60.append(max(total_45_60[i] - total_45_60[i-1], 0))
                daily_60_100.append(max(total_60_100[i] - total_60_100[i-1], 0))

                daily_male.append(max(total_male[i] - total_male[i-1], 0))
                daily_female.append(max(total_female[i] - total_female[i-1], 0))
                daily_trans.append(max(total_trans[i] - total_trans[i-1], 0))

                daily_first.append(max(total_first[i] - total_first[i-1], 0))
                daily_second.append(max(total_second[i] - total_second[i-1], 0))

                daily_sites.append(max(total_sites[i] - total_sites[i-1], 0))

            else:
                daily_vaccine.append(total_vaccine[i])
                daily_covaxin.append(total_covaxin[i])
                daily_covidshield.append(total_covidshield[i])

                daily_18_30.append(total_18_30[i])
                daily_30_45.append(total_30_45[i])
                daily_45_60.append(total_45_60[i])
                daily_60_100.append(total_60_100[i])

                daily_male.append(total_male[i])
                daily_female.append(total_male[i])
                daily_trans.append(total_male[i])

                daily_first.append(total_first[i])
                daily_second.append(total_second[i])

                daily_sites.append(total_sites[i])

        self.data['total_vaccine'] = total_vaccine
        self.data['total_covaxin'] = total_covaxin
        self.data['total_covidshield'] = total_covidshield

        self.data['daily_vaccine'] = daily_vaccine
        self.data['daily_covaxin'] = daily_covaxin
        self.data['daily_covidshield'] = daily_covidshield

        self.data['daily_18_30'] = daily_18_30
        self.data['daily_30_45'] = daily_30_45
        self.data['daily_45_60'] = daily_45_60
        self.data['daily_60_100'] = daily_60_100

        self.data['daily_male'] = daily_male
        self.data['daily_female'] = daily_female
        self.data['daily_trans'] = daily_trans

        self.data['daily_first'] = daily_first
        self.data['daily_second'] = daily_second

        self.data['daily_sites'] = daily_sites

    # @st.cache

    def process(self):
        # Preprocessing dataset
        self.preprocess()
