# coding=utf-8
import streamlit as st
import yaml

# Environment Variables from '../.env'
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("..") / ".env"
load_dotenv(dotenv_path=env_path, override=True)

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

# Packages
from streamlit import caching
import session
import time

def main():

    # SESSION STATE
    time.sleep(
        0.05
    )  # minimal wait time so we give time for the user session to appear in steamlit
    session_state = session.SessionState.get(
        key=session.get_user_id(),
        update=False,
        state_name="Acre",
        state_num_id=None,
        health_region_name="Todos",
        health_region_id=None,
        city_name="Todos",
        city_id=None,
        number_beds=None,
        number_ventilators=None,
        number_cases=None,
        number_deaths=None,
        population_params=dict(),
        refresh=False,
        reset=False,
        saude_ordem_data=None,
        already_generated_user_id=None,
        pages_open=None,
        amplitude_events=None,
        old_amplitude_events=None,
        button_styles=dict(),
        continuation_selection=None,
    )
    # AMPLITUDE EVENT
    # In those amplitude events objects we are going to save a dict with every state as keys
    # in each state, the value will be something that allows us to identify there is a change or not
    # which in turn allows us to decide if we should log the event or not
    utils.manage_user_existence(utils.get_server_session(), session_state)
    utils.update_user_public_info()
    # CLOSES THE SIDEBAR WHEN THE USER LOADS THE PAGE
    st.write(
        """
    <iframe src="resources/sidebar-closer.html" height=0 width=0>
    </iframe>""",
        unsafe_allow_html=True,
    )
    # For Http debug
    # st.write(utils.parse_headers(utils.get_server_session().ws.request))

    # BUTTON STYLE
    # st.markdown(
    #     """<style>
    #             button[data-baseweb="button"] {
    #                 border: 1px solid var(--main-white);
    #                 box-sizing: border-box;
    #                 border-radius: 12px;
    #                 width: auto;
    #                 padding: 0.5em;
    #                 text-transform: uppercase;
    #                 font-family: var(--main-header-font-family);
    #                 color: var(--main-white);
    #                 background-color: var(--main-primary);
    #                 font-weight: bold;
    #                 text-align: center;
    #                 text-decoration: none;
    #                 font-size: 12px;
    #                 animation-name: fadein;
    #                 animation-duration: 3s;
    #                 margin-top: 1em;
    #             } </style>""",
    #     unsafe_allow_html=True,
    # )

    # MENU
    page = st.sidebar.radio(
        "Menu",
        [
            "FarolCovid",
            "Análises",
            "Níveis de Risco",
            "Estimando Ritmo de Contágio",
            "Modelo Epidemiológico",
            # "Metodologia do Saúde em Ordem",
            "Quem somos?",
        ],
    )

    if page == "Modelo Epidemiológico":
        if __name__ == "__main__":
            md.main(session_state)

    elif page == "FarolCovid":
        if __name__ == "__main__":
            fc.main(session_state)
            utils.applyButtonStyles(session_state)

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

