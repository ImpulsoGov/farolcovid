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

DO_IT_BY_RANGE = True


def chunks(l, n):
    """
    Yields n sequential chunks from l. Used for our sector splitting protocol
    """
    d, r = divmod(len(l), n)
    for i in range(n):
        si = (d + 1) * (i if i < r else r) + d * (0 if i < r else i - r)
        yield l[si : si + (d + 1 if i < r else d)]


def chunk_indexes(size, n):
    """
    Similar to the one above except it gives us splitting indexes
    """
    last = 0
    while n > 1:
        new_index = last + math.ceil(size / n)
        yield new_index
        size = size - math.ceil(size / n)
        last = new_index
        n = n - 1


def range_separators_indexes(values, n):
    # Values must be ordered from lowest to highest
    separations = [
        (((values[-1] - values[0]) / (n)) * (order + 1)) + values[0]
        for order in range(n - 1)
    ]
    # print(separations)
    return [
        bisect.bisect_right(values, separationvalue) for separationvalue in separations
    ]


def chunks_by_range(target_list, key, n):
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


def convert_money(money):
    """ Can be used later to make money look like whatever we want, but a of
        now just adding the decimal separator should be enough
    """
    return f"{int(money):,}".replace(",", ".")


def gen_sorted_sectors(sectors_data, slider_value, by_range=True):
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
            "opened_tables": [False, False, False, False],
            "opened_detailed_view": False,
        }
    score_groups, economic_data = get_score_groups(config, session_state)
    # gen_header()
    gen_intro()
    gen_illustrative_plot(score_groups, session_state)
    gen_slider(session_state)
    gen_detailed_vision(economic_data, session_state)
    gen_sector_tables(session_state, score_groups, default_size=5)


def get_score_groups(config, session_state):
    """ Takes our data and splits it into 4 sectors for use by our diagram generator """
    uf_num = utils.get_place_id_by_names(session_state.state)
    CNAE_sectors = loader.read_data(
        "br", config, config["br"]["safereopen"]["cnae_sectors"]
    )
    CNAE_sectors = dict(zip(CNAE_sectors.cnae, CNAE_sectors.activity))
    economic_data = loader.read_data(
        "br", config, config["br"]["safereopen"]["economic_data"]
    )
    economic_data = economic_data.loc[economic_data["state_num_id"] == uf_num]
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
                <div class="section-header primary-span">VEJA OS SETORES MAIS SEGUROS PARA REABRIR</div>
                <div class="ambassador-question"><b>Se o seu município ou estado se encontra em ordem e com risco <span style="color:#02B529;">BAIXO</span>, você já pode começar a pensar um plano de reabertura.</b> Nós compilamos aqui dados econômicos do seu estado para lhe ajudar a planejar quais setores devem ser reabertos.</div>
        </div>""",
        unsafe_allow_html=True,
    )


def gen_illustrative_plot(sectors_data, session_state):
    """ Generates our illustrative sector diagram """
    if session_state.city == "Todos":
        section_title = session_state.state.upper() + " (ESTADO)"
    else:
        section_title = session_state.city.upper()
    text = f"""
    <div class="saude-sector-basic-plot-area">
        <div class="saude-veja-title" style="text-align:left;">SAUDE EM ORDEM | {section_title}</div>
        <div class="saude-sector-basic-plot-disc">
            Os indicadores utilizados para o Saúde em Ordem são o tamanho da Contribuição Econômica e o Nível de Segurança do setor. <b>Quanto mais seguro de infecções o setor for e mais volumoso na produção do estado, mais vale a pena pensar em reabri-lo.</b>
        </div>
        <div class="saude-sector-basic-plot-title">
            Top 5 Setores por grupo de custo-benefício
        </div>
        <div class="saude-segurança-eixo-label">Segurança Sanitária</div>
        <div class="saude-plot-axis">"""
    names_in_order = ["d", "c", "b", "a"]
    for index, sector_dict in enumerate(sectors_data):
        text += gen_sector_plot_card(names_in_order[index], sector_dict, size_sectors=5)
    text += """
            <div class="saude-vertical-arrow-full">
                <div class="saude-arrow-up-pos">
                    <i class="saude-arrow up"></i>
                </div>
                <div class="saude-vertical-line"></div>
            </div>
            <div class="saude-horizontal-arrow-full">
                <div class="saude-horizontal-line"></div>
                <div class="saude-arrow-right-pos">
                    <i class="saude-arrow right"></i>
                </div>
            </div>
            <div class="saude-economia-eixo-label">Contribuição Econômica</div>
        </div>
    </div>"""
    st.write(text, unsafe_allow_html=True)


def gen_sector_plot_card(sector_name, sector_data, size_sectors=5):
    """ Generates One specific card from the sector diagram  """
    titles = {"a": "Grupo A ✅", "b": "Grupo B 🙌", "c": "Grupo C ‼", "d": "Grupo D ⚠"}
    top_n_sectors = sector_data[-size_sectors::]
    # The last 5 are the best
    item_list = "<br>".join(["- " + i["activity_name"] for i in top_n_sectors])
    average_wage = int(
        sum([float(i["total_wage_bill"]) for i in top_n_sectors]) / size_sectors
    )
    num_people = sum([int(i["n_employee"]) for i in top_n_sectors])
    text = f"""
    <div class="saude-sector-{sector_name}-frame">
        <div class="saude-plot-group-title">{titles[sector_name]}</div>
        <div class="saude-plot-group-sectors-list">
            {item_list}
        </div>
        <div class="saude-plot-group-massa-salarial-label">Massa Salarial média:</div>
        <div class="saude-plot-group-massa-salarial-value">R$ {convert_money(average_wage)}</div>
        <div class="saude-plot-group-separator-line"></div>
        <div class="saude-plot-group-pessoas-label">Número de pessoas: </div>
        <div class="saude-plot-group-pessoas-value">{num_people}</div>
    </div>"""
    return text


def gen_slider(session_state):
    """ Generates the weight slider we see after the initial sector diagram and saves it to session_state"""
    st.write(
        """
        <div class="base-wrapper">
            <div class="saude-slider-wrapper">
                <span class="section-header primary-span">ESCOLHA O PESO PARA A SEGURANÇA SANITÁRIA</span><p>
                <span class="ambassador-question" style="width:80%;max-width:1000px;"><b>O peso padrão da simulação atribui 70% para Segurança Sanitária e 30% para Contribuição Econômica,</b> seguindo decisão do RS, principal inspiração para a ferramenta. 
                <br>Este parâmetro pode ser alterado abaixo; entre em contato conosco para mais detalhes.</span><p>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    session_state.saude_ordem_data["slider_value"] = st.slider(
        "Selecione o valor abaixo", 70, 100, step=10
    )
    st.write(
        f"""
        <div class="base-wrapper">
            <div class="saude-slider-value-display">Valor selecionado (Segurança): {session_state.saude_ordem_data["slider_value"]}% </div>
            <div class="saude-slider-value-display">Valor selecionado (Economia): {100 - session_state.saude_ordem_data["slider_value"]}% </div>
        </div>""",
        unsafe_allow_html=True,
    )


def gen_detailed_vision(economic_data, session_state):
    """ Uses session_state to decided wheter to hide or show the plot """
    if st.button(
        "Visão Detalhada"
    ):  # If the button is clicked just alternate the opened flag and plot it
        session_state.saude_ordem_data[
            "opened_detailed_view"
        ] = not session_state.saude_ordem_data["opened_detailed_view"]
        if session_state.saude_ordem_data["opened_detailed_view"] is True:
            display_detailed_plot(economic_data, session_state)
    else:  # If the button is not clicked plot it as well but do not alter the flag
        if session_state.saude_ordem_data["opened_detailed_view"] is True:
            display_detailed_plot(economic_data, session_state)


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
    st.plotly_chart(fig, use_container_width=False)


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
        font=dict(family="Oswald", size=18, color="#000000"),
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


def gen_sector_tables(session_state, score_groups, default_size=5):
    """
    Major function that will generate all the tables from all the sectors.
    Uses session_state to decided if the table is open or closed
    """
    text = ""
    titles = ["D", "C", "B", "A"]
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


def gen_single_table(session_state, score_groups, data_index, n=5):
    """ Generates an entire table fro one sector given the data we have and the index of such sector from D to A """
    text = ""  # Our HTML will be stored here
    # Constants
    titles = ["Grupo D ⚠", "Grupo C ‼", "Grupo B 🙌", "Grupo A ✅"]
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
    working_data = list(reversed(score_groups[data_index][-n:]))
    proportion = (
        str((n + 1) * 5) + "vw"
    )  # The height of our table so we can draw the lines
    total_workers = sum([sec_data["n_employee"] for sec_data in working_data])
    total_wages = sum([sec_data["total_wage_bill"] for sec_data in working_data])
    text += f"""<div class="saude-table">
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
            <div class="saude-table-field te3">{total_workers}</div>
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
            <div class="saude-table-field tf3">{sector_data["n_employee"]}</div>
            <div class="saude-table-field tf4">R$ {convert_money(sector_data["total_wage_bill"])}</div>
            <div class="saude-table-field tf5">{"%0.2f"%sector_data["score"]}</div>
        </div>"""

