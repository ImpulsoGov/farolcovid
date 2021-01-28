import pandas as pd
import numpy as np
import streamlit as st
import os
import yaml

config = yaml.load(open("configs/config.yaml", "r"), Loader=yaml.FullLoader)


def read_data(country, config, endpoint, params=None):

    # if os.getenv("IS_LOCAL") == "TRUE":
    #     api_url = config[country]["api"]["local"]
    # else:
    #     api_url = config[country]["api"]["external"]
    api_url = config[country]["api"]["external"]
    url = api_url + endpoint
    if params:
        url = url + '?state_id=' + params['state_id']
    df = pd.read_csv(url)

    if "last_updated" in df.columns:
        # fix types
        df["last_updated"] = df["last_updated"].replace("0", np.nan)
        # df["is_last"] = df["is_last"].astype(bool)
        df[[c for c in df.columns if "last_updated" in c]] = df[
            [c for c in df.columns if "last_updated" in c]
        ].apply(pd.to_datetime)

    return df


if __name__ == "__main__":
    pass
