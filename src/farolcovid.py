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


def main():
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
    )  # "Central COVID19"
    # Changing the style of the button
    st.markdown(
        """<style>
                button[data-baseweb="button"] {
                    border: 1px solid var(--main-white);
                    box-sizing: border-box;
                    border-radius: 15px;
                    width: auto;
                    padding: 0.5em;
                    text-transform: uppercase;
                    font-family: var(--main-header-font-family);
                    color: var(--main-white);
                    background-color: var(--main-primary);
                    font-weight: bold;
                    text-align: center;
                    text-decoration: none;
                    font-size: 18px;
                    animation-name: fadein;
                    animation-duration: 3s;
                    margin-top: 1em;
                } </style>""",
        unsafe_allow_html=True,
    )
    if page == "Modelo Epidemiológico":
        if __name__ == "__main__":
            md.main()

    elif page == "FarolCovid":
        if __name__ == "__main__":
            fc.main()

    elif page == "Análises":
        if __name__ == "__main__":
            anal.main()

    elif page == "Quem somos?":
        if __name__ == "__main__":
            tm.main()

    elif page == "Níveis de Risco":
        if __name__ == "__main__":
            rd.main()

    elif page == "Estimando Ritmo de Contágio":
        if __name__ == "__main__":
            rt.main()
    elif page == "Metodologia do Saúde em Ordem":
        if __name__ == "__main__":
            sod.main()


if __name__ == "__main__":
    main()

