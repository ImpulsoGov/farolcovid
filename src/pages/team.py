import streamlit as st
import utils
from models import  Logo

def main():

    utils.localCSS("style.css")

    # Time
    time = {
        "ana": {
            "foto": "https://media-exp1.licdn.com/dms/image/C4E03AQGdLO2wZpvasA/profile-displayphoto-shrink_200_200/0?e=1591833600&v=beta&t=BsnUsaEI-eLrn_oxLf7cEyXKGx2_7OBJZ9suUrRev_8",
            "bio": "<b>Ana Paula Pellegrino</b><br><i>Coordenação</i><br> Doutoranda em Ciência Política da Georgetown University"
        },

        "diego": {
            "foto": "https://media-exp1.licdn.com/dms/image/C4D03AQGc03RUyqn7rQ/profile-displayphoto-shrink_200_200/0?e=1591833600&v=beta&t=VQeYTDAIkwXnCBISvvBne6GO-hOnHUu70s35OwcH4RE",
            "bio": "<b>Diego Oliveira</b><br><i>Voluntário Desenvolvimento BE</i><br>Mestre em Física Aplicada pela Unicamp"
        },

        "fernanda": {
            "foto": "https://media-exp1.licdn.com/dms/image/C4D03AQFveYuReCqBVg/profile-displayphoto-shrink_200_200/0?e=1593043200&v=beta&t=14iMvOQdBESRi2OmsqmAdDBWVh0xdb_77Tw_dUycAto",
            "bio": "<b>Fernanda Scovino</b><br><i>Coordenação e Desenvolvimento</i><br> Graduada em Matemática Aplicada pela FGV"
        }, 

        "francisco": {
            "foto": "https://media-exp1.licdn.com/dms/image/C5103AQEgizhRREvpXw/profile-displayphoto-shrink_400_400/0?e=1595462400&v=beta&t=4tbQssvl-9TbFcnYCs2m7KpC_Y9wGry8lHKUt2XNk2o",
            "bio": "<b>Francisco Nogueira</b><br><i>Voluntário Desenvolvimento BE</i><br>Graduando em Engenharia Civil na Universidade Federal do Ceará"
        },

        "gabriel_saru": {
                "foto": "https://media-exp1.licdn.com/dms/image/C5603AQHB6rggvacwQw/profile-displayphoto-shrink_200_200/0?e=1591833600&v=beta&t=jj_atUnkJJm8SDKB1GQBF5n8bM-8dUKsTJE1Nsph3qE",
                "bio":  "<b>Gabriel Saruhashi</b><br><i>Voluntário Desenvolvimento FE</i><br>Graduando em Ciência da Computação e Psicologia na Yale University"
        },

        "joao_abreu": {
            "foto": "https://media-exp1.licdn.com/dms/image/C4E03AQF-9YgG5RDaMA/profile-displayphoto-shrink_400_400/0?e=1595462400&v=beta&t=DqvapZaWe1nRo9HgQS6bmZtX8U-j1DmvV2RbE37oY-4",
            "bio": "<b>João Abreu</b><br><i>Coordenação</i><br>Co-fundador da Impulso e Mestre em Desenvolvimento Internacional pela Universidade de Harvard"
        },

        "joao_carabetta": {
            "foto": "https://media-exp1.licdn.com/dms/image/C4D03AQF8rJe40DpQqA/profile-displayphoto-shrink_200_200/0?e=1591833600&v=beta&t=6smhmNk7Ppktq5cX4vxhD4x-A6mMTdZnIAEu5DlV18g",
            "bio": "<b>João Carabetta</b><br><i>Voluntário Desenvolvimento BE</i><br>Mestre em Matemática Aplicada pela FGV"
        },

        "luiz": {
            "foto": "https://www.gravatar.com/avatar/1617e0d1d8ac9ec461c5f215772f7552?s=200&d=mm&r=g",
            "bio": "<b>Luiz Felipe Costa</b><br><i>Voluntário Desenvolvimento BE</i><br>Graduado em Sistemas de Informação pela UNIFEI"
        },

        "paula": {
            "foto": "https://media-exp1.licdn.com/dms/image/C4D03AQG8RMTG5WMF3A/profile-displayphoto-shrink_800_800/0?e=1595462400&v=beta&t=1g8QyLGjF0NiGlhJeud0PKtdSIMnu9_RlpFiZNOa7tI",
            "bio": "<b>Paula Minardi Fonseca</b><br><i>Programa Embaixadores</i><br>Mestre em Administração Financeira pelo Insper"
        },

        "sarah": {
            "foto": "https://media-exp1.licdn.com/dms/image/C4D03AQGSIQDtT8mcFw/profile-displayphoto-shrink_400_400/0?e=1595462400&v=beta&t=AQdHfqJ9Ly3wxdYiHSBCePGldEnxOyHpp89TOS-A1K4",
            "bio": "<b>Sarah Leal</b><br><i>Programa Embaixadores</i><br>Médica no Hospital Israelita Albert Einstein"
        },
        
        "victor": {
            "foto": "https://media-exp1.licdn.com/dms/image/C4E03AQHCS8t2-1adVw/profile-displayphoto-shrink_800_800/0?e=1595462400&v=beta&t=ER4ycSCGwPHR1fT8I4AxiPS0JKl--QskB6ouFBaeOkY",
            "bio": "<b>Victor Cortez</b><br><i>Voluntário Desenvolvimento BE</i><br>Graduando em Engenharia Mecânica na Columbia University"
        }
    }

    colaboradores = {
        "<span><b>Fátima Marinho</b>: Doutora em Epidemiologia e Medicina Preventiva pela USP e professora da Faculdade de Medicina da Universidade de Minas Gerais</span>",
        "<span><b>H. F. Barbosa</b>: Mestre em Relações Internacionais pela Universidade da Califórnia, San Diego</span>",
        "<span><b>Teresa Soter</b>: Mestranda em Sociologia na Oxford University</span>"
    }


    def quem_somos(time):
        text = ""
        for nome, info in time.items():
            text += "<div class='profile'><img class='profile-photo' src='{}'/><br><span class='profile-name'>{}</span></div>".format(
                time[nome]["foto"], 
                time[nome]["bio"]
            )
    
        return text

    st.write(
        """
        <div class="base-wrapper">
            <a href="https://coronacidades.org/"><img class="coronacidades-logo" src="%s" width="300"/></a><br><br>
                <span>
                Coronacidades é uma plataforma feita para gestores públicos, que reúne
                ferramentas e informações chave para superar a COVID-19.<br>Além dos recursos online, 
                nosso time multidisciplinar está a postos para apoiar municípios e estados
                parceiros no planejamento e implementação de ações específicas nas áreas
                de saúde, assistência social, planejamento e economia. Entre em contato
                conosco.<br><br>
                <i>O CoronaCidades é uma iniciativa da Impulso, do Instituto Arapyau e do
                Instituto de Estudos de Políticas de Saúde (IEPS).</i>
                </span><br><br><br>
            <a href="https://www.impulsogov.com.br/"><img class="impulso-logo" src="%s" width="150"/></a><br><br>
                <span>
                O FarolCovid e SimulaCovid são desenvolvidos pela Impulso, uma
                organização não-governamental sem fins lucrativos cujo principal
                objetivo é criar capacidade analítica em governos. Fortalecemos o
                processo de coleta e análise de dados para auxiliar gestores públicos na
                tomada de decisão diária, visando aprimoramento contínuo de suas
                políticas.
                </span><br><br>
            <h1 class="primary-span">Quem Somos</h1>
                <div class="profiles-container">
                    %s
            </div>
            <div class="collaborator-container">
                <h1 class="primary-span">Com colaboração de:</h1>
                    %s
            </div>
        </div>
        """ % (Logo.CORONACIDADES.value, Logo.IMPULSO.value, quem_somos(time), "".join(colaboradores)), 
        unsafe_allow_html=True
    )


