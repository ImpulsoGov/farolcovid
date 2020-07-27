import streamlit as st
import yaml
import loader
import numpy as np
import pandas as pd

# import sys
from models import IndicatorType, IndicatorCards, ProductCards

from model.simulator import run_simulation, get_dmonth
import pdf_report.pdfgen as pdfgen
import pages.simulacovid as sm
import pages.saude_em_ordem as so
import plots
import utils
import amplitude
import session

from streamlit.server.Server import Server


def fix_type(x, group):

    if type(x) == np.ndarray:
        return " a ".join(
            [str(round(i, 1)) if type(i) != str else i.strip() for i in x]
        )

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

        # Displays
        indicators[group].display = fix_type(
            data[config["br"]["indicators"][group]["display"]].fillna("- ").values[0],
            group,
        )

        # Risk
        indicators[group].risk = [
            str(data[config["br"]["indicators"][group]["risk"]].values[0])
            if group != "social_isolation"
            else "Fonte: inloco"
        ][0]

        # Left display
        indicators[group].left_display = fix_type(
            data[config["br"]["indicators"][group]["left_display"]]
            .fillna("- ")
            .values[0],
            group,
        )

        # Right display
        indicators[group].right_display = fix_type(
            data[config["br"]["indicators"][group]["right_display"]]
            .fillna("- ")
            .values[0],
            group,
        )

        if data[ref].fillna("").values[0] == "":

            indicators[group].display = "- "
            indicators[group].risk = "nan"

            if group == "rt":  # doesn't show values
                indicators[group].right_display = "- "
                indicators[group].left_display = "- "

    indicators["subnotification_rate"].left_display = session_state.number_cases
    indicators["hospital_capacity"].left_display = int(session_state.number_beds)
    indicators["hospital_capacity"].right_display = int(
        session_state.number_ventilators
    )

    # Caso o usuário altere os casos confirmados, usamos esse novo valor para a estimação
    # TODO: vamos acabar com o user_iput e manter só session_state?
    if (session_state.number_cases is not None) and (
        session_state.number_cases != user_input["population_params"]["I_compare"]
    ):
        user_input["population_params"]["I"] = session_state.number_cases
        user_input["population_params"]["D"] = session_state.number_cases

    # Recalcula capacidade hospitalar
    user_input["strategy"] = "estavel"
    user_input = sm.calculate_recovered(user_input, data)

    dmonth = get_dmonth(
        run_simulation(user_input, config), "I2", session_state.number_beds
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


def update_user_input_places(data, user_input):
    
    user_input["state_id"] = data["state_id"].values[0]
    user_input["health_region_id"] = False
    user_input["city_id"] = False

    if user_input["place_type"] == "state_id":
        return user_input
    
    # health region level
    user_input["health_region_id"] = data["health_region_id"].values[0]
    if user_input["place_type"] == "health_region_id":
        return user_input

    # city level
    user_input["city_id"] = data["city_id"].values[0]
    return user_input


def filter_options(user_input, dfs, config):

    if user_input["city_name"] == "Todos" and user_input["health_region_name"] == "Todos":
        data = dfs["states"][dfs["states"]["state_name"] == user_input["state_name"]]
        user_input["place_type"] = "state_id"

    elif user_input["city_name"] == "Todos":
        data = dfs["health_region"][dfs["health_region"]["health_region_name"] == user_input["health_region_name"]]
        user_input["place_type"] = "health_region_id"

    else:
        data = dfs["cities"][
            (dfs["cities"]["state_name"] == user_input["state_name"])
            & (dfs["cities"]["city_name"] == user_input["city_name"])
        ]

        user_input["place_type"] = "city_id"

        # para simulacovid
        user_input["state_rt"] = {
            "best": dfs["states"][dfs["states"]["state_name"] == user_input["state_name"]][
                "rt_10days_ago_low"
            ].values[0],
            "worst": dfs["states"][dfs["states"]["state_name"] == user_input["state_name"]][
                "rt_10days_ago_high"
            ].values[0],
        }
    
    user_input = update_user_input_places(data, user_input)

    user_input["locality"] = utils.choose_place(
        city=user_input["city_name"], state=user_input["state_name"], region=user_input["health_region_name"]
    )

    return user_input, data


@st.cache(suppress_st_warning=True)
def get_data(config):

    dfs = {place: loader.read_data(
            "br",
            config,
            endpoint=config["br"]["api"]["endpoints"]["farolcovid"][place],
        ).replace({"medio": "médio", "insatisfatorio": "insatisfatório"})
        for place in ["cities", "health_region", "states"]}

    return dfs


def main(session_state):

    # Get user info
    user_analytics = amplitude.gen_user(utils.get_server_session())
    opening_response = user_analytics.safe_log_event(
        "opened farol", session_state, is_new_page=True
    )

    utils.localCSS("style.css")

    utils.genHeroSection(
        "Farol", "Entenda e controle a Covid-19 em sua cidade e estado."
    )

    # GET DATA
    config = yaml.load(open("configs/config.yaml", "r"), Loader=yaml.FullLoader)
    dfs = get_data(config)

    # REGION/CITY USER INPUT
    user_input = dict()

    user_input["state_name"] = st.selectbox(
        "Estado", dfs["cities"]["state_name"].sort_values().unique()
    )

    user_input["health_region_name"] = st.selectbox(
        "Regional de Saúde", 
        utils.add_all(
            dfs["cities"][dfs["cities"]["state_name"] == user_input["state_name"]][
                "health_region_name"
            ].unique()
        ),
    )

    user_input["city_name"] = st.selectbox(
        "Município",
        utils.add_all(
            dfs["cities"][dfs["cities"]["state_name"] == user_input["state_name"]][
                "city_name"
            ].unique()
        ),
    )
    changed_city = user_analytics.safe_log_event(
        "picked farol place",
        session_state,
        event_args={"state": user_input["state_name"], "city": user_input["city_name"]},
    )
    user_input, data = filter_options(user_input, dfs, config)

    # SOURCES PARAMS
    user_input = utils.get_sources(user_input, data, dfs["cities"], ["beds", "ventilators"])

    # POPULATION PARAMS
    user_input["population_params"] = {
        "N": int(data["population"].fillna(0).values[0]),
        "D": int(data["deaths"].fillna(0).values[0]),
        "I": int(data["active_cases"].fillna(0).values[0]),
        "I_confirmed": int(data["confirmed_cases"].fillna(0).values[0]),
        "I_compare": int(data["confirmed_cases"].fillna(0).values[0]),
    }

    user_input["Rt"] = {
        "best": data["rt_10days_ago_low"].values[0],
        "worst": data["rt_10days_ago_high"].values[0],
        "is_valid": data["rt_classification"].apply(str).values[0],
    }

    user_input["last_updated_cases"] = data["last_updated_subnotification"].max()
    # Update session values to standard ones if changed city or opened page or reseted values
    if (
        session_state.state != user_input["state_name"]
        or session_state.health_region != user_input["health_region_name"]
        or session_state.city != user_input["city_name"]
        or session_state.number_beds is None
        or session_state.reset
    ):
        session_state.state = user_input["state_name"]
        session_state.state = user_input["health_region_name"]
        session_state.city = user_input["city_name"]
        session_state.number_beds = int(
            user_input["number_beds"]
            * config["br"]["simulacovid"]["resources_available_proportion"]
        )
        session_state.number_ventilators = int(
            user_input["number_ventilators"]
            * config["br"]["simulacovid"]["resources_available_proportion"]
        )
        session_state.number_cases = user_input["population_params"]["I_confirmed"]
        session_state.number_deaths = user_input["population_params"]["D"]
        session_state.reset = True

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

    if "state" in user_input["place_type"]:

        # Add disclaimer to cities in state alert levels
        total_alert_cities = dfs["cities"][
            dfs["cities"]["state_id"] == data["state_id"].unique()[0]
        ]["overall_alert"].value_counts()

        utils.genKPISection(
            place_type=user_input["place_type"],
            locality=user_input["locality"],
            alert=data["overall_alert"].values[0],
            indicators=indicators,
            n_colapse_alert_cities=total_alert_cities[
                total_alert_cities.index.isin(["alto", "médio"])
            ].sum(),
        )

    else:
        utils.genKPISection(
            place_type=user_input["place_type"],
            locality=user_input["locality"],
            alert=data["overall_alert"].values[0],
            indicators=indicators,
        )

    # AVAILABLE CAPACITY DISCLAIMER
    st.write(
        """
        <div class='base-wrapper'>
            <i>* Utilizamos %s&percnt; da capacidade hospitalar reportada por %s em %s 
            para cálculo da projeção de dias para atingir a capacidade máxima.<br>
            Consideramos leitos disponíveis para Covid-19 os tipos: cirúrgicos, clínicos e hospital-dia.
            Caso tenha dados mais atuais, sugerimos que mude abaixo e refaça essa estimação.</i>
        </div>
        """
        % (
            str(
                int(config["br"]["simulacovid"]["resources_available_proportion"] * 100)
            ),
            user_input["author_number_beds"],
            user_input["last_updated_number_beds"],
        ),
        unsafe_allow_html=True,
    )

    # TODO: remove comment on this later!
    # utils.gen_pdf_report()

    # INDICATORS PLOTS
    if st.button("Confira a evolução de indicadores-chave"):
        opening_response = user_analytics.log_event("picked key_indicators", dict())
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
            fig = plots.gen_social_dist_plots_placeid(locality_id)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.write(
                """<div class="base-wrapper"><b>Seu município ou estado não possui mais de 30 dias de dados, ou não possui o índice calculado pela inloco.</b>""",
                unsafe_allow_html=True,
            )
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
            fig2 = plots.plot_rt_wrapper(locality_id)
            st.plotly_chart(fig2, use_container_width=True)
        except:
            st.write(
                """<div class="base-wrapper"><b>Seu município, regional ou estado não possui mais de 30 dias de dados de casos confirmados.</b>""",
                unsafe_allow_html=True,
            )
        st.write(
            "<div class='base-wrapper'><i>Em breve:</i> gráficos de subnotificação.</div>",
            unsafe_allow_html=True,
        )

    # CHANGE DATA SECTION
    utils.genInputCustomizationSectionHeader(user_input["locality"])
    old_user_input = dict(user_input)
    user_input, session_state = utils.genInputFields(user_input, config, session_state)
    if session_state.reset:
        session.rerun()
    if session_state.update:
        opening_response = user_analytics.log_event(
            "updated sim_numbers",
            {
                "beds_change": session_state.number_beds
                - int(old_user_input["number_beds"]),
                "vent_change": session_state.number_ventilators
                - int(old_user_input["number_ventilators"]),
                "cases_change": session_state.number_cases
                - int(old_user_input["population_params"]["I_confirmed"]),
                "deaths_change": session_state.number_deaths
                - int(old_user_input["population_params"]["D"]),
            },
        )
        session_state.update = False
        session.rerun()

    # AMBASSADOR SECTION
    utils.gen_ambassador_section()

    indicators["hospital_capacity"].left_display = user_input["number_beds"]
    indicators["hospital_capacity"].right_display = user_input["number_ventilators"]
    indicators["subnotification_rate"].left_display = user_input["population_params"][
        "D"
    ]
    # PDF-REPORT GEN BUTTON
    if st.button("Gerar Relatório PDF"):
        user_analytics.log_event("generated pdf")
        st.write(
            """<div class="base-wrapper">Aguarde um momento por favor...</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            pdfgen.gen_pdf_report(user_input, indicators, data, config),
            unsafe_allow_html=True,
        )
    # TOOLS
    products = ProductCards
    products[1].recommendation = f'Risco {data["overall_alert"].values[0]}'
    utils.genProductsSection(products)
    product = st.selectbox(
        "", ["Como você gostaria de prosseguir?", "SimulaCovid", "Saúde em Ordem",],
    )
    if product == "SimulaCovid":
        user_analytics.safe_log_event(
            "picked simulacovid",
            session_state,
            event_args={"state": session_state.state, "city": session_state.city,},
            alternatives=["picked saude_em_ordem", "picked simulacovid"],
        )
        # Downloading the saved data from memory
        user_input["number_beds"] = session_state.number_beds
        user_input["number_ventilators"] = session_state.number_ventilators
        user_input["number_deaths"] = session_state.number_deaths
        user_input["number_cases"] = session_state.number_cases
        sm.main(user_input, indicators, data, config, session_state)
        # TODO: remove comment on this later!
        # utils.gen_pdf_report()
    elif product == "Saúde em Ordem":
        user_analytics.safe_log_event(
            "picked saude_em_ordem",
            session_state,
            event_args={"state": session_state.state, "city": session_state.city,},
            alternatives=["picked saude_em_ordem", "picked simulacovid"],
        )
        so.main(user_input, indicators, data, config, session_state)
        pass

    utils.gen_whatsapp_button(config["impulso"]["contact"])
    utils.gen_footer()
    user_analytics.conclude_user_session(session_state)


if __name__ == "__main__":
    main()
