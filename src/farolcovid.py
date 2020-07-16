# coding=utf-8
import streamlit as st
import yaml

# Environment Variables from '../.env'
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("..") / ".env"
load_dotenv(dotenv_path=env_path, override=True)

import plotly.express as px
from streamlit import caching

# Pages
# import pages.simulacovid as sm
import pages.model_description as md
import pages.team as tm
import pages.data_analysis as anal
import pages.main as fc
import pages.risk_description as rd
import pages.rt_description as rt
import pages.saude_em_ordem_description as sod
import utils
import session


def main():
    # Defines the db structure of our makeshift session db
    session_state = session.SessionState.get(
        key=session.get_user_id(),
        update=False,
        number_beds=None,
        number_ventilators=None,
        number_cases=None,
        number_deaths=None,
        state="Acre",
        city="Todos",
        refresh=False,
        reset=False,
        saude_ordem_data=None,
        already_generated_user_id=None,
        pages_open=None,
        amplitude_events=None,
        old_amplitude_events=None,
    )
    # In those amplitude events objects we are going to save a dict with every state as keys
    # in each state, the value will be something that allows us to identify there is a change or not
    # which in turn allows us to decide if we should log the event or not"""
    utils.manage_user_existence(utils.get_server_session(), session_state)
    page = st.sidebar.radio(
        "Menu",
        [
            "FarolCovid",
            "Análises",
            "Níveis de Risco",
            "Estimando Ritmo de Contágio",
            "Modelo Epidemiológico",
            "Metodologia do Saúde em Ordem",
            "Quem somos?",
        ],
    )  # "Central COVID19",

    if page == "Modelo Epidemiológico":
        if __name__ == "__main__":
            md.main(session_state)

    elif page == "FarolCovid":
        if __name__ == "__main__":
            fc.main(session_state)

    elif page == "Análises":
        if __name__ == "__main__":
            anal.main(session_state)

    elif page == "Quem somos?":
        if __name__ == "__main__":
            tm.main(session_state)

    elif page == "Níveis de Risco":
        if __name__ == "__main__":
            rd.main(session_state)

    elif page == "Estimando Ritmo de Contágio":
        if __name__ == "__main__":
            rt.main(session_state)
    elif page == "Metodologia do Saúde em Ordem":
        if __name__ == "__main__":
            sod.main(session_state)


if __name__ == "__main__":
    main()

