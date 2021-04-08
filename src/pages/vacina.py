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
        subtitle="Veja a evolução da vacinação em sua cidade ou estado!",
        logo="https://i.imgur.com/w5yVANW.png",
        header=False,
    )
    he.genHeader("4")
    st.write(
        """
        <div class="base-wrapper flex flex-column" style="background-color: rgb(0, 144, 167);">
            <div class="white-span header p1" style="font-size:30px;">Acompanhe e compare as informações mais atualizadas sobre a vacinação nos municípios do Brasil.</div>
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
    
