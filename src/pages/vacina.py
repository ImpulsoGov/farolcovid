import streamlit as st
import numpy as np
import pandas as pd
import utils
import pages.header as he
import json

def main(session_state):
    utils.localCSS("vacinastyle.css")
    he.genHeader("4")
    st.write(
        f"""
        <div class="base-wrapper" style="background-color:#0090A7;">
            <div class="hero-wrapper">
                <div class="hero-container" style="width:45%;">
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
    selected_options =  container.multiselect("Selecione o(s) Estado(s):",
            list(df2["state_name"].sort_values().unique()))
    df2 = df2[df2["state_name"].isin(selected_options)]
    
    # df = pd.DataFrame([['Apple pie', '20'], ['Lemon cake', '30']], index=['row 1', 'row 2'], columns=['Product', 'Quantity'])
    # json_data = df.to_json(orient='records')
    # webdatarocks = {
    #     "container": "#pivot-container",
    #     "width": "100%",
    #     "height": 430,
    #     "toolbar": True,
    #     "report": {
    #         "dataSource": {
    #             "type": "json",
    #             "data": json.loads(json_data)
    #         },
    #         "slice": {
    #             "rows": [
    #                 {
    #                     "uniqueName": "Product"
    #                 }
    #             ],
    #             "columns": [
    #                 {
    #                     "uniqueName": "Measures"
    #                 }
    #             ],
    #             "measures": [
    #                 {
    #                     "uniqueName": "Quantity",
    #                     "aggregation": "sum"
    #                 }
    #             ]
    #         }
    #     }
    # }
    # webdatarocks_json_object = json.dumps(webdatarocks)
    # st.write(
    #     """ 
    #         <link href="https://cdn.webdatarocks.com/latest/webdatarocks.min.css" rel="stylesheet">
    #         <script src="https://cdn.webdatarocks.com/latest/webdatarocks.js"></script>
    #         <div id="pivot-container"></div>
    #         <script>
    #         new WebDataRocks({0});
    #         </script>
    #     """.format(webdatarocks_json_object),
    #     unsafe_allow_html=True,
    # )
    # selected_city_name = container.multiselect("Selecione o(s) Municípios(s):",
    #         list(df2["city_name"].sort_values().unique()),list(df2["city_name"].sort_values().unique()))
    # df2 = df2[df2["city_name"].isin(selected_city_name)]

    # all = st.checkbox("Todos os Estados", value=False)
    # if all:
    #     selected_options = container.multiselect("Selecione o(s) Estado(s):",
    #         list(df2["state_name"].sort_values().unique()),list(df2["state_name"].sort_values().unique()))
    # else:
    #     selected_options =  container.multiselect("Selecione o(s) Estado(s):",
    #         list(df2["state_name"].sort_values().unique()))
    
    
    df2['vacinados'] = df2['vacinados'].replace(np.nan, 0).astype(int)
    df2['imunizados'] = df2['imunizados'].replace(np.nan, 0).astype(int)
    df2['perc_vacinados'] = df2['perc_vacinados'].replace(np.nan, 0).map('{:,.2f}'.format)
    df2['perc_imunizados'] = df2['perc_imunizados'].replace(np.nan, 0).map('{:,.2f}'.format)
    df2['nao_vacinados'] = df2['nao_vacinados'].replace(np.nan, 0).map('{:,.0f}'.format)
    df2["nao_vacinados"] = [x.replace(",", ".") for x in df2["nao_vacinados"]]
    df2['perc_imunizados'] = df2['perc_imunizados'] + ' %'
    df2['perc_vacinados'] = df2['perc_vacinados'] + ' %'
    df2.rename(columns={'state_name': 'Estado',
                        'city_name': 'Cidade', 
                        'vacinados': 'Vacinados (1 Dose)', 
                        'perc_vacinados': 'População vacinada', 
                        'imunizados': 'Imunizados (Dose completas)', 
                        'perc_imunizados': 'População imunizada', 
                        'nao_vacinados': 'População restante a vacinar'}, inplace=True)
    st.dataframe(df2.assign(hack='').set_index('hack'), 1500, 500)
    
    # st.write(
    #     """
    #     <div class="base-wrapper">
    #         <embed src="https://codepen.io/gabriellearruda/embed/yLgPjyR?height=432&theme-id=light&default-tab=result" width="100%" height="550">
    #     </div>""",
    #     unsafe_allow_html=True,
    # )