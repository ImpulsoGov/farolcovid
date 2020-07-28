import streamlit as st
import amplitude
import utils
import loader
import bisect
import random
import plotly as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import math
import os
import pandas as pd
import io
import requests

DO_IT_BY_RANGE = (
    True  # DEFINES IF WE SHOULD RUN OUR CODE BY METHOD 1 (TRUE) OR 2 (FALSE)
)
# METHOD 1 IS DIVIDING THE RANGE OF VALUES IN 4 EQUAL PARTS IN SCORE VALUE
# METHOD 2 IS DIVIDING OUR ACTIVITIES IN GROUPS OF ROUGHLY EQUAL SIZE AFTER RANKING THEM

# INITIAL DATA PROCESSING
def get_score_groups(config, session_state):
    """ Takes our data and splits it into 4 sectors for use by our diagram generator """
    uf_num = utils.get_place_id_by_names(session_state.state)
    CNAE_sectors = loader.read_data(
        "br", config, config["br"]["api"]["endpoints"]["safereopen"]["cnae_sectors"]
    )
    CNAE_sectors = dict(zip(CNAE_sectors.cnae, CNAE_sectors.activity))
    economic_data = loader.read_data(
        "br", config, config["br"]["api"]["endpoints"]["safereopen"]["economic_data"]
    )
    economic_data = economic_data.loc[economic_data["state_num_id"] == uf_num]
    # REMOVE LINE BELOW ASAP
    # economic_data = economic_data[economic_data["cnae"] != 44]
    economic_data["activity_name"] = economic_data.apply(
        lambda row: CNAE_sectors[row["cnae"]], axis=1
    )
    return (
        gen_sorted_sectors(
            economic_data,
            session_state.saude_ordem_data["slider_value"],
            DO_IT_BY_RANGE,
        ),
        economic_data,
    )


def gen_sorted_sectors(sectors_data, slider_value, by_range=True):
    """ Cleans the data and separates in those 4 groups for later use by the table generator """
    column_name = "cd_id_" + "%02d" % (int(slider_value / 10))
    kept_columns = [
        "cnae",
        "n_employee",
        "security_index",
        "total_wage_bill",
        "sector",
        column_name,
        "activity_name",
    ]
    data_for_objects = sectors_data[kept_columns]
    data_for_objects = data_for_objects.rename(columns={column_name: "score"})
    sectors = data_for_objects.to_dict(orient="records")
    sectors.sort(key=lambda x: x["score"])
    if by_range:
        sector_groups = chunks_by_range(sectors, "score", 4)
    else:
        sector_groups = list(chunks(sectors, 4))
    return sector_groups


def chunks_by_range(target_list, key, n):
    """ Divides a list of dictionaries by a given key through the method 1 group division method"""
    # For use in a list of dicts and to sort them by a specific key
    split_indexes = range_separators_indexes(
        [element[key] for element in target_list], n
    )
    chunks = []
    last = 0
    for i in range(n - 1):
        chunks.append(target_list[last : split_indexes[i]])
        last = split_indexes[i]
    chunks.append(target_list[last::])
    return chunks


def range_separators_indexes(values, n):
    """ Given a list of values separates them into n chunks by the method 1 and returns the index of cutting"""
    # Values must be ordered from lowest to highest
    separations = [
        (((values[-1] - values[0]) / (n)) * (order + 1)) + values[0]
        for order in range(n - 1)
    ]
    return [
        bisect.bisect_right(values, separationvalue) for separationvalue in separations
    ]


def chunks(l, n):
    """
    Yields n sequential chunks of l. Used for our sector splitting protocol in method2
    """
    # Values should be sorted
    d, r = divmod(len(l), n)
    for i in range(n):
        si = (d + 1) * (i if i < r else r) + d * (0 if i < r else i - r)
        yield l[si : si + (d + 1 if i < r else d)]


# SEÇÃO DE INTRODUÇÃO
def gen_header():
    st.write(
        """
        <div class="base-wrapper">
            <div class="hero-wrapper">
                    <div class="hero-container">
                            <div class="hero-container-content">
                                    <span class="hero-container-product primary-span">SAÚDE EM<br>ORDEM</span>
                                    <span class="hero-container-subtitle primary-span">Contribuindo para uma retomada inteligente</span>
                            </div>
                    </div>   
                    <img class="hero-container-image" src="https://i.imgur.com/FiNi6fy.png">
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def gen_intro():
    st.write(
        """
        <div class="base-wrapper">
                <div class="section-header primary-span">VEJA OS SETORES MAIS SEGUROS PARA REABRIR</div><br>
                <div class="ambassador-question"><b>Se o seu município ou estado se encontra em ordem e com risco <span style="color:#02B529;">BAIXO</span>, você já pode começar a pensar um plano de reabertura.</b> Nós compilamos aqui dados econômicos do seu estado para retomada segura de atividades econômicas, ordenadas a com critérios objetivos.</div>
        </div>""",
        unsafe_allow_html=True,
    )


def gen_illustrative_plot(sectors_data, session_state):
    """ Generates our illustrative sector diagram Version saude v2 """
    text = f""" 
    <div class="saude-alert-banner saude-blue-bg mb" style="margin-bottom: 0px;">
        <div class="base-wrapper flex flex-column" style="margin-top: 0px;">
            <div class="flex flex-row flex-space-between flex-align-items-center">
                <span class="white-span header p1"> Ordem de Retomada dos Setores | {session_state.state + " (Estado)"}</span>
            </div>
            <span class="white-span p3">Sugerimos uma retomada <b>em fases</b>, a começar pelos <b>setores mais seguros</b> e com <b>maior contribuição econômica.</b></span>
            <div class="flex flex-row flex-m-column">"""
    names_in_order = list(reversed(["d", "c", "b", "a"]))
    for index, sector_dict in enumerate(reversed(sectors_data)):
        text += gen_sector_plot_card(names_in_order[index], sector_dict, size_sectors=3)
    text += """
            </div>
        </div>
        <div class="saude-white-banner-pt0"></div>
    </div>
    <div class="saude-white-banner-pt2">
        <div class="base-wrapper flex flex-column" style="margin-top: 0px;">
            <div class="saude-banner-arrow-body"></div>
            <div class="saude-banner-arrow-tip">
                <i class="saude-arrow right"></i>
            </div>
            <div class="saude-banner-button high-security">Seguro</div>
            <div class="saude-banner-button high-economy">Forte</div>
            <div class="saude-banner-desc">
                <b>Segurança Sanitária</b> mede o risco de exposição à Covid-19 dos trabalhadores de cada atividade econômica.
            </div>
            <div class="saude-banner-desc">
                <b>Contribuição Econômica</b> é medida da massa salarial dos setores formais e informais de cada atividade econômica.<br>(Veja mais em Metodologia)
            </div>
            <div class="saude-banner-button low-security">Inseguro</div>
            <div class="saude-banner-button low-economy">Fraca</div>
        </div>
    </div>"""
    st.write(text, unsafe_allow_html=True)


# SEÇÃO PLOT SAUDE EM ORDEM
# def gen_illustrative_plot(sectors_data, session_state):
#     """ Generates our illustrative sector diagram """
#     text = f"""
#     <div class="saude-sector-basic-plot-area">
#         <div class="saude-veja-title" style="text-align:left;">SAUDE EM ORDEM | {session_state.state.upper() + " (ESTADO)"}</div>
#         <div class="saude-sector-basic-plot-disc">
#             Os dois principais indicadores utilizados são a Importância Econômica (medida pela soma dos salários pagos) e o Nível de Segurança Sanitária do setor. A ideia é que devemos iniciar a reabertura pelos setores de mais seguros do ponto de vista da saúde e de maior importância econômica.
#         </div>
#         <div class="saude-sector-basic-plot-title">
#             Top 5 Setores por grupo de custo-benefício
#         </div>
#         <div class="saude-segurança-eixo-label">Segurança Sanitária</div>
#         <div class="saude-plot-axis">"""
#     names_in_order = ["d", "c", "b", "a"]
#     for index, sector_dict in enumerate(sectors_data):
#         text += gen_sector_plot_card(names_in_order[index], sector_dict, size_sectors=5)
#     text += """
#             <div class="saude-vertical-arrow-full">
#                 <div class="saude-arrow-up-pos">
#                     <i class="saude-arrow up"></i>
#                 </div>
#                 <div class="saude-vertical-line"></div>
#             </div>
#             <div class="saude-horizontal-arrow-full">
#                 <div class="saude-horizontal-line"></div>
#                 <div class="saude-arrow-right-pos">
#                     <i class="saude-arrow right"></i>
#                 </div>
#             </div>
#             <div class="saude-economia-eixo-label">Contribuição Econômica</div>
#         </div>
#     </div>"""
#     st.write(text, unsafe_allow_html=True)


def gen_sector_plot_card(sector_name, sector_data, size_sectors=5):
    """ Generates One specific card from the sector diagram version saude v2"""
    titles = {"a": "Fase 1 ✅", "b": "Fase 2 🙌", "c": "Fase 3 ‼", "d": "Fase 4 ⚠"}
    redirect_id_conversion = {"a": 3, "b": 2, "c": 1, "d": 0}
    redirect_id = "saude-table-" + str(redirect_id_conversion[sector_name])
    top_n_sectors = sector_data[-size_sectors::]
    size_rest = max(0, len(sector_data) - size_sectors)
    continuation_text = f"<b>+ {size_rest} setor{['','es'][int(size_rest >= 2)]} do grupo<br> <a href='#{redirect_id}' style='color:#00003d;'>(clique aqui para acessar)</a></b>"
    # The last 5 are the best
    item_list = "<br>".join(["- " + i["activity_name"] for i in top_n_sectors])
    average_wage = int(
        sum([float(i["total_wage_bill"]) for i in top_n_sectors]) / size_sectors
    )
    num_people = sum([int(i["n_employee"]) for i in top_n_sectors])
    text = f"""
    <div class="saude-indicator-card flex flex-column mr" style="z-index:1;display:inline-block;position:relative;">
        <span class="saude-card-header-v2">{titles[sector_name]}</span>
        <span class="saude-card-list-v2">
            {item_list}
        </span>
        <div class="flex flex-row flex-justify-space-between mt" style="width:250px;">
        </div>
        <div class="saude-card-redirect">
            {continuation_text}
        </div>
        <div class="saude-card-display-text-v2 sdcardtext-left">
                <span class="lighter">Massa Salarial Média:<br></span>
                <span class="bold">R$ {convert_money(average_wage)}</span>
        </div>
        <div class="saude-card-display-text-v2 sdcardtext-right">
                <span class="lighter">Número de Trabalhadores:<br></span>
                <span class="bold">{convert_money(num_people)}</span>
        </div>
    </div>"""
    return text


# def gen_sector_plot_card(sector_name, sector_data, size_sectors=5):
#     """ Generates One specific card from the sector diagram  """
#     titles = {"a": "Grupo A ✅", "b": "Grupo B 🙌", "c": "Grupo C ‼", "d": "Grupo D ⚠"}
#     top_n_sectors = sector_data[-size_sectors::]
#     # The last 5 are the best
#     item_list = "<br>".join(["- " + i["activity_name"] for i in top_n_sectors])
#     average_wage = int(
#         sum([float(i["total_wage_bill"]) for i in top_n_sectors]) / size_sectors
#     )
#     num_people = sum([int(i["n_employee"]) for i in top_n_sectors])
#     text = f"""
#     <div class="saude-sector-{sector_name}-frame">
#         <div class="saude-plot-group-title">{titles[sector_name]}</div>
#         <div class="saude-plot-group-sectors-list">
#             {item_list}
#         </div>
#         <div class="saude-plot-group-massa-salarial-label">Massa Salarial média:</div>
#         <div class="saude-plot-group-massa-salarial-value">R$ {convert_money(average_wage)}</div>
#         <div class="saude-plot-group-separator-line"></div>
#         <div class="saude-plot-group-pessoas-label">Número de trabalhadores: </div>
#         <div class="saude-plot-group-pessoas-value">{convert_money(num_people)}</div>
#     </div>"""
#     return text


def convert_money(money):
    """ Can be used later to make money look like whatever we want, but a of
        now just adding the decimal separator should be enough
    """
    return f"{int(money):,}".replace(",", ".")


# SEÇÃO DE SELEÇÃO DE PESOS
# def gen_slider(session_state):
#     """ Generates the weight slider we see after the initial sector diagram and saves it to session_state"""
#     st.write(
#         """
#         <div class="base-wrapper">
#             <div class="saude-slider-wrapper">
#                 <span class="section-header primary-span">ESCOLHA O PESO PARA A SEGURANÇA SANITÁRIA</span><p>
#                 <span class="ambassador-question" style="width:80%;max-width:1000px;"><br><b>O peso padrão da simulação atribui 70% para Segurança Sanitária e 30% para Contribuição Econômica,</b> seguindo decisão do RS, principal inspiração para a ferramenta.
#                 Este parâmetro pode ser alterado abaixo; entre em contato conosco para mais detalhes.</span><p>
#             </div>
#         </div>""",
#         unsafe_allow_html=True,
#     )
#     session_state.saude_ordem_data["slider_value"] = st.slider(
#         "Selecione o peso para Segurança Sanitária abaixo:", 70, 100, step=10
#     )
#     amplitude.gen_user(utils.get_server_session()).safe_log_event(
#         "chose saude_slider_value",
#         session_state,
#         event_args={"slider_value": session_state.saude_ordem_data["slider_value"]},
#     )
#     st.write(
#         f"""
#         <div class="base-wrapper">
#             <div class="saude-slider-value-display"><b>Peso selecionado (Segurança): {session_state.saude_ordem_data["slider_value"]}%</b>&nbsp;&nbsp;|  &nbsp;Peso restante para Economia: {100 - session_state.saude_ordem_data["slider_value"]}%</div>
#         </div>""",
#         unsafe_allow_html=True,
#     )


def gen_slider(session_state):
    """ Generates the weight slider we see after the initial sector diagram and saves it to session_state"""
    radio_label = "Caso queira, altere abaixo o peso dado à Segurança Sanitária:"
    # Code in order to horizontalize the radio buttons
    radio_horizontalization_html = utils.get_radio_horizontalization_html(radio_label)
    st.write(
        f"""
        <div class="base-wrapper">
            <div class="saude-slider-wrapper">
                <span class="section-header primary-span">ESCOLHA O PESO PARA A SEGURANÇA SANITÁRIA</span><p>
                <span class="ambassador-question" style="width:80%;max-width:1000px;"><br><b>O peso determina em qual fase classificamos cada setor econômico.</b> O peso padrão utilizado é de <b>70% para Segurança Sanitária e 30% para Contribuição Econômica</b> - a partir desse valor você pode atribuir mais peso para Segurança (mais detalhes na Metodologia).
                Este parâmetro pode ser alterado abaixo; entre em contato conosco para mais detalhes.</span><p>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    session_state.saude_ordem_data["slider_value"] = st.radio(
        radio_label, [70, 80, 90, 100]
    )
    st.write(
        f"""
        <div class="base-wrapper">
            {radio_horizontalization_html}
            <div class="saude-slider-value-display"><b>Peso selecionado (Segurança): {session_state.saude_ordem_data["slider_value"]}%</b>&nbsp;&nbsp;|  &nbsp;Peso restante para Economia: {100 - session_state.saude_ordem_data["slider_value"]}%</div>
        </div>""",
        unsafe_allow_html=True,
    )
    amplitude.gen_user(utils.get_server_session()).safe_log_event(
        "chose saude_slider_value",
        session_state,
        event_args={"slider_value": session_state.saude_ordem_data["slider_value"]},
    )
    # st.write(radio_horizontalization_html,unsafe_allow_html=True)


# SEÇÃO DE DETALHES (INCLUDES THE DETAILED PLOT AND THE FULL DATA DOWNLOAD BUTTON)
def gen_detailed_vision(economic_data, session_state, config):
    """ Uses session_state to decided wheter to hide or show the plot """
    st.write(
        f"""
        <div class="base-wrapper">
            <span style="width: 80%; max-width: 1000px; margin-top: -50px;">
            <i><b>Clique em "Visão Detalhada" para ver o gráfico completo com todas as informações.</b></i>
            </span><br>""",
        unsafe_allow_html=True,
    )
    if st.button(
        "Visão Detalhada"
    ):  # If the button is clicked just alternate the opened flag and plot it
        amplitude.gen_user(utils.get_server_session()).safe_log_event(  # Logs the event
            "picked saude_em_ordem_detailed_view",
            session_state,
            event_args={"state": session_state.state, "city": session_state.city,},
        )
        session_state.saude_ordem_data[
            "opened_detailed_view"
        ] = not session_state.saude_ordem_data["opened_detailed_view"]
        if session_state.saude_ordem_data["opened_detailed_view"] is True:
            display_detailed_plot(economic_data, session_state)
    else:  # If the button is not clicked plot it as well but do not alter the flag
        if session_state.saude_ordem_data["opened_detailed_view"] is True:
            display_detailed_plot(economic_data, session_state)
    detailed_button_style = """border: 1px solid var(--main-white);box-sizing: border-box;border-radius: 15px; width: auto;padding: 0.5em;text-transform: uppercase;font-family: var(--main-header-font-family);color: var(--main-white);background-color: var(--main-primary);font-weight: bold;text-align: center;text-decoration: none;font-size: 18px;animation-name: fadein;animation-duration: 3s;margin-top: 1em;"""
    utils.stylizeButton("Visão Detalhada", detailed_button_style, session_state)


def get_state_clean_data_url(session_state, config):
    """Reads which state are we using and returns the correct file download url for it"""
    state_num_id = utils.get_place_id_by_names(session_state.state)
    index_file_url = f'https://drive.google.com/uc?export=download&id={config["br"]["drive_ids"]["br_states_clean_data_index"]}'
    state_data_index = pd.read_csv(
        io.BytesIO(requests.get(index_file_url).content),
        encoding="utf8",
        # index_col="state_num_id",
    )
    uf_file_id = state_data_index.loc[state_data_index["state_num_id"] == state_num_id][
        "file_id"
    ].values[0]
    return f"https://drive.google.com/uc?export=download&id={uf_file_id}"


def display_detailed_plot(economic_data, session_state):
    fig = plot_cnae(
        economic_data, session_state.saude_ordem_data["slider_value"], DO_IT_BY_RANGE,
    )
    st.write(
        """
        <div class="base-wrapper">
            <span class="ambassador-question" style="width: 80%; max-width: 1000px;">
            <b>Passe o mouse sobre cada bolinha para ver todos os detalhes daquela atividade econômica.</b><br>
            Se você está no celular é só clicar na bolinha. Além disso talvez seja necessário rolar a tela para ver o gráfico inteiro.
            </span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_cnae(economic_data, slider_value, by_range=True):
    """ Will generate the colored plot seen in the detailed view section """
    fig = go.Figure()
    column_name = "cd_id_" + "%02d" % (int(slider_value / 10))

    numpy_econ_version = economic_data[
        ["activity_name", column_name, "total_wage_bill"]
    ].to_numpy()
    fig.add_trace(
        go.Scatter(
            x=economic_data["total_wage_bill"],
            y=economic_data["security_index"],
            name="Atividade Econômica",
            mode="markers",
            customdata=numpy_econ_version,
            text=economic_data["sector"],
            hovertemplate="<b>%{customdata[0]}</b><br><br>"
            + "Pontuação: %{customdata[1]}<br>"
            + "índice de Segurança: %{y:,.2f}<br>"
            + "Massa Salarial: R$%{customdata[2]:.0}<br>"
            + "Setor: %{text}"
            + "<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_type="log",
        xaxis_title="Contribuição Econômica",
        yaxis_title="Índice de Segurança",
        font=dict(family="Oswald", size=12, color="#000000"),
    )
    wage_range = [
        int(np.amin(economic_data["total_wage_bill"].values)),
        int(np.amax(economic_data["total_wage_bill"].values)),
    ]
    safety_range = [
        int(np.amin(economic_data["security_index"].values)),
        int(np.amax(economic_data["security_index"].values)),
    ]
    sorted_score = sorted(economic_data[column_name])
    if by_range:
        score_group_limits = (
            [0]
            + [
                sorted_score[index]
                for index in range_separators_indexes(sorted_score, 4)
            ]
            + [200]
        )
    else:
        score_group_limits = (
            [0] + [sorted_score[i] for i in chunk_indexes(len(sorted_score), 4)] + [200]
        )
    gen_isoscore_lines(fig, score_group_limits, wage_range, slider_value / 100)
    fig.update_layout(  # The 0.85 and 1.15 factors are to add some margin to the plot
        xaxis=dict(
            range=[
                math.log(wage_range[0] * 0.85, 10),
                math.log(wage_range[1] * 1.15, 10),
            ]
        ),
        yaxis=dict(
            range=[safety_range[0] * 0.95, safety_range[1] * 1.05]
        ),  # Same reason for 0.95 and 1.05
        height=540,
        width=900,
    )
    return fig


def chunk_indexes(size, n):
    """
    Similar to the chunks() method but it gives us the splitting indexes
    """
    last = 0
    while n > 1:
        new_index = last + math.ceil(size / n)
        yield new_index
        size = size - math.ceil(size / n)
        last = new_index
        n = n - 1


def gen_isoscore_lines(fig, score_parts, wage_range, weight):
    """
    Goes through each value defining a iso-score line and draws it on the plot with a colored area.
    Must also include the minimum limit and the maximum limit in score_parts if we want 4 shaded areas we include 5 lines
    and the plot will be colored between line 1 and 2, 2 and 3, 3 and 4 and 4 and 5 totalling 4 parts
    
    """
    # x is wage_range
    x_data = np.logspace(
        np.log(wage_range[0] * 0.85), np.log(wage_range[1] * 1.15), 50, base=np.e
    )
    names = ["Nan", "Grupo D", "Grupo C", "Grupo B", "Grupo A"]
    area_colors = [
        "#FFFFFF",
        "rgba(252,40,3,0.2)",
        "rgba(252,190,3,0.2)",
        "rgba(227,252,3,0.2)",
        "rgba(3,252,23,0.2)",
    ]
    legend_visibility = [False, True, True, True, True]
    for index, score in enumerate(score_parts):
        y_data = np.power(
            np.divide(score, np.power(np.log(x_data), 1 - weight)), 1 / weight
        )
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=y_data,
                fill="tonexty",
                mode="none",
                name=names[index],
                line_color=area_colors[index],
                fillcolor=area_colors[index],
                visible=True,
                showlegend=legend_visibility[index],
            )
        )


# SEÇÃO DE TABELAS DE SETORES
def gen_sector_tables(
    session_state, score_groups, config, default_size=5, download=False
):
    """
    Major function that will generate all the tables from all the sectors.
    Uses session_state to decided if the table is open or closed
    """
    text = ""
    titles = ["D", "C", "B", "A"]
    if download:
        download_text = f"""
                <a href="{get_state_clean_data_url(session_state,config)}" download="dados_estado.csv" class="btn-ambassador">
                    Baixar dados completos do estado
                </a>"""
    else:
        # download_text = f"""
        # <a href="" download="dados_estado.csv" class="btn-ambassador disabled">
        # Baixar dados (Desativado)
        # </a>"""
        download_text = " "
    st.write(
        f"""
        <div class="base-wrapper">
            <span class="section-header primary-span">TABELAS DE CONTRIBUIÇÃO DOS SETORES</span><p><br>
            <span class="ambassador-question">Abaixo você pode conferir todos os setores de cada grupo de apresentados, ordenados pelo <b>índice de priorização de reabertura Saúde em Ordem.</b></span>
            <div><br>
            <div class="saude-download-clean-data-button-div">{download_text}
            </div>""",
        unsafe_allow_html=True,
    )

    for table_index in reversed(range(4)):
        # We create it all under a button but the table will be shown either way
        # The button is merely to alternate the state between open and closed
        if st.button("Mostrar/Ocultar mais do Grupo " + titles[table_index]):
            session_state.saude_ordem_data["opened_tables"][
                table_index
            ] = not session_state.saude_ordem_data["opened_tables"][table_index]
            gen_single_table(session_state, score_groups, table_index, default_size)
        else:
            gen_single_table(session_state, score_groups, table_index, default_size)
        table_button_style = """border: 1px solid var(--main-white);box-sizing: border-box;border-radius: 15px; width: auto;padding: 0.5em;text-transform: uppercase;font-family: var(--main-header-font-family);color: var(--main-white);background-color: var(--main-primary);font-weight: bold;text-align: center;text-decoration: none;font-size: 18px;animation-name: fadein;animation-duration: 3s;margin-top: 1em;"""
        utils.stylizeButton(
            "Mostrar/Ocultar mais do Grupo " + titles[table_index],
            table_button_style,
            session_state,
        )


def gen_single_table(session_state, score_groups, data_index, n=5):
    """ Generates an entire table for one sector given the data we have and the index of such sector from D to A """
    text = ""  # Our HTML will be stored here
    # Constants
    titles = ["Fase 4 ⚠", "Fase 3 ‼", "Fase 2 🙌", "Fase 1 ✅"]
    safety_statuses = [
        [["Inseguro", "#FF5F6B"], ["Fraco", "#FF5F6B"]],
        [["Inseguro", "#FF5F6B"], ["Forte", "#02BC17"]],
        [["Seguro", "#02BC17"], ["Fraco", "#FF5F6B"]],
        [["Seguro", "#02BC17"], ["Forte", "#02BC17"]],
    ]
    safety_display = safety_statuses[data_index]
    # If the user chose to open the table we extende the amount of rows to the full size of the group
    if session_state.saude_ordem_data["opened_tables"][data_index] is True:
        n = len(score_groups[data_index])
    table_id = "saude-table-" + str(data_index)
    working_data = list(reversed(score_groups[data_index][-n:]))
    proportion = (
        str((n + 1) * 5) + "vw"
    )  # The height of our table so we can draw the lines
    total_workers = sum([sec_data["n_employee"] for sec_data in working_data])
    total_wages = sum([sec_data["total_wage_bill"] for sec_data in working_data])
    text += f"""<div class="saude-table" id="{table_id}">
        <div class="saude-table-title-box">
            <div class="saude-table-title">{titles[data_index]}</div>
            <div class="saude-table-title-security-label">Segurança Sanitária</div>
            <div class="saude-table-title-economy-label">Contribuição Econômica</div>
            <div class="saude-table-title-button tbsecurity" style="background: {safety_display[0][1]};">{safety_display[0][0]}</div>
            <div class="saude-table-title-button tbeconomy" style="background: {safety_display[1][1]};">{safety_display[1][0]}</div>
        </div>
        <div class="saude-table-head-box">
            <div class="saude-table-line tl1" style="height: {proportion};"></div>
            <div class="saude-table-line tl2" style="height: {proportion};"></div>
            <div class="saude-table-line tl3" style="height: {proportion};"></div>
            <div class="saude-table-line tl4" style="height: {proportion};"></div>
            <div class="saude-table-field tt1">Nome do setor</div>
            <div class="saude-table-field tt2">Índice de Segurança Sanitária</div>
            <div class="saude-table-field tt3">N°de Trabalhadores</div>
            <div class="saude-table-field tt4">Massa Salarial</div>
            <div class="saude-table-field tt5">índice Saúde em Ordem</div>
        </div>"""
    for index, sector_data in enumerate(working_data):
        text += gen_sector_table_row(sector_data, index)
    text += f"""<div class="saude-table-total-box">
            <div class="saude-table-field te1">Total</div>
            <div class="saude-table-field te3">{convert_money(total_workers)}</div>
            <div class="saude-table-field te4">R$ {convert_money(total_wages)}</div>
        </div>
        <div class="saude-table-endspacer">
        </div>
    </div>"""
    st.write(text, unsafe_allow_html=True)
    return text


def gen_sector_table_row(sector_data, row_index):
    """ Generates a row of a table given the necessary information coming from a sector data row """
    return f"""<div class="saude-table-row {["tlblue","tlwhite"][row_index % 2]}">
            <div class="saude-table-field tf1">{sector_data["activity_name"]}</div>
            <div class="saude-table-field tf2">{"%0.2f"%sector_data["security_index"]}</div>
            <div class="saude-table-field tf3">{convert_money(sector_data["n_employee"])}</div>
            <div class="saude-table-field tf4">R$ {convert_money(sector_data["total_wage_bill"])}</div>
            <div class="saude-table-field tf5">{"%0.2f"%sector_data["score"]}</div>
        </div>"""


# SEÇÃO DE PROTOCOLOS
def gen_protocols_section():
    st.write(
        """
    <div class="base-wrapper">
        <span class="section-header primary-span">
            DIRETRIZES PARA A ELABORAÇÃO DE PROTOCOLOS DE REABERTURA
        </span><br><br>
        <span class="ambassador-question"><br>
            <b>Eliminação</b> – contempla a transferência para o trabalho remoto, ou seja, elimina riscos ocupacionais. Mesmo que a residência do funcionário não tenha a infraestrutura necessária, a transferência de computadores ou melhorias de acesso à internet são medidas possíveis e de baixo custo, com fácil implementação.
            <br><br>
            <b>Substituição</b>  – consiste em substituir riscos onde eles são inevitáveis, por um de menor magnitude. Vale assinalar os times que são ou não essenciais no trabalho presencial e segmentar a força de trabalho, mantendo somente o mínimo necessário de operação presencial e reduzindo o contato próximo entre times diferentes. 
            <br><br>
            <b>Controles de engenharia</b>  – fala de aspectos estruturais do ambiente de trabalho. No caso do coronavírus, podem ser citados como exemplos o controle de ventilação e purificação de ar, reduzindo o risco da fonte e não no nível individual. São fatores altamente ligados ao contexto, seja da atividade, seja do espaço físico onde ocorrem.
            <br><br>
            <b>Controles administrativos</b>  – consiste nos controles de fluxo e quantidade de pessoas no ambiente de trabalho (de-densificação do ambiente) e sobre protocolos e regras a serem seguidos, como periodicidade e métodos de limpeza, montagem de plantões e/ou escala, organização de filas para elevadores e uso de áreas comuns, proibição de reuniões presenciais, reorganização das estações de trabalho para aumentar distância entre pessoas para 2m ou mais, etc. 
            <br><br>
            <b>EPIs</b>  – definição de qual é o EPI necessário para cada função, levando em conta o risco de cada atividade e também o ambiente. Trabalhos mais fisicamente exaustivos geralmente requerem troca de EPI mais constante ou especificações diferentes de outras atividades. É preciso garantir o correto uso desses equipamentos. No caso de máscaras simples, convém que a empresa distribua para os funcionários, garantindo certas especificações. Por exemplo, 
            <br><br>
            <i>OBSERVAÇÃO:</i> quanto mais alto na hierarquia, menos capacidade de supervisão e execução é exigida do empregador. Por isso, a primeira pergunta é sempre “quem pode ficar em casa?”. Treinar supervisores, garantir alinhamento institucional e cumprimento impecável de protocolos, etc. tem um custo e são medidas de difícil controle.
            <br><br>
            <b>Materiais de Referência:</b><br>
            <a href="http://www.pe.sesi.org.br/Documents/Guia_SESI_de_prevencao_2805_2%20(1).pdf" style="color: blue;">[1] Guia SESI de prevenção da Covid-19 nas empresas (atualizado em 26/5/2020).</a><br>
            <a href="https://www.osha.gov/shpguidelines/hazard-prevention.html" style="color: blue;">[2] Recommended Practices for Safety and Health Programs - United States Department of Labor</a></br>
            <br><br>
        </span>
        <figure>
            <img class="saude-reopening-protocol-img-1" alt="Fonte: HIERARCHY OF CONTROLS -The National Institute for Occupational Safety and Health (NIOSH); disponível em https://www.cdc.gov/niosh/topics/hierarchy/default.html" src="https://i.imgur.com/St9fAMB.png"><br>
            <figcaption><i>Fonte: HIERARCHY OF CONTROLS -The National Institute for Occupational Safety and Health (NIOSH); disponível em https://www.cdc.gov/niosh/topics/hierarchy/default.html</i></figcaption>
        </figure>
    </div>""",
        unsafe_allow_html=True,
    )


# MAIN
def main(user_input, indicators, data, config, session_state):
    st.write(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        unsafe_allow_html=True,
    )
    if (
        session_state.saude_ordem_data == None
    ):  # If not loaded, load the data we are going to use in the user database
        session_state.saude_ordem_data = {
            "slider_value": 70,
            "opened_tables": [True, True, True, True],
            "opened_detailed_view": False,
        }
    score_groups, economic_data = get_score_groups(config, session_state)
    # gen_header()
    gen_intro()
    gen_illustrative_plot(score_groups, session_state)
    gen_slider(session_state)
    gen_detailed_vision(economic_data, session_state, config)
    gen_sector_tables(session_state, score_groups, config, default_size=5)
    gen_protocols_section()
