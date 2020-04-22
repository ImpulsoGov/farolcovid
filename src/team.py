import streamlit as st
import utils
from models import  Logo

def main():
    ana = 'https://media-exp1.licdn.com/dms/image/C4E03AQGdLO2wZpvasA/profile-displayphoto-shrink_200_200/0?e=1591833600&v=beta&t=BsnUsaEI-eLrn_oxLf7cEyXKGx2_7OBJZ9suUrRev_8'
    carabetta = 'https://media-exp1.licdn.com/dms/image/C4D03AQF8rJe40DpQqA/profile-displayphoto-shrink_200_200/0?e=1591833600&v=beta&t=6smhmNk7Ppktq5cX4vxhD4x-A6mMTdZnIAEu5DlV18g'
    fernanda = 'https://media-exp1.licdn.com/dms/image/C4D03AQFveYuReCqBVg/profile-displayphoto-shrink_200_200/0?e=1593043200&v=beta&t=14iMvOQdBESRi2OmsqmAdDBWVh0xdb_77Tw_dUycAto'
    saru = 'https://media-exp1.licdn.com/dms/image/C5603AQHB6rggvacwQw/profile-displayphoto-shrink_200_200/0?e=1591833600&v=beta&t=jj_atUnkJJm8SDKB1GQBF5n8bM-8dUKsTJE1Nsph3qE'
    diego = 'https://media-exp1.licdn.com/dms/image/C4D03AQGc03RUyqn7rQ/profile-displayphoto-shrink_200_200/0?e=1591833600&v=beta&t=VQeYTDAIkwXnCBISvvBne6GO-hOnHUu70s35OwcH4RE'
    luiz = 'https://media-exp1.licdn.com/dms/image/C4E03AQHSVHQ8br4SoQ/profile-displayphoto-shrink_200_200/0?e=1591833600&v=beta&t=rzj5_o4-AXYpcLG2EN6xOaB_c8-Ki-HQSIBUArD_ZxM'

    utils.localCSS("style.css")

    logo = Logo.IMPULSO.value

    st.write('''
    <div class="base-wrapper">
        <img class="team-logo" src="%s" />
            <h1 class="primary-span">Quem Somos</h1>
            <div class="profiles-container">
            <div class="profile">
                <img class="profile-photo" src="%s"/>
                <span class="profile-name">Ana Paula Pellegrino, Doutoranda em Ciência Política da Georgetown University</span>
            </div>
            <div class="profile">
                <img class="profile-photo" src="%s"/>
                <span class="profile-name">Diego Oliveira, Mestre em Física Aplicada pela Unicamp</span>
            </div>
            <div class="profile">
                <img class="profile-photo" src="%s"/>
                <span class="profile-name">Fernanda Scovino, Graduada em Matemática Aplicada pela FGV</span>
            </div>
            <div class="profile">
                <img class="profile-photo" src="%s"/>
                <span class="profile-name">Gabriel Saruhashi, Graduando em Ciência da Computação e Psicologia na Yale University</span>
            </div>
            <div class="profile">
                <img class="profile-photo" src="%s"/>
                <span class="profile-name">João Carabetta, Mestre em Matemática Aplicada pela FGV</span>
            </div>
            <div class="profile">
                <img class="profile-photo" src="%s"/>
                <span class="profile-name">Luiz Felipe Costa, Graduado em Sistemas de Informação pela UNIFEI</span>
            </div>
        </div>
        <div class="collaborator-container">
            <h1 class="primary-span">Com colaboração de:</h1>
            <span>Fátima Marinho, Doutora em Epidemiologia e Medicina Preventiva pela USP e professora da Faculdade de Medicina da Universidade de Minas Gerais</span>
            <span>Sarah Barros Leal, Médica e Mestranda em Saúde Global na University College London</span>
            <span>H. F. Barbosa, Mestre em Relações Internacionais pela Universidade da Califórnia, San Diego</span>
            <span>Teresa Soter, mestranda em Sociologia na Oxford University</span>
        </div>
    </div>
''' % (logo, ana, diego, fernanda, saru, carabetta, luiz), unsafe_allow_html=True)
