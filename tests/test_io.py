import pytest
import pandas as pd
import yaml

from src import io

def test_download_from_drive():

    # Any download returns df
    test_url = 'https://docs.google.com/spreadsheets/d/1k8mXuUggBuBEghHhhLrLtA-5wa4JsAc-D35S5bNlf24'
    assert isinstance(io._download_from_drive(test_url), pd.core.frame.DataFrame)

def test_read_cities_data():

    config = yaml.loads('src/configs/config.yaml')

    result = io.read_cities_data('br', config)

    assert isinstance(result, dict)
    
    for v in result.values():
        assert isinstance(v, dict)