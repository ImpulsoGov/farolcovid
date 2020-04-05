import streamlit as st
from models import BackgroundColor, Document, Strategies, SimulatorOutput, ResourceAvailability
from typing import List
import utils
from model import seir
import os
import plotly.express as px
import yaml

import loader
from model import seir

def add_all(x, all_string='Todos'):
        return [all_string] + list(x)

def filter_frame(_df, name, all_string='Todos'):

        if name == all_string:
                return _df[[]].sum()


# =======> TESTANDO (para funcionar, descomente o código nas linhas 112-116!)
def run_evolution():
    
    st.sidebar.subheader('Selecione os dados do seu município para rodar o modelo')

    population_params = dict()
    population_params['N'] = st.sidebar.number_input('População', 0, 10000, 10000, key='N')
    population_params['I'] = st.sidebar.number_input('Casos confirmados', 0, 10000, 1000, key='I')
    population_params['D'] = st.sidebar.number_input('Mortes confirmadas', 0, 10000, 10, key='D')
    population_params['R'] = st.sidebar.number_input('Pessoas recuperadas', 0, 10000, 0, key='R')
    
    model_parameters = yaml.load(open(os.getcwd() + '/model_parameters.yaml', 'r'), Loader=yaml.FullLoader)
    evolution = seir.entrypoint(population_params, model_parameters, initial=True)
    
    # Generate fig
    fig = px.line(evolution.melt('dias'), x='dias', y='value', color='variable')
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 
                       'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                       'yaxis_title': 'Número de pessoas'})

    return fig
# <================
        
def main():
        utils.localCSS("style.css")

        config = yaml.load(open('configs/config.yaml', 'r'))
        cities = loader.read_data('br', config)    

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
                <span class="section-header">Qual a situação do meu município?</span>
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


        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.RED, min_range=24, max_range=25, label='LEITOS'))
        
        st.write('<br/>', unsafe_allow_html=True)

        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.ORANGE, min_range=24, max_range=25, label='VENTILADORES'))
        

        st.write('''
        <div class="scenario">
                <h3>
                        Caso o município decrete hoje o isolamento social, <b>e fechando comércios e suspendendo transporte público, além de quarentena para doentes, estima-se que...</b>
                </h3>
        </div>
        ''', unsafe_allow_html=True)

        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.GREEN, min_range=24, max_range=25, label='LEITOS'))
        
        st.write('<br/>', unsafe_allow_html=True)

        utils.generateSimulatorOutput(SimulatorOutput(color=BackgroundColor.GREEN, min_range=24, max_range=25, label='VENTILADORES'))
        
        st.write('<br/>', unsafe_allow_html=True)

        utils.generateStrategiesSection(Strategies)

        st.write("""
## Simule o impacto de estratégias semelhantes na capacidade o sistema de saúde em sua cidade:
""")


        st.write("""
## Em quantos dias você quer acionar a Estratégia 2, medidas de restrição?
""")
        st.number_input('Dias:', 0, 90, 90, key='strategy2')

        st.write("""
## Em quantos dias você quer acionar a Estratégia 3, lockdown?
""")

        st.number_input('Dias:', 0, 90, 90, key='strategy3')

        st.write("""
## A partir desses números, ajuste a capacidade que será alocada na intervenção:?
""")

        st.write("""
## Mude o percentual de leitos destinados aos pacientes com Covid-19:
""")
        st.number_input('Leitos:', 0, None, 90)

        st.write("""
## Mude o percentual de ventiladores destinados aos pacientes com Covid-19:
""")

        st.number_input('Ventiladores:', 0, None, 90)

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
