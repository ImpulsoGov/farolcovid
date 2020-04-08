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
    if city == 'Todos' and region == 'Todos':
        return state + ' (Estado)' if state != 'Todos' else 'Brasil'
    if city == 'Todos':
        return region + ' (Região SUS)' if region != 'Todos' else 'Todas as regiões SUS'
    return city

def simulator_menu(user_input):
        st.sidebar.subheader("""Simule o impacto de estratégias de isolamento em sua cidade:""")

        user_input['strategy']['isolation'] = st.sidebar.number_input('Em quantos dias você quer acionar a Estratégia 2, medidas restritivas?', 0, 90, 90, key='strategy2')


        user_input['strategy']['lockdown'] = st.sidebar.number_input('Em quantos dias você quer acionar a Estratégia 3, quarentena?', 0, 90, 90, key='strategy3')
        
        st.sidebar.subheader("""Ajuste a capacidade que será alocada na intervenção:""")

        total_beds = user_input['n_beds']
        user_input['n_beds'] = st.sidebar.number_input('Mude o número de leitos destinados aos pacientes com Covid-19:', 0, None, total_beds)

        total_ventilators = user_input['n_ventilators']
        user_input['n_ventilators'] = st.sidebar.number_input('Mude o número de ventiladores destinados aos pacientes com Covid-19:', 0, None, total_ventilators)
        
        return user_input

def refresh_rate(config):
        dt = (math.floor(datetime.now().minute/config['refresh_rate'])*config['refresh_rate'])
        return datetime.now().replace(minute=dt,second=0, microsecond=0)

def main():
        utils.localCSS("style.css")
 
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
        
        # MENU OPTIONS: Input population params
        st.sidebar.subheader('Mude os dados de COVID-19 do seu município caso necessário')

        user_input['population_params'] = {#'N': st.sidebar.number_input('População', 0, None, int(N0), key='N'),
                     'N': selected_region['population'],
                     'I': st.sidebar.number_input('Casos confirmados', 0, None, int(selected_region['number_cases'])),
                     'D': st.sidebar.number_input('Mortes confirmadas', 0, None, int(selected_region['deaths'])),
                     'R': st.sidebar.number_input('Pessoas recuperadas', 0, None, 0)}

        # INITIAL VALUES FOR BEDS AND VENTILATORS
        user_input['n_beds'] = int(selected_region['number_beds']*0.2)
        user_input['n_ventilators'] = int(selected_region['number_ventilators']*0.2)
        
        st.write('<br/>', unsafe_allow_html=True)

        # >>>> CHECK city: city or state?
        utils.genResourceAvailabilitySection(ResourceAvailability(locality=choose_place(user_input['city'], user_input['region'], user_input['state']), 
                                                                  cases=selected_region['number_cases'],
                                                                  deaths=selected_region['deaths'], 
                                                                  beds=user_input['n_beds'], 
                                                                  ventilators=user_input['n_ventilators']))


        st.write('<br/>', unsafe_allow_html=True)

        
        # DEFAULT WORST SCENARIO  
        user_input['strategy'] = {'isolation': 90, 'lockdown': 90}
        user_input['population_params']['I'] = [user_input['population_params']['I'] if user_input['population_params']['I'] != 0 else 1][0]

        _, dday_beds, dday_ventilators = simulator.run_evolution(user_input)
        
        worst_case = SimulatorOutput(color=BackgroundColor.GREY_GRADIENT,
                        min_range_beds=dday_beds['worst'], 
                        max_range_beds=dday_beds['best'], 
                        min_range_ventilators=dday_ventilators['worst'],
                        max_range_ventilators=dday_ventilators['best'])
        
        # DEFAULT BEST SCENARIO
        user_input['strategy'] = {'isolation': 90, 'lockdown': 0}
        _, dday_beds, dday_ventilators = simulator.run_evolution(user_input)
        
        best_case = SimulatorOutput(color=BackgroundColor.LIGHT_BLUE_GRADIENT,
                        min_range_beds=dday_beds['worst'], 
                        max_range_beds=dday_beds['best'], 
                        min_range_ventilators=dday_ventilators['worst'],
                        max_range_ventilators=dday_ventilators['best'])

        
        utils.genSimulationSection(choose_place(user_input['city'], user_input['region'], user_input['state']), worst_case, best_case)
        
        utils.generateStrategiesSection(Strategies)

        # SIMULATOR MENU
        user_input = simulator_menu(user_input)

        # SIMULATOR SCENARIOS: BEDS & RESPIRATORS
        fig, dday_beds, dday_ventilators = simulator.run_evolution(user_input)        
        
        # st.write('<div class="lightgrey-bg"><div class="base-wrapper"><span class="section-header primary-span">Simulador de demanda hospitalar</span></div></div>', unsafe_allow_html=True)
        st.write('''
        <div class="lightgrey-bg">
                <div class="base-wrapper">
                        <div style="display: flex; flex-direction: column"> 
                                <span class="section-header primary-span">Simulador de demanda hospitalar</span>
                                <i>Ajuste os valores no menu à esquerda para testar a evolução com diferentes estratégias.</i>
                        </div>
                </div>
        </div>
        ''',  unsafe_allow_html=True)

        utils.genChartSimulationSection(SimulatorOutput(color=BackgroundColor.SIMULATOR_CARD_BG,
                        min_range_beds=dday_beds['worst'], 
                        max_range_beds=dday_beds['best'], 
                        min_range_ventilators=dday_ventilators['worst'],
                        max_range_ventilators=dday_ventilators['best']))


        # PLOT SCENARIOS EVOLUTION
        st.write('''
                <div class="lightgrey-bg">
                        <div class="base-wrapper">
                                <div style="display: flex; flex-direction: column"> 
                                        <span class="chart-simulator-instructions subsection-header">EVOLUÇÃO DIÁRIA DA DEMANDA HOSPITALAR</span><br>
                                        <i>Veja como mudanças na estratégia adotada afetam a necessidade de internação em leitos 
                                        hospitalares e de ventiladores<br> na sua cidade ao longo dos dias. <b>A sua demanda a cada dia deve ficar 
                                        entre os valores mínimo e máximo estimados no gráfico.</b></i>
                                </div>
                        </div>
                </div>''',  unsafe_allow_html=True)

        st.plotly_chart(fig)
        
        utils.genFooter()
        
if __name__ == "__main__":
    main()
