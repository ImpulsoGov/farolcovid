import streamlit as st
import yaml
import loader
import numpy as np
import pandas as pd

# import sys
from models import IndicatorType, IndicatorCards, ProductCards

from model.simulator import run_simulation, get_dmonth
import pages.simulacovid as sm
import pages.plots as plts
import utils

import session


def fix_type(x, group):

    if type(x) == np.ndarray:
        return " a ".join([str(round(i, 1)) for i in x])

    if (type(x) == str) or (type(x) == np.int64) or (type(x) == int):
        return x

    if type(x) == np.float64:
        if (x <= 1) & (group == "subnotification_rate"):
            return int(round(10 * x, 0))

        if (x <= 1) & (group == "social_isolation"):
            return str(int(round(100 * x, 0))) + "%"

        else:
            return int(x)


def default_indicator(data, col, position, group):

    return fix_type(data[col[position]].fillna("- ").values[0], group)


def update_indicators(indicators, data, config, user_input, session_state):

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

            if group == "subnotification_rate":
                indicators[group].display = str(
                    int(
                        10
                        * data[config["br"]["indicators"][group]["display"]]
                        .fillna("- ")
                        .values[0]
                    )
                )

            else:
                indicators[group].display = fix_type(
                    data[config["br"]["indicators"][group]["display"]]
                    .fillna("- ")
                    .values[0],
                    group,
                )

            indicators[group].risk = [
                str(data[config["br"]["indicators"][group]["risk"]].values[0])
                if group != "social_isolation"
                else "Fonte: inloco"
            ][0]

            indicators[group].left_display = fix_type(
                data[config["br"]["indicators"][group]["left_display"]]
                .fillna("- ")
                .values[0],
                group,
            )

            indicators[group].right_display = fix_type(
                data[config["br"]["indicators"][group]["right_display"]]
                .fillna("- ")
                .values[0],
                group,
            )

    if (session_state.state != user_input["state_name"]) or (
        session_state.city != user_input["city_name"]
    ):

        session_state.state = user_input["state_name"]
        session_state.city = user_input["city_name"]

    elif session_state.refresh:

        indicators["subnotification_rate"].left_display = session_state.cases

        indicators["hospital_capacity"].left_display = session_state.number_beds
        indicators["hospital_capacity"].right_display = session_state.number_ventilators

        user_input["number_beds"] = session_state.number_beds
        user_input["number_ventilators"] = session_state.number_ventilators

    # recalcula capacidade hospitalar
    user_input["strategy"] = "isolation"
    user_input = sm.calculate_recovered(user_input, data)

    dmonth = get_dmonth(
        run_simulation(user_input, config),
        "I2",
        user_input["number_beds"]
        * config["br"]["simulacovid"]["resources_available_proportion"],
    )["best"]

    # TODO: add no config e juntar com farol
    dic_dmonth = {
        1: {"preffix": "até 1", "class": "ruim"},
        2: {"preffix": "até 2", "class": "insatisfatório"},
        3: {"preffix": "+ de 2", "class": "bom"},
    }
    indicators["hospital_capacity"].risk = dic_dmonth[dmonth]["class"]
    indicators["hospital_capacity"].display = dic_dmonth[dmonth]["preffix"]

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
        ).replace({"medio": "médio", "insatisfatorio": "insatisfatório"}),
        loader.read_data(
            "br",
            config,
            endpoint=config["br"]["api"]["endpoints"]["farolcovid"]["states"],
        ).replace({"medio": "médio", "insatisfatorio": "insatisfatório"}),
    )


def main():

    session_state = session.SessionState.get(
        update=False,
        number_beds=None,
        number_ventilators=None,
        deaths=None,
        cases=None,
        state="Acre",
        city="Todos",
        refresh=False,
    )

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

    # SOURCES PARAMS
    user_input = utils.get_sources(user_input, data, df_cities, ["beds", "ventilators"])

    # POPULATION PARAMS
    user_input["population_params"] = {
        "N": int(data["population"].fillna(0).values[0]),
        "D": int(data["deaths"].fillna(0).values[0]),
        "I": int(data["active_cases"].fillna(0).values[0]),
        "I_confirmed": int(data["confirmed_cases"].fillna(0).values[0]),
    }

    user_input["last_updated_cases"] = data["last_updated_subnotification"].max()

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
        O número de casos confirmados oficialmente no seu município ou estado é de {int(data['confirmed_cases'].sum())} em {pd.to_datetime(data["data_last_refreshed"].values[0]).strftime("%d/%m/%Y")}. 
        Dada a progressão clínica da doença (em média, {infectious_period} dias) e a taxa de notificação ajustada para o município ou estado de ({int(100*data['notification_rate'].values[0])}%), 
        <b>estimamos que o número de casos ativos é de {int(data['active_cases'].sum())}</b>.<br>
        <br>Caso queria, você pode mudar esse número para a simulação abaixo:
                </div>""",
            unsafe_allow_html=True,
        )

    # INDICATORS CARDS
    indicators = IndicatorCards

    indicators = update_indicators(indicators, data, config, user_input, session_state)

    utils.genKPISection(
        place_type=user_input["place_type"],
        locality=user_input["locality"],
        alert=data["overall_alert"].values[0],
        indicators=indicators,
    )

    # SPACE AFTER CARDS
    st.write("<div class='base-wrapper product-section'></div>", unsafe_allow_html=True)
    st.write(
        """
        <div class='base-wrapper'>
            <i>* Utilizamos %s&percnt; da capacidade hospitalar reportada por %s em %s 
            para o cálculo da projeção de dias para atingir a capacidade máxima.<br> 
            Consideramos leitos disponíveis para Covid os tipos de leitos cirúrgicos, clínicos e hospital-dia.
            Caso tenha dados mais atuais, sugerimos que mude os valores e refaça essa estimação abaixo.</i>
        </div>
        """
        % (
            str(int(config["br"]["simulacovid"]["resources_available_proportion"] * 100)),
            user_input["author_number_beds"],
            user_input["last_updated_number_beds"],
        ),
        unsafe_allow_html=True,
    )

    if st.button("Confira a evolução de indicadores-chave"):

        if st.button("Esconder"):
            pass

        st.write(
            f"""
            <div class="base-wrapper">
                    <span class="section-header primary-span">TAXA DE ISOLAMENTO SOCIAL EM {user_input["locality"]}</span>
                    <br><br>
                    Percentual de smartphones que não deixou o local de residência, em cada dia, calculado pela inloco. 
                    Para mais informações, <a target="_blank" style="color:#3E758A;" href="https://mapabrasileirodacovid.inloco.com.br/pt/">veja aqui</a>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if user_input["city_id"]:
            locality_id = user_input["city_id"]
        else:
            df_state_mapping = pd.read_csv("./configs/states_table.csv")
            locality_id = df_state_mapping.loc[
                df_state_mapping["state_name"] == data["state_name"].values[0]
            ].iloc[0]["state_num_id"]

        try:
            fig = plts.gen_social_dist_plots_placeid(locality_id)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.write("Seu município ou estado não possui mais de 30 dias de dado.")
        st.write(
            f"""
            <div class="base-wrapper">
                    <span class="section-header primary-span">CÁLCULO DO RITMO DE CONTÁGIO EM {user_input["locality"]}</span>
                    <br><br>
                    O ritmo de contágio, conhecido como número de reprodução efetivo (Rt), traduz a dinâmica de disseminação do Covid a cada dia. 
                    <br>O valor pode ser lido como o número médio de novas infecções diárias causadas por uma única pessoa infectada. 
                    Para mais informações, visite a página de Metodologia.
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            fig2 = plts.plot_rt_wrapper(locality_id)
            st.plotly_chart(fig2, use_container_width=True)
        except:
            st.write("Seu município ou estado não possui mais de 30 dias de dado.")
        st.write(
            "<div class='base-wrapper'><i>Em breve:</i> gráficos de subnotificação.</div>",
            unsafe_allow_html=True,
        )

    # CHANGE DATA SECTION
    utils.genInputCustomizationSectionHeader(user_input["locality"])
    user_input, session_state = utils.genInputFields(user_input, config, session_state)

    if session_state.update:

        session_state.refresh = True
        session_state.update = False

        session.rerun()

    # AMBASSADOR SECTION
    utils.genAmbassadorSection()

    indicators["hospital_capacity"].left_display = user_input["number_beds"]
    indicators["hospital_capacity"].right_display = user_input["number_ventilators"]
    indicators["subnotification_rate"].left_display = user_input["population_params"][
        "D"
    ]

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
        sm.main(user_input, indicators, data, config, session_state)

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
