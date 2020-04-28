import pandas as pd
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
    df[[c for c in df.columns if 'last_updated' in c]] = df[[c for c in df.columns if 'last_updated' in c]].apply(pd.to_datetime)

    return  df


if __name__ == "__main__":
    pass
