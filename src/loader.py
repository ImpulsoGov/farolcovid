import pandas as pd
import numpy as np
import requests
import streamlit as st
import datetime

def _download_from_drive(url):

    return pd.read_csv(url + '/export?format=csv&id')

def _get_credentials():
    
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
             'configs/gcloud-credentials.json', scope) 

    gc = gspread.authorize(credentials) 

    return credentials, gc

def _read_sheets_tables():
    
    credentials, gc = _get_credentials()

    gc = gspread.authorize(credentials)
    
    wks = gc.open('regions_metadata')

    datasets = {}
    for w in wks.worksheets():

        data = w.get_all_values()

        headers = data.pop(0)

        datasets[w.title] = pd.DataFrame(data, columns=headers)

    return datasets

def _read_cities_data(country, config):

    paths = config[country]['drive_paths']

    return {name: _download_from_drive(url) for name, url in paths.items()}

def _read_cases_data(country, config):

    if country == 'br':
        df = pd.read_csv(config[country]['cases']['url'])
        df = df.query('place_type == "city"').dropna(subset=['city_ibge_code'])

        cases_params = config['br']['cases']
        df = df.rename(columns=cases_params['rename'])

        infectious_period = config['br']['seir_parameters']['severe_duration'] + \
                            config['br']['seir_parameters']['critical_duration']
        
        df['last_updated'] = pd.to_datetime(df['last_updated'])
        first_day = df['last_updated'].max() - datetime.timedelta(infectious_period)

        df = df.merge(df[df['last_updated'] >= first_day].groupby('city_id')['number_cases'].sum(), 
                    on='city_id', suffixes=('_x', ''))

        df['recovered'] = df['last_available_confirmed'] - df['number_cases'] - df['deaths']
        # Ajustando casos que recuperados < 0: provável remoção de mortos no acumulado de infetados
        df['recovered'] = np.where(df['recovered'] < 0, df['last_available_confirmed'] - df['number_cases'], df['recovered'])

        df = df[df['is_last'] == True][cases_params['rename'].values()]
        df['city_id'] = df['city_id'].astype(int)

    return df

@st.cache(allow_output_mutation=True)
def read_data(country, config, refresh_rate):

    cases = _read_cases_data(country, config)
    cities = _read_cities_data(country, config)

    if country == 'br':

        # merge cities
        df = pd.merge(
            cities['cities_population'], cities['health_infrastructure'],
            on='city_id', how='left', suffixes=('', '_y'))
        df = df.drop([c for c in df.columns if '_y' in c], 1)

        # merge cities
        df = df.merge(cases, on='city_id', how='left')

    return df

if __name__ == "__main__":

    pass