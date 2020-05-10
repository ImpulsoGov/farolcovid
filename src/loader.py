import pandas as pd
import numpy as np
import streamlit as st
import os

@st.cache(allow_output_mutation=True)
def read_data(country, config, refresh_rate):

    if os.getenv('IS_LOCAL') == 'TRUE':
        url = config[country]['data_endpoints']['raw']['local']
    else:
        url = config[country]['data_endpoints']['raw']['external']

    print(url)

    df = pd.read_csv(url)
    
    # fix types
    df['last_updated'] = df['last_updated'].replace('0', np.nan)
    df['is_last'] = df['is_last'].astype(bool)
    df[[c for c in df.columns if 'last_updated' in c]] = df[[c for c in df.columns if 'last_updated' in c]].apply(pd.to_datetime)

    return  df


if __name__ == "__main__":
    pass
