import os
import sys
sys.path.insert(0,'./model/')

import streamlit as st
from models import BackgroundColor, Document, Strategies, SimulatorOutput, ResourceAvailability
from typing import List
import utils
import plotly.express as px
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
        
def choose_place(city, state):
    if not city:
        return state
    return city

def simulator_menu(user_input):
        st.sidebar.header("""Simulador de demanda hospitalar""")
        st.sidebar.subheader("""Simule o impacto de estratégias de isolamento em sua cidade:""")

        user_input['strategy']['isolation'] = st.sidebar.number_input('Em quantos dias você quer acionar a Estratégia 2, medidas de restrição?', 0, 90, 90, key='strategy2')


        user_input['strategy']['lockdown'] = st.sidebar.number_input('Em quantos dias você quer acionar a Estratégia 3, lockdown?', 0, 90, 90, key='strategy3')
        
        st.sidebar.subheader("""A partir desses números, ajuste a capacidade que será alocada na intervenção:""")

        total_beds = user_input['n_beds']
        user_input['n_beds'] = st.sidebar.number_input('Mude o percentual de leitos destinados aos pacientes com Covid-19:', 0, None, total_beds)

        total_ventilators = user_input['n_ventilators']
        user_input['n_ventilators'] = st.sidebar.number_input('Mude o percentual de ventiladores destinados aos pacientes com Covid-19:', 0, None, total_ventilators)
        
        return user_input
        
def main():
        
        utils.localCSS("style.css")

        config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)
        cities = loader.read_data('br', config)

        user_input = dict()

        utils.genHeroSection()
        utils.genMunicipalityInputSection()
        
        user_input['state'] = st.selectbox('Estado', add_all(cities['state_name'].unique()))
        cities_filtered = filter_options(cities, user_input['state'], 'state_name')
        
        user_input['region'] = st.selectbox('Região SUS', add_all(cities_filtered['health_system_region'].unique()))
        cities_filtered = filter_options(cities, user_input['region'], 'health_system_region')
        
        user_input['city'] = st.selectbox('Município', add_all(cities_filtered['city_name'].unique()))
        cities_filtered = filter_options(cities, user_input['city'], 'city_name')

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
        
        # >>>> CHECK city: city or state?
        utils.genResourceAvailabilitySection(ResourceAvailability(city=choose_place(user_input['city'], user_input['state']), 
                                                                  cases=selected_region['number_cases'],
                                                                  deaths=selected_region['deaths'], 
                                                                  beds=user_input['n_beds'], 
                                                                  ventilators=user_input['n_ventilators']))

        utils.generateStrategiesSection(Strategies)
        
        st.write('<br/>', unsafe_allow_html=True)

        
        # DEFAULT WORST SCENARIO  
        user_input['strategy'] = {'isolation': 90, 'lockdown': 90}
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

        
        utils.genSimulationSection(choose_place(user_input['city'], user_input['state']), worst_case, best_case)

        # SIMULATOR MENU
        user_input = simulator_menu(user_input)

        # SIMULATOR SCENARIOS: BEDS & RESPIRATORS
        fig, dday_beds, dday_ventilators = simulator.run_evolution(user_input)
        
        st.write('<br/>', unsafe_allow_html=True)
        
        # PLOT SCENARIOS EVOLUTION
        st.plotly_chart(fig)
        
        st.write('<br/>', unsafe_allow_html=True)
        
        # FINAL TEXT
        st.write("""
# <Simulador da demanda hospitalar>
""")


        st.write("""
A presente ferramenta, voluntária, parte de estudos referenciados já 
publicados e considera os dados de saúde pública dos municípios brasileiros 
disponibilizados no DataSus.
""")

        st.write("""
Os cenários projetados são meramente indicativos e dependem de variáveis
 que aqui não podem ser consideradas. Trata-se de mera contribuição à 
 elaboração de cenários por parte dos municípios e não configura qualquer 
 obrigação ou responsabilidade perante as decisões efetivadas. Saiba mais em 
 nossa metodologia.
""")

        st.write("""
Estamos em constante desenvolvimento e queremos ouvir sua opinião sobre a 
ferramenta - caso tenha sugestões ou comentários, entre em contato via o chat 
ao lado. Caso seja gestor público e necessite de apoio para preparo de seu 
município, acesse a Checklist e confira o site do CoronaCidades.
""")

        st.write("""
Esta plataforma foi desenvolvida por:

João Carabetta, Mestre em Matemática Aplicada pela FGV
Fernanda Scovino, Graduada em Matemática Aplicada pela FGV
Diego Oliveira, Mestre em Física Aplicada pela Unicamp
Ana Paula Pellegrino, Doutoranda em Ciência Política da Georgetown University
""")

        st.write("""
    < IMAGE IMPULSO >
""")

        st.write("""
   com colaboração de:

Fátima Marinho, Doutora em Epidemiologia e Medicina Preventiva pela USP e 
professora da Faculdade de Medicina da Universidade de Minas Gerais
Sarah Barros Leal, Médica e Mestranda em Saúde Global na University College London
H. F. Barbosa, Mestre em Relações Internacionais pela Universidade da Califórnia, San Diego
Teresa Soter, mestranda em Sociologia na Oxford University

Toda a documentação da ferramenta está disponível aqui.
""")

        st.write("""
    < IMAGES IMPULSO ARAPYAU CORONACIDADES>
""")

        
if __name__ == "__main__":
    main()
