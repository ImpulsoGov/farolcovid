import streamlit as st
import numpy as np
import pandas as pd
import utils
import pages.header as he

def main(session_state):
    utils.localCSS("vacinastyle.css")
    he.genHeader("4")
    st.write(
        f"""
        <div class="base-wrapper" style="background-color:#0090A7;">
            <div class="hero-wrapper">
                <div class="hero-container" style="width:40%;">
                    <div class="hero-container-content">
                        <span class="subpages-container-product white-span">Vacinômetro</span>
                        <span class="subpages-subcontainer-product white-span">Veja a evolução da vacinação em sua cidade ou estado! </span>
                        <span class="subpages-container-subtitle white-span">Acompanhe e compare as informações mais atualizadas sobre a vacinação nos municípios do Brasil.</span>
                    </div>
                </div>
                <div class="subpages-container-image">   
                    <img style="width: 100%;" src="https://i.imgur.com/w5yVANW.png"/>
                </div>
            </div><br>
        </div>
        <div>
            <br><br>
        </div>
        """,
        unsafe_allow_html=True,
    )
    df2 = pd.read_csv("http://datasource.coronacidades.org/br/cities/vacina")
    df2 = df2[["state_name", "city_name", "vacinados", "perc_vacinados", "imunizados", "perc_imunizados", "nao_vacinados"]]
    container = st.beta_container()
    all = st.checkbox("Todos", value=True)
    if all:
        selected_options = container.multiselect("Estado",
            list(df2["state_name"].sort_values().unique()),list(df2["state_name"].sort_values().unique()))
    else:
        selected_options =  container.multiselect("Estado",
            list(df2["state_name"].sort_values().unique()))
    df2 = df2[df2["state_name"].isin(selected_options)]
    
    # import pdb; pdb.set_trace()
    # df2['perc_imunizados'] = df2['perc_vacinados'] + ' %'
    df2.rename(columns={'state_name': 'Estado',
                        'city_name': 'Cidade', 
                        'vacinados': 'Vacinados', 
                        'perc_vacinados': 'População vacinada', 
                        'imunizados': 'Imunizados (doses completas)', 
                        'perc_imunizados': 'População imunizada', 
                        'nao_vacinados': 'População restante a vacinar'}, inplace=True)
    # st.dataframe(df2.assign(hack='').set_index('hack'), 1500, 500)
    st.write(
        """
        <div class="base-wrapper">
            <embed src="https://codepen.io/gabriellearruda/embed/yLgPjyR?height=432&theme-id=light&default-tab=result" width="100%" height="550">
        </div>""",
        unsafe_allow_html=True,
    )