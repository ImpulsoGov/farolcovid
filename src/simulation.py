import os
import sys
sys.path.insert(0,'./model/')

import streamlit as st
from models import BackgroundColor, Document, Strategies, SimulatorOutput, KPI 
from typing import List
import utils
import plotly.express as px
import yaml
import numpy as np

import loader
from model import simulator


def add_all(x, all_string='Todos'):
        return [all_string] + list(x)

def filter_frame(_df, name, all_string='Todos'):

        if name == all_string:
                return _df[[]].sum()
            
def filter_options(_df, var, col, all_string='Todos'):

    if var == 'Todos':
            return _df
    else:
            return _df.query(f'{col} == "{var}"')
        
def main():
        
        utils.localCSS("style.css")

        config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)
        cities = loader.read_data('br', config)

        user_input = dict()
        
        st.title("SimulaCovid")
        st.subheader('Como seu município pode se preparar para a Covid-19')

        st.write('## SimulaCovid é um simulador da demanda por leitos hospitalares e ventiladores.')        

        st.write('''<i>
Usando dados do DataSUS e de casos confirmados, ele estima por quantos dias - até o limite de 90 - 
durará o estoque desses equipamentos em cada município. Ao explorar diferentes estratégias de resposta 
à crise, a ferramenta permite que gestores públicos simulem abordagens e planejem seu curso de ação para 
evitar o colapso do sistema.</i>
        ''', unsafe_allow_html=True)



        st.write('''
        <br/>
        <i>
                Confira nossa
                <a href="%s">metodologia</a>
                e o 
                <a href="%s">github</a> 
                do projeto. Acesse nossas 
                <a href="%s">Perguntas Frequentes.</a>
        </i>''' % (Document.METHODOLOGY.value, Document.GITHUB.value, Document.FAQ.value), unsafe_allow_html=True)

        st.write('### Selecione seu município abaixo para gerar as projeções')
        
        user_input['state'] = st.selectbox('Estado', add_all(cities['state_name'].unique()))
        cities_filtered = filter_options(cities, user_input['state'], 'state_name')
        
        user_input['region'] = st.selectbox('Região SUS', add_all(cities_filtered['health_system_region'].unique()))
        cities_filtered = filter_options(cities, user_input['region'], 'health_system_region')
        
        user_input['city'] = st.selectbox('Município', add_all(cities_filtered['city_name'].unique()))
        cities_filtered = filter_options(cities, user_input['city'], 'city_name')

        selected_region = cities_filtered.sum(numeric_only=True)
        
        
        # Menu options: Input population params
        st.sidebar.subheader('Mude os dados de COVID-19 do seu município caso necessário')
        
        user_input['population_params'] = {#'N': st.sidebar.number_input('População', 0, None, int(N0), key='N'),
                     'N': selected_region['population'],
                     'I': st.sidebar.number_input('Casos confirmados', 0, None, int(selected_region['number_cases'])),
                     'D': st.sidebar.number_input('Mortes confirmadas', 0, None, int(selected_region['deaths'])),
                     'R': st.sidebar.number_input('Pessoas recuperadas', 0, None, 0)}


        utils.generateKPIRow(KPI(label="CASOS CONFIRMADOS", value=selected_region['number_cases']),
                       KPI(label="MORTES CONFIRMADAS", value=selected_region['deaths']))

        st.write('''
**Fonte:** Brasil.IO atualizado diariamente com base em boletins das secretarias de saúde publicados.
        ''')

        st.write('''
        <div class="info">
                <span>
                        <b>Lembramos que podem existir casos não diagnosticados em sua cidade.</b> Sugerimos que consulte o
                        Checklist para orientações específicas sobre o que fazer antes do primeiro caso diagnosticado.
                </span>
        ''', unsafe_allow_html=True)

        st.write('''
### Seu município tem a seguinte **capacidade hospitalar:**
        ''')

        utils.generateKPIRow(KPI(label="LEITOS", value=53231), KPI(label="VENTILADORES", value=1343))

        st.write('''
        <b>Fonte:</b> DATASUS CNes, Fevereiro 2020. Incluímos leitos hospitalares da rede SUS 
        e não-SUS. Para excluir a última categoria, precisaríamos estimar também a 
        opulação susdependente. Para mais informações, confira nossa
        <a href="%s" target="blank">metodologia</a>.
        ''' % (Document.METHODOLOGY.value), unsafe_allow_html=True)


        st.write('''
        <div class="info">
                A maioria das pessoas que contraem Covid-19, conseguem se recuperar em casa - 
                mas uma parte irá desenvolver sintomas graves e precisará de internação em 
                leitos hospitalares. Outros terão sintomas críticos e precisarão de ventiladores 
                mecânicos e tratamento intensivo (UTI). Apesar de serem necessários outros 
                insumos, esses têm sido fatores limitantes na resposta à crise.
        <div>
        ''', unsafe_allow_html=True)

        st.write('<br/>', unsafe_allow_html=True)

        st.write('''
        <div class="scenario">
                <h3>
                        Assumiremos que 20% destes poderão ser destinados a pacientes com Covid-19 (você poderá ajustar abaixo). 
                        Caso seu município conte apenas com atitudes sindividuais, **sem políticas de restrição de contato, estima-se que....**
                </h3>
        </div>
        ''', unsafe_allow_html=True)
        
        ### INITIAL VALUES FOR BEDS AND VENTILATORS
        user_input['n_beds'], user_input['n_ventilators'] = int(selected_region['number_beds']*0.2), int(selected_region['number_ventilators']*0.2)
        
        #WORST SCENARIO SIMULATION  
        user_input['strategy'] = {'isolation': 90, 'lockdown': 90}
        _, dday_beds, dday_ventilators = simulator.run_evolution(user_input)
        
        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.RED, min_range=dday_beds['worst'], max_range=dday_beds['best'], label='LEITOS'))
        
        st.write('<br/>', unsafe_allow_html=True)

        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.ORANGE, min_range=dday_ventilators['worst'], max_range=dday_ventilators['best'], label='VENTILADORES'))

        
        st.write('''
        <div class="scenario">
                <h3>
                        Caso o município decrete hoje o isolamento social, <b>e fechando comércios e suspendendo transporte público, além de quarentena para doentes, estima-se que...</b>
                </h3>
        </div>
        ''', unsafe_allow_html=True)
        
        #BEST SCENARIO SIMULATION
        user_input['strategy'] = {'isolation': 90, 'lockdown': 0}
        _, dday_beds, dday_ventilators = simulator.run_evolution(user_input)

        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.GREEN, min_range=dday_beds['worst'], max_range=dday_beds['best'], label='LEITOS'))
        
        st.write('<br/>', unsafe_allow_html=True)
        
        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.GREEN, min_range=dday_ventilators['worst'], max_range=dday_ventilators['best'], label='VENTILADORES'))
        
        st.write('<br/>', unsafe_allow_html=True)

        utils.generateStrategiesSection(Strategies)

        st.sidebar.header("""Simulador de demanda hospitalar""")
        st.sidebar.subheader("""Simule o impacto de estratégias de isolamento em sua cidade:""")
#         st.sidebar.subheader("""
# ## Em quantos dias você quer acionar a Estratégia 2, medidas de restrição?
# """)

        user_input['strategy']['isolation'] = st.sidebar.number_input('Em quantos dias você quer acionar a Estratégia 2, medidas de restrição?', 0, 90, 90, key='strategy2')
        
#         st.sidebar.subheader("""
# ## Em quantos dias você quer acionar a Estratégia 3, lockdown?
# """)

        user_input['strategy']['lockdown'] = st.sidebar.number_input('Em quantos dias você quer acionar a Estratégia 3, lockdown?', 0, 90, 90, key='strategy3')
        
        st.sidebar.subheader("""A partir desses números, ajuste a capacidade que será alocada na intervenção:""")

#         st.sidebar.subheader("""
# ## Mude o percentual de leitos destinados aos pacientes com Covid-19:
# """)
        total_beds = user_input['n_beds']
        user_input['n_beds'] = st.sidebar.number_input('Mude o percentual de leitos destinados aos pacientes com Covid-19:', 0, None, total_beds)

#         st.sidebar.subheader("""
# ## Mude o percentual de ventiladores destinados aos pacientes com Covid-19:
# """)
        total_ventilators = user_input['n_ventilators']
        user_input['n_ventilators'] = st.sidebar.number_input('Mude o percentual de ventiladores destinados aos pacientes com Covid-19:', 0, None, total_ventilators)


        # Show scenario ddays and evolution
        fig, dday_beds, dday_ventilators = simulator.run_evolution(user_input)
        
        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.GREEN, min_range=dday_beds['worst'], max_range=dday_beds['best'], label='LEITOS'))
        
        st.write('<br/>', unsafe_allow_html=True)

        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.GREEN, min_range=dday_ventilators['worst'], max_range=dday_ventilators['best'], label='VENTILADORES'))
        
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
