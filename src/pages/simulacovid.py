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

FIXED = datetime.now().minute


def add_all(x, all_string="Todos"):
    return [all_string] + list(x)


def filter_options(_df, var, col, all_string="Todos"):
    if var == "Todos":
        return _df
    else:
        return _df.query(f'{col} == "{var}"')


def refresh_rate(config):
    dt = (
        math.floor(datetime.now().minute / config["refresh_rate"])
        * config["refresh_rate"]
    )
    return datetime.now().replace(minute=dt, second=0, microsecond=0)


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


def main(user_input, locality, indicators, data, config):

    st.write(
        f"""
        <div class="base-wrapper">
                <span class="section-header primary-span">Simule o impacto de diferentes ritmos de contágio no seu sistema hospitalar</span>
                <br><br>
                <span>Agora é a hora de se preparar para evitar a sobrecarga hospitalar. 
                No momento, em {locality}, estimamos que <b>o ritmo de contágio esteja entre {indicators["rt"].display}</b>, 
                ou seja, cada pessoa doente infectará em média entre outras {indicators["rt"].display} pessoas</b>.
                </span>
        </div>""",
        unsafe_allow_html=True,
    )

    dic_scenarios = {
        "Cenário Estável: O que acontece se seu ritmo de contágio continuar constante?": {
            "isolation": 0,
            "lockdown": 90,
        },
        "Cenário Negativo: O que acontece se dobrar o seu ritmo de contágio?": {
            "isolation": 90,
            "lockdown": 90,
        },
        "Cenário Positivo: O que acontece se seu ritmo de contágio diminuir pela metade?": {
            "isolation": 90,
            "lockdown": 0,
        },
    }

    user_input["strategy"] = dic_scenarios[
        st.selectbox(
            "Simule como mudanças no seu ritmo de contágio afetam a demanda por leitos e ventiladores no local:",
            list(dic_scenarios.keys()),
        )
    ]

    st.write("<br/><br/>", unsafe_allow_html=True)

    # calculate recovered cases
    user_input = calculate_recovered(user_input, data)

    # SIMULATOR SCENARIOS: BEDS & RESPIRATORS
    fig, dday_beds, dday_ventilators = simulator.run_evolution(user_input, config)

    utils.genChartSimulationSection(
        SimulatorOutput(
            color=BackgroundColor.SIMULATOR_CARD_BG,
            min_range_beds=dday_beds["worst"],
            max_range_beds=dday_beds["best"],
            min_range_ventilators=dday_ventilators["worst"],
            max_range_ventilators=dday_ventilators["best"],
        ),
        fig,
    )

    utils.genWhatsappButton()
    utils.genFooter()


if __name__ == "__main__":
    main()
