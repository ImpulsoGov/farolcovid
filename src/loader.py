import pandas as pd
import numpy as np
import requests
import streamlit as st
import datetime
import subprocess

def _download_from_drive(url):

    response = subprocess.run(['curl', '-o', 'temp.csv', url + '/export?format=csv&id'],
                    check=True, text=True)

    return pd.read_csv('temp.csv')

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