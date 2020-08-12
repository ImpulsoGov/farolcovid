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


def gen_banners():
    st.write(
        """
    <div class="base-wrapper flex flex-column" style="background-color:#F02C2E">
        <div class="white-span header p1" style="font-size:30px;">
        Acre está a 5 dias em crescimento da média móvel de mortes.<br>
        O pico de mortes até agora foi de 432 mortes  em 03/08/2020.
        </div>
    </div>
    <div class="base-wrapper flex flex-column" style="background-color:#0090A7">
        <div class="white-span header p1" style="font-size:30px;">
        Seu município está a 10 dias em queda da média móvel de mortes.<br>
        Seu pico de mortes foi de 53 mortes em 25/06/2020.
        </div>
    </div>""",
        unsafe_allow_html=True,
    )


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
        # load data
        br_cases = loader.read_data(
            "br",
            loader.config,
            endpoint=config["br"]["api"]["endpoints"]["analysis"]["cases"],
        )
        my_dict = utils.Dictionary()
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
            dfs, "city", state_name=state_name, health_region_name="Todos"
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
    print("Checking")
    if city_name != "Todos":  # the user selected something
        gen_banners()
        uf = my_dict.get_state_alphabetical_id_by_name(state_name)
        print(uf)
        da.prepare_heatmap(
            br_cases, place_type="city_name", group=uf, your_city=city_name
        )
    # COUNTRY HEATMAP
    # prepare_heatmap(
    # loader.read_data(
    # "br", loader.config, endpoint=config["br"]["api"]["endpoints"]["analysis"]["owid"]
    # ),
    # place_type="country_pt",
    # )
