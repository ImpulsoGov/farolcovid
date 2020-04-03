import pandas as pd

def _download_from_drive(url):

    return pd.read_csv(url + '/export?format=csv&id')

def read_cities_data(country, config):

    paths = config[country]['drive_paths']

    return {name: _download_from_drive(url) for name, url in paths.items()}

def read_cases_data(country, config):

    if country == 'br':
        result = requests.get(config[country]['cases']['url']).json()['results']
        df = pd.DataFrame(result)

    return df