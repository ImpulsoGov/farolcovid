import streamlit as st
import loader
import yaml
import plotly.graph_objs as go
from plotly.io import to_html
import plotly.io as pio
import numpy as np
import pandas as pd
import utils


def _get_rolling_amount(grp, time, data_col="last_updated", col_to_roll="deaths"):
    return grp.rolling(time, min_periods=1, on=data_col)[col_to_roll].mean()


def _df_to_plotly(df):
    return {"z": df.values.tolist(), "x": df.columns.tolist(), "y": df.index.tolist()}


def _generate_hovertext(df_to_plotly):

    hovertext = list()
    for yi, yy in enumerate(df_to_plotly["y"]):
        hovertext.append(list())
        for xi, xx in enumerate(df_to_plotly["x"]):
            hovertext[-1].append(
                "<b>{}<b><br>Data: {}<br>Percentual do máximo: {}".format(
                    yy, str(xx)[:10], round(df_to_plotly["z"][yi][xi], 2)
                )
            )

    return hovertext


def plot_heatmap(df, place_type, legend, min_deaths=0, title=None, group=None):

    if place_type == "state" or place_type == "city":
        col_date = "last_updated"
        col_deaths = "deaths"

    if place_type == "iso_code":
        col_date = "date"
        col_deaths = "total_deaths"

    pivot = (
        df.reset_index()
        .pivot(index=place_type, columns=col_date, values="rolling_deaths_new")
        .fillna(0)
        .apply(lambda x: x / x.max(), axis=1)
        .dropna(how="all")
    )

    # remove days with all states zero
    pivot = pivot.loc[:, (pivot != 0).any(axis=0)]

    # TODO: arrumar essa selecao e ordenacao dos locais
    place_max_deaths = (
        df.groupby(place_type)[[col_deaths]]
        .max()
        .reset_index()
        .sort_values(col_deaths)
        .iloc[-1][place_type]
    )

    # entender o que acontece aqui
    states_total_deaths = [
        df[df[place_type] == x][col_deaths].max() for x in pivot.index
    ]

    idy = np.argsort(states_total_deaths)
    idx = np.array(states_total_deaths, dtype=np.int32)[idy] > min_deaths

    states_total_deaths = np.array(states_total_deaths)

    data = _df_to_plotly(pivot.iloc[idy, :].loc[idx, :])
    trace1 = go.Heatmap(
        data,
        hoverinfo="text",
        hovertext=_generate_hovertext(data),
        colorscale="temps",
        showscale=False,
    )

    trace2 = go.Bar(
        x=states_total_deaths[idy][idx],
        y=pivot.iloc[idy, :].loc[idx, :].index,
        xaxis="x2",
        yaxis="y2",
        orientation="h",
    )

    d = [trace1, trace2]
    layout = go.Layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        # autosize= True,
        width=1200,
        height=700,
        margin={"l": 600, "t": 50},
        xaxis=dict(domain=[0, 0.8]),
        xaxis2=dict(domain=[0.85, 1]),
        yaxis=dict(tickmode="linear"),
        # yaxis2=dict(tickmode="linear", anchor="x2"),
    )

    legend = legend.format(
        place_max_deaths,
        states_total_deaths.max(),
        states_total_deaths.sum(),
        pivot.columns[-1],
    )

    fig = go.Figure(data=d, layout=layout)

    if place_type == "city":
        fontsize = 11
    else:
        fontsize = 12

    fig.add_annotation(
        dict(
            font=dict(color="black", size=fontsize),
            x=-1.1,
            y=1,
            showarrow=False,
            text=legend,
            xref="paper",
            yref="paper",
            align="left",
        )
    )

    # fig.add_annotation(
    #     dict(
    #         font=dict(color="black", size=14),
    #         x=-1.1,
    #         y=1,
    #         showarrow=False,
    #         text=legend,
    #         xref="paper",
    #         yref="paper",
    #         align="left",
    #     )
    # )

    st.plotly_chart(fig)


def _generate_pivot_table(df, place_type, mavg_days):

    df = (
        df[~df["deaths"].isnull()][[place_type, "last_updated", "deaths"]]
        .groupby([place_type, "last_updated"])["deaths"]
        .sum()
        .reset_index()
    )

    df["rolling_deaths_new"] = df.groupby(
        place_type, as_index=False, group_keys=False
    ).apply(lambda x: _get_rolling_amount(x, mavg_days))

    return df


def prepare_heatmap(df, place_type, min_deaths=0, group=None, mavg_days=5):

    if place_type == "city":
        df = _generate_pivot_table(df[df["state"] == group], place_type, mavg_days)

        legend = """
            O gráfico ao lado mostra a média do número de mortes<br>
            diárias dos últimos cinco dias em cada município com mais<br>
            de 10 mortes, desde a data da primeira morte reportada.<br>
            Para comparação, os números foram normalizados pelo <br>
            maior valor encontrado em cada município:<br>
            <b>quanto mais vermelho, mais próximo está o valor do<br>
            maior número de mortes por dia observado no município<br>
            até hoje</b>.
            <br><br>
            Os municípios estão ordenadas pelo número de mortos total, <br>
            ou seja, os município com mais mortes nominais. {}<br>
            é o município com o maior número de mortos, com: <i>{}</i>. <br>
            e o estado totaliza: <i>{}</i>.
            <br><br>

            <i>Última atualização: {}</i>
        """

    if place_type == "state":
        df = _generate_pivot_table(df, place_type, mavg_days)

        legend = """
            O gráfico ao lado mostra a média do número de mortes<br>
            diárias dos últimos cinco dias em cada UF, desde a data da<br>
            primeira morte reportada. Para comparação, os números foram<br>
            normalizados pelo maior valor encontrado em cada UF:<br>
            <b>quanto mais vermelho, mais próximo está o valor do<br>
            maior número de mortes por dia observado na UF até hoje</b>.
            <br><br>
            As UFs estão ordenadas pelo número de mortos total,<br>
            ou seja, os estados com mais mortes nominais. {}<br>
            é o estado com o maior número de mortos, com: <i>{}</i>. <br>
            e o Brasil totaliza: <i>{}</i>.
            <br><br>

            <i>Última atualização: {}</i>
        """

    if place_type == "iso_code":

        legend = """
            O gráfico ao lado mostra a média do número de mortes<br>
            diárias dos últimos cinco dias para cada país com mais<br>
            de 1000 mortes, desde a data da primeira morte reportada.<br>
            Para comparação, os números foram normalizados pelo maior<br>
            valor encontrado em cada país:<b> quanto mais vermelho,<br>
            mais próximo está o valor do maior número de mortes por<br>
            dia observado na UF até hoje</b>.
            <br><br>
            Os países estão ordenadas pelo número de mortos total,<br>
            ou seja, os países com mais mortes nominais. {}<br>
            é o país com o maior número de mortos, com: <i>{}</i>. <br>
            e o mundo totaliza: <i>{}</i>.
            <br><br>

            <i>Última atualização: {}</i>
        """
        # .format(
        #     min_deaths, states_total_deaths.max(), t.columns[-1]
        # )

    return plot_heatmap(
        df,
        place_type,
        min_deaths=min_deaths,
        legend=legend,
        # title ="Distribuição de novas mortes nas UFs (mavg = 5 days)",
    )


ufs = [
    "AC",
    "AL",
    "AM",
    "AP",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MG",
    "MS",
    "MT",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
]


def main():

    utils.localCSS("style.css")
    utils.localCSS("icons.css")

    config = yaml.load(open("configs/config.yaml", "r"), Loader=yaml.FullLoader)
    br_cases = loader.read_data(
        "br", config, endpoint=config["br"]["api"]["endpoints"]["analysis"]["cases"]
    )

    st.write(
        """
        <div class="base-wrapper">
                <span class="section-header primary-span">MORTES DIÁRIAS POR MUNICÍPIO</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_uf = st.selectbox("Selecione um estado para análise:", ufs)

    prepare_heatmap(
        br_cases, place_type="city", min_deaths=10, group=user_uf,
    )

    st.write(
        """
        <div class="base-wrapper">
                <span class="section-header primary-span">MORTES DIÁRIAS POR ESTADO</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prepare_heatmap(
        br_cases, place_type="state",
    )

    st.write(
        """
        <div class="base-wrapper">
                <span class="section-header primary-span">MORTES DIÁRIAS POR PAÍS</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prepare_heatmap(
        loader.read_data(
            "br", config, endpoint=config["br"]["api"]["endpoints"]["analysis"]["owid"]
        ),
        place_type="iso_code",
        min_deaths=1000,
    )


# st.write('Dados atualizados para 10 de maio. Os dados dos dias mais recentes são provisórios e podem ser revisados para cima à medida que testes adicionais são processados.')

if __name__ == "__main__":
    main()


# def plot_cities_deaths_heatmap(
#     t, state, place_type, min_deaths, title=None, colors="temps", save_img=False
# ):

#     t = t[t["state"] == state]
#     df_heatmap = (
#         t.reset_index()
#         .pivot(index=place_type, columns="last_updated", values="rolling_deaths_new")
#         .fillna(0)
#         .apply(lambda x: x / x.max(), axis=1)
#         .dropna(how="all")
#     )

#     # remove days with all states zero
#     df_heatmap = df_heatmap.loc[:, (df_heatmap != 0).any(axis=0)]

#     city_total_deaths = [t[t["city"] == x]["deaths"].max() for x in df_heatmap.index]
#     idy = np.argsort(city_total_deaths)
#     idx = np.array(city_total_deaths, dtype=np.int32)[idy] > min_deaths

#     # Remove the column '0' that only exist in some states
#     try:
#         trace1 = go.Heatmap(
#             _df_to_plotly(df_heatmap.iloc[idy, :].loc[idx, :].drop("0", axis=1)),
#             colorscale=colors,
#             showscale=False,
#         )
#     except:
#         trace1 = go.Heatmap(
#             _df_to_plotly(df_heatmap.iloc[idy, :].loc[idx, :]),
#             colorscale=colors,
#             showscale=False,
#         )

#     trace2 = go.Bar(
#         x=np.array(city_total_deaths)[idy][idx],
#         y=df_heatmap.iloc[idy, :].loc[idx, :].index,
#         xaxis="x2",
#         yaxis="y2",
#         orientation="h",
#     )
#     d = [trace1, trace2]
#     layout = go.Layout(
#         title=title,
#         plot_bgcolor="rgba(0,0,0,0)",
#         xaxis=dict(domain=[0, 0.7]),
#         xaxis2=dict(domain=[0.8, 1], showticklabels=True),
#         yaxis=dict(tickmode="linear"),
#         yaxis2=dict(tickmode="linear", anchor="x2"),
#     )

#     fig = go.Figure(data=d, layout=layout)
#     if save_img:
#         pio.write_image(
#             fig,
#             "data/output/Mortes_{}.jpeg".format(state),
#             format="jpeg",
#             width=1920,
#             height=1080,
#         )
#     fig.show()
