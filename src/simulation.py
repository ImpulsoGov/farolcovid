import os
import sys
sys.path.insert(0,'./model/')

import streamlit as st
from streamlit import caching
from models import BackgroundColor, Document, Strategies, SimulatorOutput, ResourceAvailability
from typing import List
import utils
import plotly.express as px
from datetime import datetime
import math
import yaml
import numpy as np
import loader
from model import simulator

def add_all(x, all_string='Todos'):
        return [all_string] + list(x)
            
def filter_options(_df, var, col, all_string='Todos'):
    if var == 'Todos':
            return _df
    else:
            return _df.query(f'{col} == "{var}"')
        
def choose_place(city, region, state):
    if city == 'Todos' and region == 'Todos' and state == 'Todos':
        return 'Brasil'
    if city == 'Todos' and region == 'Todos':
        return state + ' (Estado)' if state != 'Todos' else 'Brasil'
    if city == 'Todos':
        return region + ' (Região SUS)' if region != 'Todos' else 'Todas as regiões SUS'
    return city

def refresh_rate(config):
        dt = (math.floor(datetime.now().minute/config['refresh_rate'])*config['refresh_rate'])
        return datetime.now().replace(minute=dt,second=0, microsecond=0)

def initialize_params(user_input, selected_region):
        user_input['population_params'] = {#'N': st.sidebar.number_input('População', 0, None, int(N0), key='N'),
                     'N': selected_region['population'],
                     'I': int(selected_region['number_cases']),
                     'D': int(selected_region['deaths']),
                     'R': int(selected_region['recovered'])}

        # INITIAL VALUES FOR BEDS AND VENTILATORS
        user_input['n_beds'] = int(selected_region['number_beds']*0.2)
        user_input['n_ventilators'] = int(selected_region['number_ventilators']*0.2)
        return user_input

def main():
        utils.localCSS("style.css")
        utils.localCSS("icons.css")
 
        if datetime.now().hour < 1:
                caching.clear_cache()

        config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)
        cities = loader.read_data('br', config, refresh_rate=refresh_rate(config))

        user_input = dict()

        utils.genHeroSection()
        utils.genStateInputSectionHeader()
        

        user_input['state'] = st.selectbox('Estado', add_all(cities['state_name'].unique()))
        cities_filtered = filter_options(cities, user_input['state'], 'state_name')
        
        utils.genMunicipalityInputSection()

        user_input['region'] = st.selectbox('Região SUS', add_all(cities_filtered['health_system_region'].unique()))
        cities_filtered = filter_options(cities_filtered, user_input['region'], 'health_system_region')

        user_input['city'] = st.selectbox('Município', add_all(cities_filtered['city_name'].unique()))
        cities_filtered = filter_options(cities_filtered, user_input['city'], 'city_name')

        selected_region = cities_filtered.sum(numeric_only=True)   

        # pick locality according to hierarchy
        locality = choose_place(user_input['city'], user_input['region'], user_input['state'])

        # initialize default parameters for models
        user_input = initialize_params(user_input, selected_region)

        st.write('<br/>', unsafe_allow_html=True)

        utils.genInputCustomizationSectionHeader(locality)

        user_input['population_params']['I'] = st.number_input('Número de casos confirmados:', 0, None, int(selected_region['number_cases']))
        user_input['population_params']['R'] = st.number_input('Número de recuperados:', 0, None, int(selected_region['recovered']))
        user_input['population_params']['D'] = st.number_input('Número de mortes:', 0, None, int(selected_region['deaths']))

        total_beds = user_input['n_beds']
        user_input['n_beds'] = st.number_input('Número de leitos destinados aos pacientes com Covid-19:', 0, None, total_beds)
        total_ventilators = user_input['n_ventilators']
        user_input['n_ventilators'] = st.number_input('Número de ventiladores destinados aos pacientes com Covid-19:', 0, None, total_ventilators)

        st.write('<br/>', unsafe_allow_html=True)

        
        # DEFAULT WORST SCENARIO  
        user_input['strategy'] = {'isolation': 90, 'lockdown': 90}
        user_input['population_params']['I'] = [user_input['population_params']['I'] if user_input['population_params']['I'] != 0 else 1][0]

        _, dday_beds, dday_ventilators = simulator.run_evolution(user_input, config)
        
        worst_case = SimulatorOutput(color=BackgroundColor.GREY_GRADIENT,
                        min_range_beds=dday_beds['worst'], 
                        max_range_beds=dday_beds['best'], 
                        min_range_ventilators=dday_ventilators['worst'],
                        max_range_ventilators=dday_ventilators['best'])
        
        # DEFAULT BEST SCENARIO
        user_input['strategy'] = {'isolation': 90, 'lockdown': 0}
        _, dday_beds, dday_ventilators = simulator.run_evolution(user_input, config)
        
        best_case = SimulatorOutput(color=BackgroundColor.LIGHT_BLUE_GRADIENT,
                        min_range_beds=dday_beds['worst'], 
                        max_range_beds=dday_beds['best'], 
                        min_range_ventilators=dday_ventilators['worst'],
                        max_range_ventilators=dday_ventilators['best'])

        utils.genSimulationSection(locality, worst_case, best_case)
        
        utils.genActNowSection(locality, worst_case)
        utils.genStrategiesSection(Strategies)


        st.write('''
        <div class="base-wrapper">
                <span class="section-header primary-span">Etapa 4: Simule estratégias e veja o resultado da intervenção</span>
                <br />
                <span>Agora é a hora de planejar como você pode melhor se preparar para evitar a sobrecarga hospitalar. Veja como mudanças na estratégia adotada afetam a necessidade de internação em leitos.</span>
        </div>''', unsafe_allow_html=True)

        user_input['strategy']['isolation'] = st.number_input('Em quantos dias você quer acionar a Estratégia 2, medidas restritivas?', 0, 90, 90, key='strategy2')

        user_input['strategy']['lockdown'] = st.number_input('Em quantos dias você quer acionar a Estratégia 3, quarentena?', 0, 90, 90, key='strategy3')
        
        st.write('<br/><br/>', unsafe_allow_html=True)
        
        # SIMULATOR SCENARIOS: BEDS & RESPIRATORS
        fig, dday_beds, dday_ventilators = simulator.run_evolution(user_input, config) 

        utils.genChartSimulationSection(SimulatorOutput(color=BackgroundColor.SIMULATOR_CARD_BG,
                        min_range_beds=dday_beds['worst'], 
                        max_range_beds=dday_beds['best'], 
                        min_range_ventilators=dday_ventilators['worst'],
                        max_range_ventilators=dday_ventilators['best']), fig)

        # >>>> CHECK city: city or state?
        utils.genResourceAvailabilitySection(ResourceAvailability(locality=locality, 
                                                                  cases=selected_region['number_cases'],
                                                                  deaths=selected_region['deaths'], 
                                                                  beds=user_input['n_beds'], 
                                                                  ventilators=user_input['n_ventilators']))
        utils.genWhatsappButton()
        utils.genFooter()
        
if __name__ == "__main__":
    main()
