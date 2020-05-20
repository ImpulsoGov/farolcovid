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

def main(user_input, locality, cities_filtered, config):
        
        sources = cities_filtered[[c for c in cities_filtered.columns if (('author' in c) or ('last_updated_' in c))]]
 
        selected_region = cities_filtered.sum(numeric_only=True)
       

        locality=locality
        st.write('<br/>', unsafe_allow_html=True)


        # DEFAULT WORST SCENARIO  

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
