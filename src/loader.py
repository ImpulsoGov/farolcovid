import pandas as pd
import requests
import streamlit as st

def _download_from_drive(url):

    print(url + '/export?format=csv&id')

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
        cases_params = config[country]['cases']
        result = requests.get(cases_params['url']).json()['results']
        df = pd.DataFrame(result)
        df = df.query('place_type == "city"').dropna(subset=['city_ibge_code'])
        df = df.rename(columns=cases_params['rename'])
        df = df.drop(cases_params['drop'], 1)
        df['city_id'] = df['city_id'].astype(int)

    return df

@st.cache
def read_data(country, config):

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