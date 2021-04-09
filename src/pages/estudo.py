import streamlit as st
import utils
import base64
from pathlib import Path
import os
import pages.header as he

def main(session_state):
    utils.localCSS("style.css")
    he.genHeader("3")
    st.write(
        f"""
        <div class="base-wrapper" style="background-color:#0090A7;">
            <div class="hero-wrapper">
                <div class="hero-container" style="width:45%;">
                    <div class="hero-container-content">
                        <span class="subpages-container-product white-span">Estudo sobre vacinação </br>contra covid-19 e </br>redução de óbitos no Brasil</span>
                        <span class="subpages-container-subtitle white-span">Saiba quando podemos controlar a pandemia no Brasil no nosso estudo realizado com dados inéditos obtidos pela Lei de Acesso à Informação.</span>
                    </div>
                </div>
                <div class="subpages-container-image">   
                    <img style="width: 100%;" src="https://i.imgur.com/w5yVANW.png"/>
                </div>
            </div><br>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(
        """
        <div>
                <div class="base-wrapper">
                        <div>
                            <span>Utilizando dados inéditos sobre os grupos prioritários para vacinação da Covid-19, obtidos pela Lei de Acesso à Informação, nós da Impulso Gov, projetamos quando podemos controlar a pandemia no Brasil.<br><br></span>
                            <span>A partir da análise das informações disponíveis publicamente sobre produção nacional de vacina e dos acordos do Brasil para importação, e considerando quantas pessoas estão em cada grupo prioritário nos municípios brasileiros, eliminando a dupla-contagem, foi possível apontar três cenários para o avanço da vacinação no país.<br><br></span>
                            <span><b>Os números mostram que, no cenário intermediário, que parece mais provável agora, a vacinação dos grupos prioritários seria possível até o fim de abril.</b> Já no pior cenário, em que o país só consiga alcançar metade da sua capacidade de produção de vacinas, todas as pessoas integrantes de grupos prioritários no Brasil estariam imunizadas até o fim de julho.<br><br></span>
                            <span>O estudo, coordenado por Marco Brancher, especialista em dados e saúde da Impulso Gov, também projeta como a vacinação pode impactar na redução de óbitos no Brasil.<br><br></span>
                        </div>
                        <embed src="https://coronacidades.org/wp-content/uploads/2021/04/2020.03.31-Apresentac%CC%A7a%CC%83o-Dados-Vacinac%CC%A7a%CC%83o.pdf" width="100%" height="550">
                </div>
        </div>
        """,
        unsafe_allow_html=True,
    )