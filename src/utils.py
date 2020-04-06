import streamlit as st
from models import SimulatorOutput, ContainmentStrategy, ResourceAvailability, BackgroundColor
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
                                <span class="hero-container-product primary-span">Simula</span>
                                <span class="hero-container-product primary-span">Covid</span>
                                <span class="hero-container-subtitle primary-span">Um simulador da demanda por leitos hospitalares e ventiladores.</span>
                        </div>   
                        <img class="hero-container-image" src="https://i.imgur.com/w5yVANW.png"/>
                </div>
        </div class="base-wrapper>
        ''', unsafe_allow_html=True)
def genResourceAvailabilitySection(resources: ResourceAvailability) -> None:
        st.write('''
        <div class="primary-bg"> 
                <div class="base-wrapper">
                        <span class="section-header white-span">
                                Panorama em <span class="yellow-span">%s</span>
                        </span>
                        <div class="resources-wrapper">
                                <div class="resources-title-container">
                                        <span class="resources-title">Casos de Coronavírus</span>
                                </div>
                                <div class="resources-container-wrapper">
                                        <div class="resource-container"> 
                                                <span class='resource-container-value'>%i</span>  
                                                <span class='resource-container-label'>confirmados</span>  
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
                                        <span class="resources-title">Casos de Coronavírus</span>
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
                        </div>
                </div>
        </div>
        ''' 
        %(resources.city, resources.cases, resources.deaths, resources.beds, resources.ventilators)
        , unsafe_allow_html=True)


def genSimulatorOutput(output: SimulatorOutput) -> str:
        bed_img = 'https://i.imgur.com/27hutU0.png'
        ventilator_icon = 'https://i.imgur.com/8kxC2Fi.png'

        output =  '''
        <div>
                <div class="simulator-container %s">
                        <div class="simulator-output-wrapper">
                                <span class="simulator-output-timeframe">entre</span>
                                <div class="simulator-output-row">
                                        <span class="simulator-output-row-prediction-value">
                                                %i <span class="simulator-output-row-prediction-separator">e</span> %i
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
                                <span class="simulator-output-timeframe">entre</span>
                                <div class="simulator-output-row">
                                        <span class="simulator-output-row-prediction-value">
                                                %i <span class="simulator-output-row-prediction-separator">e</span> %i
                                        </span>  
                                </div> 
                                <span class="simulator-output-row-prediction-label">
                                        dias será atingida a capacidade máxima de <b>ventiladores</b>
                                </span>
                        </div>
                        <img src="%s" class="simulator-output-image"/>
                </div>
        </div>''' % (output.color.value, output.min_range_beds, output.max_range_beds, bed_img,
                     output.color.value, output.min_range_ventilators, output.max_range_ventilators, ventilator_icon)

        return output.strip('\n\t')
                

def genSimulationSection(city) -> None:
        status_quo = genSimulatorOutput(SimulatorOutput(
                                color=BackgroundColor.GREY_GRADIENT,
                                min_range_beds=24, 
                                max_range_beds=25, 
                                min_range_ventilators=15,
                                max_range_ventilators=10)) 

        restrictions = genSimulatorOutput(SimulatorOutput(
                                color=BackgroundColor.LIGHT_BLUE_GRADIENT,
                                min_range_beds=24, 
                                max_range_beds=25, 
                                min_range_ventilators=15,
                                max_range_ventilators=10)) 

        st.write('''<div class="base-wrapper">
                <div class="simulator-wrapper">
                        <span class="section-header primary-span">
                                Projeção em <span class="yellow-span">%s</span>
                        </span>
                        <div class="simulation-scenario-header-container">
                                <span class="simulator-scenario-header grey-bg">
                                        Cenário 1: Não Intervenção
                                </span>
                        </div>
                        %s
                        <div class="simulation-scenario-header-container">
                                <span class="simulator-scenario-header light-blue-bg">
                                        Cenário 2: Medidas-Restritivas
                                </span>
                        </div>
                        %s
                </div>
        </div>
        ''' % (city, status_quo, restrictions), unsafe_allow_html=True)

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
        <div class="scenario-wrapper primary-bg">
                <div class="base-wrapper">
                        <span class="section-header white-span">E como me preparo?</span>
                        <div class="scenario-cards-container">
                                %s
                        </div>
                </div>
        </div>
        ''' % cards,
        unsafe_allow_html= True)