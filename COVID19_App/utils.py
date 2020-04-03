import streamlit as st
from models import SimulatorOutput, KPI, ContainmentStrategy
from typing import List

def localCSS(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def generateKPIRow(kpi1: KPI, kpi2: KPI) -> None:
        st.write('''
        <div class='kpi-wrapper'>
                <div class='kpi-container green-bg'>
                        <h3>%s:</h3>   
                        <span class='kpi'>%s</span>    
                </div>
                <div class='kpi-container green-bg'>
                        <h3>%s:</h3>
                        <span class='kpi'>%s</span>
                </div>
        <div>''' % (kpi1.label, '{:,}'.format(kpi1.value), kpi2.label, '{:,}'.format(kpi2.value)), 
        unsafe_allow_html=True)

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
        background = '{}-bg'.format(strategy.color)
        code_color = strategy.color + '-span'

        return '''<div class="scenario-card">
                        <div class="scenario-card-header">
                                <span class="scenario-card-header-code %s">ESTRATÉGIA %i</span>
                                <div class="scenario-card-header-name-background %s">
                                        <span class="scenario-card-header-name">%s</span>
                                </div>
                        </div>
                        <img src="%s" class="scenario-card-img"/>
                        <span class="scenario-card-description">%s</span>
        </div>''' % (code_color, strategy.code, background, strategy.name, strategy.image_url, strategy.description)

def generateStrategiesSection(strategies: List[ContainmentStrategy]) -> None:
        cards = list(map(generateStrategyCard, strategies))

        st.write('''
        <div class="scenario-wrapper">
                <h2><b>E COMO ME PREPARO?</b></h2>
                %s
        </div>
        ''' % ''.join(cards),
        unsafe_allow_html= True)