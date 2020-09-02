import streamlit as st
import yaml
import loader
import numpy as np
import pandas as pd

# import sys
from models import IndicatorType, IndicatorCards, ProductCards, DimensionCards

from model.simulator import run_simulation, get_dmonth

# import pdf_report.pdfgen as pdfgen
import pages.simulacovid as sm
import pages.saude_em_ordem as so
import pages.distancing as ds
import pages.onda_covid as oc
import plots
import utils
import amplitude
import session

from streamlit.server.Server import Server
import os

import bisect
import math


def fix_type(x, group, position):
    if type(x) == np.ndarray:
        if "- " in x:
            return "- "
        else:
            return " a ".join(
                [str(round(i, 1)) if type(i) != str else i.strip() for i in x]
            )

    if x == "- ":
        return x

    if (group == "situation" and position == "display") or (
        group == "trust" and position == "left_display"
    ):
        return round(float(x), 2)

    if group == "trust" and position == "display":
        return int(round(10 * (1 - x), 0))  # muda para não notificado

    if group == "situation" and position == "left_display":
        return str(int(x)) + " dias"

    if group == "capacity" and position == "display":
        x = math.ceil(x / 30)
        # TODO: passar para config
        dmonth = {1: "até 1", 2: "até 2", 3: "até 3", 4: "+ 3"}
        return dmonth[x]

    if (type(x) == str) or (type(x) == np.int64) or (type(x) == int):
        return x

    if type(x) == np.float64:
        if (x <= 1) & (group == "social_isolation"):
            return str(int(round(100 * x, 0))) + "%"
        else:
            return int(x)


def update_indicators(indicators, data, config, user_input, session_state):
    # TODO: indicadores quando cidade não posssui dados
    for group in config["br"]["indicators"].keys():
        # Fix values for each position
        dic_indicators = dict()
        for position in config["br"]["indicators"][group].keys():
            # Filter indicators
            if config["br"]["indicators"][group][position] != "None":
                dic_indicators[position] = fix_type(
                    data[config["br"]["indicators"][group][position]]
                    .fillna("- ")
                    .values[0],
                    group,
                    position,
                )
            else:
                dic_indicators[position] = "None"

        if np.isnan(data[config["br"]["indicators"][group]["risk"]].values[0]):
            # print("aqui!!!")
            # dic_indicators["display"] = "- "
            dic_indicators["risk"] = "nan"

            if group == "rt":  # doesn't show values
                indicators[group].right_display = "- "
                indicators[group].left_display = "- "

        print(dic_indicators)

        indicators[group].risk = dic_indicators["risk"]
        indicators[group].left_display = dic_indicators["left_display"]
        indicators[group].right_display = dic_indicators["right_display"]
        indicators[group].display = dic_indicators["display"]

    # indicators["subnotification_rate"].left_display = session_state.number_cases
    indicators["capacity"].left_display = int(session_state.number_beds)
    indicators["capacity"].right_display = int(session_state.number_icu_beds)

    # Caso o usuário altere os casos confirmados, usamos esse novo valor para a estimação
    # TODO: vamos acabar com o user_iput e manter só session_state?
    if (session_state.number_cases is not None) and (
        session_state.number_cases != user_input["population_params"]["I_compare"]
    ):
        user_input["population_params"]["I"] = session_state.number_cases
        user_input["population_params"]["D"] = session_state.number_cases

    return indicators


def update_user_input_ids(data, user_input):

    user_input["state_num_id"] = data["state_num_id"].values[0]
    user_input["health_region_id"] = False
    user_input["city_id"] = False

    if user_input["place_type"] == "state_num_id":
        return user_input

    # health region level
    user_input["health_region_id"] = data["health_region_id"].values[0]
    if user_input["place_type"] == "health_region_id":
        return user_input

    # city level
    user_input["city_id"] = data["city_id"].values[0]
    return user_input


def choose_rt(user_input, dfs, level):

    places = {1: "city", 2: "health_region", 3: "state"}

    place_name = places[level] + "_name"
    df = dfs[places[level]][dfs[places[level]][place_name] == user_input[place_name]]

    if level > 3:
        user_input["rt_values"] = {"best": 2.5, "worst": 3}
        user_input["rt_level"] = "nan"
        return user_input

    elif len(df["rt_low_95"].values) > 0:
        user_input["rt_values"] = {
            "best": df["rt_low_95"].values[0],
            "worst": df["rt_high_95"].values[0],
        }

        user_input["rt_level"] = [
            places[level] + "_id"
            if places[level] != "state"
            else places[level] + "_num_id"
        ][0]

        return user_input

    else:
        return choose_rt(user_input, dfs, level + 1)


def update_user_input_places(user_input, dfs, config):

    # Nivel Estado
    if (
        user_input["city_name"] == "Todos"
        and user_input["health_region_name"] == "Todos"
    ):
        data = dfs["state"][dfs["state"]["state_name"] == user_input["state_name"]]
        user_input["place_type"] = "state_num_id"
        # Escolhe Rt para SimulaCovid
        user_input = choose_rt(user_input, dfs, level=3)

    # Nivel Regional
    elif user_input["city_name"] == "Todos":
        data = dfs["health_region"][
            dfs["health_region"]["health_region_name"]
            == user_input["health_region_name"]
        ]
        user_input["place_type"] = "health_region_id"
        # Escolhe Rt para SimulaCovid
        user_input = choose_rt(user_input, dfs, level=2)

    # Nivel Cidade
    else:
        data = dfs["city"][
            (dfs["city"]["state_name"] == user_input["state_name"])
            & (dfs["city"]["city_name"] == user_input["city_name"])
        ]
        user_input["place_type"] = "city_id"
        # Escolhe Rt para SimulaCovid
        user_input = choose_rt(user_input, dfs, level=1)

    # Seleciona localidade para títulos
    user_input["locality"] = utils.choose_place(
        city=user_input["city_name"],
        region=user_input["health_region_name"],
        state=user_input["state_name"],
    )

    # Update dos ids
    user_input = update_user_input_ids(data, user_input)
    return user_input, utils.fix_dates(data)


def gen_big_table(config, dfs):
    # st.write(dfs["state"])
    state_data = dfs["state"].sort_values(by="state_name")
    proportion = str((state_data.shape[0] + 1) * 5) + "vw"
    text = f"""
    <br>
    <div class="base-wrapper flex flex-column" style="background-color: rgb(0, 144, 167);">
        <div class="white-span header p1" style="font-size:30px;">FAROL COVID: Como estão os estados?</div>
        <div class="white-span">Uma visão detalhada dos indicadores para os estados brasileiros.</div>
    </div><br><br>
    <div class="big-table" id="big-table">
        <div class="big-table-head-box">
            <div class="big-table-line btl0" style="height: {proportion};"></div>
            <div class="big-table-line btl1" style="height: {proportion};"></div>
            <div class="big-table-line btl2" style="height: {proportion};"></div>
            <div class="big-table-line btl3" style="height: {proportion};"></div>
            <div class="big-table-line btl4" style="height: {proportion};"></div>
            <div class="big-table-field btt0">Estado e nível de alerta</div>
            <div class="big-table-field btt1">Média móvel de novos casos por 100mil habitantes</div>
            <div class="big-table-field btt2">Ritmo de contágio</div>
            <div class="big-table-field btt3">Capacidade do sistema de saúde</div>
            <div class="big-table-field btt4">Taxa de subnotificação</div>
            <div class="big-table-field btt5">Média móvel de novas mortes por 100mil habitantes</div>
        </div>
    """
    row_order = 0
    for index, sector_data in state_data.iterrows():
        text += gen_sector_big_row(sector_data, row_order, config)
        row_order += 1
    text += f"""<div class="big-table-endspacer">
        </div>
    </div>"""
    st.write(text, unsafe_allow_html=True)


def gen_sector_big_row(my_state, index, config):
    """ Generates a row of a table given the necessary information coming from a sector data row """
    alert_info = {
        "nan": ["grey", "❓"],
        0: ["#0090A7", "👍"],
        1: ["#F7B500", "😨"],
        2: ["#F77800", "⚠"],
        3: ["#F02C2E", "🛑"],
    }
    level_data = config["br"]["farolcovid"]["rules"]

    # TODO: passar para config
    dmonth = {1: "até 1", 2: "até 2", 3: "até 3", 4: "+ 3"}

    return f"""<div class="big-table-row {["btlgrey","btlwhite"][index % 2]}">
            <div class="big-table-index-background" style="background-color:{alert_info[my_state["overall_alert"]][0]};"></div>
            <div class="big-table-field btf0">{my_state["state_name"]} {alert_info[my_state["overall_alert"]][1]}</div>
            <div class="big-table-field btf1" style="color:{alert_info[find_level(level_data["situation_classification"]["cuts"],level_data["situation_classification"]["categories"],my_state["daily_cases_mavg_100k"])][0]};">{"%0.2f"%my_state["daily_cases_mavg_100k"]}</div>
            <div class="big-table-field btf2" style="color:{alert_info[find_level(level_data["control_classification"]["cuts"],level_data["control_classification"]["categories"],my_state["rt_most_likely"])][0]};" > {"%0.2f"%my_state["rt_most_likely"]}</div>
            <div class="big-table-field btf3" style="color:{alert_info[find_level(level_data["capacity_classification"]["cuts"],level_data["capacity_classification"]["categories"],my_state["dday_icu_beds"])][0]};">{dmonth[math.ceil(my_state["dday_icu_beds"] / 30)]} mês(es)</div>
            <div class="big-table-field btf4" style="color:{alert_info[find_level(level_data["trust_classification"]["cuts"],level_data["trust_classification"]["categories"],my_state["notification_rate"])][0]};">{int(my_state["subnotification_rate"]*100)}%</div>
            <div class="big-table-field btf5">{"%0.2f"%my_state["new_deaths_mavg_100k"]}</div>
        </div>"""


def find_level(cuts, levels, value):
    if np.isnan(value):
        return "nan"
    index = bisect.bisect(cuts, value)
    return levels[min(index - 1, len(levels) - 1)]


@st.cache(suppress_st_warning=True)
def get_data(config):

    dfs = {
        place: loader.read_data(
            "br",
            config,
            endpoint=config["br"]["api"]["endpoints"]["farolcovid"][place],
        ).pipe(utils.fix_dates)
        for place in ["city", "health_region", "state"]
    }

    # places_ids = loader.read_data("br", config, "br/places/ids")
    return dfs


def main(session_state):
    #  ==== GOOGLE ANALYTICS SETUP ====
    GOOGLE_ANALYTICS_CODE = os.getenv("GOOGLE_ANALYTICS_CODE")
    if GOOGLE_ANALYTICS_CODE:
        import pathlib
        from bs4 import BeautifulSoup

        GA_JS = (
            """
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', '%s');
        """
            % GOOGLE_ANALYTICS_CODE
        )
        index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
        soup = BeautifulSoup(index_path.read_text(), features="lxml")
        if not soup.find(id="google-analytics-loader"):
            script_tag_import = soup.new_tag(
                "script",
                src="https://www.googletagmanager.com/gtag/js?id=%s"
                % GOOGLE_ANALYTICS_CODE,
            )
            soup.head.append(script_tag_import)
            script_tag_loader = soup.new_tag("script", id="google-analytics-loader")
            script_tag_loader.string = GA_JS
            soup.head.append(script_tag_loader)
            index_path.write_text(str(soup))
    # ====

    # Amplitude: Get user info
    user_analytics = amplitude.gen_user(utils.get_server_session())
    opening_response = user_analytics.safe_log_event(
        "opened farol", session_state, is_new_page=True
    )

    utils.localCSS("style.css")

    utils.genHeroSection(
        title1="Farol",
        title2="Covid",
        subtitle="Entenda e controle a Covid-19 em sua cidade e estado.",
        logo="https://i.imgur.com/CkYDPR7.png",
        header=True,
    )

    config = yaml.load(open("configs/config.yaml", "r"), Loader=yaml.FullLoader)

    # TEMPORARY BANNER FC
    st.write(
        """
        <div>
            <div class="base-wrapper flex flex-column" style="background-color:#0090A7">
                <div class="white-span header p1" style="font-size:30px;">O FAROLCOVID ESTÁ DE CARA NOVA!</div>
                <span class="white-span">Aprimoramos a plataforma, a metodologia e adicionamos novas ferramentas para acompanhamento da crise da Covid-19 no Brasil.<br><b>Que tal explorar com a gente?</b></span>
                <br><div style="margin-top: 15px;"></div>
            <div>
                <a href="#novidades" class="info-btn">Entenda como navegar</a>
            </div>
            <div id="novidades" class="nov-modal-window">
                <div>
                    <a href="#" title="Close" class="info-btn-close" style="color: white;">&times</a>
                    <div style="margin: 10px 15px 15px 15px;">
                        <h1 class="primary-span">Saiba como cada ferramenta apoia a resposta ao coronavírus</h1>
                        <p class="darkblue-span uppercase"> <b>Farol Covid</b> </p>
                        <img class="img-modal" src=%s alt="Ícone Farol Covid">
                        <div>
                            <p> <b>Importante: mudamos a metodologia dos indicadores - veja mais em Modelos, limitações e fontes no menu lateral.</b> Descubra o nível de alerta do estado, regional de saúde ou município de acordo com os indicadores:</p>
                            - <b>Situação da doença</b>: média de novos casos 100 mil por habitantes;</br>
                            - <b>Controle da doença</b>: taxa de contágio</br>
                            - <b>Capacidade do sistema</b>: tempo para ocupação de leitos UTI Covid</br>
                            - <b>Confiança de dados</b>: taxa de subnotificação de casos</br><br>
                        </div>
                        <div>
                        <p class="darkblue-span uppercase"> <b>SimulaCovid</b> </p>
                        <img class="img-modal" src=%s alt="Ícone SimulaCovid">	
                        <p style="height:100px;">Simule o que pode acontecer com o sistema de saúde local se o ritmo de contágio aumentar 
                            ou diminuir e planeje suas ações para evitar a sobrecarga hospitalar.</p>
                        </div>
                        <div>
                        <p class="darkblue-span uppercase"> <b>Distanciamento Social</b> </p>
                        <img class="img-modal" src=%s alt="Ícone Distanciamento Social">
                            <p style="height:100px;">Acompanhe a atualização diária do índice e descubra como está a circulação de pessoas 
                                e o distanciamento social no seu estado ou município.    
                            </p>
                        </div>
                        <div>
                        <p class="darkblue-span uppercase"> <b>Saúde em Ordem</b> </p>
                        <img class="img-modal" src=%s alt="Ícone Saúde em Ordem">
                        <p> Entenda quais atividades deveriam reabrir primeiro no seu estado ou regional, considerando:
                            - <b>Segurança Sanitária</b>: quais setores têm menor exposição à Covid-19?</br>
                            - <b>Contribuição Econômica</b>: quais setores movimentam mais a economia local?</br></p>
                        <p> </p>
                        </div>
                        <div>
                        <p class="darkblue-span uppercase"> <b>Onda Covid</b> </p>
                        <img class="img-modal" src=%s alt="Ícone Onda Covid">
                        <p>Com base no número de óbitos de Covid-19 registrados, acompanhe se seu município já saiu do pico da doença. </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>"""
        % (
            config["br"]["icons"]["farolcovid_logo"],
            config["br"]["icons"]["simulacovid_logo"],
            config["br"]["icons"]["distanciamentosocial_logo"],
            config["br"]["icons"]["saudeemordem_logo"],
            config["br"]["icons"]["ondacovid_logo"],
        ),
        unsafe_allow_html=True,
    )

    st.write(
        """
    <div class="base-wrapper primary-span">
        <span class="section-header">Selecione seu estado ou município no mapa abaixo:</span>
    </div>""",
        unsafe_allow_html=True,
    )

    # GET DATA
    dfs = get_data(config)

    # REGION/CITY USER INPUT
    user_input = dict()
    user_input["state_name"] = st.selectbox("Estado", utils.filter_place(dfs, "state"))

    user_input["health_region_name"] = st.selectbox(
        "Região de Saúde",
        utils.filter_place(dfs, "health_region", state_name=user_input["state_name"]),
    )

    user_input["city_name"] = st.selectbox(
        "Município",
        utils.filter_place(
            dfs,
            "city",
            state_name=user_input["state_name"],
            health_region_name=user_input["health_region_name"],
        ),
    )

    changed_city = user_analytics.safe_log_event(
        "picked farol place",
        session_state,
        event_args={"state": user_input["state_name"], "city": user_input["city_name"]},
    )

    user_input, data = update_user_input_places(user_input, dfs, config)

    # GENERATE MAPS
    map_place_id = utils.Dictionary().get_state_alphabetical_id_by_name(
        user_input["state_name"]
    )

    if os.getenv("IS_LOCAL") == "TRUE":
        map_url = config["br"]["api"]["mapserver_local"]
    else:
        map_url = config["br"]["api"]["mapserver_external"]

    st.write(
        f"""
    <div class="brazil-map-div">
        <div class="alert-levels-map-overlay">
        </div>
        <div>
        <iframe id="map" src="resources/iframe-gen.html?url={map_url}maps/map-iframe?place_id=BR" class="map-br" scrolling="no">
        </iframe>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.write(
        f"""
    <iframe id="map-state" src="resources/iframe-gen.html?url={map_url}maps/map-iframe?place_id={map_place_id}" class="map-state" scrolling="no">
    </iframe>
    """,
        unsafe_allow_html=True,
    )
    st.write(
        f"""
        <div class="selectors-box" id="selectors-box">
        </div>
        <iframe src="resources/select-box-mover.html?place_id={user_input["state_name"]}{user_input["health_region_name"]}{user_input["city_name"]}" height="0px">
        </iframe>""",
        unsafe_allow_html=True,
    )

    # SOURCES PARAMS
    user_input = utils.get_sources(user_input, data, dfs["city"], ["beds", "icu_beds"])

    # POPULATION PARAMS
    try:
        user_input["population_params"] = {
            "N": int(data["population"].fillna(0).values[0]),
            "D": int(data["deaths"].fillna(0).values[0]),
            "I": int(data["active_cases"].fillna(0).values[0]),
            "I_confirmed": int(data["confirmed_cases"].fillna(0).values[0]),
            "I_compare": int(data["confirmed_cases"].fillna(0).values[0]),
        }
    except:
        user_input["population_params"] = {
            "N": int(data["population"].fillna(0).values[0]),
            "D": int(data["deaths"].fillna(0).values[0]),
            "I": 0,
            "I_confirmed": int(data["confirmed_cases"].fillna(0).values[0]),
            "I_compare": int(data["confirmed_cases"].fillna(0).values[0]),
        }

    user_input["Rt"] = {
        "best": data["rt_low_95"].values[0],
        "worst": data["rt_high_95"].values[0],
        "is_valid": data["rt_most_likely"].apply(str).values[0],
    }

    user_input["last_updated_cases"] = data["last_updated_subnotification"].max()
    # Update session values to standard ones if changed city or opened page or reseted values
    if (
        session_state.state_name != user_input["state_name"]
        or session_state.health_region_name != user_input["health_region_name"]
        or session_state.city_name != user_input["city_name"]
        or session_state.number_beds is None
        or session_state.reset
    ):
        session_state.state_name = user_input["state_name"]
        session_state.health_region_name = user_input["health_region_name"]
        session_state.city_name = user_input["city_name"]

        session_state.state_num_id = user_input["state_num_id"]
        session_state.health_region_id = user_input["health_region_id"]
        session_state.city_id = user_input["city_id"]

        session_state.number_beds = int(
            user_input["number_beds"]
            * config["br"]["simulacovid"]["resources_available_proportion"]
        )
        session_state.number_icu_beds = int(
            user_input["number_icu_beds"]
            * config["br"]["simulacovid"]["resources_available_proportion"]
        )
        session_state.number_cases = user_input["population_params"]["I_confirmed"]
        session_state.number_deaths = user_input["population_params"]["D"]
        session_state.reset = True

    if data["confirmed_cases"].sum() == 0:
        st.write(
            f"""<div class="base-wrapper">
                    Seu município ou Região de Saúde ainda não possui casos reportados oficialmente. Portanto, simulamos como se o primeiro caso ocorresse hoje.
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
        placeholder_value_pls_solve_this = 0

    # DIMENSIONS CARDS
    dimensions = DimensionCards
    utils.genAnalysisDimmensionsSection(dimensions)

    # INDICATORS CARDS
    indicators = IndicatorCards

    indicators = update_indicators(indicators, data, config, user_input, session_state)

    data["overall_alert"] = data["overall_alert"].map(
        config["br"]["farolcovid"]["categories"]
    )
    if "state" in user_input["place_type"]:
        # Add disclaimer to cities in state alert levels
        total_alert_regions = (
            dfs["health_region"][
                dfs["health_region"]["state_num_id"] == data["state_num_id"].unique()[0]
            ]
            .assign(
                overall_alert=lambda df: df["overall_alert"].map(
                    config["br"]["farolcovid"]["categories"]
                )
            )["overall_alert"]
            .value_counts()
        )

        utils.genKPISection(
            place_type=user_input["place_type"],
            locality=user_input["locality"],
            alert=data["overall_alert"].values[0],
            indicators=indicators,
            n_colapse_regions=total_alert_regions[
                total_alert_regions.index.isin(["altíssimo", "alto"])
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
            para cálculo da projeção de dias para atingir capacidade máxima.<br><b>Para municípios, utilizamos os recursos da respectiva regional de saúde.</b>
            São considerados leitos os tipos: cirúrgicos, clínicos e hospital-dia. A capacidade de UTI é dada pelo total de leitos UTI Covid adulto.</i>
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
            fig2 = plots.plot_rt_wrapper(
                user_input[user_input["place_type"]], user_input["place_type"]
            )
            st.plotly_chart(fig2, use_container_width=True)
        except:
            st.write(
                """<div class="base-wrapper"><b>Seu município, regional ou estado não possui mais de 30 dias de dados de casos confirmados.</b>""",
                unsafe_allow_html=True,
            )
        st.write(
            "<div class='base-wrapper'><i>Em breve:</i> gráficos de subnotificação e média móvel de novos casos por 100k habitantes.</div>",
            unsafe_allow_html=True,
        )

    utils.stylizeButton(
        name="Confira a evolução de indicadores-chave",
        style_string="""border: 1px solid var(--main-white);box-sizing: border-box;border-radius: 15px; width: auto;padding: 0.5em;text-transform: uppercase;font-family: var(--main-header-font-family);color: var(--main-white);background-color: var(--main-primary);font-weight: bold;text-align: center;text-decoration: none;font-size: 18px;animation-name: fadein;animation-duration: 3s;margin-top: 1em;""",
        session_state=session_state,
    )

    # AMBASSADOR SECTION
    utils.gen_ambassador_section()

    # indicators["hospital_capacity"].left_display = user_input["number_beds"]
    # indicators["hospital_capacity"].right_display = user_input["number_icu_beds"]
    # indicators["subnotification_rate"].left_display = user_input["population_params"][
    # "D"
    # ]

    # PDF-REPORT GEN BUTTON
    # if st.button("Gerar Relatório PDF"):
    #     user_analytics.log_event("generated pdf")
    #     st.write(
    #         """<div class="base-wrapper">Aguarde um momento por favor...</div>""",
    #         unsafe_allow_html=True,
    #     )
    #     st.markdown(
    #         pdfgen.gen_pdf_report(user_input, indicators, data, config),
    #         unsafe_allow_html=True,
    #     )

    # TOOLS
    products = ProductCards
    # products[2].recommendation = f'Risco {data["overall_alert"].values[0]}'

    utils.genProductsSection(products)

    # SELECTION BUTTONS
    # TODO: limpar esse código! está 100% repetido!!!
    if session_state.continuation_selection is None:
        session_state.continuation_selection = [False, False, False, False]

    simula_button_name = "Clique Aqui"  # Simula covid 0space
    saude_button_name = "Clique Aqui "  # Saude em ordem 1space
    distancia_button_name = "Clique_Aqui"  # Distanciamento social
    onda_button_name = "Clique_Aqui "  # onda covid
    if st.button(simula_button_name):  # SIMULA
        session_state.continuation_selection = [True, False, False, False]
    if st.button(distancia_button_name):  # DISTANCIAMENTO
        session_state.continuation_selection = [False, True, False, False]
    if st.button(saude_button_name):  # SAUDE
        session_state.continuation_selection = [False, False, True, False]
    if st.button(onda_button_name):  # ONDA
        session_state.continuation_selection = [False, False, False, True]

    utils.stylizeButton(
        name=simula_button_name,
        style_string="""border: 1px solid black;""",
        session_state=session_state,
        others={"ui_binSelect": 1},
    )

    utils.stylizeButton(
        name=distancia_button_name,
        style_string="""border: 1px solid black;""",
        session_state=session_state,
        others={"ui_binSelect": 2},
    )
    utils.stylizeButton(
        name=saude_button_name,
        style_string="""border: 1px solid black;""",
        session_state=session_state,
        others={"ui_binSelect": 3},
    )
    utils.stylizeButton(
        name=onda_button_name,
        style_string="""border: 1px solid black;""",
        session_state=session_state,
        others={"ui_binSelect": 4},
    )
    if session_state.continuation_selection[0]:
        user_analytics.safe_log_event(
            "picked simulacovid",
            session_state,
            event_args={
                "state": session_state.state_name,
                "health_region": session_state.health_region_name,
                "city": session_state.city_name,
            },
            alternatives=[
                "picked saude_em_ordem",
                "picked simulacovid",
                "picked onda",
                "picked distanciamento",
            ],
        )
        # Downloading the saved data from memory
        user_input["number_beds"] = session_state.number_beds
        user_input["number_icu_beds"] = session_state.number_icu_beds
        user_input["number_deaths"] = session_state.number_deaths
        user_input["number_cases"] = session_state.number_cases
        sm.main(user_input, indicators, data, config, session_state)
        # TODO: remove comment on this later!
        # utils.gen_pdf_report()

    elif session_state.continuation_selection[1]:
        user_analytics.safe_log_event(
            "picked distanciamento",
            session_state,
            event_args={
                "state": session_state.state_name,
                "health_region": session_state.health_region_name,
                "city": session_state.city_name,
            },
            alternatives=[
                "picked saude_em_ordem",
                "picked simulacovid",
                "picked onda",
                "picked distanciamento",
            ],
        )
        ds.main(user_input, indicators, data, config, session_state)

    elif session_state.continuation_selection[2]:
        user_analytics.safe_log_event(
            "picked saude_em_ordem",
            session_state,
            event_args={
                "state": session_state.state_name,
                "health_region": session_state.health_region_name,
                "city": session_state.city_name,
            },
            alternatives=[
                "picked saude_em_ordem",
                "picked simulacovid",
                "picked onda",
                "picked distanciamento",
            ],
        )
        so.main(user_input, indicators, data, config, session_state)

    elif session_state.continuation_selection[3]:
        user_analytics.safe_log_event(
            "picked onda",
            session_state,
            event_args={
                "state": session_state.state_name,
                "health_region": session_state.health_region_name,
                "city": session_state.city_name,
            },
            alternatives=[
                "picked saude_em_ordem",
                "picked simulacovid",
                "picked onda",
                "picked distanciamento",
            ],
        )
        oc.main(user_input, indicators, data, config, session_state)

    # BIG TABLE
    gen_big_table(config, dfs)
    # FOOTER
    utils.gen_whatsapp_button(config["impulso"]["contact"])
    utils.gen_footer()
    user_analytics.conclude_user_session(session_state)


if __name__ == "__main__":
    main()
