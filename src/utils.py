import streamlit as st
from datetime import datetime
from datetime import timedelta
from models import SimulatorOutput, ContainmentStrategy, ResourceAvailability, BackgroundColor, Logo, Link
from typing import List
import re

def make_clickable(text, link):
    # target _blank to open new window
    # extract clickable text to display for your link
        return f'<a target="_blank" href="{link}">{text}</a>'

def localCSS(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def genHeroSection():
        st.write('''<div class="base-wrapper hero-bg">
                <a href="https://coronacidades.org/" target="blank" class="logo-link"><span class="logo-bold">corona</span><span class="logo-lighter">cidades</span></a>
                <div class="hero-wrapper">
                        <div class="hero-container">
                                <div class="hero-container-content">
                                        <span class="hero-container-product primary-span">Simula<br/>Covid</span>
                                        <span class="hero-container-subtitle primary-span">Um simulador da demanda por leitos hospitalares e ventiladores.</span>
                                </div>
                        </div>   
                        <img class="hero-container-image" src="https://i.imgur.com/w5yVANW.png"/>
                </div>
        </div>
        ''', unsafe_allow_html=True)

def genVideoTutorial():
        st.write('''<div class="base-wrapper">
                        <span class="section-header primary-span">Antes de começar: entenda como usar!</span>
                </div>''', unsafe_allow_html=True)
        st.video(Link.YOUTUBE_TUTORIAL.value)

def genStateInputSectionHeader() -> None:        
        st.write('''
        <div class="base-wrapper">
                <span class="section-header primary-span">Etapa 1: Selecione o seu Estado</span>
        </div>
        ''',  unsafe_allow_html=True)


def genMunicipalityInputSection() -> None:        
        st.write('''
        <div class="base-wrapper">
                <div style="display: flex; flex-direction: column"> 
                        <span class="section-header primary-span">Etapa 2: Selecione seu Município ou Região SUS</span>
                        <span>Se seu município não possui unidade de tratamento intensivo, sugerimos simular a situação da sua regional. Não recomendamos a simulação a nível estadual.</span>
                </div>
        </div>
        ''',  unsafe_allow_html=True)

def genInputCustomizationSectionHeader(locality: str) -> None:
        st.write('''
        <div class="base-wrapper">
                <span class="section-header primary-span">Etapa 3: Verifique os dados disponíveis <span class="yellow-span">(%s)</span></span>
                <br />
                <span>Usamos os dados do Brasil.io e DataSUS, mas é possível que eles dados estejam um pouco desatualizados. Se estiverem, é só ajustar os valores abaixo para continuar a simulação.</span>
                <br />
        </div>''' % locality, unsafe_allow_html=True)

def genAmbassadorSection() -> None:
        st.write('''
        <div class="base-wrapper">
                <div class="ambassador-container">
                        <span class="ambassador-question bold">Você teve que atualizar algum dos dados acima? Você tem informações mais recentes e pode colaborar conosco?</span>
                        <span>Estamos montando uma rede para manter o SimulaCovid sempre atualizado e nossas projeções serem úteis para tomada de decisão na sua cidade. Venha ser parte do nosso time de embaixadores!</span>
                        <a class="btn-ambassador" href="%s" target="blank">Quero ser embaixador</a>
                </div>
        </div>
        ''' % Link.AMBASSADOR_FORM.value, unsafe_allow_html=True)

def genResourceAvailabilitySection(resources: ResourceAvailability) -> None:
        msg = f'''
        🚨 *BOLETIM CoronaCidades:*  {resources.locality} - {datetime.now().strftime('%d/%m')}  🚨%0a%0a
        😷 *{int(resources.cases)}* casos confirmados e *{int(resources.deaths)}* mortes%0a%0a
        🏥 Hoje estão disponíveis *{resources.beds}* leitos e *{resources.ventilators}* ventiladores destinados à Covid %0a%0a
        👉 _Acompanhe e simule a situação do seu município acessando o *SimulaCovid* aqui_: https://coronacidades.org/ ''' 
        
        st.write('''
        <div class="primary-bg"> 
                <div class="base-wrapper">
                        <div class="resource-header-container">
                                <span class="section-header white-span">Panorama <span class="locality-name yellow-span">%s</span></span>
                                <a class="btn-wpp" href="whatsapp://send?text=%s" target="blank">Compartilhar no Whatsapp</a>
                        </div>
                        <div class="resources-wrapper">
                                <div class="resources-title-container">
                                        <span class="resources-title">Progressão da Transmissão</span>
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
                                        <span class="resources-title">Capacidade hospitalar destinada à COVID</span>
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
                                        DATASUS CNES, Fevereiro 2020. Assumimos que 20%% dos leitos complementares e ventiladores registrados da rede SUS e não-SUS seriam alocados para pacientes da Covid-19. Esse número poderá ser ajustado na simulação abaixo.                             
                                </span>
                                <div class="ambassador-container">
                                        <span class="ambassador-question white-span bold">Esse dado está desatualizado? Você tem informações mais recentes e pode colaborar conosco?</span>
                                        <span class="white-span">Estamos montando uma rede para manter o SimulaCovid sempre atualizado e nossas projeções serem úteis para tomada de decisão na sua cidade. Venha ser parte do nosso time de embaixadores!</span>
                                        <a class="btn-ambassador" href="%s" target="blank">Quero ser embaixador</a>
                                </div>
                        </div>
                </div>
        </div>
        ''' 
        %(resources.locality, msg, resources.cases, 
        resources.deaths, resources.beds, resources.ventilators, Link.AMBASSADOR_FORM.value)
        , unsafe_allow_html=True)

def genSimulatorOutput(output: SimulatorOutput) -> str:
        bed_img = 'https://i.imgur.com/27hutU0.png'
        ventilator_icon = 'https://i.imgur.com/V419ZRI.png'
        
        has_bed_projection = (output.min_range_beds != -1 and  output.max_range_beds != -1)
        bed_prep = 'entre' if has_bed_projection else 'em'
        
        has_ventilator_projection = (output.min_range_ventilators != -1 and output.max_range_ventilators != -1)
        ventilator_prep = 'entre' if has_ventilator_projection else 'em'
        
        if has_bed_projection:
                bed_min_range_date = (datetime.now() + timedelta(days=int(output.min_range_beds))).strftime("%d/%m")
                bed_max_range_date =(datetime.now() + timedelta(days=int(output.max_range_beds))).strftime("%d/%m")
                bed_projection = f'''{output.min_range_beds}
                        <span class="simulator-output-row-prediction-separator">e</span> 
                        {output.max_range_beds} '''
                bed_rng = f' ({bed_min_range_date} - {bed_max_range_date}) '
        else:
                bed_projection = 'mais de 90'
                bed_rng = f''

        if has_ventilator_projection: 
                ventilator_min_range_date = (datetime.now() + timedelta(days=int(output.min_range_ventilators))).strftime("%d/%m")
                ventilator_max_range_date =(datetime.now() + timedelta(days=int(output.max_range_ventilators))).strftime("%d/%m")
                ventilator_projection = '%i <span class="simulator-output-row-prediction-separator">e</span> %i' % (output.min_range_ventilators, output.max_range_ventilators)
                ventilator_rng =  f' ({ventilator_min_range_date} - {ventilator_max_range_date}) '
        else:
                ventilator_projection = 'mais de 90'
                ventilator_rng = ''

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
                                        dias%s será atingida a capacidade máxima de <b>leitos</b>
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
                                        dias%s será atingida a capacidade máxima de <b>ventiladores</b>
                                </span>
                        </div>
                        <img src="%s" class="simulator-output-image"/>
                </div>
        </div>''' % (output.color.value, bed_prep, bed_projection, bed_rng, bed_img, 
                     output.color.value, ventilator_prep, ventilator_projection, ventilator_rng, ventilator_icon)

        return output.strip('\n\t')
                

def genSimulationSection(locality: str, resources: ResourceAvailability, worst_case: SimulatorOutput, best_case: SimulatorOutput) -> None:
        no_quarentine = 'mais de 90' if(worst_case.max_range_beds == -1 and worst_case.max_range_ventilators == -1) else  min(worst_case.max_range_beds, worst_case.max_range_ventilators) 
        date_proj = ''
        if no_quarentine != 'mais de 90':
                proj = (datetime.now() + timedelta(days=int(no_quarentine))).strftime("%d/%m")
                date_proj = f' *({proj})* '

        msg = f'''
        🚨 *BOLETIM SimulaCovid:*  {resources.locality} - {datetime.now().strftime('%d/%m')}  🚨%0a%0a
        🏥 Considerando que {resources.locality} tem *{resources.beds}* leitos 🛏️ e *{resources.ventilators}* ventiladores ⚕ %0a%0a
        😷 Na ausência, {resources.locality} poderia atingir a sua capacidade hospitalar em *{no_quarentine}* dias{date_proj}%0a%0a
        👉 _Acompanhe e simule a situação do seu município acessando o *SimulaCovid* aqui_: https://coronacidades.org/ ''' 
        
        status_quo = genSimulatorOutput(worst_case) 
        restrictions = genSimulatorOutput(best_case) 

        st.write('''
        <div class="lightgrey-bg">
                <div class="base-wrapper">
                        <div class="simulator-wrapper">
                                <span class="section-header primary-span">
                                        <span  class="yellow-span">%s</span>
                                        <br/>
                                        Daqui a quantos dias será atingida a capacidade <span class="yellow-span">hospitalar</span>?
                                </span>
                                <br/>
                                <br/>
                                <div class="simulation-scenario-header-container">
                                        <span class="simulator-scenario-header grey-bg">
                                                Sem Políticas de Restrição
                                        </span>
                                </div>
                                %s
                                <br/>
                                <br/>
                                <div class="simulation-scenario-header-container">
                                        <span class="simulator-scenario-header lightblue-bg">
                                                Com Medidas de Isolamento Social
                                        </span>
                                </div>
                                %s
                                <a class="btn-wpp" href="whatsapp://send?text=%s" target="blank">Compartilhar no Whatsapp</a>
                        </div>
                </div>
        </div>
        ''' % (locality, status_quo, restrictions, msg), unsafe_allow_html=True)

def genActNowSection(locality, worst_case):
        display = '' if any(value != -1 for value in [worst_case.min_range_beds, worst_case.max_range_beds, worst_case.min_range_ventilators, worst_case.max_range_ventilators]) else 'hide'

        st.write('''
        <div class="primary-bg %s">
                <div class="base-wrapper">
                        <div class="act-now-wrapper">
                        <span class="section-header white-span"><span class="yellow-span">%s | </span> Você precisa agir agora </span>
                        <span class="white-span">Para prevenir uma sobrecarga hospitalar, é preciso implementar uma estratégia de contenção. Quanto antes você agir, mais vidas consegue salvar.</span>
                        </div>
                </div>
        </div>
        ''' % (display, locality),  unsafe_allow_html=True)

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

def genStrategiesSection(strategies: List[ContainmentStrategy]) -> None:
        cards = list(map(genStrategyCard, strategies))
        cards = ''.join(cards)
        st.write('''
        <div class="primary-bg">
                <div class="base-wrapper">
                        <span class="section-header white-span">E como você pode reagir?</span>
                        <div class="scenario-cards-container">%s</div>
                </div>
        </div>
        ''' % cards,
        unsafe_allow_html= True)

def genChartSimulationSection(time2sd: int, time2lockdown: int, simulation: SimulatorOutput, fig) -> None:

        simulation = genSimulatorOutput(simulation) 
        sd_date = (datetime.now() + timedelta(days=int(time2sd))).strftime("%d/%m")
        lockdown_date = (datetime.now() + timedelta(days=int(time2lockdown))).strftime("%d/%m")

        simulation_description = ''
        if time2lockdown <= time2sd:
                
                if time2lockdown == 0:
                        simulation_description = f'Começando a quarentena <b>hoje</b> ({lockdown_date}):'
                else:
                        simulation_description = f'Começando a quarentena em <b>{time2lockdown}</b> dias ({lockdown_date}):'
        else: # lockdown after social distancing
                if time2sd == 0:
                        simulation_description = f'Começando o isolamento social <b>hoje</b>  ({sd_date}) e a quarentena em <b>{time2lockdown}</b> dias ({lockdown_date}):'
                else:
                        simulation_description = f'Começando o isolamento social em <b>{time2sd}</b> dias ({sd_date}) e a quarentena em <b>{time2lockdown}</b> dias ({lockdown_date}):'
                

        st.write('''<div class="lightgrey-bg">
                <div class="base-wrapper">
                        <div class="simulator-header">
                                <span class="section-header primary-span">Aqui está o resultado da sua simulação</span>
                                <span class="chart-simulator-instructions subsection-header">%s</span>
                        </div>
                        <div class="simulator-wrapper">
                                %s
                        </div>
                         <div style="display: flex; flex-direction: column; margin-top: 5em"> 
                                <span class="section-header primary-span">Visão detalhada da sua simulação</span><br>
                                <span style="border-radius: 15px; border: dashed 2px  #F2C94C; padding: 1em">
                                        <b>NOTA:</b> 
                                        Para evitar uma sobrecarga hospitalar, a sua demanda (a curva 📈) deve ficar sempre abaixo da respectiva linhas tracejadas (a reta horizontal ➖).
                                        Em outras palavras, a quantidade de pessoas que precisam ser internadas por dia não deve ultrapassar o número de equipamentos disponíveis.
                                </span>
                        </div>
                </div>
        </div>
        ''' % (simulation_description, simulation), unsafe_allow_html=True)

        st.plotly_chart(fig)


def genFooter() -> None:
        st.write('''
        <div class="magenta-bg">
                <div class="base-wrapper">
                        <div class="logo-wrapper">
                                <span>A presente ferramenta, voluntária, parte de estudos referenciados já publicados e considera os dados de saúde pública dos municípios brasileiros disponibilizados no DataSus. O repositório do projeto pode ser acessado no nosso <a class="github-link" href="">Github</a></span>
                                <br/>
                                <span>Os cenários projetados são meramente indicativos e dependem de variáveis que aqui não podem ser consideradas. Trata-se de mera contribuição à elaboração de cenários por parte dos municípios e não configura qualquer obrigação ou responsabilidade perante as decisões efetivadas. Saiba mais em nossa metodologia.</span>
                                <br/>
                                <span>Estamos em constante desenvolvimento e queremos ouvir sua opinião sobre a ferramenta - caso tenha sugestões ou comentários, entre em contato via o chat ao lado. Caso seja gestor público e necessite de apoio para preparo de seu município, acesse a Checklist e confira o site do CoronaCidades.</span>
                                <br/>
                                <img class="logo-img" src="%s"/>
                                <div class="logo-section">
                                        <img class="logo-img" src="%s"/>
                                        <img class="logo-img" src="%s"/>
                                </div>
                        </div>'
                </div>
        </div>''' % (Logo.IMPULSO.value, Logo.CORONACIDADES.value, Logo.ARAPYAU.value), unsafe_allow_html=True)


def genWhatsappButton() -> None:
        msg = f'Olá Equipe Coronacidades. Vocês podem me ajuda com uma dúvida?'
        phone = '+5511964373097'
        url = 'whatsapp://send?text={}&phone=${}'.format(msg, phone)
        st.write(''' 
         <a href="%s" class="float" target="_blank" id="messenger">
                <i class="material-icons">question_answer</i>
                <p class="float-header">Dúvidas?</p></a>
        ''' % url,  unsafe_allow_html=True)
        