import streamlit as st
import yaml
import loader
import numpy as np
import pandas as pd

from simulator import run_evolution
from simulation import calculate_recovered, filter_options
import utils


def main():

    # GET DATA
    config = yaml.load(open("configs/config.yaml", "r"), Loader=yaml.FullLoader)
    df = loader.read_data(
        "br", config, endpoint=config["br"]["api"]["endpoints"]["farolcovid"]
    )

    # REGION/CITY USER INPUT
    user_input = dict()

    level = st.selectbox("Nível", ["Municipal"])  # ["Estadual", "Municipal"])

    # if level == "Estadual":
    #     user_input['state'] = st.selectbox('Estado', cities['state_name'].unique())
    #     cities_filtered = filter_options(cities, user_input['state'], 'state_name')
    #     user_input["place_type"] = "state"

    if level == "Municipal":
        user_input["city"] = st.selectbox("Município", df["city_name"].unique())
        cities_filtered = filter_options(df, user_input["city"], "city_name")
        user_input["place_type"] = "city_id"

    # selected_region = cities_filtered.sum(numeric_only=True)

    st.write(
        "<b>Nível de Alerta: </b>",
        cities_filtered["overall_alert"].values[0].upper(),
        unsafe_allow_html=True,
    )

    st.write(
        "Subnotificação: {}%".format(
            100 * round(float(cities_filtered["subnotification_rate"].values[0]), 4)
        )
    )
    st.write(
        "Taxa de mortalidade: {}%".format(
            100
            * round(
                float(
                    cities_filtered["subnotification_last_mortality_ratio"].values[0]
                ),
                4,
            )
        )
    )
    st.write(
        "Ranking da UF: <i>{}º município com maior subnotificação</i>".format(
            int(cities_filtered["subnotification_rank"].values[0])
        ),
        unsafe_allow_html=True,
    )

    st.write(
        "Taxa de contagio (ultimos 10 dias): entre {} e {}  - Classificação: <i>{}</i>".format(
            cities_filtered["rt_10days_ago_low"].values[0],
            cities_filtered["rt_10days_ago_high"].values[0],
            cities_filtered["rt_classification"].values[0],
        ),
        unsafe_allow_html=True,
    )

    st.write(
        "Taxa de contagio (ultimos 17 dias): entre {} e {} - Comparação: <i>{}</i>".format(
            cities_filtered["rt_17days_ago_low"].values[0],
            cities_filtered["rt_17days_ago_high"].values[0],
            cities_filtered["rt_comparision"].values[0],
        ),
        unsafe_allow_html=True,
    )

    st.write(
        "Distanciamento social (hoje): {}%".format(
            100 * round(float(cities_filtered["inloco_today_7days_avg"].values[0]), 3)
        ),
        unsafe_allow_html=True,
    )
    st.write(
        "Distanciamento social: {}% (ultima semana) - Comparação: <i>{}</i>".format(
            100
            * round(float(cities_filtered["inloco_last_week_7days_avg"].values[0]), 3),
            cities_filtered["inloco_comparision"].values[0],
        ),
        unsafe_allow_html=True,
    )

    st.write(
        "Capacidade Hospitalar: entre {} e {} dias  - Classificação: <i>{}</i>".format(
            cities_filtered["dday_beds_best"].values[0],
            cities_filtered["dday_beds_worst"].values[0],
            cities_filtered["dday_classification"].values[0],
        ),
        unsafe_allow_html=True,
    )

    st.write("Você está aqui!")


if __name__ == "__main__":
    main()
