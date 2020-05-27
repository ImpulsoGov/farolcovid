import streamlit as st
import yaml
import loader
import numpy as np
import pandas as pd

from simulator import run_evolution
from simulation import calculate_recovered, filter_options
import utils
import simulation as sm
from models import IndicatorType, IndicatorCards, ProductCards

# Dados da projeção de capacidade de leitos
def dday_city(params, alert, config, supply_type="n_beds"):

    params["population_params"] = {
        "N": alert["population"],
        "I": alert["active_cases"],
        "D": alert["deaths"]
    }

    params["strategy"] = {'isolation': 90, 'lockdown': 90}

    params["n_beds"] = alert["number_beds"]
    params["n_ventilators"] = alert["number_ventilators"]

    if np.isnan(alert["active_cases"]):
        params["population_params"]["I"] = 1
    
    if np.isnan(alert["deaths"]):
        params["population_params"]["D"] = 0
    
    params = calculate_recovered(params, alert, params['notification_rate'])
    _, dday_beds, dday_ventilators = run_evolution(params, config)
    
    return dday_beds["best"], dday_beds["worst"]
        
def update_indicator(indicator, display, left_display, right_display, risk):
    indicator.risk = risk
    indicator.display = display
    indicator.left_display=left_display
    indicator.right_display=right_display

    return indicator

def main():
    utils.localCSS("style.css")
    utils.genHeroSection("Farol", "Entenda e controle a Covid-19 em sua cidade e estado.")
    # GET DATA
    config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)
    cities = loader.read_data('br', config, endpoint=config['br']['api']['endpoints']['simulacovid'])

    # Dados Central
    df_cities = loader.read_data("br", config,endpoint=config['br']['api']['endpoints']['farolcovid']['cities'])
    df_states = loader.read_data("br", config,endpoint=config['br']['api']['endpoints']['farolcovid']['states'])
    
    # REGION/CITY USER INPUT
    user_input = dict()
    indicators = IndicatorCards

    level = st.selectbox('Nível', ["Estadual", "Municipal"])
    pd.set_option('display.max_columns', None)

    if level == "Estadual":
        user_input['state'] = st.selectbox('Estado', cities['state_name'].unique())
        user_input['place_type'] = 'state'
        cities_filtered = filter_options(cities, user_input['state'], 'state_name')
        locality = user_input['state']
        alert = df_states[df_states["state_name"] == cities_filtered["state_name"].iloc[0]].iloc[0]
        user_input["notification_rate"] = alert["notification_rate"]

    if level == "Municipal":
        user_input['city'] = st.selectbox('Município', cities['city_name'].unique())
        user_input['place_type'] = 'city'
        cities_filtered = filter_options(cities, user_input['city'], 'city_name')
        locality = user_input['city']
        alert = df_cities[df_cities["city_id"] == cities_filtered["city_id"].iloc[0]]
        
        if np.isnan(alert["notification_rate"]):
            alert["notification_rate"] = df_states[df_states["state_name"] == cities_filtered["state_name"].iloc[0]].iloc[0]["notification_rate"]
            st.write("Seu município não possui dados suficientes para calcular a taxa de subnotificação. Vamos utilizar a do Estado.")
        if np.inan(alert["rt_10days_ago_most_likely"]):
            state = df_states[df_states["state_name"] == cities_filtered["state_name"].iloc[0]].iloc[0]
            alert["rt_10days_ago_most_likely"] = state["rt_10days_ago_most_likely"]
            alert["rt_10days_ago_low"] = state["rt_10days_ago_low"]
            alert["rt_10days_ago_high"] = state["rt_10days_ago_high"]
            st.write("Seu município não possui dados suficientes para calcular o índice de contágio. Vamos utilizar o do Estado.")
    
        user_input["notification_rate"] = alert["notification_rate"]

        

    selected_region = cities_filtered.sum(numeric_only=True)
    # CUSTOMIZE INPUT SECTION

    # GET NOTIFICATION RATE & Rt 

    # if len(cities_filtered) > 1: # pega taxa do estado quando +1 municipio selecionado
    #         user_input["notification_rate"] = round(cities_filtered['state_notification_rate'].mean(), 2)
    #         rt = df_cities[df_cities["state"] == cities_filtered["state"].unique()[0]]
    #         alert = df_cities[df_cities["state"] == cities_filtered["state"].unique()[0]]
    # elif np.isnan(cities_filtered['notification_rate'].values):
    #         user_input["notification_rate"] = 1
    #         rt = df_cities[df_cities["city_id"] == cities_filtered["city_id"].iloc[0]]
    #         alert = df_cities[df_cities["city_id"] == cities_filtered["city_id"].iloc[0]]

    # else:
    #         user_input["notification_rate"] = round(cities_filtered['notification_rate'], 4)
    #         rt = df_cities[df_cities["city_id"] == cities_filtered["city_id"].iloc[0]]
    #         alert = df_cities[df_cities["city_id"] == cities_filtered["city_id"].iloc[0]]

    if alert['confirmed_cases'] == 0:
        st.write(f'''<div class="base-wrapper">
        Seu município ou regional de saúde ainda não possui casos reportados oficialmente. Portanto, simulamos como se o primeiro caso ocorresse hoje.
        <br><br>Caso queria, você pode mudar esse número abaixo:
                </div>''', unsafe_allow_html=True)


    else:
        infectious_period = config['br']['seir_parameters']['severe_duration'] + config['br']['seir_parameters']['critical_duration']
        estimation = int(selected_region['infectious_period_cases'] / user_input['notification_rate'])
        if not np.all(cities_filtered['last_updated'].isna()):
                last_update_cases = cities_filtered['last_updated'].max().strftime('%d/%m')
        st.write(f'''<div class="base-wrapper">
        O número de casos confirmados oficialmente no seu município ou regional de saúde é de {int(alert['confirmed_cases'].sum())} em {last_update_cases}. 
        Dada a progressão clínica da doença (em média, {infectious_period} dias) e a taxa de notificação ajustada para a região ({int(100*user_input['notification_rate'])}%), 
        <b>estimamos que o número de casos ativos é de {estimation}</b>.
        <br>Caso queria, você pode mudar esse número para a simulação abaixo:
                </div>''', unsafe_allow_html=True)

    

    if st.button('Alterar dados'):
        utils.genInputCustomizationSectionHeader(locality)
        
        user_input = utils.genInputFields(locality, user_input, cities_filtered, alert, config)
         # AMBASSADOR SECTION
        utils.genAmbassadorSection()

    # if np.isnan(alert['rt_10days_ago_most_likely']): #TODO in case no RT edge case
    #     st.write("Rt: Sua cidade não possui casos suficiente para o cálculo!")
    # else:
        # pd.set_option('display.max_columns', None)
        # kill metricc, add risk direclty kill function

    indicators["rt"] = update_indicator(indicators["rt"],
                                        display=f'{str(round(alert["rt_10days_ago_low"], 1))} - {str(round(alert["rt_10days_ago_high"], 1))}',
                                        left_display=f'{round(alert["rt_17days_ago_low"], 1)} - {round(alert["rt_17days_ago_high"], 1)}',
                                        right_display=f'{alert["rt_growth"]}',
                                        risk=alert["rt_classification"])
    indicators['subnotification_rate'] = update_indicator( 
                                                    indicators["subnotification_rate"], 
                                                    display=int((1.0 - user_input["notification_rate"]) * 10),
                                                    left_display=f'{round(alert["deaths"])}',
                                                    right_display=f'{round(alert["subnotification_rank"])}',
                                                    risk="")
    

    # Populating base indicator template
    dday_beds_best, dday_beds_worst = dday_city(user_input, alert, config, supply_type="n_beds")
    if dday_beds_best != dday_beds_worst:
        display = f'{round(dday_beds_worst, 1)} e {round(dday_beds_best, 1)}'
    else:
        display = f'''{dday_beds_best}'''
    indicators['hospital_capacity'] = update_indicator(indicators['hospital_capacity'], 
                                                display=f'{display}',
                                                left_display=f'{round(alert["number_ventilators"])}',
                                                right_display=f'{round(alert["number_beds"])}',
                                                risk=alert["dday_classification"])

    indicators[IndicatorType.SOCIAL_ISOLATION.value] = update_indicator(indicators[IndicatorType.SOCIAL_ISOLATION.value], 
                                                display=f'{int(alert["inloco_today_7days_avg"] * 100)}%',
                                                left_display=f'{int(alert["inloco_last_week_7days_avg"] * 100)}%',
                                                right_display=f'{alert["inloco_growth"]}', 
                                                risk="inloco")

    utils.genKPISection(locality=locality, alert=alert['overall_alert'], indicators=indicators)
   
    products = ProductCards
    products[1].recommendation = f'Risco {alert["overall_alert"]}'
    utils.genProductsSection(products)
    product = st.selectbox( 'Como você gostaria de prosseguir?', ('Contenção', 'Reabertura'))
    
    if product == 'Contenção':
        sm.main(user_input=user_input, locality=locality, cities_filtered=cities_filtered, config=config)
    
    # elif product == 'Reabertura':
        # so.main()

    # INDICATORS
    # sources = cities_filtered[[c for c in cities_filtered.columns if (('author' in c) or ('last_updated_' in c))]]

if __name__ == "__main__":
    main()