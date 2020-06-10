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
import plotly.express as px
from datetime import datetime
import math
import yaml
import numpy as np
import loader
from model import simulator
from pandas import Timestamp

from pages.plots import plot_simulation

FIXED = datetime.now().minute

# def refresh_rate(config):
#     dt = (
#         math.floor(datetime.now().minute / config["refresh_rate"])
#         * config["refresh_rate"]
#     )
#     return datetime.now().replace(minute=dt, second=0, microsecond=0)


def calculate_recovered(user_input, data):

    confirmed_adjusted = int(
        data[["confirmed_cases"]].sum() / data["notification_rate"].values[0]
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

    if indicators["rt"].display != "- ":
        st.write(
            f"""
            <div class="base-wrapper">
                    <span class="section-header primary-span">Simule o impacto de diferentes ritmos de contágio no seu sistema hospitalar</span>
                    <br><br>
                    <span>Agora é a hora de se preparar para evitar a sobrecarga hospitalar. 
                    No momento, em {user_input["locality"]}, estimamos que <b>o ritmo de contágio esteja entre {indicators["rt"].display}</b>, 
                    ou seja, cada pessoa doente infectará em média entre outras {indicators["rt"].display} pessoas.
                    </span>
            </div>""",
            unsafe_allow_html=True,
        )
    else:

        st.write(
            f"""
            <div class="base-wrapper">
                    <span class="section-header primary-span">Simule o impacto de diferentes ritmos de contágio no seu sistema hospitalar</span>
                    <br><br>
                    <span>Agora é a hora de se preparar para evitar a sobrecarga hospitalar. 
                    No momento, em {user_input["locality"]}, não temos dados suficientes para estimativa do ritmo de contágio. 
                    Por isso, <b>iremos simular com o ritmo de contágio do seu estado, que está entre {user_input["state_rt"]}</b>, 
                    ou seja, cada pessoa doente infectará em média entre outras {user_input["state_rt"]} pessoas.
                    </span>
            </div>""",
            unsafe_allow_html=True,
        )

    dic_scenarios = {
        "Cenário Estável: O que acontece se seu ritmo de contágio continuar constante?": "isolation",
        "Cenário Negativo: O que acontece se dobrar o seu ritmo de contágio?": "nothing",
        "Cenário Positivo: O que acontece se seu ritmo de contágio diminuir pela metade?": "lockdown",
    }

    option = st.selectbox(
        "",
        ["Selecione uma mudança no seu ritmo de contágio"] + list(dic_scenarios.keys()),
    )

    if option == "Selecione uma mudança no seu ritmo de contágio":
        pass

    else:

        # utils.genInputCustomizationSectionHeader(user_input["locality"])
        # user_input, session_state = utils.genInputFields(
        #     user_input, sources, config, session_state
        # )

        # calculate recovered cases
        user_input = calculate_recovered(user_input, data)

        # SIMULATOR SCENARIOS: BEDS & RESPIRATORS
        user_input["strategy"] = dic_scenarios[option]

        # TODO: melhorar aqui! como fazer a estimatima de casos ativos quando é modificado?
        if (
            user_input["population_params"]["I"]
            == user_input["population_params"]["I_confirmed"]
        ):
            user_input["population_params"]["I"] = user_input["population_params"][
                "I_confirmed"
            ]

        dfs = simulator.run_simulation(user_input, config)

        dday_beds = simulator.get_dmonth(dfs, "I2", int(user_input["number_beds"]))

        dday_ventilators = simulator.get_dmonth(
            dfs, "I3", int(user_input["number_ventilators"])
        )
        # fig, dday_beds, dday_ventilators = simulator.run_simulation(user_input, config)

        utils.genChartSimulationSection(
            SimulatorOutput(
                color=BackgroundColor.SIMULATOR_CARD_BG,
                min_range_beds=dday_beds["worst"],
                max_range_beds=dday_beds["best"],
                min_range_ventilators=dday_ventilators["worst"],
                max_range_ventilators=dday_ventilators["best"],
            ),
            plot_simulation(dfs, user_input, config),
        )

        utils.genWhatsappButton()
        utils.genFooter()


if __name__ == "__main__":
    pass
