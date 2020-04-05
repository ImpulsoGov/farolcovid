import streamlit as st
from models import SimulatorOutput, ContainmentStrategy, ResourceAvailability
from typing import List

def localCSS(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


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


def generateSimulatorOutput(output: SimulatorOutput) -> None:
        st.write('''
                <div class="simulator-output-wrapper %s">
                        <h3>entre</h3>
                        <div class="simulator-output-row">
                                <div class="simulator-output-row-prediction">
                                        <span class="simulator-output-row-prediction-value">%i</span>
                                        <span class="simulator-output-row-prediction-separator">e</span>
                                        <span class="simulator-output-row-prediction-value">%i</span>
                                </div>
                                <span class="simulator-output-row-prediction-label">
                                        *DIAS SERÁ ATINGIDA A CAPACIDADE MÁXIMA DE %s
                                </span>
                        </div> 
                </div>
        ''' % (output.color.value, output.min_range, output.max_range, output.label),
        unsafe_allow_html=True)

def generateStrategyCard(strategy: ContainmentStrategy) -> str:
        return '''<div class="scenario-card">
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
        cards = list(map(generateStrategyCard, strategies))

        st.write('''
        <div class="scenario-wrapper">
                <h2><b>E COMO ME PREPARO?</b></h2>
                %s
        </div>
        ''' % ''.join(cards),
        unsafe_allow_html= True)