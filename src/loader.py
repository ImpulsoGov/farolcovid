import pandas as pd
import numpy as np
import requests
import streamlit as st
import datetime
import subprocess
import unicodedata
from copy import deepcopy

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

def _remove_accents(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').upper()

def _drop_forbiden(text):

    forbiden = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG',
       'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR',
       'RS', 'SC', 'SE', 'SP', 'TO']
    
    words = [t.strip() for t in text.split(' ')]
    
    for f in forbiden:
        if f in words:
            words.remove(f)
        
    return ' '.join(words)

def _treat_text(s):

    s = s.apply(_remove_accents)
    s = s.apply(_drop_forbiden)
    return s

def _get_last(_df, sort_by='last_updated'):
    
    return _df.sort_values(sort_by).groupby(['city_id']).last().reset_index()

def _get_updates(country, config):
    
    updates = _download_from_drive(config[country]['drive_paths']['embaixadores'])
    
    # change column names
    updates.columns = [
        'timestamp',
        'email',
        'city_norm',
        'state_id',
        'name',
        'last_updated',
        'number_ventilators',
        'number_beds',
        'n_casos',
        'n_mortes',
        'number_icu_beds'
    ]
    
    # treat text
    c = ['city_norm']
    updates[c] = updates[c].apply(_treat_text)

    # treat timestamp
    updates['last_updated'] = updates['timestamp'].apply(pd.to_datetime)
    
    return updates

def _prepare_cities(country, config):
    
    cities = _read_cities_data(country, config)
    cities = pd.merge(
        cities['cities_population'], cities['health_infrastructure'],
        on='city_id', how='left', suffixes=('', '_y'))
    cities = cities.drop([c for c in cities.columns if '_y' in c], 1)

    cities[['city_norm']] = cities[['city_name']].apply(_treat_text)

    time_cols = [c for c in cities.columns if 'last_updated' in c]
    cities[time_cols] = cities[time_cols].apply(pd.to_datetime)
    
    return cities

def _get_supplies(cities, updates, country, config):
    
    final_cols = config[country]['columns']['final']
    
    final = []
    for h in config[country]['columns']['health']:
        u = updates.rename(columns={'name': 'author'
                                   })[final_cols + [h]].dropna(subset=[h])
        u = _get_last(u)
        cities['author'] = config[country]['health']['source']
        c = cities.rename(columns={'last_updated_' + h: 'last_updated'})[final_cols + [h]]
        c[h] = c[h] * config[country]['health']['initial_proportion']
        f = _get_last(pd.concat([c, u]))
        f.columns = ['city_id'] + [i + '_' + h for i in final_cols if i != 'city_id'] + [h]
        final.append(deepcopy(f))
        
    supplies = pd.concat(final, 1)
    supplies = supplies.loc[:,~supplies.columns.duplicated()]
    
    return supplies

@st.cache(allow_output_mutation=True)
def read_data(country, config, refresh_rate):

    cases = _read_cases_data(country, config)
    

    if country == 'br':

        updates = _get_updates('br', config)
        cities = _prepare_cities('br', config)

        updates = cities[['state_id', 'city_norm', 'city_id']]\
                .merge(updates, on=['state_id', 'city_norm'], how='right')

        supplies = _get_supplies(cities, updates, 'br', config)

        # merge cities
        df = cities[
                ['country_iso',
                'country_name',
                'state_id',
                'state_name',
                'city_id',
                'city_name',
                'population',
                'health_system_region',
                ]].merge(supplies, on='city_id')

        # merge cities
        df = df.merge(cases, on='city_id', how='left')


    return df

if __name__ == "__main__":

    pass