import streamlit as st
import yaml
import loader
import numpy as np
import pandas as pd

from simulator import run_evolution
from simulation import calculate_recovered, filter_options
import utils

# Dados da projeção de capacidade de leitos
def dday_city(params, selected_region, config, supply_type="n_beds"):

    params["population_params"] = {
        "N": selected_region["population"],
        "I": selected_region["active_cases"],
        "D": selected_region["deaths"]
    }

    params["strategy"] = {'isolation': 90, 'lockdown': 90}

    params["n_beds"] = selected_region["number_beds"]
    params["n_ventilators"] = selected_region["number_ventilators"]

    if np.isnan(selected_region["active_cases"]):
        params["population_params"]["I"] = 1
    
    if np.isnan(selected_region["deaths"]):
        params["population_params"]["D"] = 0
    
    params = calculate_recovered(params, selected_region, params['notification_rate'])
    _, dday_beds, dday_ventilators = run_evolution(params, config)
    
    return dday_beds["best"], dday_beds["worst"]

def main():

    # GET DATA
    config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)
    cities = loader.read_data('br', config, endpoint=config['br']['api']['endpoints']['simulacovid'])

    # # Dados In Loco
    # inloco_url = yaml.load(open("configs/secrets.yaml", "r"), Loader=yaml.FullLoader)["inloco"]
    # df_inloco_cities = pd.read_csv(inloco_url["cities"])
    # df_inloco_states = pd.read_csv(inloco_url["states"])

    # Dados Rt
    df_rt_cities = loader.read_data("br", config, endpoint="br/cities/rt")
    df_rt_states = loader.read_data("br", config, endpoint="br/states/rt")

    # REGION/CITY USER INPUT
    user_input = dict()
    indicators = dict()

    level = st.selectbox('Nível', ["Estadual", "Municipal"])

    if level == "Estadual":
        user_input['state'] = st.selectbox('Estado', cities['state_name'].unique())
        cities_filtered = filter_options(cities, user_input['state'], 'state_name')

    if level == "Municipal":
        user_input['city'] = st.selectbox('Município', cities['city_name'].unique())
        cities_filtered = filter_options(cities, user_input['city'], 'city_name')

    selected_region = cities_filtered.sum(numeric_only=True)

    # GET NOTIFICATION RATE & Rt
    if len(cities_filtered) > 1: # pega taxa do estado quando +1 municipio selecionado
            user_input["notification_rate"] = round(cities_filtered['state_notification_rate'].mean(), 4)
            rt = df_rt_states[df_rt_states["state"] == cities_filtered["state"].unique()[0]]

    elif np.isnan(cities_filtered['notification_rate'].values):
            user_input["notification_rate"] = 1
            rt = df_rt_cities[df_rt_cities["city_id"] == cities_filtered["city_id"].iloc[0]]

    else:
            user_input["notification_rate"] = round(cities_filtered['notification_rate'], 4)
            rt = df_rt_cities[df_rt_cities["city_id"] == cities_filtered["city_id"].iloc[0]]

    if len(rt) < 1:
        st.write("Rt: Sua cidade não possui casos suficiente para o cálculo!")
    else:
        indicators["rt_high"] = rt.iloc[-1]["Rt_high_95"]
        indicators["rt_low"] = rt.iloc[-1]["Rt_low_95"]

        st.write(" ".join(["Rt: entre", str(indicators["rt_low"]), "e" , str(indicators["rt_high"])]))


    # GET DDAY BEDS
    indicators["dday_beds_best"], indicators["dday_beds_worst"] = dday_city(user_input, selected_region, config, supply_type="n_beds")
    st.write(" ".join(["Dias para capacidade: entre", str(indicators["dday_beds_worst"]), "e", str(indicators["dday_beds_best"])]))

    # INDICATORS
    # sources = cities_filtered[[c for c in cities_filtered.columns if (('author' in c) or ('last_updated_' in c))]]
    st.write("Você está aqui!")

if __name__ == "__main__":
    main()