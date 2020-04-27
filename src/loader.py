import pandas as pd
import streamlit as st

@st.cache(allow_output_mutation=True)
def read_data(country, config, refresh_rate):

    df = pd.read_csv(config[country]['data_endpoints']['raw'])
    df[[c for c in df.columns if 'last_updated' in c]] = df[[c for c in df.columns if 'last_updated' in c]].apply(pd.to_datetime)

    return  df


if __name__ == "__main__":
    pass
