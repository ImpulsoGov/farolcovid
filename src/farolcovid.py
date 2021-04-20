# coding=utf-8
import streamlit as st
import yaml

# Environment Variables from '../.env'
from dotenv import load_dotenv
from pathlib import Path
import urllib.parse as urlparse
from urllib.parse import parse_qs

env_path = Path("..") / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Pages
import pages.team as tm
import pages.estudo as estudo
import pages.vacina as vacina
# import pages.model_description as md
# import pages.saude_em_ordem_description as sod
import pages.main as fc
import pages.methodology as method
import urllib.parse as _parse
from streamlit.report_thread import get_report_ctx as _get_report_ctx
import utils

# Packages
from streamlit import caching
import session
import time


st.set_page_config(
page_title="Farol Covid",
layout='wide',
initial_sidebar_state='collapsed')

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
        number_icu_beds=None,
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
    
    # Gambiarra para ter o menu lateral com caracteres especiais e ainda ter várias páginas
    # Retirar depois de encontrar saída mais apropriada
    page_list = ["FarolCovid", "Modelos, limitações e fontes", "Quem somos?", "Estudo Vacinação", "Vacinômetro"]
    pages_dict = {   
        "FarolCovid" : "Inicio",
        "Modelos, limitações e fontes" : "Metodologia",
        "Quem somos?" : "Quem-Somos",
        "Estudo Vacinação" : "Estudo-Vacinacao",
        "Vacinômetro": "Vacinometro"
    }
    pages_index = {   
        "Inicio" : 0,
        "Metodologia" : 1,
        "Quem-Somos" : 2,
        "Estudo-Vacinacao" : 3,
        "Vacinometro": 4
    }
    PAGES = {   
        "Inicio" : fc,
        "Metodologia" : method,
        "Quem-Somos" : tm,
        "Estudo-Vacinacao" : estudo,
        "Vacinometro": vacina
    }
    query_params = st.experimental_get_query_params()
    if query_params:
        # Gambiarra para redirecionar páginas
        if query_params["page"][0] == '0' or query_params["page"][0] == 'FarolCovid':
            query_params["page"][0] = "Inicio"
        elif query_params["page"][0] == '1' or query_params["page"][0] == 'Modelos, limitações e fontes':
            query_params["page"][0] = "Metodologia"
        elif query_params["page"][0] == '2' or query_params["page"][0] == 'Quem somos?':
            query_params["page"][0] = "Quem-Somos"
        elif query_params["page"][0] == '3' or query_params["page"][0] == 'Estudo Vacinação':
            query_params["page"][0] = "Estudo-Vacinacao"
        elif query_params["page"][0] == '4' or query_params["page"][0] == 'Vacinômetro':
            query_params["page"][0] = "Vacinometro"
    default = query_params["page"][0] if "page" in query_params else "Inicio"
    page = st.sidebar.radio("Menu",page_list,index=pages_index[default])
    st.experimental_set_query_params(page=pages_dict[page])
    PAGES[pages_dict[page]].main(session_state)


if __name__ == "__main__":
    main()
