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
from pandas import Timestamp

FIXED = datetime.now().minute

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
        user_input['n_beds'] = int(selected_region['number_beds'])
        user_input['n_ventilators'] = int(selected_region['number_ventilators'])
        return user_input

def main():
        utils.localCSS("style.css")
        utils.localCSS("icons.css")

        config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)

        if abs(datetime.now().minute - FIXED) > config['refresh_rate']:
                caching.clear_cache()

        cities = loader.read_data('br', config, refresh_rate=refresh_rate(config))

        user_input = dict()

        utils.genHeroSection()

        utils.genVideoTutorial()

        utils.genStateInputSectionHeader()

        user_input['state'] = st.selectbox('Estado', add_all(cities['state_name'].unique()))
        cities_filtered = filter_options(cities, user_input['state'], 'state_name')
        
        utils.genMunicipalityInputSection()

        user_input['region'] = st.selectbox('Região SUS', add_all(cities_filtered['health_system_region'].unique()))
        cities_filtered = filter_options(cities_filtered, user_input['region'], 'health_system_region')

        user_input['city'] = st.selectbox('Município', add_all(cities_filtered['city_name'].unique()))
        cities_filtered = filter_options(cities_filtered, user_input['city'], 'city_name')

        sources = cities_filtered[[c for c in cities_filtered.columns 
                                if (('author' in c) or ('last_updated' in c))]]
 
        selected_region = cities_filtered.sum(numeric_only=True)

        # pick locality according to hierarchy
        locality = choose_place(user_input['city'], user_input['region'], user_input['state'])

        # initialize default parameters for models
        user_input = initialize_params(user_input, selected_region)

        st.write('<br/>', unsafe_allow_html=True)

        utils.genInputCustomizationSectionHeader(locality)

        total_beds = user_input['n_beds']

        source_beds = sources[['author_number_beds', 'last_updated_number_beds']].\
                        drop_duplicates().iloc[0]
        source_beds.last_updated_number_beds = source_beds.last_updated_number_beds.strftime('%d/%m')

        user_input['n_beds'] = st.number_input(
                f'Número de leitos destinados aos pacientes com Covid-19 (fonte: {source_beds.author_number_beds}, atualizado: {source_beds.last_updated_number_beds})'
                , 0, None, total_beds)

        total_ventilators = user_input['n_ventilators']
        source_ventilators = sources[['author_number_ventilators', 'last_updated_number_ventilators']].\
                drop_duplicates().iloc[0]
        source_ventilators.last_updated_number_ventilators = source_ventilators.last_updated_number_ventilators.strftime('%d/%m')

        user_input['n_ventilators'] = st.number_input(
                f'Número de ventiladores destinados aos pacientes com Covid-19 (fonte: {source_ventilators.author_number_ventilators}, atualizado: {source_ventilators.last_updated_number_ventilators}):'
                , 0, None, total_ventilators)

        user_input['population_params']['R'] = int(selected_region['recovered'])
        user_input['population_params']['D'] = st.number_input('Número de mortes:', 0, None, int(selected_region['deaths']))
        user_input['population_params']['I'] = st.number_input('Número de casos ativos:', 0, None, int(selected_region['number_cases']))
        utils.genAmbassadorSection()

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

        resources = ResourceAvailability(locality=locality, 
                                        cases=selected_region['number_cases'],
                                        deaths=selected_region['deaths'], 
                                        beds=user_input['n_beds'], 
                                        ventilators=user_input['n_ventilators'])
        utils.genSimulationSection(locality, resources, worst_case, best_case)
        
        utils.genActNowSection(locality, worst_case)
        utils.genStrategiesSection(Strategies)


        st.write('''
        <div class="base-wrapper">
                <span class="section-header primary-span">Etapa 4: Simule o resultado de possíveis intervenções</span>
                <br />
                <span>Agora é a hora de planejar como você pode melhor se preparar para evitar a sobrecarga hospitalar. Veja como mudanças na estratégia adotada afetam a necessidade de internação em leitos.</span>
        </div>''', unsafe_allow_html=True)

        user_input['strategy']['isolation'] = st.slider('Em quantos dias você quer acionar a Estratégia 2, medidas restritivas? (deixe como 0 se a medida já estiver em vigor)', 0, 90, 0, key='strategy2')

        user_input['strategy']['lockdown'] = st.slider('Em quantos dias você quer acionar a Estratégia 3, quarentena?', 0, 90, 90, key='strategy3')
        
        st.write('<br/><br/>', unsafe_allow_html=True)
        
        # SIMULATOR SCENARIOS: BEDS & RESPIRATORS
        fig, dday_beds, dday_ventilators = simulator.run_evolution(user_input, config) 

        utils.genChartSimulationSection(SimulatorOutput(color=BackgroundColor.SIMULATOR_CARD_BG,
                        min_range_beds=dday_beds['worst'], 
                        max_range_beds=dday_beds['best'], 
                        min_range_ventilators=dday_ventilators['worst'],
                        max_range_ventilators=dday_ventilators['best']), fig)

        # >>>> CHECK city: city or state?
        # utils.genResourceAvailabilitySection(ResourceAvailability(locality=locality, 
        #                                                           cases=selected_region['number_cases'],
        #                                                           deaths=selected_region['deaths'], 
        #                                                           beds=user_input['n_beds'], 
        #                                                           ventilators=user_input['n_ventilators']))
        utils.genWhatsappButton()
        utils.genFooter()
        
if __name__ == "__main__":
    main()
