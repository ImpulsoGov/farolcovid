import os
import sys

sys.path.insert(0, "./model/")

import streamlit as st
from streamlit import caching
from models import (
    BackgroundColor,
    Document,
    Strategies,
    SimulatorOutput,
    ResourceAvailability,
)
from typing import List
import utils
import amplitude
import plotly.express as px
from datetime import datetime
import math
import yaml
import numpy as np
import loader
from model import simulator
from plots import plot_simulation
from pandas import Timestamp
import session


def calculate_recovered(user_input, data):
    print(data)
    confirmed_adjusted = int(
        # data[["confirmed_cases"]].sum() / data["notification_rate"].values[0]
        data[["confirmed_cases"]].sum()
        / 1
    )

    if confirmed_adjusted == 0:  # dont have any cases yet
        user_input["population_params"]["R"] = 0
        return user_input

    user_input["population_params"]["R"] = (
        confirmed_adjusted
        - user_input["population_params"]["I"]
        - user_input["population_params"]["D"]
    )

    if user_input["population_params"]["R"] < 0:
        user_input["population_params"]["R"] = (
            confirmed_adjusted - user_input["population_params"]["D"]
        )

    return user_input


def main(user_input, indicators, data, config, session_state):
    user_analytics = amplitude.gen_user(utils.get_server_session())
    if (
        user_input["place_type"] == user_input["rt_level"]
    ):  # indicators["rt"].display != "- ":
        st.write(
            f"""
            <div class="base-wrapper">
                    <span class="section-header primary-span">Simule o impacto de diferentes ritmos de contágio no seu sistema hospitalar</span>
                    <br><br>
                    <span>Agora é a hora de se preparar para evitar a sobrecarga hospitalar. 
                    No momento, em {user_input["locality"]}, estimamos que <b>a taxa de contágio esteja entre {indicators["control"].left_display}</b>, 
                    ou seja, cada pessoa doente infectará em média entre outras {indicators["control"].left_display} pessoas.
                    </span>
            </div>""",
            unsafe_allow_html=True,
        )

    else:
        places = {"health_region_id": "Regional", "state_num_id": "Estado"}
        st.write(
            f"""
            <div class="base-wrapper">
                    <span class="section-header primary-span">Simule o impacto de diferentes ritmos de contágio no seu sistema hospitalar</span>
                    <br><br>
                    <span>Agora é a hora de se preparar para evitar a sobrecarga hospitalar. 
                    No momento, em {user_input["locality"]}, não temos dados suficientes para estimativa do ritmo de contágio. 
                    Por isso, <b>iremos simular com a taxa de contágio do seu {places[user_input["rt_level"]]}, que está entre {str(user_input["rt_values"]["best"])}-{str(user_input["rt_values"]["worst"])}</b>, 
                    ou seja, cada pessoa doente infectará em média entre outras {str(user_input["rt_values"]["best"])}-{str(user_input["rt_values"]["worst"])} pessoas.
                    </span>
            </div>""",
            unsafe_allow_html=True,
        )
    # CHANGE DATA SECTION
    utils.genInputCustomizationSectionHeader(user_input["locality"])
    old_user_input = dict(user_input)
    user_input, session_state = utils.genInputFields(user_input, config, session_state)
    if session_state.reset:
        session.rerun()
    if session_state.update:
        opening_response = user_analytics.log_event(
            "updated sim_numbers",
            {
                "beds_change": session_state.number_beds
                - int(old_user_input["number_beds"]),
                "icu_beds_change": session_state.number_icu_beds
                - int(old_user_input["number_icu_beds"]),
                "cases_change": session_state.number_cases
                - int(old_user_input["population_params"]["I_confirmed"]),
                "deaths_change": session_state.number_deaths
                - int(old_user_input["population_params"]["D"]),
            },
        )
        session_state.update = False
        session.rerun()

    dic_scenarios = {
        "Cenário Estável: O que acontece se seu ritmo de contágio continuar constante?": "estavel",
        "Cenário Negativo: O que acontece se dobrar o seu ritmo de contágio?": "negativo",
        "Cenário Positivo: O que acontece se seu ritmo de contágio diminuir pela metade?": "positivo",
    }

    option = st.selectbox(
        "",
        ["Selecione uma mudança no seu ritmo de contágio"] + list(dic_scenarios.keys()),
    )

    if option == "Selecione uma mudança no seu ritmo de contágio":
        pass

    else:

        # calculate recovered cases
        user_input = calculate_recovered(user_input, data)

        # SIMULATOR SCENARIOS: BEDS & RESPIRATORS
        user_input["strategy"] = dic_scenarios[option]
        if user_input["strategy"] == "estavel":
            user_analytics.log_event("picked stable_scenario")
        elif user_input["strategy"] == "positivo":
            user_analytics.log_event("picked positive_scenario")
        elif user_input["strategy"] == "negativo":
            user_analytics.log_event("picked negative_scenario")

        # Caso o usuário altere os casos confirmados, usamos esse valor para a estimação

        if (session_state.number_cases is not None) and (
            session_state.number_cases != user_input["population_params"]["I_compare"]
        ):
            user_input["population_params"]["I"] = session_state.number_cases

        dfs = simulator.run_simulation(user_input, config)

        dday_beds = simulator.get_dmonth(dfs, "I2", int(user_input["number_beds"]))

        dday_icu_beds = simulator.get_dmonth(
            dfs, "I3", int(user_input["number_icu_beds"])
        )
        dday_icu_beds = simulator.get_dmonth(
            dfs, "I3", int(user_input["number_icu_beds"])
        )

        utils.genChartSimulationSection(
            SimulatorOutput(
                # color=BackgroundColor.SIMULATOR_CARD_BG,
                min_range_beds=dday_beds["worst"],
                max_range_beds=dday_beds["best"],
                min_range_icu_beds=dday_icu_beds["worst"],
                max_range_icu_beds=dday_icu_beds["best"],
            ),
            plot_simulation(dfs, user_input),
        )


if __name__ == "__main__":
    pass
