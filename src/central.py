import streamlit as st
import yaml
import loader
import numpy as np
import pandas as pd

from simulator import run_evolution
from simulation import calculate_recovered, filter_options
import utils
import simulation as sm
from models import IndicatorType, IndicatorCards, Alert, RiskLabel, ProductCards

# Dados da projeção de capacidade de leitos
def dday_city(params, selected_region, config, supply_type="n_beds"):

    params["population_params"] = {
        "N": selected_region["population"],
        "I": selected_region["active_cases"],
        "D": selected_region["deaths"]
    }

    params["strategy"] = {'isolation': 90, 'lockdown': 90}

    params["n_beds"] = selected_region["number_beds"]
    params["n_ventilators"] = selected_region["number_ventilators"]

    if np.isnan(selected_region["active_cases"]):
        params["population_params"]["I"] = 1
    
    if np.isnan(selected_region["deaths"]):
        params["population_params"]["D"] = 0
    
    params = calculate_recovered(params, selected_region, params['notification_rate'])
    _, dday_beds, dday_ventilators = run_evolution(params, config)
    
    return dday_beds["best"], dday_beds["worst"]

def get_overall_alert_level(indicators):
    if indicators["rt"].metric < 1.0 and \
        indicators["hospital_capacity"] > 30 and \
        indicators["subnotification_rate"] < 0.5: 
        return Alert.LOW
    
    elif (indicators["rt"].metric >= 1.0 and indicators["rt"].metric <= 1.2) and indicators["hospital_capacity"] > 30 and indicators["subnotification_rate"] < 0.5: 
        return Alert.MEDIUM
    else:
        return Alert.HIGH

def get_indicator_alert(name, indicator):
    if name == IndicatorType.RT.name:
        if indicator < 1.0:
            return Alert.LOW.name
        elif (indicator >= 1.0 and indicator <= 1.2):
            return Alert.MEDIUM.name
        else:
            return Alert.HIGH.name
    elif name == IndicatorType.HOSPITAL_CAPACITY.name:
        if indicator < 30:
            return Alert.HIGH.name
        elif indicator >= 30 and indicator <= 60:
            return Alert.MEDIUM.name
        else:
            return Alert.LOW.name
    else:
        return Alert.NONE.name
        
def update_indicator(key, indicator, metric, display, left_display, right_display):
    indicator.metric = metric
    indicator.display = display
    indicator.risk = get_indicator_alert(key, metric)
    indicator.risk_label= RiskLabel(indicator.risk).value
    indicator.left_display=left_display
    indicator.right_display=right_display

    return indicator

def main():
    utils.localCSS("style.css")
    utils.genHeroSection("Farol", "Como sua comunidade pode reagir à crise?")
    # GET DATA
    config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)
    cities = loader.read_data('br', config, endpoint=config['br']['api']['endpoints']['simulacovid'])

    # Dados Rt
    df_rt_cities = loader.read_data("br", config, endpoint="br/cities/rt")
    df_rt_states = loader.read_data("br", config, endpoint="br/states/rt")

    # Dados Central
    df_alert = loader.read_data("br", config,endpoint=config['br']['api']['endpoints']['farolcovid'])

    # REGION/CITY USER INPUT
    user_input = dict()
    indicators = IndicatorCards

    level = st.selectbox('Nível', ["Estadual", "Municipal"])

    if level == "Estadual":
        user_input['state'] = st.selectbox('Estado', cities['state_name'].unique())
        cities_filtered = filter_options(cities, user_input['state'], 'state_name')
        locality = user_input['state']

    if level == "Municipal":
        user_input['city'] = st.selectbox('Município', cities['city_name'].unique())
        cities_filtered = filter_options(cities, user_input['city'], 'city_name')
        locality = user_input['city']

    selected_region = cities_filtered.sum(numeric_only=True)
    # CUSTOMIZE INPUT SECTION

    # GET NOTIFICATION RATE & Rt 

    if len(cities_filtered) > 1: # pega taxa do estado quando +1 municipio selecionado
            user_input["notification_rate"] = round(cities_filtered['state_notification_rate'].mean(), 2)
            rt = df_rt_states[df_rt_states["state"] == cities_filtered["state"].unique()[0]]
            alerts = df_alert[df_alert["state"] == cities_filtered["state"].unique()[0]]
    elif np.isnan(cities_filtered['notification_rate'].values):
            user_input["notification_rate"] = 1
            rt = df_rt_cities[df_rt_cities["city_id"] == cities_filtered["city_id"].iloc[0]]
            alerts = df_alert[df_alert["city_id"] == cities_filtered["city_id"].iloc[0]]

    else:
            user_input["notification_rate"] = round(cities_filtered['notification_rate'], 4)
            rt = df_rt_cities[df_rt_cities["city_id"] == cities_filtered["city_id"].iloc[0]]
            alerts = df_alert[df_alert["city_id"] == cities_filtered["city_id"].iloc[0]]

    utils.genInputCustomizationSectionHeader(locality)
    
    user_input = utils.genInputFields(locality, user_input, cities_filtered, selected_region, config)
    if len(rt) < 1: #TODO in case no RT edge case
        st.write("Rt: Sua cidade não possui casos suficiente para o cálculo!")
    else:
        pd.set_option('display.max_columns', None)
        print(alerts)
        indicators["rt"] = update_indicator(IndicatorType.RT.name, indicators["rt"],
                                            metric=(rt.iloc[-1]["Rt_most_likely"]), 
                                            display=f'{str(round(rt.iloc[-1]["Rt_low_95"], 1))} - {str(round(rt.iloc[-1]["Rt_high_95"], 1))}',
                                            left_display=f'{alerts.iloc[-1]["rt_17days_ago_low"]} - {alerts.iloc[-1]["rt_17days_ago_high"]}',
                                            right_display=f'{alerts.iloc[-1]["rt_comparision"]}')
        indicators['subnotification_rate'] = update_indicator(IndicatorType.SUBNOTIFICATION_RATE.name, indicators["subnotification_rate"], 
                                                        metric=(1.0 - user_input["notification_rate"]), 
                                                        display=int((1.0 - user_input["notification_rate"]) * 10),
                                                        left_display=f'{int(alerts.iloc[-1]["deaths"])}',
                                                        right_display=f'{alerts.iloc[-1]["subnotification_rank"]}')
    
    # AMBASSADOR SECTION
    utils.genAmbassadorSection()

    # Populating base indicator template
    dday_beds_best, dday_beds_worst = dday_city(user_input, selected_region, config, supply_type="n_beds")
    if dday_beds_best == dday_beds_worst:
        display = f'''{str(dday_beds_worst)} e {str(dday_beds_best)}'''
    else:
        display = f'''{str(dday_beds_best)}'''
    indicators['hospital_capacity'] = update_indicator(IndicatorType.HOSPITAL_CAPACITY.name, indicators['hospital_capacity'], 
                                                metric=((dday_beds_worst + dday_beds_best) / 2), 
                                                display=f'''{str(dday_beds_worst)} e {str(dday_beds_best)}''',
                                                left_display=f'{alerts.iloc[-1]["number_ventilators"]}',
                                                right_display=f'{alerts.iloc[-1]["number_beds"]}')

    utils.genKPISection(locality=locality, alert=get_overall_alert_level(indicators), indicators=indicators)
   
    products = ProductCards;
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