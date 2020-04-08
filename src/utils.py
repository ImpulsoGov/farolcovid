import streamlit as st
from models import SimulatorOutput, ContainmentStrategy, ResourceAvailability, BackgroundColor, Logo, Link
from typing import List
import re

def localCSS(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def genHeroSection():
        st.write('''<div class="base-wrapper hero-bg">
                <span class="logo-bold">corona</span><span class="logo-lighter">cidades</span>
                <div class="hero-wrapper">
                        <div class="hero-container">
                                <span class="hero-container-product primary-span">Simula<br/>Covid</span>
                                <span class="hero-container-subtitle primary-span">Um simulador da demanda por leitos hospitalares e ventiladores.</span>
                        </div>   
                        <img class="hero-container-image" src="https://i.imgur.com/w5yVANW.png"/>
                </div>
        </div class="base-wrapper>
        ''', unsafe_allow_html=True)

def genMunicipalityInputSection() -> None:        
        st.write('''
        <div class="base-wrapper">
                <span class="section-header primary-span">Qual a situação do meu município?</span>
        </div>
        ''',  unsafe_allow_html=True)

def genResourceAvailabilitySection(resources: ResourceAvailability) -> None:
        preposition, city = ('', 'Geral') if resources.city == 'Todos' else ('em', resources.city)

        st.write('''
        <div class="primary-bg"> 
                <div class="base-wrapper">
                        <span class="section-header white-span">
                                Panorama %s <span class="locality-name yellow-span">%s</span>
                        </span>
                        <div class="resources-wrapper">
                                <div class="resources-title-container">
                                        <span class="resources-title">Ao todo são</span>
                                </div>
                                <div class="resources-container-wrapper">
                                        <div class="resource-container"> 
                                                <span class='resource-container-value'>%i</span>  
                                                <span class='resource-container-label'>casos confirmados</span>  
                                        </div>
                                        <div class="resource-container"> 
                                                <span class='resource-container-value'>%i</span>  
                                                <span class='resource-container-label'>mortes</span>  
                                        </div>
                                </div>
                                <span class="resource-font"><b>Fonte:</b> Brasil.IO atualizado diariamente com base em boletins das secretarias de saúde publicados.</span>
                        </div>
                        <div class="resources-wrapper">
                                <div class="resources-title-container">
                                        <span class="resources-title">A capacidade hospitalar é</span>
                                </div>
                                <div class="resources-container-wrapper">
                                        <div class="resource-container"> 
                                                <span class='resource-container-value'>%i</span>  
                                                <span class='resource-container-label'>leitos</span>  
                                        </div>
                                        <div class="resource-container"> 
                                                <span class='resource-container-value'>%i</span>  
                                                <span class='resource-container-label'>ventiladores</span>  
                                        </div>
                                </div>
                                <span class="resource-font"><b>Fonte:</b> 
                                        DATASUS CNes, Fevereiro 2020. Incluímos leitos hospitalares da rede SUS e não-SUS. Para excluir a última categoria, precisaríamos estimar também a população susdependente. Para mais informações, confira nossa metodologia.                                
                                </span>
                                <div class="ambassador-container">
                                        <span class="ambassador-question white-span bold">Esse dado parece desatualizado? Venha ser parte do nosso time de embaixadores!</span>
                                        <span class="white-span">Estamos montando uma rede para manter o SimulaCovid sempre atualizado e nossas projeções serem úteis para tomada de decisão na sua cidade!</span>
                                        <a class="btn-ambassador" href="%s" target="blank">Quero ser embaixador</a>
                                </div>
                        </div>
                </div>
        </div>
        ''' 
        %(preposition, city, resources.cases, resources.deaths, resources.beds, resources.ventilators, Link.AMBASSADOR_FORM.value)
        , unsafe_allow_html=True)


def genSimulatorOutput(output: SimulatorOutput) -> str:
        bed_img = 'https://i.imgur.com/27hutU0.png'
        ventilator_icon = 'https://i.imgur.com/8kxC2Fi.png'
        
        has_bed_projection = (output.min_range_beds != -1 and  output.max_range_beds != -1)
        bed_prep = 'entre' if has_bed_projection else 'em'
        
        has_ventilator_projection = (output.min_range_ventilators != -1 and output.max_range_ventilators != -1)
        ventilator_prep = 'entre' if has_ventilator_projection else 'em'
        
        if has_bed_projection:
                bed_projection = '%i <span class="simulator-output-row-prediction-separator">e</span> %i' % (output.min_range_beds, output.max_range_beds)
        else:
                bed_projection = 'mais de 90'

        if has_ventilator_projection: 
                ventilator_projection = '%i <span class="simulator-output-row-prediction-separator">e</span> %i' % (output.min_range_ventilators, output.max_range_ventilators)
        else:
                ventilator_projection = 'mais de 90'

        output =  '''
        <div>
                <div class="simulator-container %s">
                        <div class="simulator-output-wrapper">
                                <span class="simulator-output-timeframe">%s</span>
                                <div class="simulator-output-row">
                                        <span class="simulator-output-row-prediction-value">
                                                %s
                                        </span>  
                                </div> 
                                <span class="simulator-output-row-prediction-label">
                                        dias será atingida a capacidade máxima de <b>leitos</b>
                                </span>
                        </div>
                        <img src="%s" class="simulator-output-image"/>
                </div>
                <br />
                <div class="simulator-container %s">
                        <div class="simulator-output-wrapper">
                                <span class="simulator-output-timeframe">%s</span>
                                <div class="simulator-output-row">
                                        <span class="simulator-output-row-prediction-value">
                                                %s
                                        </span>  
                                </div> 
                                <span class="simulator-output-row-prediction-label">
                                        dias será atingida a capacidade máxima de <b>ventiladores</b>
                                </span>
                        </div>
                        <img src="%s" class="simulator-output-image"/>
                </div>
        </div>''' % (output.color.value, bed_prep, bed_projection, bed_img,
                     output.color.value, ventilator_prep, ventilator_projection, ventilator_icon)

        return output.strip('\n\t')
                

def genSimulationSection(city: str, worst_case: SimulatorOutput, best_case: SimulatorOutput) -> None:

        status_quo = genSimulatorOutput(worst_case) 
        restrictions = genSimulatorOutput(best_case) 

        preposition, city = ('', 'Geral') if city == 'Todos' else ('em', city)

        st.write('''<div class="base-wrapper">
                <div class="simulator-wrapper">
                        <span class="section-header primary-span">
                                Projeção %s <span class="yellow-span">%s</span>
                        </span>
                        <div class="simulation-scenario-header-container">
                                <span class="simulator-scenario-header grey-bg">
                                        Cenário 1: Não Intervenção
                                </span>
                        </div>
                        %s
                        <br/>
                        <br/>
                        <div class="simulation-scenario-header-container">
                                <span class="simulator-scenario-header lightblue-bg">
                                        Cenário 2: Medidas-Restritivas
                                </span>
                        </div>
                        %s
                </div>
        </div>
        ''' % (preposition, city, status_quo, restrictions), unsafe_allow_html=True)

def genStrategyCard(strategy: ContainmentStrategy) -> str:
        return '''
        <div class="scenario-card">
                        <div class="scenario-card-header">
                                <span class="scenario-card-header-code %s">ESTRATÉGIA %i</span>
                                <div class="scenario-card-header-name-background %s">
                                        <span class="scenario-card-header-name">%s</span>
                                </div>
                        </div>
                        <img src="%s" class="scenario-card-img"/>
                        <span class="scenario-card-description">%s</span>
        </div>''' % (strategy.color.value, strategy.code, strategy.background.value, strategy.name, strategy.image_url, strategy.description)

def generateStrategiesSection(strategies: List[ContainmentStrategy]) -> None:
        cards = list(map(genStrategyCard, strategies))
        cards = ''.join(cards)
        st.write('''
        <div class="lightgrey-bg">
                <div class="base-wrapper">
                        <span class="section-header primary-span">E como me preparo?</span>
                        <div class="scenario-cards-container">%s</div>
                </div>
        </div>
        ''' % cards,
        unsafe_allow_html= True)

def genLogosSection() -> None:
        st.write('''
                <div class="logo-wrapper magenta-bg">
                        <img class="logo-img" src="%s"/>
                        <div class="logo-section">
                                <img class="logo-img" src="%s"/>
                                <img class="logo-img" src="%s"/>
                        </div>
                </div>''' % (Logo.IMPULSO.value, Logo.CORONACIDADES.value, Logo.ARAPYAU.value), unsafe_allow_html=True)