import streamlit as st
import utils
import base64
from pathlib import Path
import os
import pages.header as he

def main(session_state):
    utils.localCSS("style.css")
    utils.genHeroSection(
        title1="Farol",
        title2="Covid",
        subtitle="Estudo sobre vacinação contra Covid-19.",
        logo="https://i.imgur.com/CkYDPR7.png",
        header=False,
    )
    he.genHeader("3")
    st.write(
        """
        <div class="base-wrapper flex flex-column" style="background-color: rgb(0, 144, 167);">
            <div class="white-span header p1" style="font-size:30px;">Dados sobre vacinação contra Covid-19 e redução de óbitos no Brasil</div>
        </div>
        <div class="magenta-bg">
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