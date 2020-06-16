import streamlit as st
from datetime import datetime
from datetime import timedelta
from typing import List, Dict
from models import (
    SimulatorOutput,
    ContainmentStrategy,
    ResourceAvailability,
    BackgroundColor,
    Logo,
    Link,
    Indicator,
    AlertBackground,
    IndicatorBackground,
    Illustration,
    Product,
)
from typing import List
import re
import numpy as np
import math
import pandas as pd
import os

import collections
import functools
import inspect
import textwrap
import yaml

configs_path = os.path.join(os.path.dirname(__file__), "configs")
cities = pd.read_csv(os.path.join(configs_path, "cities_table.csv"))
states = pd.read_csv(os.path.join(configs_path, "states_table.csv"))

# DATASOURCE TOOLS


def get_inloco_url(config):

    api_inloco = dict()

    if os.getenv("IS_LOCAL") == "TRUE":
        api_url = config["br"]["api"]["local"]
    else:
        api_url = config["br"]["api"]["external"]

    if os.getenv("INLOCO_CITIES_ROUTE") and os.getenv("INLOCO_STATES_ROUTE"):
        api_inloco["cities"] = api_url + os.getenv("INLOCO_CITIES_ROUTE")
        api_inloco["states"] = api_url + os.getenv("INLOCO_STATES_ROUTE")

    else:
        secrets = yaml.load(
            open("../src/configs/secrets.yaml", "r"), Loader=yaml.FullLoader
        )
        api_inloco["cities"] = api_url + secrets["inloco"]["cities"]["route"]
        api_inloco["states"] = api_url + secrets["inloco"]["states"]["route"]

    return api_inloco


# DATES TOOLS


def fix_dates(df):

    for col in df.columns:
        if "last_updated" in col:
            df[col] = pd.to_datetime(df[col]).apply(lambda x: x.strftime("%d/%m/%Y"))
    return df


def convert_times_to_real(row):
    today = datetime.now()
    return today + timedelta(row["ddias"])


# TODO: melhorar essa funcao
def get_sources(user_input, data, cities_sources, resources):

    cols_agg = {
        "number": lambda x: x.sum() if np.isnan(x.sum()) == False else 0,
        "last_updated_number": lambda x: pd.to_datetime(x).max(),
        "author_number": lambda x: x.drop_duplicates().str.cat(),
    }

    for x in resources:  # beds, ventilators

        for item in cols_agg.keys():

            col = "_".join([item, x])

            if user_input["place_type"] == "state_id":

                user_input[col] = cities_sources[
                    cities_sources["state_id"] == data["state_id"].iloc[0]
                ][col].agg(cols_agg[item])

            if user_input["place_type"] == "city_id":
                user_input[col] = data[col].fillna(0).values[0]

                # if "last_updated" in col:
                #     user_input[col] = pd.to_datetime(user_input[col]).strftime("%d/%m")

    user_input["last_updated_number_beds"] = pd.to_datetime(
        user_input["last_updated_number_beds"]
    ).strftime("%d/%m")

    user_input["last_updated_number_ventilators"] = pd.to_datetime(
        user_input["last_updated_number_ventilators"]
    ).strftime("%d/%m")

    # user_input["n_beds"] = sources["number_beds"][0]
    # user_input["n_ventilators"] = sources["number_ventilators"][0]

    # user_input["authors_beds"] = ", ".join(sources["author_number_beds"])
    # user_input["authors_ventilators"] = ", ".join(sources["author_number_ventilators"])

    # user_input["last_updated_beds"] = sources["last_updated_number_beds"].max()
    # user_input["last_updated_ventilators"] = sources["last_updated_number_ventilators"].max()

    return user_input


# PLACES TOOLS


def add_all(x, all_string="Todos"):
    return [all_string] + list(x)


def choose_place(city, region, state):
    if city == "Todos" and region == "Todos" and state == "Todos":
        return "Brasil"
    if city == "Todos" and region == "Todos":
        return state + " (Estado)" if state != "Todos" else "Brasil"
    if city == "Todos":
        return region + " (Região SUS)" if region != "Todos" else "Todas as regiões SUS"
    return city


def get_place_id_by_names(state_name, city_name_input="Todos"):
    """
    In: name of the state (returns a numerical id of only the state) or the name of the state and the name of the city
    Out: the numerical id of the state of the city
    """

    configs_path = os.path.join(os.path.dirname(__file__), "configs")
    cities = pd.read_csv(os.path.join(configs_path, "cities_table.csv"))
    states = pd.read_csv(os.path.join(configs_path, "states_table.csv"))

    state_num_id = states.query("state_name == '%s'" % state_name).values[0][-1]

    if city_name_input == "Todos":
        return state_num_id
    city_id = (
        cities.query("state_num_id == '%s'" % state_num_id)
        .query("city_name == '%s'" % city_name_input)
        .values[0][1]
    )
    return city_id


def get_place_names_by_id(place_id):
    """
    In: id of a place (id < 100 for states, id > 100 for cities)
    Out: either a string representing the name of the state or a list contaning [state name,city name]
    """
    configs_path = os.path.join(os.path.dirname(__file__), "configs")
    cities = pd.read_csv(os.path.join(configs_path, "cities_table.csv"))
    states = pd.read_csv(os.path.join(configs_path, "states_table.csv"))

    state_name_index = [i for i in states.columns].index("state_name")

    if place_id <= 100:
        state_name_index = [i for i in states.columns].index("state_name")
        return states.query("state_num_id == '%s'" % place_id).values[0][
            state_name_index
        ]
    else:
        data = cities.query("city_id == '%s'" % place_id).values[0]
        city_name_index = [i for i in cities.columns].index("city_name")
        state_num_id_index = [i for i in cities.columns].index("state_num_id")
        city_name = data[city_name_index]
        state_id = data[state_num_id_index]
        state_name = states.query("state_num_id == '%s'" % state_id).values[0][
            state_name_index
        ]
        return [state_name, city_name]


def get_state_str_id_by_id(place_id):

    states = pd.read_csv(
        os.path.join(
            os.path.join(os.path.dirname(__file__), "configs"), "states_table.csv"
        )
    )

    index = [i for i in states.columns].index("state_id")
    return states.query("state_num_id == '%s'" % place_id).values[0][index]


def get_ufs_list():

    return [
        "AC",
        "AL",
        "AM",
        "AP",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MG",
        "MS",
        "MT",
        "PA",
        "PB",
        "PE",
        "PI",
        "PR",
        "RJ",
        "RN",
        "RO",
        "RR",
        "RS",
        "SC",
        "SE",
        "SP",
        "TO",
    ]


# FRONT-END TOOLS


def gen_pdf_report():
    st.write(
        """
    <iframe src="resources/ctrlp.html" height="100" width="350" style="border:none;"></iframe>
    """,
        unsafe_allow_html=True,
    )


def make_clickable(text, link):
    # target _blank to open new window
    # extract clickable text to display for your link
    return f'<a target="_blank" href="{link}">{text}</a>'


def localCSS(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def genWhatsappButton() -> None:
    msg = f"Olá Equipe Coronacidades. Vocês podem me ajuda com uma dúvida?"
    phone = "+5511964373097"
    url = "whatsapp://send?text={}&phone=${}".format(msg, phone)
    st.write(
        """ 
         <a href="%s" class="float" target="_blank" id="messenger">
                <i class="material-icons">?</i>
                <p class="float-header">Dúvidas?</p></a>
        """
        % url,
        unsafe_allow_html=True,
    )


# VIEW COMPONENTS FAROLCOVID


def genHeroSection(title: str, subtitle: str):
    st.write(
        f"""
        <div class="base-wrapper hero-bg">
                <a href="https://coronacidades.org/" target="blank" class="logo-link"><span class="logo-bold">corona</span><span class="logo-lighter">cidades</span></a>
                <div class="hero-wrapper">
                        <div class="hero-container">
                                <div class="hero-container-content">
                                        <span class="hero-container-product primary-span">{title}<br/>Covid</span>
                                        <span class="hero-container-subtitle primary-span">{subtitle}</span>
                                </div>
                        </div>   
                        <img class="hero-container-image" src="https://i.imgur.com/l3vuQdP.png"/>
                </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def genInputFields(user_input, config, session):

    # # Inicia sem update
    # session.update = False

    authors_beds = user_input["author_number_beds"]
    beds_update = user_input["last_updated_number_beds"]

    authors_ventilators = user_input["author_number_ventilators"]
    ventilators_update = user_input["last_updated_number_ventilators"]

    number_beds = int(user_input["number_beds"])
    number_ventilators = int(user_input["number_ventilators"])

    if not session.refresh:
        number_beds = int(
            number_beds * config["br"]["simulacovid"]["resources_available_proportion"]
        )
        number_ventilators = int(
            number_ventilators
            * config["br"]["simulacovid"]["resources_available_proportion"]
        )

    cases_update = pd.to_datetime(user_input["last_updated_cases"]).strftime("%d/%m")

    locality = user_input["locality"]

    if locality == "Brasil":
        authors_beds = "SUS e Embaixadores"
        authors_ventilators = "SUS e Embaixadores"

    user_input["number_beds"] = st.number_input(
        f"Número de leitos destinados aos pacientes com Covid-19 (50% do reportado em {authors_beds}; atualizado: {beds_update})",
        0,
        None,
        number_beds,
    )

    user_input["number_ventilators"] = st.number_input(
        f"Número de ventiladores destinados aos pacientes com Covid-19 (50% do reportado em {authors_ventilators}; atualizado: {ventilators_update}):",
        0,
        None,
        number_ventilators,
    )

    user_input["population_params"]["I_confirmed"] = st.number_input(
        f"Casos confirmados (fonte: Brasil.IO; atualizado: {cases_update}):",
        0,
        None,
        user_input["population_params"]["I_confirmed"],
    )

    user_input["population_params"]["D"] = st.number_input(
        f"Mortes confirmadas (fonte: Brasil.IO; atualizado: {cases_update}):",
        0,
        None,
        int(user_input["population_params"]["D"]),
    )

    # Faz o update quando clica o botão
    if st.button("Finalizar alteração"):

        session.number_beds = user_input["number_beds"]
        session.number_ventilators = user_input["number_ventilators"]
        session.cases = user_input["population_params"]["I_confirmed"]

        session.update = True

    return user_input, session


def genIndicatorCard(indicator: Indicator):
    display_left = "flex"
    display_right = "flex"

    if str(indicator.left_display) == "nan":
        display_left = "hide-bg"

    if str(indicator.right_display) == "nan":
        display_right = "hide-bg"

    if indicator.risk == "Fonte: inloco":
        risk_html_class = "black-span p4"
    else:
        risk_html_class = "bold white-span p4"

    return f"""<div class="indicator-card flex flex-column mr">
                        <span class="header p3">{indicator.header}</span>
                        <span class="p4">{indicator.caption}</span>
                        <span class="bold p2">{indicator.display}<span class="bold p5"> {indicator.unit}</span></span>
                        <div class="{IndicatorBackground(indicator.risk).name}-alert-bg risk-pill">
                                <span class="{risk_html_class}">{indicator.risk}</span>
                        </div>
                        <div class="flex flex-row flex-justify-space-between mt"> 
                                <div class="br {display_left} flex-column text-align-center pr">
                                        <span class="lighter">{indicator.left_label}</span>
                                        <span class="bold">{indicator.left_display}</span>
                                </div>
                                <div class=" bl flex flex-column text-align-center pl {display_right}">
                                        <span class="lighter">{indicator.right_label}</span>
                                        <span class="bold">{indicator.right_display}</span>
                                </div>
                        </div>
                </div>
        """


def genKPISection(
    place_type: str, locality: str, alert: str, indicators: Dict[str, Indicator]
):
    if not isinstance(alert, str):
        bg = "gray"
        caption = "Sugerimos que confira o nível de risco de seu estado. (Veja Níveis de Risco no menu ao lado)<br/>Seu município nao possui dados suficientes para calcularmos o nível de risco."
        stoplight = "%0a%0a"
    else:
        bg = AlertBackground(alert).name
        caption = f"Risco {alert} de colapso no sistema de saúde (Veja Níveis de Risco no menu ao lado)"
        if "state" in place_type:
            place_type = "estado"
        else:
            place_type = "município"

        if alert == "baixo":
            stoplight = f"Meu {place_type} está em *ALERTA BAIXO*! E o seu? %0a%0a"
        elif alert == "médio":
            stoplight = f"Meu {place_type} está em *ALERTA MÉDIO*! E o seu? %0a%0a"
        else:
            stoplight = f"Meu {place_type} está em *ALETA ALTO*! E o seu? %0a%0a"

    cards = list(map(genIndicatorCard, indicators.values()))
    cards = "".join(cards)
    msg = f"""
    🚨 BOLETIM CoronaCidades |  *{locality}, {datetime.now().strftime('%d/%m')}*  🚨%0a%0a
    {stoplight} 😷 _Contágio_: Cada contaminado infecta em média outras *{indicators['rt'].display} pessoas* %0a%0a
    🏥 _Capacidade_: A capacidade hospitalar será atingida em *{indicators['hospital_capacity'].display.replace("+", "mais")} meses* %0a%0a
    🔍 _Subnotificação_: A cada 10 pessoas infectadas, *{indicators['subnotification_rate'].display} são diagnosticadas* %0a%0a
    🏠 _Isolamento_: Na semana passada, *{indicators['social_isolation'].display} das pessoas ficou em casa* %0a%0a
    👉 _Saiba se seu município está no nível de alerta baixo, médio ou alto acessando o *FarolCovid* aqui_: https://coronacidades.org/farol-covid/
    """

    st.write(
        """<div class="alert-banner %s-alert-bg mb" style="margin-bottom: 0px;">
                <div class="base-wrapper flex flex-column" style="margin-top: 100px;">
                        <div class="flex flex-row flex-space-between flex-align-items-center">
                         <span class="white-span header p1">%s</span>
                         <a class="btn-wpp" href="whatsapp://send?text=%s" target="blank">Compartilhar no Whatsapp</a>
                         </div>
                        <span class="white-span p3">%s</span>
                        <div class="flex flex-row flex-m-column">%s</div>
                </div>
        </div>
        """
        % (bg, locality, msg, caption, cards),
        unsafe_allow_html=True,
    )


def genProductCard(product: Product):
    if product.recommendation == "Sugerido":
        badge_style = "primary-bg"
    elif product.recommendation == "Risco alto":
        badge_style = f"red-alert-bg"
    else:
        badge_style = "hide-bg"

    return f"""<div class="flex flex-column elevated pr pl product-card mt  ">
                <div class="flex flex-row">
                        <span class="p3 header bold uppercase">{product.name}</span>
                         <span class="{badge_style} ml secondary-badge">{product.recommendation}</span>
                </div>
                <span>{product.caption}</span>
                <img src="{product.image}" style="width: 200px" class="mt"/>
        </div>
        """


def genProductsSection(products: List[Product]):
    cards = list(map(genProductCard, products))
    cards = "".join(cards)

    st.write(
        f"""
        <div class="base-wrapper">
                <span class="section-header primary-span">COMO SEGUIR COM SEGURANÇA?</span>
                <div class="flex flex-row flex-space-around mt flex-m-column">{cards}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def genInputCustomizationSectionHeader(locality: str) -> None:
    st.write(
        """
        <div class="base-wrapper">
                <span class="section-header primary-span">Verifique os dados disponíveis <span class="yellow-span">(%s)</span></span>
                <br />
                <span>Usamos os dados do Brasil.io e DataSUS, mas é possível que eles dados estejam um pouco desatualizados. Se estiverem, é só ajustar os valores abaixo para continuar a simulação.</span>
                <br />
        </div>"""
        % locality,
        unsafe_allow_html=True,
    )


def genFooter() -> None:

    st.write(
        """
        <div class="magenta-bg">
                <div class="base-wrapper">
                        <div class="logo-wrapper">
                                <span><b>Estamos à disposição para apoiar o gestor público a aprofundar a análise para seu estado ou município, de forma inteiramente gratuita. 
                                <a target="_blank" style="color:#3E758A;" href="https://coronacidades.org/fale-conosco/">Entre em contato conosco</a></span><br/>
                                <span>A presente ferramenta, voluntária, parte de estudos referenciados já publicados e considera os dados de saúde pública dos municípios 
                                brasileiros disponibilizados no DataSus. O repositório do projeto pode ser acessado no 
                                nosso <a class="github-link" href="https://github.com/ImpulsoGov/simulacovid">Github</a>.</span><br/>
                                Os cenários projetados são meramente indicativos e dependem de variáveis que aqui não podem ser consideradas. 
                                Trata-se de mera contribuição à elaboração de cenários por parte dos municípios e não configura qualquer obrigação ou 
                                responsabilidade perante as decisões efetivadas. Saiba mais em nossa Metodologia. 
                                Estamos em constante desenvolvimento e queremos ouvir sua opinião sobre a ferramenta - caso tenha sugestões ou comentários, 
                                entre em contato via o chat ao lado. Caso seja gestor público e necessite de apoio para preparo de seu município, 
                                acesse a Checklist e confira o site do CoronaCidades.
                                <br/></br></br></span>
                                <img class="logo-img" src="%s"/>
                                <div class="logo-section">
                                        <img class="logo-img" src="%s"/>
                                        <img class="logo-img" src="%s"/>
                                </div>
                        </div>
                </div>
        </div>"""
        % (Logo.IMPULSO.value, Logo.CORONACIDADES.value, Logo.ARAPYAU.value),
        unsafe_allow_html=True,
    )


# VIEW COMPONENTS SIMULACOVID


def genAmbassadorSection() -> None:
    st.write(
        """
        <div class="base-wrapper">
                <div class="ambassador-container">
                        <span class="ambassador-question bold">Você gostaria de atualizar algum dos dados acima? Você tem informações mais recentes e pode colaborar conosco?</span>
                        <span>Estamos montando uma rede para manter o SimulaCovid sempre atualizado e nossas projeções serem úteis para tomada de decisão na sua cidade. Venha ser parte do nosso time de embaixadores!</span>
                        <a class="btn-ambassador" href="%s" target="blank">Quero ser embaixador</a>
                </div>
        </div>
        """
        % Link.AMBASSADOR_FORM.value,
        unsafe_allow_html=True,
    )


def genSimulatorOutput(output: SimulatorOutput) -> str:

    bed_img = "https://i.imgur.com/27hutU0.png"
    ventilator_icon = "https://i.imgur.com/V419ZRI.png"

    if output.min_range_beds < 3 and output.max_range_beds < 3:
        bed_projection = f"em até {output.max_range_beds} mês(es)"
    else:
        bed_projection = "mais de 2 meses"

    if output.min_range_ventilators < 3 and output.max_range_ventilators < 3:
        ventilator_projection = f"em até {output.max_range_ventilators} mês(es)"
    else:
        ventilator_projection = "mais de 2 meses"

    output = """
        <div>
                <div class="simulator-container %s">
                        <div class="simulator-output-wrapper">
                                <div class="simulator-output-row">
                                        <span class="simulator-output-row-prediction-value">
                                                %s
                                        </span>  
                                </div> 
                                <span class="simulator-output-row-prediction-label">
                                        será atingida a capacidade máxima de <b>leitos</b>
                                </span>
                        </div>
                        <img src="%s" class="simulator-output-image"/>
                </div>
                <br />
                <div class="simulator-container %s">
                        <div class="simulator-output-wrapper">
                                <div class="simulator-output-row">
                                        <span class="simulator-output-row-prediction-value">
                                                %s
                                        </span>  
                                </div> 
                                <span class="simulator-output-row-prediction-label">
                                        meses será atingida a capacidade máxima de <b>ventiladores</b>
                                </span>
                        </div>
                        <img src="%s" class="simulator-output-image"/>
                </div>
        </div>""" % (
        output.color.value,
        bed_projection,
        bed_img,
        output.color.value,
        ventilator_projection,
        ventilator_icon,
    )

    return output.strip("\n\t")


def genChartSimulationSection(simulation: SimulatorOutput, fig) -> None:

    simulation = genSimulatorOutput(simulation)

    st.write(
        """<div class="lightgrey-bg">
                <div class="base-wrapper">
                        <div class="simulator-header">
                                <span class="section-header primary-span">Aqui está o resultado da sua simulação</span>
                        </div>
                        <div class="simulator-wrapper">
                                %s
                        </div>
                         <div style="display: flex; flex-direction: column; margin-top: 5em"> 
                                <span class="section-header primary-span">Visão detalhada da sua simulação</span><br>
                                <span style="border-radius: 15px; border: dashed 2px  #F2C94C; padding: 1em">
                                        <b>NOTA:</b> 
                                        Para evitar uma sobrecarga hospitalar, a sua demanda (a curva 📈) deve ficar sempre abaixo da respectiva linhas tracejadas (a reta horizontal ➖).
                                        Em outras palavras, a quantidade de pessoas que precisam ser internadas por dia não deve ultrapassar o número de equipamentos disponíveis.
                                </span>
                        </div>
                </div>
        </div>
        """
        % (simulation),
        unsafe_allow_html=True,
    )

    st.plotly_chart(fig, use_container_width=True)


# def genVideoTutorial():
#     st.write(
#         """<div class="base-wrapper">
#                         <span class="section-header primary-span">Antes de começar: entenda como usar!</span>
#                 </div>""",
#         unsafe_allow_html=True,
#     )
#     st.video(Link.YOUTUBE_TUTORIAL.value)


# def genStateInputSectionHeader() -> None:
#     st.write(
#         """
#         <div class="base-wrapper">
#                 <span class="section-header primary-span">Etapa 1: Selecione o seu Estado</span>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )


# def genMunicipalityInputSection() -> None:
#     st.write(
#         """
#         <div class="base-wrapper">
#                 <div style="display: flex; flex-direction: column">
#                         <span class="section-header primary-span">Etapa 2: Selecione seu Município ou Região SUS</span>
#                         <span>Se seu município não possui unidade de tratamento intensivo, sugerimos simular a situação da sua regional. Não recomendamos a simulação a nível estadual.</span>
#                 </div>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )


# def genResourceAvailabilitySection(resources: ResourceAvailability) -> None:
#     msg = f"""
#         🚨 *BOLETIM CoronaCidades:*  {resources.locality} - {datetime.now().strftime('%d/%m')}  🚨%0a%0a
#         😷 *{int(resources.cases)}* casos confirmados e *{int(resources.deaths)}* mortes%0a%0a
#         🏥 Hoje estão disponíveis *{resources.beds}* leitos e *{resources.ventilators}* ventiladores destinados à Covid %0a%0a
#         👉 _Acompanhe e simule a situação do seu município acessando o *SimulaCovid* aqui_: https://coronacidades.org/ """

#     st.write(
#         """
#         <div class="primary-bg">
#                 <div class="base-wrapper">
#                         <div class="resource-header-container">
#                                 <span class="section-header white-span">Panorama <span class="locality-name yellow-span">%s</span></span>
#                                 <a class="btn-wpp" href="whatsapp://send?text=%s" target="blank">Compartilhar no Whatsapp</a>
#                         </div>
#                         <div class="resources-wrapper">
#                                 <div class="resources-title-container">
#                                         <span class="resources-title">Progressão da Transmissão</span>
#                                 </div>
#                                 <div class="resources-container-wrapper">
#                                         <div class="resource-container">
#                                                 <span class='resource-container-value'>%i</span>
#                                                 <span class='resource-container-label'>casos confirmados</span>
#                                         </div>
#                                         <div class="resource-container">
#                                                 <span class='resource-container-value'>%i</span>
#                                                 <span class='resource-container-label'>mortes</span>
#                                         </div>
#                                 </div>
#                                 <span class="resource-font"><b>Fonte:</b> Brasil.IO atualizado diariamente com base em boletins das secretarias de saúde publicados.</span>
#                         </div>
#                         <div class="resources-wrapper">
#                                 <div class="resources-title-container">
#                                         <span class="resources-title">Capacidade hospitalar destinada à COVID</span>
#                                 </div>
#                                 <div class="resources-container-wrapper">
#                                         <div class="resource-container">
#                                                 <span class='resource-container-value'>%i</span>
#                                                 <span class='resource-container-label'>leitos</span>
#                                         </div>
#                                         <div class="resource-container">
#                                                 <span class='resource-container-value'>%i</span>
#                                                 <span class='resource-container-label'>ventiladores</span>
#                                         </div>
#                                 </div>
#                                 <span class="resource-font"><b>Fonte:</b>
#                                         DATASUS CNES, Fevereiro 2020. Assumimos que 20%% dos leitos complementares e ventiladores registrados da rede SUS e não-SUS seriam alocados para pacientes da Covid-19. Esse número poderá ser ajustado na simulação abaixo.
#                                 </span>
#                                 <div class="ambassador-container">
#                                         <span class="ambassador-question white-span bold">Esse dado está desatualizado? Você tem informações mais recentes e pode colaborar conosco?</span>
#                                         <span class="white-span">Estamos montando uma rede para manter o SimulaCovid sempre atualizado e nossas projeções serem úteis para tomada de decisão na sua cidade. Venha ser parte do nosso time de embaixadores!</span>
#                                         <a class="btn-ambassador" href="%s" target="blank">Quero ser embaixador</a>
#                                 </div>
#                         </div>
#                 </div>
#         </div>
#         """
#         % (
#             resources.locality,
#             msg,
#             resources.cases,
#             resources.deaths,
#             resources.beds,
#             resources.ventilators,
#             Link.AMBASSADOR_FORM.value,
#         ),
#         unsafe_allow_html=True,
#     )


# def genSimulationSection(
#     active_cases: int,
#     locality: str,
#     resources: ResourceAvailability,
#     worst_case: SimulatorOutput,
#     best_case: SimulatorOutput,
# ) -> None:
#     no_quarentine = (
#         "mais de 90"
#         if (worst_case.max_range_beds == -1 and worst_case.max_range_ventilators == -1)
#         else min(worst_case.max_range_beds, worst_case.max_range_ventilators)
#     )
#     date_proj = ""
#     if no_quarentine != "mais de 90":
#         proj = (datetime.now() + timedelta(days=int(no_quarentine))).strftime("%d/%m")
#         date_proj = f" *({proj})* "

#     msg = f"""
#         🚨 *BOLETIM SimulaCovid:*  {resources.locality} - {datetime.now().strftime('%d/%m')}  🚨%0a%0a
#         🏥 Considerando que {resources.locality} tem *{resources.beds}* leitos 🛏️ e *{resources.ventilators}* ventiladores ⚕ %0a%0a
#         😷 Na ausência de isolamento social, {resources.locality} poderia atingir a sua capacidade hospitalar em *{no_quarentine}* dias{date_proj}%0a%0a
#         👉 _Acompanhe e simule a situação do seu município acessando o *SimulaCovid* aqui_: https://coronacidades.org/ """

#     status_quo = genSimulatorOutput(worst_case)
#     restrictions = genSimulatorOutput(best_case)

#     st.write(
#         """
#         <div class="lightgrey-bg">
#                 <div class="base-wrapper">
#                         <div class="simulator-wrapper">
#                                 <span class="section-header primary-span">
#                                         <span  class="yellow-span">%s</span>
#                                         <br/>
#                                         Daqui a quantos dias será atingida a capacidade <span class="yellow-span">hospitalar</span>?
#                                 </span>
#                                 <br/>
#                                 <br/>
#                                 <div class="simulation-scenario-header-container">
#                                         <span class="simulator-scenario-header grey-bg">
#                                                 Sem Políticas de Restrição
#                                         </span>
#                                 </div>
#                                 %s
#                                 <br/>
#                                 <br/>
#                                 <div class="simulation-scenario-header-container">
#                                         <span class="simulator-scenario-header lightblue-bg">
#                                                 Com Medidas Restritivas (Isolamento Social)
#                                         </span>
#                                 </div>
#                                 %s
#                                 <a class="btn-wpp" href="whatsapp://send?text=%s" target="blank">Compartilhar no Whatsapp</a>
#                         </div>
#                 </div>
#         </div>
#         """
#         % (locality, status_quo, restrictions, msg),
#         unsafe_allow_html=True,
#     )


# def genActNowSection(locality, worst_case):
#     display = (
#         ""
#         if any(
#             value != -1
#             for value in [
#                 worst_case.min_range_beds,
#                 worst_case.max_range_beds,
#                 worst_case.min_range_ventilators,
#                 worst_case.max_range_ventilators,
#             ]
#         )
#         else "hide"
#     )

#     st.write(
#         """
#         <div class="primary-bg %s">
#                 <div class="base-wrapper">
#                         <div class="act-now-wrapper">
#                         <span class="section-header white-span"><span class="yellow-span">%s | </span> Você precisa agir agora </span>
#                         <span class="white-span">Para prevenir uma sobrecarga hospitalar, é preciso implementar uma estratégia de contenção. Quanto antes você agir, mais vidas consegue salvar.</span>
#                         </div>
#                 </div>
#         </div>
#         """
#         % (display, locality),
#         unsafe_allow_html=True,
#     )

# def genStrategyCard(strategy: ContainmentStrategy) -> str:
#     return """
#         <div class="scenario-card">
#                         <div class="scenario-card-header">
#                                 <span class="scenario-card-header-code %s">ESTRATÉGIA %i</span>
#                                 <div class="scenario-card-header-name-background %s">
#                                         <span class="scenario-card-header-name">%s</span>
#                                 </div>
#                         </div>
#                         <img src="%s" class="scenario-card-img"/>
#                         <span class="scenario-card-description">%s</span>
#         </div>""" % (
#         strategy.color.value,
#         strategy.code,
#         strategy.background.value,
#         strategy.name,
#         strategy.image_url,
#         strategy.description,
#     )


# def genStrategiesSection(strategies: List[ContainmentStrategy]) -> None:
#     cards = list(map(genStrategyCard, strategies))
#     cards = "".join(cards)
#     st.write(
#         """
#         <div class="primary-bg">
#                 <div class="base-wrapper">
#                         <span class="section-header white-span">E como você pode reagir?</span>
#                         <div class="scenario-cards-container">%s</div>
#                 </div>
#         </div>
#         """
#         % cards,
#         unsafe_allow_html=True,
#     )
