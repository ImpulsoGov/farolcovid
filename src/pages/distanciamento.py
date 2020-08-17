import streamlit as st
import plots


def main(user_input, indicators, data, config, session_state):

    st.write(
        f"""
        <div class="base-wrapper distanciamento-titlebox">
            <div class="distanciamento-titleboxtext">
                <div class="distanciamento-title">DISTANCIAMENTO SOCIAL</div>
                <div class="distanciamento-titlecaption">Explore o cumprimento de medidas de segurança sanitária na sua cidade.</div>
                <div class="distanciamento-titlecity"></div>
            </div>
            <img src="https://i.imgur.com/VkG1NLL.png" class="distanciamento-titleimage">
        </div>
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
        fig = plots.gen_social_dist_plots_state_session_wrapper(session_state)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.write(
            """<div class="base-wrapper"><b>Seu município ou estado não possui mais de 30 dias de dados, ou não possui o índice calculado pela inloco.</b>""",
            unsafe_allow_html=True,
        )
