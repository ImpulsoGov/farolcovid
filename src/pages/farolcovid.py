import streamlit as st
import yaml
import loader
import numpy as np
import pandas as pd

# import sys
from models import IndicatorType, IndicatorCards, ProductCards
from model.simulator import run_evolution

import pages.simulacovid as sm
import pages.social_distancing_plots as sdp
import utils


def fix_type(x):

    if (type(x) == str) or (type(x) == np.int64):
        return x

    if type(x) == np.ndarray:
        return "-".join([str(round(i, 1)) for i in x])

    if type(x) == np.float64:
        if x <= 1:
            return str(int(x * 100)) + "%"
        else:
            return int(x)


def update_indicators(indicators, data, config):

    # TODO: indicadores quando cidade não posssui dados
    for group in config["br"]["indicators"].keys():

        ref = [
            config["br"]["indicators"][group]["risk"]
            if group != "social_isolation"
            else config["br"]["indicators"][group]["display"]
        ][0]

        if data[ref].fillna("").values[0] == "":

            indicators[group].display = "- "
            indicators[group].risk = "nan"

            if group != "hospital_capacity":
                indicators[group].right_display = "- "
                indicators[group].left_display = "- "

        else:
            indicators[group].risk = [
                str(data[config["br"]["indicators"][group]["risk"]].values[0])
                if group != "social_isolation"
                else "Fonte: inloco"
            ][0]

            indicators[group].display = fix_type(
                data[config["br"]["indicators"][group]["display"]]
                .fillna("- ")
                .values[0]
            )

            indicators[group].left_display = fix_type(
                data[config["br"]["indicators"][group]["left_display"]]
                .fillna("- ")
                .values[0]
            )

            indicators[group].right_display = fix_type(
                data[config["br"]["indicators"][group]["right_display"]]
                .fillna("- ")
                .values[0]
            )

    return indicators


def filter_options(user_input, df_cities, df_states, config):

    if user_input["city_name"] == "Todos":

        data = df_states[df_states["state_name"] == user_input["state_name"]]

        user_input["state_id"] = data["state_id"].values[0]
        user_input["city_id"] = False
        user_input["place_type"] = "state_id"

    else:
        data = df_cities[
            (df_cities["state_name"] == user_input["state_name"])
            & (df_cities["city_name"] == user_input["city_name"])
        ]

        user_input["state_id"] = False
        user_input["city_id"] = data["city_id"].values[0]
        user_input["place_type"] = "city_id"

        # para simulacovid
        user_input["state_rt"] = (
            df_states[df_states["state_name"] == user_input["state_name"]][
                ["rt_10days_ago_low", "rt_10days_ago_high"]
            ]
            .astype(str)
            .agg("-".join, axis=1)
            .values[0]
        )

    user_input["locality"] = utils.choose_place(
        city=user_input["city_name"], state=user_input["state_name"], region="Todos"
    )

    return user_input, data


@st.cache(suppress_st_warning=True)
def get_data(config):
    return (
        loader.read_data(
            "br",
            config,
            endpoint=config["br"]["api"]["endpoints"]["farolcovid"]["cities"],
        ),
        loader.read_data(
            "br",
            config,
            endpoint=config["br"]["api"]["endpoints"]["farolcovid"]["states"],
        ),
    )


def main():

    utils.localCSS("style.css")

    utils.genHeroSection(
        "Farol", "Entenda e controle a Covid-19 em sua cidade e estado."
    )

    # GET DATA
    config = yaml.load(open("configs/config.yaml", "r"), Loader=yaml.FullLoader)
    df_cities, df_states = get_data(config)

    # REGION/CITY USER INPUT
    user_input = dict()

    user_input["state_name"] = st.selectbox(
        "Estado", df_cities["state_name"].sort_values().unique()
    )

    user_input["city_name"] = st.selectbox(
        "Município",
        utils.add_all(
            df_cities[df_cities["state_name"] == user_input["state_name"]][
                "city_name"
            ].unique()
        ),
    )

    user_input, data = filter_options(user_input, df_cities, df_states, config)
    # print(len(data))

    # SOURCES PARAMS
    sources = utils.get_sources(data, ["beds", "ventilators"], df_cities)
    # print(sources)

    user_input["n_beds"] = sources["number_beds"][0]
    user_input["n_ventilators"] = sources["number_ventilators"][0]

    # POPULATION PARAMS
    user_input["population_params"] = {
        "N": int(data["population"].fillna(0).values[0]),
        "D": int(data["deaths"].fillna(0).values[0]),
        "I": int(data["active_cases"].fillna(0).values[0]),
    }

    if data["confirmed_cases"].sum() == 0:
        st.write(
            f"""<div class="base-wrapper">
                    Seu município ou regional de saúde ainda não possui casos reportados oficialmente. Portanto, simulamos como se o primeiro caso ocorresse hoje.
                    <br><br>Caso queria, você pode mudar esse número abaixo:
                </div>""",
            unsafe_allow_html=True,
        )

        user_input["population_params"]["I"] = 1

    else:
        infectious_period = (
            config["br"]["seir_parameters"]["severe_duration"]
            + config["br"]["seir_parameters"]["critical_duration"]
        )
        st.write(
            f"""<div class="base-wrapper">
        O número de casos confirmados oficialmente no seu município ou estado é de {int(data['confirmed_cases'].sum())} em {data["last_updated_subnotification"].values[0]}. 
        Dada a progressão clínica da doença (em média, {infectious_period} dias) e a taxa de notificação ajustada para o município ou estado de ({int(100*data['notification_rate'].values[0])}%), 
        <b>estimamos que o número de casos ativos é de {int(data['active_cases'].sum())}</b>.<br>
        <br>Caso queria, você pode mudar esse número para a simulação abaixo:
                </div>""",
            unsafe_allow_html=True,
        )

    if st.button("Alterar dados"):

        utils.genInputCustomizationSectionHeader(user_input["locality"])

        user_input = utils.genInputFields(
            user_input["locality"], user_input, sources, config
        )

        # TODO: Confirmar as mudanças dos valores dos cards aqui!
        config["br"]["indicators"]["hospital_capacity"]["right_display"] = user_input[
            "n_beds"
        ]
        config["br"]["indicators"]["hospital_capacity"]["left_display"] = user_input[
            "n_ventilators"
        ]
        config["br"]["indicators"]["subnotification_rate"]["left_display"] = user_input[
            "population_params"
        ]["D"]

        # AMBASSADOR SECTION
        utils.genAmbassadorSection()

    # INDICATORS CARDS
    indicators = IndicatorCards

    # TODO: casos de municipios sem dados
    indicators = update_indicators(indicators, data, config)

    utils.genKPISection(
        locality=user_input["locality"],
        alert=data["overall_alert"].values[0],
        indicators=indicators,
    )

    # PLOTS
    # st.write("<div class='see-more-btn'></div>", unsafe_allow_html=True)

    if st.button("Veja mais"):

        st.write(
            """
            <div class="base-wrapper product-section">
                    <span class="section-header primary-span">ISOLAMENTO SOCIAL (IN LOCO)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if user_input["city_id"]:
            locality_id = user_input["city_id"]
        else:
            df_state_mapping = pd.read_csv("./configs/states_table.csv")
            state = df_state_mapping.loc[
                df_state_mapping["state_name"] == data["state_name"].values[0]
            ]
            locality_id = state.iloc[0]["state_num_id"]

        try:
            fig = sdp.gen_social_dist_plots_placeid(locality_id)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.write("Seu município ou estado não possui mais de 30 dias de dado.")

    # TOOLS
    products = ProductCards
    products[1].recommendation = f'Risco {data["overall_alert"].values[0]}'
    utils.genProductsSection(products)

    product = st.selectbox(
        "",
        [
            "Como você gostaria de prosseguir?",
            "SimulaCovid",
            "Saúde em Ordem (em breve)",
        ],
    )

    if product == "SimulaCovid":
        sm.main(user_input, indicators, data, config)

    elif product == "Saúde em Ordem (em breve)":
        pass

    st.write(
        """
    <div class="base-wrapper">
        Estamos à disposição para apoiar o gestor público a aprofundar a 
        análise para seu estado ou município, de forma inteiramente gratuita. 
        <a target="_blank" style="color:#3E758A;" href="https://coronacidades.org/fale-conosco/"><b>Entre em contato conosco</a>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
