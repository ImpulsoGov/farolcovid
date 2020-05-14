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

def calculate_recovered(user_input, selected_region, notification_rate):

        confirmed_adjusted = int(selected_region[['confirmed_cases']].sum()/notification_rate)

        if confirmed_adjusted == 0: # dont have any cases yet
                user_input['population_params']['R'] = 0
                return user_input

        user_input['population_params']['R'] = confirmed_adjusted - user_input['population_params']['I'] - user_input['population_params']['D']

        if user_input['population_params']['R'] < 0:
                user_input['population_params']['R'] = confirmed_adjusted - user_input['population_params']['D']
        
        return user_input

def main():
        utils.localCSS("style.css")
        utils.localCSS("icons.css")


        # HEADER
        utils.genHeroSection()
        utils.genVideoTutorial()


        # GET DATA
        config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)
        # if abs(datetime.now().minute - FIXED) > config['refresh_rate']:
        #         caching.clear_cache()
        cities = loader.read_data('br', config, refresh_rate=refresh_rate(config))
        # Getting cities (1) with cases & (2) without cases
        cities = cities[(cities['is_last'] == True) | (cities['last_updated'].isnull())]

        # REGION/CITY USER INPUT
        user_input = dict()
        
        utils.genStateInputSectionHeader()

        user_input['state'] = st.selectbox('Estado', add_all(cities['state_name'].unique()))
        cities_filtered = filter_options(cities, user_input['state'], 'state_name')
        
        utils.genMunicipalityInputSection()

        user_input['region'] = st.selectbox('Região SUS', add_all(cities_filtered['health_system_region'].unique()))
        cities_filtered = filter_options(cities_filtered, user_input['region'], 'health_system_region')

        user_input['city'] = st.selectbox('Município', add_all(cities_filtered['city_name'].unique()))
        cities_filtered = filter_options(cities_filtered, user_input['city'], 'city_name')

        sources = cities_filtered[[c for c in cities_filtered.columns if (('author' in c) or ('last_updated_' in c))]]
 
        selected_region = cities_filtered.sum(numeric_only=True)


        # GET LAST UPDATE DATE
        if not np.all(cities_filtered['last_updated'].isna()):
                last_update_cases = cities_filtered['last_updated'].max().strftime('%d/%m')


        # GET NOTIFICATION RATE
        if len(cities_filtered) > 1: # pega taxa do estado quando +1 municipio selecionado
                notification_rate = round(cities_filtered['state_notification_rate'].mean(), 4)

        elif np.isnan(cities_filtered['notification_rate'].values):
                notification_rate = 1
        else:
                notification_rate = round(cities_filtered['notification_rate'].values[0], 4)

        # pick locality according to hierarchy
        locality = choose_place(user_input['city'], user_input['region'], user_input['state'])

        st.write('<br/>', unsafe_allow_html=True)

        utils.genInputCustomizationSectionHeader(locality)


        # SOURCES USER INPUT
        source_beds = sources[['author_number_beds', 'last_updated_number_beds']].drop_duplicates()
        authors_beds = source_beds.author_number_beds.str.cat(sep=', ')

        source_ventilators = sources[['author_number_ventilators', 'last_updated_number_ventilators']].drop_duplicates()
        authors_ventilators = source_ventilators.author_number_ventilators.str.cat(sep=', ')

        if locality == 'Brasil':
                authors_beds = 'SUS e Embaixadores'
                authors_ventilators = 'SUS e Embaixadores'

        user_input['n_beds'] = st.number_input(
                f"Número de leitos destinados aos pacientes com Covid-19 (fonte: {authors_beds}, atualizado: {source_beds.last_updated_number_beds.max().strftime('%d/%m')})"
                , 0, None,  int(selected_region['number_beds']))

        user_input['n_ventilators'] = st.number_input(
                f"Número de ventiladores destinados aos pacientes com Covid-19 (fonte: {authors_ventilators}, atualizado: {source_ventilators.last_updated_number_ventilators.max().strftime('%d/%m')}):"
                , 0, None, int(selected_region['number_ventilators']))


        # POP USER INPUTS
        user_input['population_params'] = {'N': int(selected_region['population'])}
        user_input['population_params']['D'] = st.number_input('Mortes confirmadas:', 0, None, int(selected_region['deaths']))
        
        # get infected cases
        infectious_period = config['br']['seir_parameters']['severe_duration'] + config['br']['seir_parameters']['critical_duration']
        
        if selected_region['confirmed_cases'] == 0:
                st.write(f'''<div class="base-wrapper">
                Seu município ou regional de saúde ainda não possui casos reportados oficialmente. Portanto, simulamos como se o primeiro caso ocorresse hoje.
                <br><br>Caso queria, você pode mudar esse número abaixo:
                        </div>''', unsafe_allow_html=True)

                user_input['population_params']['I'] = st.number_input('Casos ativos estimados:', 0, None, 1)

        else:
                user_input['population_params']['I'] = int(selected_region['infectious_period_cases'] / notification_rate)

                st.write(f'''<div class="base-wrapper">
                O número de casos confirmados oficialmente no seu município ou regional de saúde é de {int(selected_region['confirmed_cases'].sum())} em {last_update_cases}. 
                Dada a progressão clínica da doença (em média, {infectious_period} dias) e a taxa de notificação ajustada para a região ({int(100*notification_rate)}%), 
                <b>estimamos que o número de casos ativos é de {user_input['population_params']['I']}</b>.
                <br><br>Caso queria, você pode mudar esse número para a simulação abaixo:
                        </div>''', unsafe_allow_html=True)

                user_input['population_params']['I'] = st.number_input('Casos ativos estimados:', 0, None, user_input['population_params']['I'])
        
        # calculate recovered cases
        user_input = calculate_recovered(user_input, selected_region, notification_rate)
        
        # AMBASSADOR SECTION
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
        user_input['strategy'] = {'isolation': 0, 'lockdown': 90}
        _, dday_beds, dday_ventilators = simulator.run_evolution(user_input, config)
        
        best_case = SimulatorOutput(color=BackgroundColor.LIGHT_BLUE_GRADIENT,
                        min_range_beds=dday_beds['worst'], 
                        max_range_beds=dday_beds['best'], 
                        min_range_ventilators=dday_ventilators['worst'],
                        max_range_ventilators=dday_ventilators['best'])

        resources = ResourceAvailability(locality=locality, 
                                        cases=selected_region['active_cases'],
                                        deaths=selected_region['deaths'], 
                                        beds=user_input['n_beds'], 
                                        ventilators=user_input['n_ventilators'])
        
        utils.genSimulationSection(int(user_input['population_params']['I']), locality, resources, worst_case, best_case)
        
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

        utils.genChartSimulationSection(user_input['strategy']['isolation'], 
                                        user_input['strategy']['lockdown'], 
                                        SimulatorOutput(color=BackgroundColor.SIMULATOR_CARD_BG,
                                                min_range_beds=dday_beds['worst'], 
                                                max_range_beds=dday_beds['best'], 
                                                min_range_ventilators=dday_ventilators['worst'],
                                                max_range_ventilators=dday_ventilators['best']), 
                                        fig)

        utils.genWhatsappButton()
        utils.genFooter()
        
if __name__ == "__main__":
    main()
