import streamlit as st
import yaml
import loader
import numpy as np
import pandas as pd

# import sys
# sys.path.append("../")

from models import IndicatorType, IndicatorCards, ProductCards
from model.simulator import run_evolution

import pages.simulacovid as sm

# from pages.simulacovid import calculate_recovered, filter_options

import utils


def update_indicator(indicator, display, left_display, right_display, risk):
    indicator.risk = risk
    indicator.display = display
    indicator.left_display = left_display
    indicator.right_display = right_display

    return indicator


def main():

    utils.localCSS("style.css")

    utils.genHeroSection(
        "Farol", "Entenda e controle a Covid-19 em sua cidade e estado."
    )

    # GET DATA
    config = yaml.load(open("configs/config.yaml", "r"), Loader=yaml.FullLoader)

    df_cities = loader.read_data(
        "br", config, endpoint=config["br"]["api"]["endpoints"]["farolcovid"]["cities"]
    )

    df_states = loader.read_data(
        "br", config, endpoint=config["br"]["api"]["endpoints"]["farolcovid"]["states"]
    )

    # REGION/CITY USER INPUT
    user_input = dict()

    user_input["state"] = st.selectbox(
        "Estado", df_cities["state_name"].sort_values().unique()
    )
    data = utils.filter_options(
        df_cities, user_input["state"], "state_name"
    )  # .fillna("")

    user_input["city"] = st.selectbox(
        "Município", utils.add_all(data["city_name"].unique())
    )
    data = utils.filter_options(data, user_input["city"], "city_name")

    if user_input["city"] == "Todos":

        data = df_states[df_states["state_id"] == data["state_id"].iloc[0]]

        user_input["state"] = data["state_id"].values[0]
        user_input["city_id"] = False
        user_input["place_type"] = "state"

    else:
        user_input["state"] = False
        user_input["city_id"] = data["city_id"].values[0]
        user_input["place_type"] = "city_id"

    # print(len(data))

    locality = utils.choose_place(
        city=user_input["city"], state=user_input["state"], region="Todos"
    )

    # SOURCES PARAMS
    sources = utils.get_sources(data, ["beds", "ventilators"], df_cities)
    # print(sources)

    user_input["n_beds"] = sources["number_beds"][0]
    user_input["n_ventilators"] = sources["number_ventilators"][0]

    # POPULATION PARAMS
    user_input["population_params"] = {
        "N": int(data["population"].values[0]),
        "D": int(data["deaths"].values[0]),
        "I": int(data["active_cases"].values[0]),
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

        utils.genInputCustomizationSectionHeader(locality)
        # OK
        user_input = utils.genInputFields(locality, user_input, sources, config)
        # AMBASSADOR SECTION
        utils.genAmbassadorSection()

    # INDICATORS CARDS
    indicators = IndicatorCards

    # TODO: casos de municipios sem dados
    # state_notification_rate == state, => subnotification_rank == np.nan => dday_beds_best == np.nan
    # rt_classification == np.nan,
    # inloco_growth == np.nan, ...

    # if np.isnan(alert['rt_10days_ago_most_likely']): #TODO in case no RT edge case
    #     st.write("Rt: Sua cidade não possui casos suficiente para o cálculo!")
    # else:
    # pd.set_option('display.max_columns', None)
    # kill metricc, add risk direclty kill function

    indicators["rt"] = update_indicator(
        indicators["rt"],
        display=f'{str(round(data["rt_10days_ago_low"].values[0], 1))} - {str(round(data["rt_10days_ago_high"].values[0], 1))}',
        left_display=f'{round(data["rt_17days_ago_low"].values[0], 1)} - {round(data["rt_17days_ago_high"].values[0], 1)}',
        right_display=f'{data["rt_growth"].values[0]}',
        risk=str(data["rt_classification"].values[0]),
    )

    indicators["subnotification_rate"] = update_indicator(
        indicators["subnotification_rate"],
        display=int((data["notification_rate"].values[0]) * 10),
        left_display=f'{int(data["deaths"].values[0])}',
        right_display=[
            f'{int(data["subnotification_rank"].values[0])}º'
            if not np.isnan(data["subnotification_rank"].values[0])
            else "-"
        ][0],
        risk=str(data["subnotification_classification"].values[0]),
    )

    indicators["hospital_capacity"] = update_indicator(
        indicators["hospital_capacity"],
        display=f"{int(data['dday_beds_best'].values[0])}",
        left_display=f'{int(data["number_ventilators"].values[0])}',
        right_display=f'{int(data["number_beds"].values[0])}',
        risk=str(data["dday_classification"].values[0]),
    )

    indicators[IndicatorType.SOCIAL_ISOLATION.value] = update_indicator(
        indicators[IndicatorType.SOCIAL_ISOLATION.value],
        display=f'{int(data["inloco_today_7days_avg"].values[0] * 100)}%',
        left_display=f'{int(data["inloco_last_week_7days_avg"].values[0] * 100)}%',
        right_display=f'{data["inloco_growth"].values[0]}',
        risk="Fonte: inloco",
    )

    utils.genKPISection(
        locality=locality, alert=data["overall_alert"].values[0], indicators=indicators
    )

    products = ProductCards
    products[1].recommendation = f'Risco {data["overall_alert"].values[0]}'
    utils.genProductsSection(products)

    product = st.radio(
        "Como você gostaria de prosseguir?",
        ("SimulaCovid", "Saúde em Ordem (em breve)"),
    )

    if product == "SimulaCovid":
        sm.main(user_input, locality, indicators, data, config)

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
