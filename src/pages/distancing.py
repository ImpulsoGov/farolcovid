import streamlit as st
import plots
import utils

def gen_alert():
        st.write(
                f"""
                <div class="distancing-cards">
                        <div class="distancing-alert distancing-card-bg">
                                <div class="distancing-output-wrapper">
                                        <div class="distancing-output-row">
                                                <span style="font-weight: bold; word-wrap: no-wrap; font-size: 28px;">
                                                        Atenção: Dados descontinuados
                                                </span>  
                                        </div> 
                                        <span style="font-weight: lighter; font-size: 20px;">
                                                A fonte de dados da taxa de isolamento social foi descontinuada em 31/03/201. 
                                                <br>Estamos trabalhando em novas fontes de dados para continuar levando informações úteis até você!
                                        </span>
                                </div>
                                <img src="https://i.imgur.com/z5e70pg.png" class="distancing-alert-image">
                        </div>
                </div>""",
                unsafe_allow_html=True,
        )

def gen_cards(distancing_data):

    st.write(
        f"""<div class="distancing-cards">
                <div class="distancing-container distancing-card-bg">
                        <div class="distancing-output-wrapper">
                                <div class="distancing-output-row">
                                        <span class="distancing-output-row-prediction-value">
                                                {round(distancing_data[-1]*100, 0)}%
                                        </span>  
                                </div> 
                                <span class="distancing-output-row-prediction-label">
                                        das pessoas em média ficaram em casa nos últimos 7 dias.
                                </span>
                        </div>
                        <img src="https://i.imgur.com/CywR6Rs.png" class="distancing-output-image">
                </div>
                <div class="distancing-card-separator"></div>
                <div class="distancing-container distancing-card-bg">
                        <div class="distancing-output-wrapper">
                                <div class="distancing-output-row">
                                        <span class="distancing-output-row-prediction-value">
                                                {round(distancing_data[-8]*100, 0)}%
                                        </span>  
                                </div> 
                                <span class="distancing-output-row-prediction-label">
                                        das pessoas em média ficaram em casa entre 14 e 7 dias atrás.
                                </span>
                        </div>
                        <img src="https://i.imgur.com/CywR6Rs.png" class="distancing-output-image">
                </div>
            </div>""",
        unsafe_allow_html=True,
    )


def main(user_input, indicators, data, config, session_state):

    utils.genHeroSection(
        title1="DISTANCIAMENTO", 
        title2="SOCIAL",
        subtitle="Explore o cumprimento de medidas de segurança sanitária na sua cidade.", 
        logo="https://i.imgur.com/VkG1NLL.png",
        header=False
    )

    st.write(
        f"""
        <div class="base-wrapper">
                <span class="section-header primary-span">TAXA DE ISOLAMENTO SOCIAL EM {user_input["locality"]}</span>
                <br><br>
                <div class="distanciamento-headercaption">
                Percentual de smartphones que não deixou o local de residência, em cada dia, calculado pela inloco. 
                Para mais informações, <a target="_blank" style="color:black;" href="https://mapabrasileirodacovid.inloco.com.br/pt/">veja aqui</a>.
                </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        fig, final_y = plots.gen_social_dist_plots_state_session_wrapper(session_state)
        # gen_cards(final_y)
        gen_alert()
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.write(
            """<div class="base-wrapper"><b>Seu município ou estado não possui mais de 30 dias de dados, ou não possui o índice calculado pela inloco.</b>""",
            unsafe_allow_html=True,
        )
        st.write(e)
