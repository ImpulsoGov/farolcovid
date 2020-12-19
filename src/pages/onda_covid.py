import streamlit as st
import plots
import pages.data_analysis as da
import loader
import utils
import copy


@st.cache(suppress_st_warning=True)
def get_places_ids(config):
    return loader.read_data("br", config, "br/places/ids")

def gen_banners():
    st.write(
        """
    <div class="base-wrapper flex flex-column" style="background-color:#F02C2E">
        <div class="white-span header p1" style="font-size:30px;">
        Acre está a 5 dias em crescimento da média móvel de mortes.<br>
        O pico de mortes até agora foi de 432 mortes  em 03/08/2020.
        </div>
    </div>
    <div class="base-wrapper flex flex-column" style="background-color:#0090A7">
        <div class="white-span header p1" style="font-size:30px;">
        Seu município está a 10 dias em queda da média móvel de mortes.<br>
        Seu pico de mortes foi de 53 mortes em 25/06/2020.
        </div>
    </div>""",
        unsafe_allow_html=True,
    )


# def gen_cards(distancing_data):

#     st.write(
#         f"""<div class="distancing-cards">
#                 <div class="distancing-container distancing-card-bg">
#                         <div class="distancing-output-wrapper">
#                                 <div class="distancing-output-row">
#                                         <span class="distancing-output-row-prediction-value">
#                                                 {int(distancing_data[-1]*100)}%
#                                         </span>  
#                                 </div> 
#                                 <span class="distancing-output-row-prediction-label">
#                                         das pessoas em média ficaram em casa nos últimos 7 dias.
#                                 </span>
#                         </div>
#                         <img src="https://i.imgur.com/27hutU0.png" class="distancing-output-image">
#                 </div>
#                 <div class="distancing-card-separator"></div>
#                 <div class="distancing-container distancing-card-bg">
#                         <div class="distancing-output-wrapper">
#                                 <div class="distancing-output-row">
#                                         <span class="distancing-output-row-prediction-value">
#                                                 {int(distancing_data[-8]*100)}%
#                                         </span>  
#                                 </div> 
#                                 <span class="distancing-output-row-prediction-label">
#                                         das pessoas em média ficaram em casa entre 14 e 7 dias atrás.
#                                 </span>
#                         </div>
#                         <img src="https://i.imgur.com/27hutU0.png" class="distancing-output-image">
#                 </div>
#             </div>""",
#         unsafe_allow_html=True,
#     )


@st.cache(suppress_st_warning=True)
def loading_cached():
    return loader.read_data(
        "br",
        loader.config,
        endpoint=loader.config["br"]["api"]["endpoints"]["analysis"]["cases"],
    )


def main(user_input, indicators, data, config, session_state):

    utils.genHeroSection(
        title1="Onda", 
        title2="Covid",
        subtitle="Veja e compare a evolução da curva de contágio da Covid-19 em seu estado ou município.", 
        logo="https://i.imgur.com/Oy7IiGB.png",
        header=False
    )

    # Prompt User to Select Heatmap Location
    view = st.selectbox("Selecione a sua visão", options=["Cidade", "Estado", "País"], index=1)

    # Load City/State/Country Heatmap
    if view == "Estado":
        load_states_heatmap(copy.deepcopy(loading_cached()))
    elif view == "Cidade":
        my_dict = utils.Dictionary()
        load_cities_heatmap(copy.deepcopy(loading_cached()), my_dict)
    elif view == "País":
        load_countries_heatmap(config)

def load_states_heatmap(br_cases):
    da.prepare_heatmap(br_cases, place_type="state_id")
    st.write("")

def load_cities_heatmap(br_cases, my_dict):
    st.write(
        """
        <div class="base-wrapper">
            <span class="section-header primary-span">ONDA MORTES DIÁRIAS POR MUNICÍPIO</span>
            <br><br>
            <span class="ambassador-question"><b>Selecione seu estado e município para prosseguir</b></span>
        </div>""",
        unsafe_allow_html=True,
    )
    
    places_ids = get_places_ids(loader.config)
    state_name = st.selectbox("Estado ", utils.filter_place( {'city' : places_ids}, "state"))
    city_name = st.selectbox(
        "Município ",
        utils.filter_place(
            {'city' : places_ids}, "city", state_name=state_name, health_region_name="Todos"
        ),
    )

    deaths_or_cases = (
        st.selectbox("Qual análise você quer ver: Número de mortes ou Taxa de letalidade (mortes por casos)?", ["Mortes", "Letalidade"])
        == "Mortes por casos"
    )
    # print("checking")
    if city_name != "Todos":  # the user selected something
        # print("passed")
        br_cases = br_cases[br_cases["state_name"] == state_name]  # .reset_index()
        # gen_banners()
        uf = my_dict.get_state_alphabetical_id_by_name(state_name)
        da.prepare_heatmap(
            br_cases,
            place_type="city_name",
            group=uf,
            your_city=city_name,
            deaths_per_cases=deaths_or_cases,
        )
        # print("finished preparation")

def load_countries_heatmap(config):
    st.write("")
    da.prepare_heatmap(
        loader.read_data(
            "br",
            loader.config,
            endpoint=config["br"]["api"]["endpoints"]["analysis"]["owid"],
        ),
        place_type="country_pt",
    )
