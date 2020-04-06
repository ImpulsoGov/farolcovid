import os
import sys
sys.path.insert(0,'./model/')

import streamlit as st
from models import BackgroundColor, Document, Strategies, SimulatorOutput, ResourceAvailability
from typing import List
import utils
import plotly.express as px
import yaml

import loader
from model import simulator


def add_all(x, all_string='Todos'):
        return [all_string] + list(x)

def filter_frame(_df, name, all_string='Todos'):

        if name == all_string:
                return _df[[]].sum()


# =======> TESTANDO (para funcionar, descomente o código nas linhas 112-116!)

def get_dday(df,col,resource_number):
    
    if max(df[col])>resource_number:
        dday = df[df[col] > resource_number].index[0]
    else:
        dday = 666
    
    return dday


def run_evolution_static(selected_region,days_until_isolation,days_until_lockdon,number_beds,number_ventilators):
    st.sidebar.subheader('Selecione os dados do seu município para rodar o modelo')
    simulation_params = dict()
    simulation_params['phase1']= {'scenario':'nothing','n_days':days_until_isolation}
    simulation_params['pahse2']= {'scenario':'isolation','n_days':days_until_lockdon}
    simulation_params['phase3']= {'scenario':'lockdown' ,'n_days':90}
    
    population_params = dict()
    population_params['N'] =  int(selected_region['population'])
    population_params['I'] = int(selected_region['number_cases'])
    population_params['D'] = int(selected_region['deaths'])
    population_params['R'] = 0
    
    dfs = simulator.run_simulation(population_params,simulation_params)
    worst = dfs['worst'].reset_index()
	
    dday_beds_worst = get_dday(dfs['worst'],'I2',number_beds)
    dday_beds_best  = get_dday(dfs['best'] ,'I2',number_beds)
    
    dday_ventilators_worst = get_dday(dfs['worst'],'I3',number_ventilators)
    dday_ventilators_best  = get_dday(dfs['best'] ,'I3',number_ventilators)

    
    return dday_beds_worst, dday_beds_best, dday_ventilators_worst, dday_ventilators_best


def run_evolution(selected_region,days_until_isolation,days_until_lockdon,number_beds,number_ventilators):
    st.sidebar.subheader('Selecione os dados do seu município para rodar o modelo')
    simulation_params = dict()
    simulation_params['phase1']= {'scenario':'nothing','n_days':days_until_isolation}
    simulation_params['pahse2']= {'scenario':'isolation','n_days':days_until_lockdon}
    simulation_params['phase3']= {'scenario':'lockdown' ,'n_days':90}
    
    N0 = selected_region['population']
    I0 = selected_region['number_cases']
    R0 = 0
    D0 = selected_region['deaths']
 
    population_params = dict()
    population_params['N'] = st.sidebar.number_input('População', 0, None, int(N0), key='N')
    population_params['I'] = st.sidebar.number_input('Casos confirmados', 0, None, int(I0), key='I')
    population_params['D'] = st.sidebar.number_input('Mortes confirmadas', 0, None, int(D0), key='D')
    population_params['R'] = st.sidebar.number_input('Pessoas recuperadas', 0, None, int(R0), key='R')
    
    dfs = simulator.run_simulation(population_params,simulation_params)
    worst = dfs['worst'].reset_index()
    fig = px.line(worst[['dias','I2','I3','D']].melt('dias'), x='dias', y='value', color='variable')
	
    dday_beds_worst = get_dday(dfs['worst'],'I2',number_beds)
    dday_beds_best  = get_dday(dfs['best'] ,'I2',number_beds)
    
    dday_ventilators_worst = get_dday(dfs['worst'],'I3',number_ventilators)
    dday_ventilators_best  = get_dday(dfs['best'] ,'I3',number_ventilators)

    
    return fig, dday_beds_worst, dday_beds_best, dday_ventilators_worst, dday_ventilators_best


# <================
        
def main():
        utils.localCSS("style.css")

        config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)
        cities = loader.read_data('br', config)

        utils.genHeroSection()
        # =======> TESTANDO
#         st.write('## Qual a situação do seu município?')
#         st.write('Selecione os dados do seu município para rodar o modelo')

#         # st.line_chart(evolution)
#         st.plotly_chart(run_evolution())
        # <================

        def filter_options(_df, var, col, all_string='Todos'):

                if var == 'Todos':
                        return _df
                else:
                        return _df.query(f'{col} == "{var}"')

        st.write('''
        <div class="base-wrapper">
                <span class="section-header primary-span">Qual a situação do meu município?</span>
        </div>
        ''',  unsafe_allow_html=True)
        
        state_name = st.selectbox('Estado', 
                        add_all(cities['state_name'].unique()))
        
        cities_filtered = filter_options(cities, state_name, 'state_name')

        health_region = st.selectbox('Região SUS', 
                            add_all(cities_filtered['health_system_region'].unique())
                            )
        cities_filtered = filter_options(cities_filtered, health_region, 'health_system_region')

        city_name = st.selectbox('Município', 
                            add_all(cities_filtered['city_name'].unique())
                            )
        cities_filtered = filter_options(cities_filtered, city_name, 'city_name')

        selected_region = cities_filtered.sum(numeric_only=True)

        utils.genResourceAvailabilitySection(ResourceAvailability(city=city_name, 
                                                                cases=selected_region['number_cases'],  
                                                                deaths=selected_region['deaths'],
                                                                beds=300,
                                                                ventilators=3000))


        st.write('<br/>', unsafe_allow_html=True)


        ### INITIAL VALUES FOR BEDS AND VENTILATORS
        beds_20_perc = int(selected_region['number_beds']*0.2)
        ventilators_20_perc = int(selected_region['number_ventilators']*0.2)
        
        #WORST SCENARIO SIMULATION        
        dday_beds_worst, dday_beds_best, dday_ventilators_worst, dday_ventilators_best = run_evolution_static(selected_region,
                                                                                                            days_until_isolation=360,                                                                                   days_until_lockdon=0,
                                                                                                            number_beds=beds_20_perc,
                                                                                                            number_ventilators=ventilators_20_perc)
        worst_case = SimulatorOutput(color=BackgroundColor.GREY_GRADIENT,
                                min_range_beds=dday_beds_worst, 
                                max_range_beds=dday_beds_best, 
                                min_range_ventilators=dday_ventilators_worst,
                                max_range_ventilators=dday_ventilators_best)        
       

         #BEST SCENARIO SIMULATION
        dday_beds_worst, dday_beds_best, dday_ventilators_worst, dday_ventilators_best = run_evolution_static(selected_region,
                                                                                                            days_until_isolation=1,
                                                                                                            days_until_lockdon=0,
                                                                                                        number_beds=beds_20_perc,
                                                                                                            number_ventilators=ventilators_20_perc)
        best_case = SimulatorOutput(color=BackgroundColor.LIGHT_BLUE_GRADIENT,
                                min_range_beds=dday_beds_worst, 
                                max_range_beds=dday_beds_best, 
                                min_range_ventilators=dday_ventilators_worst,
                                max_range_ventilators=dday_ventilators_best)   

        utils.genSimulationSection(city_name, worst_case, best_case)	
        
        utils.generateStrategiesSection(Strategies)

        st.write("""
## Simule o impacto de estratégias semelhantes na capacidade o sistema de saúde em sua cidade:
""")


        st.write("""
## Em quantos dias você quer acionar a Estratégia 2, medidas de restrição?
""")
        days_until_isolation = st.number_input('Dias:', 0, 90, 90, key='strategy2')
        
        st.write("""
## Em quantos dias você quer acionar a Estratégia 3, lockdown?
""")

        days_until_lockdon = st.number_input('Dias:', 0, 90, 90, key='strategy3')
        
        st.write("""
## A partir desses números, ajuste a capacidade que será alocada na intervenção:?
""")

        st.write("""
## Mude o percentual de leitos destinados aos pacientes com Covid-19:
""")
        number_beds = st.number_input('Leitos:', 0, None, beds_20_perc)

        st.write("""
## Mude o percentual de ventiladores destinados aos pacientes com Covid-19:
""")
        number_ventilators = st.number_input('Ventiladores:', 0, None, ventilators_20_perc)
        

        fig, dday_beds_worst, dday_beds_best, dday_ventilators_worst, dday_ventilators_best = run_evolution(selected_region,
                                                                                                            days_until_isolation,
                                                                                                            days_until_lockdon, number_beds,
                                                                                                number_ventilators)
        st.plotly_chart(fig)

                
        st.write('<br/>', unsafe_allow_html=True)

        
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
