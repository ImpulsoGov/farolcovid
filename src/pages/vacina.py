import streamlit as st
import numpy as np
import pandas as pd
import utils
import pages.header as he

def main(session_state):
    utils.localCSS("vacinastyle.css")
    utils.genHeroSection(
        title1="Vacinômetro",
        title2="",
        subtitle="Ferramenta digital para acompanhar e comparar o número de pessoas que foram vacinadas contra a Covid-19.",
        logo="https://i.imgur.com/w5yVANW.png",
        header=False,
    )
    he.genHeader("4")
    st.write(
        """
        <div class="base-wrapper flex flex-column" style="background-color: rgb(0, 144, 167);">
            <div class="white-span header p1" style="font-size:30px;">Dados sobre vacinação contra Covid-19 em município</div>
        </div>
        <div class="magenta-bg">
                <div class="base-wrapper">
                        <div>
                            <span>Acompanhe e compare como diferentes municípios estão se saindo na vacinação, com dados de quantidades de doses aplicadas, porcentagem da população vacinada e imunizada.</span>
                        </div>
                </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    df2 = pd.read_csv("http://datasource.coronacidades.org/br/cities/vacina")
    df2 = df2[["state_name", "city_name", "vacinados", "perc_vacinados", "imunizados", "perc_imunizados", "nao_vacinados"]]
    # df2 = df2[["state_name", "vacinados", "perc_vacinados", "imunizados", "perc_imunizados", "nao_vacinados"]]
    # estado = st.multiselect(
    #     "Estado",
    #     ["Todos"] + list(df2["state_name"].unique()),
    # )
    # cidade = st.multiselect(
    #     "Cidade",
    #     ["Todos"] + list(df2["city_name"].unique()),
    # )

    container = st.beta_container()
    all = st.checkbox("Todos", value=True)
    if all:
        selected_options = container.multiselect("Estado",
            list(df2["state_name"].sort_values().unique()),list(df2["state_name"].sort_values().unique()))
    else:
        selected_options =  container.multiselect("Estado",
            list(df2["state_name"].sort_values().unique()))
    df2 = df2[df2["state_name"].isin(selected_options)]
    df2.rename(columns={'state_name': 'Estado',
                        'city_name': 'Cidade', 
                        'vacinados': 'Quantidade vacinados', 
                        'perc_vacinados': 'Porcentagem vacinados', 
                        'imunizados': 'Quantidade imunizados (doses completas)', 
                        'perc_imunizados': 'Porcentagem imunizados', 
                        'nao_vacinados': 'População restante a vacinar'}, inplace=True)
    st.dataframe(df2, 1500, 500)
    
