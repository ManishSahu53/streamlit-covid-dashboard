# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import datetime
import traceback
import logging

import config
from src import util
from src import data_loader
from src import custom_plot

import numpy as np
import pandas as pd

import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title='COVID-19 India Dashboard',
                   page_icon=":chart_with_upwards_trend:",
                   layout='wide', initial_sidebar_state='collapsed')


st.title('COVID-19: Situation in India', )

LINE = """<style>
.vl {
  border-left: 2px solid black;
  height: 200px;
  position: absolute;
  left: 50%;
  margin-left: -3px;
  top: 0;
}
</style>
<div class="vl"></div>"""


@st.cache(ttl=60*60*24, allow_output_mutation=True)
def calculate_moving_average(data_time_series):
    n = len(data_time_series)
    feature = ['Daily Confirmed', 'Total Confirmed', 'Daily Recovered',
               'Total Recovered', 'Daily Deceased', 'Total Deceased']

    ma_day = 7
    for f in feature:
        temp_data = data_time_series[f].values
        temp_feature = f'{ma_day}day MA {f}'

        temp_processed = util.moving_average(
            temp_data, feature_name=f, ma=ma_day)
        data_time_series[temp_feature] = [0]*ma_day + temp_processed

    data_time_series = data_time_series[data_time_series[f'{ma_day}day MA Daily Confirmed'] > 0]
    n = len(data_time_series)

    data_time_series[f'{ma_day}day MA total_active'] = data_time_series['Total Confirmed'] - \
        data_time_series[f'{ma_day}day MA Total Recovered'] - \
        data_time_series[f'{ma_day}day MA Total Deceased']
    data_time_series[f'{ma_day}day MA daily_active'] = data_time_series['Daily Confirmed'] - \
        data_time_series[f'{ma_day}day MA Daily Recovered'] - \
        data_time_series[f'{ma_day}day MA Daily Deceased']

    data_time_series['percent_growth_active_case'] = np.round(
        data_time_series[f'{ma_day}day MA daily_active']/data_time_series[f'{ma_day}day MA total_active'], 4)

    return data_time_series


# Loading Overall Dataset of cases, recoveries
data_time_series_cls = data_loader.DataCaseOverall(
    config.path_cases_overall_timeseries)
data_time_series_cls.process()
data_time_series = data_time_series_cls.data

# Loading State wise Dataset of cases, reoveries
data_state_cls = data_loader.DataCaseState(
    config.path_cases_state_wise_timeseries)
data_state_cls.process()
data_state = data_state_cls.data

# Loading Overall Dataset of Corona Tests
data_tested_overall_cls = data_loader.DataTestOverall(
    config.path_test_overall_timeseries)
data_tested_overall_cls.process()
data_tested_overall = data_tested_overall_cls.data

# Loading State wise Dataset of Corona Tests
data_tested_state_cls = data_loader.DataTestState(
    config.path_test_state_wise_timeseries)
data_tested_state_cls.process()
data_tested_state = data_tested_state_cls.data

# Positivity Rate
columns = ['date_str', 'Daily Confirmed', 'daily_test']
data_positivity = pd.merge(data_time_series_cls.data, data_tested_overall_cls.data, on=[
                           'date_str'], how='left')[columns]

data_time_series = calculate_moving_average(data_time_series=data_time_series)

# Calculating Yesterday date
tzinfo = datetime.timezone(datetime.timedelta(hours=config.TIMEZONE_OFFSET))
current_date = datetime.datetime.now(
    tzinfo) - datetime.timedelta(1, minutes=0, hours=12)

logging.info(f'Processing for Date: {current_date}')

default_what_map = {'Infection': 0, 'Vaccines': 1}

col1, col2, _, col3 = st.beta_columns([2, 2, 8, 1, ])
query_params = st.experimental_get_query_params()

col3.write("**[Linkedin](https://www.linkedin.com/in/manishsahuiitbhu/)<br>[:beer:]**",
           unsafe_allow_html=True)
options = ['Infection', 'Vaccines']

what = col1.radio('Type of Data', options)
area = col2.selectbox("Region", list(config.POPULATION_MAP.keys()))

if what == 'Infection':
    st.header('Real time data updated till {}'.format(
        current_date.strftime('%Y-%m-%d')))

    col1, line, col3, col4, col5, col6, col7, col8 = st.beta_columns(
        [10, 1, 8, 8, 8, 8, 8, 8])
    line.markdown(LINE, unsafe_allow_html=True)

    # Loading Full india or State wise
    if area == 'India':
        daily_overall = data_time_series[data_time_series['date_str'] == current_date.strftime(
            '%d-%m-%Y')]
        daily_test_overall = data_tested_overall_cls.data[data_tested_overall_cls.data['date_str'] == current_date.strftime(
            '%d-%m-%Y')]
    else:
        data_state = data_state[(data_state['date_str'] == current_date.strftime(
            '%d-%m-%Y')) & (data_state['State'] == area)]
        daily_test_state = data_tested_state_cls.data[(data_tested_state_cls.data['date_str'] == current_date.strftime(
            '%d-%m-%Y')) & (data_tested_state_cls.data['State'] == area)]

    with col1:
        rule = st.radio('', list(config.RULE_MAP.keys()))
        st.write('')
        log = st.checkbox('Log Scale', False)

    # Daily Confirmed Cases
    with col3:
        st.markdown("<h3 style='text-align: center;'>Daily Cases</h2>",
                    unsafe_allow_html=True)

        if area.lower() == 'india':
            try:
                value = daily_overall['Daily Confirmed'].values[0]
            except Exception as e:
                logging.error(
                    f'Error: {e}. Cannot get data for overall India, Date: {current_date}')
                value = 0

        else:
            try:
                value = data_state['daily_confirmed'].values[0]
            except Exception as e:
                logging.error(
                    f'Error: {e}. Cannot get data for State level wise, Date: {current_date}')
                value = 0

        temp_confirmed = custom_plot.normalisation(
            value, config.POPULATION_MAP[area], rule)
        text = f'{temp_confirmed:.2f}' if config.RULE_MAP[
            rule] == 'percentage' else f'{int(temp_confirmed):,}'

        st.markdown(
            f"<h2 style='text-align: center; color: red;'>{text}</h1>", unsafe_allow_html=True)

    # Daily Deaths
    with col4:
        st.markdown("<h3 style='text-align: center;'>Daily Deceased</h2>",
                    unsafe_allow_html=True)

        if area.lower() == 'india':
            value = daily_overall['Daily Deceased'].values[0]
        else:
            value = data_state['daily_deceased'].values[0]

        temp_death = custom_plot.normalisation(
            value, config.POPULATION_MAP[area], rule)
        text = f'{temp_death:.2f}' if config.RULE_MAP[
            rule] == 'percentage' else f'{int(temp_death):,}'
        # print(plot.RULE_MAP[rule] == 'percentage')
        st.markdown(
            f"<h2 style='text-align: center; color: red;'>{text}</h1>", unsafe_allow_html=True)

    # Daily Recovered
    with col5:
        st.markdown("<h3 style='text-align: center;'>Daily Recovery</h2>",
                    unsafe_allow_html=True)

        if area.lower() == 'india':
            value = daily_overall['Daily Recovered'].values[0]
        else:
            value = data_state['daily_recovery'].values[0]

        temp_recovered = custom_plot.normalisation(
            value, config.POPULATION_MAP[area], rule)
        text = f'{temp_recovered:.2f}' if config.RULE_MAP[
            rule] == 'percentage' else f'{int(temp_recovered):,}'
        st.markdown(
            f"<h2 style='text-align: center; color: red;'>{text}</h1>", unsafe_allow_html=True)

    # Daily Tested
    with col6:
        st.markdown("<h3 style='text-align: center;'>Daily Tests</h2>",
                    unsafe_allow_html=True)

        if area.lower() == 'india':
            value = daily_test_overall['daily_test'].values[0]
        else:
            value = daily_test_state['daily_test'].values[0]

        # logging.info('value, config.POPULATION_MAP[area], rule', int(value), config.POPULATION_MAP[area], rule)
        temp_test = custom_plot.normalisation(
            value, config.POPULATION_MAP[area], rule)

        text = f'{temp_test:.2f}' if config.RULE_MAP[
            rule] == 'percentage' else f'{int(temp_test):,}'
        st.markdown(
            f"<h2 style='text-align: center; color: red;'>{text}</h1>", unsafe_allow_html=True)

    # Total Recovered
    with col7:
        st.markdown("<h3 style='text-align: center;'>Total Recovered</h2>",
                    unsafe_allow_html=True)

        if area.lower() == 'india':
            value = daily_overall['Total Recovered'].values[0]
        else:
            value = data_state['Recovered'].values[0]

        ingressi = custom_plot.normalisation(
            value, config.POPULATION_MAP[area], rule)
        text = f'{ingressi:.2f}' if config.RULE_MAP[
            rule] == 'percentage' else f'{int(ingressi):,}'
        st.markdown(
            f"<h2 style='text-align: center; color: red;'>{text}</h1>", unsafe_allow_html=True)

    if area == 'India':
        graph_data = data_time_series
    else:
        graph_data = data_state_cls.data[data_state_cls.data['State'] == area]

    x = graph_data['date'][-365:].values
    y = graph_data['daily_confirmed'][-365:].values
    y2 = graph_data['daily_recovered'][-365:].values

    if log:
        x = x
        y = np.log(y)
        y2 = np.log(y2)

    fig2 = px.line(y=y,
                   x=x,
                   title='Daily New Cases',
                   labels={'y': 'Daily New Cases',
                           'wide_variable_1': 'Daily Rocoveries',
                           'x': 'Time Period'},
                   line_shape='spline',
                   )

    fig2.add_vline(x='2020-09-16',
                   line_width=1,
                   line_dash="dash",
                   line_color="Orange")

    fig2.add_vline(x='2021-02-18',
                   line_width=1,
                   line_dash="dash",
                   line_color="Red")

    fig2.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        dragmode=False,
        plot_bgcolor="white",
    )
    st.plotly_chart(fig2, use_container_width=True)

    ########################### Second Chart #################################
    fig = px.area(y=100*graph_data['percent_growth_active_case'].rolling(7).mean()[-365:].values,
                  x=graph_data['date'][-365:].values,
                  title='Overall India Growth Rate of Active Cases (7 Day Moving Average)',
                  labels={'y': '% Growth Active Case',
                          'x': 'Time Period'},
                  line_shape='spline',
                  )

    fig.add_hline(y=0,
                  line_width=1,
                  line_dash="dash",
                  line_color="Green",
                  annotation_text="Recovery > Cases",
                  annotation_position="bottom left",
                  )

    fig.add_vline(x='2020-09-16',
                  line_width=1,
                  line_dash="dash",
                  line_color="Orange")

    fig.add_vline(x='2021-02-18',
                  line_width=1,
                  line_dash="dash",
                  line_color="Red")

    fig.update_layout(legend=dict(bgcolor='rgba(0,0,0,0)'),
                      xaxis_fixedrange=True,
                      yaxis_fixedrange=True,
                      dragmode=False,
                      plot_bgcolor="white",)
    st.plotly_chart(fig, use_container_width=True)

    ########################### Third Chart #################################
    rule = st.selectbox('Variables', [
                        'Daily Recovery', 'Daily New Cases', 'Daily Deaths', 'Daily Test', 'Daily Active Cases'])
    st.plotly_chart(custom_plot.summary(
        data_state_cls.data, rule), use_container_width=True)

elif what == 'Vaccines':
    # Loading Vaccine Dataset
    data_vaccine_cls = data_loader.DataVaccineState(
        config.path_vaccine_state_wise_cowin)
    data_vaccine_cls.process()

    st.header('Real time data updated till {}'.format(
        current_date.strftime('%Y-%m-%d')))

    # Loading Full india or State wise
    data_vaccine = data_vaccine_cls.data[data_vaccine_cls.data['State'] == area]

    pie1, title1, line, pie2, title2, title3, title4 = st.beta_columns([
                                                                       2, 4, 1, 2, 4, 4, 4])
    line.markdown(LINE, unsafe_allow_html=True)

    # Total Individuals Vaccinated
    with pie1:
        total_population = config.POPULATION_MAP[area]
        vaccine_population = data_vaccine['Total Individuals Vaccinated'].values[-1]
        labels = ['Population Vaccinated',  'Populaton not Vaccinated']
        x = vaccine_population
        y = total_population - vaccine_population

        st.plotly_chart(custom_plot.plot_population(
            [x, y], labels, area, height=180, t=0), use_container_width=True)

    # Total Individuals Vaccinated
    with title1:
        st.markdown("<h3 style='text-align: center;'>Total Person Vaccinated</h2>",
                    unsafe_allow_html=True)

        value = int(data_vaccine['Total Individuals Vaccinated'].values[-1])
        st.markdown(
            f"<h1 style='text-align: center; color: red;'>{value:,}</h1>", unsafe_allow_html=True)

    # Type of Vaccines Administered
    with pie2:
        x = data_vaccine['Total Covaxin Administered'].values[-1]
        y = data_vaccine['Total CoviShield Administered'].values[-1]
        labels = ['Covaxin Vaccine',  'CovidShield Vaccine']
        st.plotly_chart(custom_plot.plot_population(
            [x, y], labels, area, height=180, t=0), use_container_width=True)

    # Daily Vaccine Time Series
    with title2:
        st.markdown("<h3 style='text-align: center;'>Daily Vaccinated</h2>",
                    unsafe_allow_html=True)
        value = int(data_vaccine['daily_vaccine'].values[-1])
        st.markdown(
            f"<h1 style='text-align: center; color: red;'>{value:,}</h1>", unsafe_allow_html=True)

    # Total Vaccines Sites
    with title3:
        st.markdown("<h3 style='text-align: center;'>Total Vaccine Sites</h2>",
                    unsafe_allow_html=True)
        value = int(data_vaccine['Total Sites '].values[-1])
        st.markdown(
            f"<h1 style='text-align: center; color: red;'>{value:,}</h1>", unsafe_allow_html=True)

    # Second Dose Administered
    with title4:
        st.markdown("<h3 style='text-align: center;'>Fully Vaccinated</h2>",
                    unsafe_allow_html=True)
        value = int(data_vaccine['Second Dose Administered'].values[-1])
        st.markdown(
            f"<h1 style='text-align: center; color: red;'>{value:,}</h1>", unsafe_allow_html=True)

    x = data_vaccine['date'][-90:]
    y = [data_vaccine['daily_first'].values[-90:],
         data_vaccine['daily_second'].values[-90:]]
    names = ['First Dose', 'Second Dose']
    title = 'Total Vaccinated'
    st.plotly_chart(custom_plot.plot_bar(x=x, y=y, name=names,
                                         title=title), use_container_width=True)

    col1, col2 = st.beta_columns(2)

    # daily_covaxin', 'daily_covidshield
    with col1:
        x = data_vaccine['date'][-90:]
        y = [data_vaccine['daily_covaxin'].values[-90:],
             data_vaccine['daily_covidshield'].values[-90:]]
        names = ['Covaxin', 'CovidShield']

        title = 'Type of Vaccines'
        st.plotly_chart(custom_plot.plot_bar(
            x=x, y=y, name=names, title=title), use_container_width=True)

    # Age Group wise Vaccine Distribution
    with col2:
        x = data_vaccine['date'][-30:]
        y = [
            data_vaccine['daily_18_30'].values[-30:], data_vaccine['daily_30_45'].values[-30:],
            data_vaccine['daily_45_60'].values[-30:], data_vaccine['daily_60_100'].values[-30:]
        ]
        names = ['18-30 Age', '30-45 Age', '45-60 Age', 'Above 60 Age']

        title = 'Age Group wise Vaccine Distribution'
        st.plotly_chart(custom_plot.plot_bar(
            x=x, y=y, name=names, title=title), use_container_width=True)

    pie1, pie2, pie3 = st.beta_columns(3)

    # Age wise Distribution
    with pie1:
        st.markdown("<h3 style='text-align: center;'>Age wise Distribution</h2>",
                    unsafe_allow_html=True)
        labels = ['18-30 years',  '30-45 years', '45-60 years', '60+ years']
        values = [
            data_vaccine['18-30 years (Age)'].values[-1], data_vaccine['30-45 years (Age)'].values[-1],
            data_vaccine['45-60 years (Age)'].values[-1], data_vaccine['60+ years (Age)'].values[-1]
        ]

        pie1.plotly_chart(custom_plot.plot_population(
            values, labels, area, legend=True, height=200, t=0), use_container_width=True)

    # Type of Vaccine Distriution
    with pie2:
        # 'Total Covaxin Administered', 'Total CoviShield Administered'
        st.markdown("<h3 style='text-align: center;'>Type of Vaccine Distriution</h2>",
                    unsafe_allow_html=True)
        labels = ['Covaxin', 'CoviShield']
        values = [
            data_vaccine['Total Covaxin Administered'].values[-1],
            data_vaccine['Total CoviShield Administered'].values[-1],
        ]

        pie2.plotly_chart(custom_plot.plot_population(
            values, labels, area, legend=True, height=200, t=0), use_container_width=True)

    # Gender wise Vaccine Distriution
    with pie3:
        #  'Male(Individuals Vaccinated)', 'Female(Individuals Vaccinated)', 'Transgender(Individuals Vaccinated)'
        st.markdown("<h3 style='text-align: center;'>Gender wise Vaccine Distriution</h2>",
                    unsafe_allow_html=True)
        labels = ['Male', 'Female', 'Transgender']
        values = [
            data_vaccine['Male(Individuals Vaccinated)'].values[-1],
            data_vaccine['Female(Individuals Vaccinated)'].values[-1],
            data_vaccine['Transgender(Individuals Vaccinated)'].values[-1],
        ]

        pie3.plotly_chart(custom_plot.plot_population(
            values, labels, area, legend=True, height=200, t=0), use_container_width=True)


#     st.subheader(f"Dettaglio andamenti {area}")
#     col1, _, col2, col3, _ = st.beta_columns([1, 2, 1, 1, 1])
#     status = col1.selectbox('', ['Giornaliero', 'Cumulato'])
#     fascia_anagrafica = col2.selectbox('Seleziona fascia anagrafica', ['16-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+'], index=7)
#     dose = col3.selectbox('Seleziona dose', ['prima dose', 'seconda dose'])
#     if status == 'Cumulato':
#         cumulate = True
#     else:
#         cumulate = False
#     col1, col2 = st.beta_columns(2)
#     col1.plotly_chart(plot.ages_timeseries(vaccines.raw, area, cumulate=cumulate), use_container_width=True)
#     col2.plotly_chart(plot.age_timeseries(vaccines.raw, area, fascia_anagrafica, demography, dose=dose, cumulate=cumulate), use_container_width=True)

#     col1, col2 = st.beta_columns(2)
#     col2.plotly_chart(plot.fornitori_timeseries(vaccines.raw, area, cumulate=cumulate), use_container_width=True)
#     col1.plotly_chart(plot.categories_timeseries(vaccines.administration, area, cumulate=cumulate), use_container_width=True)
#     # col2.plotly_chart(plot.plot_fill(data_list, [''], population, cumulate=cumulate, unita=100, subplot_title=names[0]), use_container_width=True)


else:
    st.header(f'Please select from options: {options}')

st.write("**:beer: Buy me a [beer])**")
expander = st.beta_expander("This app is developed by Manish Sahu.")
expander.write(
    "Contact me on [Linkedin](https://www.linkedin.com/in/manishsahuiitbhu/)")
expander.write(
    "The source code is on [GitHub](https://github.com/ManishSahu53/streamlit-covid-dashboard)")
