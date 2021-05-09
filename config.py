import datetime 

path_cases_overall_timeseries = 'https://api.covid19india.org/csv/latest/case_time_series.csv'
path_cases_state_wise_timeseries = 'https://api.covid19india.org/csv/latest/states.csv'

path_test_overall_timeseries = 'https://api.covid19india.org/csv/latest/tested_numbers_icmr_data.csv'
path_test_state_wise_timeseries = 'https://api.covid19india.org/csv/latest/statewise_tested_numbers_data.csv'

# path_vaccine_state_wise = 'http://api.covid19india.org/csv/latest/vaccine_doses_statewise.csv'
path_vaccine_state_wise_cowin = 'http://api.covid19india.org/csv/latest/cowin_vaccine_data_statewise.csv'

UNIT = 1000000
POPULATION = 1336459178
TIMEZONE_OFFSET = 5.50  # +5:30 Indian Time # Pacific Standard Time (UTC−08:00)
tzinfo = datetime.timezone(datetime.timedelta(hours=TIMEZONE_OFFSET))

RULE_MAP = {
    'Total': 'total',
    'Data per 10,00,000': 'percentage',
}

REGION_INDEX = {
    'Himachal Pradesh': 1,
    'Punjab': 2,
    'Uttarakhand': 3,
    'Haryana': 4,
    'Rajasthan': 5,
    'Uttar Pradesh': 6,
    'Bihar': 7,
    'Sikkim': 8,
    'Arunachal Pradesh': 9,
    'Nagaland': 10,
    'Manipur': 11,
    'Mizoram': 12,
    'Tripura': 13,
    'Meghalaya': 14,
    'Assam': 15,
    'West Bengal': 16,
    'Jharkhand': 17,
    'Odisha': 18,
    'Chhattisgarh': 19,
    'Madhya Pradesh': 20,
    'Gujarat': 21,
    'Maharashtra': 22,
    'Andhra Pradesh': 23,
    'Karnataka': 24,
    'Goa': 25,
    'Kerala': 26,
    'Tamil Nadu': 27,
    'Telangana': 28,
    'Jammu and Kashmir': 29,
    'Chandigarh': 30,
    'Delhi': 31,
    'Dadra and Nagar Haveli and Daman and Diu': 32,
    'Lakshadweep': 33,
    'Puducherry': 34,
    'Andaman and Nicobar Islands': 35,
    'Ladakh': 36,
}

POPULATION_MAP = {
    'India': 1336459178,
    'Himachal Pradesh': 7316708,
    'Punjab': 29611935,
    'Uttarakhand': 11090425,
    'Haryana': 27388008,
    'Rajasthan': 78230816,
    'Uttar Pradesh': 228959599,
    'Bihar': 119461013,
    'Sikkim': 671720,
    'Arunachal Pradesh': 1528296,
    'Nagaland': 2189297,
    'Manipur': 3008546,
    'Mizoram': 1205974,
    'Tripura': 4057847,
    'Meghalaya': 3276323,
    'Assam': 34586234,
    'West Bengal': 97694960,
    'Jharkhand': 37329128,
    'Odisha': 45429399,
    'Chhattisgarh': 28566990,
    'Madhya Pradesh': 82342793,
    'Gujarat': 63907200,
    'Maharashtra': 120837347,
    'Andhra Pradesh': 52883163,
    'Karnataka': 66165886,
    'Goa': 1542750,
    'Kerala': 35330888,
    'Tamil Nadu': 76481545,
    'Telangana': 38472769,
    'Jammu and Kashmir': 14046258,
    'Chandigarh': 1182104,
    'Delhi': 18802494,
    'Dadra and Nagar Haveli and Daman and Diu': 657391,
    'Lakshadweep': 72210,
    'Puducherry': 1397707,
    'Andaman and Nicobar Islands': 426251,
    'Ladakh': 307204,
}
