import streamlit as st
import numpy as np
import pandas as pd
import utils
import pages.header as he
import json

def main(session_state):
    utils.localCSS("vacinastyle.css")
    he.genHeader("4")
    st.write(
        f"""
        <div class="base-wrapper" style="background-color:#0090A7;">
            <div class="hero-wrapper">
                <div class="hero-container" style="width:45%;">
                    <div class="hero-container-content">
                        <span class="subpages-container-product white-span">Vacinômetro</span>
                        <span class="subpages-subcontainer-product white-span">Veja a evolução da vacinação em sua cidade ou estado! </span>
                        <span class="subpages-container-subtitle white-span">Acompanhe e compare as informações mais atualizadas sobre a vacinação nos municípios do Brasil.</span>
                    </div>
                </div>
                <div class="subpages-container-image">   
                    <img style="width: 100%;" src="https://i.imgur.com/w5yVANW.png"/>
                </div>
            </div><br>
        </div>
        <div>
            <br><br>
        </div>
        <div class="base-wrapper">
            <embed src="https://helper.coronacidades.org/vacinatable" width="100%" height="550">
         </div>
        """,
        unsafe_allow_html=True,
    )

    
    # st.write(
    #     """
    #     <div class="base-wrapper">
    #         <embed src="https://codepen.io/gabriellearruda/embed/yLgPjyR?height=432&theme-id=light&default-tab=result" width="100%" height="550">
    #     </div>""",
    #     unsafe_allow_html=True,
    # )