import streamlit as st
import plots
import pages.data_analysis as da
import loader
import utils


@st.cache(suppress_st_warning=True)
def get_data(config):

    dfs = {
        place: loader.read_data(
            "br",
            config,
            endpoint=config["br"]["api"]["endpoints"]["farolcovid"][place],
        )
        .replace({"medio": "médio", "insatisfatorio": "insatisfatório"})
        .pipe(utils.fix_dates)
        for place in ["city", "health_region", "state"]
    }

    places_ids = loader.read_data("br", config, "br/places/ids")
    return dfs, places_ids


def main(user_input, indicators, data, config, session_state):

    st.write(
        f"""
        <div class="base-wrapper distanciamento-titlebox">
            <div class="distanciamento-titleboxtext">
                <div class="distanciamento-title">ONDA COVID (PROV)</div>
                <div class="distanciamento-titlecaption">
                Veja no gráfico como está seu estado na curva de contágio do novo coronavírus.<br>
                Você também pode selecionar o seu estado e município no menu abaixo e comparar ele com outros municípios do mesmo estado.
                </div>
                <div class="distanciamento-titlecity"></div>
            </div>
            <img src="https://i.imgur.com/6rCXt22.png" class="distanciamento-titleimage">
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        # br_cases = loader.read_data(
        # "br",
        # loader.config,
        # endpoint=config["br"]["api"]["endpoints"]["analysis"]["cases"],
        # )
        # da.prepare_heatmap(
        # br_cases, place_type="state_id",
        # )
        pass
    except Exception as e:
        st.write(str(e))
    st.write(
        """
        <div class="base-wrapper">
            <span class="section-header primary-span">ONDA MORTES DIÁRIAS POR MUNICÍPIO</span>
            <br><br>
            <span class="section-header primary-span">SELECIONE SEU ESTADO E MUNICÍPIO PARA PROSSEGUIR</span>
        </div>""",
        unsafe_allow_html=True,
    )
    dfs, places_ids = get_data(loader.config)
    state_name = st.selectbox("Estado ", utils.filter_place(dfs, "state"))
    city_name = st.selectbox(
        "Município ",
        utils.filter_place(
            dfs,
            "city",
            state_name=user_input["state_name"],
            health_region_name=user_input["health_region_name"],
        ),
    )
    st.write(
        """
        <div class="base-wrapper">
            <span class="section-header primary-span">Você quer ver os número de mortes our mortes por casos?</span>
        </div>""",
        unsafe_allow_html=True,
    )
    deaths_or_cases = st.selectbox(
        "Mortes ou Mortes por Casos?", ["Mortes", "Mortes por casos"]
    )
    # COUNTRY HEATMAP
    # prepare_heatmap(
    # loader.read_data(
    # "br", loader.config, endpoint=config["br"]["api"]["endpoints"]["analysis"]["owid"]
    # ),
    # place_type="country_pt",
    # )
