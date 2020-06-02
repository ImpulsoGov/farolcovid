import sys
import os

sys.path.append("..")
sys.path.append("../src")
import src.utils as utils
import src.loader as loader

# Plotting
import plotly
import plotly.graph_objs as go
import pandas as pd

# Setting cufflinks
import textwrap
import cufflinks as cf

cf.go_offline()
cf.set_config_file(offline=False, world_readable=True)

# Centering and fixing title
def iplottitle(title, width=40):
    return "<br>".join(textwrap.wrap(title, width))


# Adding custom colorscales (to add one: themes/custom_colorscales.yaml)\n",
import yaml


analysis_path = os.path.join(os.path.dirname(__file__), "../../analysis/themes/")
config_path = os.path.join(os.path.dirname(__file__), "../../src/configs/")
custom_colorscales = yaml.load(
    open(os.path.join(analysis_path, "custom_colorscales.yaml"), "r"),
    Loader=yaml.FullLoader,
)
config = yaml.load(
    open(os.path.join(config_path, "config.yaml"), "r"), Loader=yaml.FullLoader
)
cf.colors._custom_scales["qual"].update(custom_colorscales)
cf.colors.reset_scales()

# Setting cuffilinks template (use it with .iplot(theme='custom')
cf.themes.THEMES["custom"] = yaml.load(
    open(os.path.join(analysis_path, "cufflinks_template.yaml"), "r"),
    Loader=yaml.FullLoader,
)


pallete = ["#0097A7", "#17A700", "#F2C94C", "#FF5F6B"]
if os.getenv("IS_LOCAL") == "TRUE":
    api_url = config["br"]["api"]["local"]
else:
    api_url = config["br"]["api"]["external"]
if os.getenv("INLOCO_CITIES_ROUTE") and os.getenv("INLOCO_STATES_ROUTE"):
    api_cities_complement = os.getenv("INLOCO_CITIES_ROUTE")
    api_states_complement = os.getenv("INLOCO_STATES_ROUTE")
else:
    secrets = yaml.load(
        open("../src/configs/secrets.yaml", "r"), Loader=yaml.FullLoader
    )
    api_cities_complement = secrets["inloco"]["cities"]["route"]
    api_states_complement = secrets["inloco"]["states"]["route"]
cities_url = api_url + api_cities_complement
states_url = api_url + api_states_complement


import numpy as np


def plot_heatmap(df, x, y, z, title, colorscale="oranges"):

    return df.pivot(columns=y, index=x, values=z).iplot(
        kind="heatmap", theme="custom", colorscale=colorscale, title=title
    )


def plot_rt(t, title=""):
    # TODO: put dicts in config
    rt_classification = {
        "Risco médio: Acima desta linha, cada pessoa infectam em média entre outras 1.0-1.2": {
            "threshold": 1,
            "color": "rgba(132,217,217,1)",
            "fill": None,
            "width": 3,
        },
        "Risco alto: Acima desta linha, cada pessoa infectam em média mais de 1.2 outras": {
            "threshold": 1.2,
            "color": "rgba(242,185,80,1)",
            "fill": None,
            "width": 3,
        },
    }

    ic_layout = {
        "Rt_high_95": {
            "fill": "tonexty",
            "showlegend": False,
            "name": None,
            "layout": {"color": "#E5E5E5", "width": 2},
        },
        "Rt_low_95": {
            "fill": "tonexty",
            "showlegend": True,
            "name": "Intervalo de confiança - 95%",
            "layout": {"color": "#E5E5E5", "width": 2},
        },
        "Rt_most_likely": {
            "fill": None,
            "showlegend": True,
            "name": "Valor médio <b>(atual=%0.2f)" % (t["Rt_most_likely"].iloc[-1]),
            "layout": {"color": "rgba(63, 61, 87, 0.8)", "width": 3},
        },
    }

    fig = go.Figure()

    # Intervalos de confianca
    for bound in ic_layout.keys():

        fig.add_scattergl(
            x=t["last_updated"],
            y=t[bound],
            line=ic_layout[bound]["layout"],
            fill=ic_layout[bound]["fill"],
            mode="lines",
            showlegend=ic_layout[bound]["showlegend"],
            name=ic_layout[bound]["name"],
        )

    # Areas de risco
    for bound in rt_classification.keys():

        fig.add_trace(
            go.Scatter(
                x=t["last_updated"],
                y=[rt_classification[bound]["threshold"] for i in t["last_updated"]],
                line={
                    "color": rt_classification[bound]["color"],
                    "width": rt_classification[bound]["width"],
                    "dash": "dash",
                },  # 0
                fill=rt_classification[bound]["fill"],
                name=bound,
                showlegend=[False if bound == "zero" else True][0],
            )
        )

    fig.layout.yaxis.rangemode = "tozero"
    fig.layout.yaxis.range = [0, 5]

    fig.update_layout(template="plotly_white", title=title)
    return fig


def plot_rt_bars(df, title, place_type="state"):

    df["color"] = np.where(
        df["Rt_most_likely"] > 1.2,
        "rgba(242,185,80,1)",
        np.where(df["Rt_most_likely"] > 1, "rgba(132,217,217,1)", "#0A96A6"),
    )

    fig = go.Figure(
        go.Bar(
            x=df[place_type],
            y=df["Rt_most_likely"],
            marker_color=df["color"],
            error_y=dict(
                type="data",
                symmetric=False,
                array=df["Rt_most_likely"] - df["Rt_low_95"],
                arrayminus=df["Rt_most_likely"] - df["Rt_low_95"],
            ),
        )
    )

    fig.add_shape(
        # Line Horizontal
        type="line",
        x0=-1,
        x1=len(df[place_type]),
        y0=1,
        y1=1,
        line=dict(color="#E5E5E5", width=2, dash="dash",),
    )

    fig.update_layout({"template": "plotly_white", "title": title})

    return fig


def plot_rt_wrapper(place_id):
    if place_id <= 100:
        pre_data = loader.read_data(
            "br", config, config["br"]["api"]["endpoints"]["rt_states"]
        )
        state_str_id = utils.get_state_str_id_by_id(place_id)
        final_data = pre_data.loc[pre_data["state"] == state_str_id]
    else:
        pre_data = loader.read_data(
            "br", config, config["br"]["api"]["endpoints"]["rt_cities"]
        )
        final_data = pre_data.loc[pre_data["city_id"] == place_id]
    fig = plot_rt(final_data)
    fig.update_layout(xaxis=dict(tickformat="%d/%m"))
    fig.update_layout(margin=dict(l=20, r=20, b=10, t=20, pad=4))
    fig.update_yaxes(automargin=True)
    return fig


####Social distancing indices


def genColor(value):
    critical = 0.50
    bad = 0.70
    if value <= critical:
        return pallete[3]
    elif value <= bad:
        return pallete[2]
    else:
        return pallete[1]


def generateFigsStates(states, clean_df, decoration=False):
    fig = go.Figure()
    buttons_list = [
        dict(
            label="Todos",
            method="update",
            args=[
                {"visible": [True for i in range(len(states))]},
                {
                    "title": "Distanciamento social para os estados selecionados",
                    "annotations": [],
                },
            ],
        )
    ]
    # Add traces
    for a, state_name in enumerate(states):
        xValues = clean_df.columns
        yValues = clean_df.query('state_name == "%s"' % state_name).values[0]
        if len(states) == 1:
            my_line_scheme = dict()
            my_line_scheme["color"] = genColor(yValues[-1])
            fig.add_trace(
                go.Scatter(
                    x=translate_dates(xValues),
                    y=yValues,
                    name=state_name,
                    line=my_line_scheme,
                )
            )
        else:
            fig.add_trace(
                go.Scatter(x=translate_dates(xValues), y=yValues, name=state_name,)
            )
        buttons_list.append(
            dict(
                label=state_name,
                method="update",
                args=[
                    {"visible": [i == a for i in range(len(states))]},
                    {
                        "title": "Distanciamento social para %s" % state_name,
                        "annotations": [],
                    },
                ],
            ),
        )
    if decoration:
        fig.update_layout(updatemenus=[dict(active=0, buttons=buttons_list,)])
    return fig


def generateFigsCities(city_states_pairs, df, decoration=False):
    fig = go.Figure()
    buttons_list = [
        dict(
            label="Todos",
            method="update",
            args=[
                {"visible": [True for i in range(len(city_states_pairs))]},
                {
                    "title": "Distanciamento social para as cidades selecionados",
                    "annotations": [],
                },
            ],
        )
    ]
    # Add traces
    for a, pair in enumerate(city_states_pairs):
        city_name, state_name = pair
        clean_df = df.query('state_name == "%s"' % state_name).query(
            'city_name == "%s"' % city_name
        )
        if len(city_states_pairs) == 1:
            my_line_scheme = dict()
            my_line_scheme["color"] = genColor(clean_df["isolated"][-1])
            fig.add_trace(
                go.Scatter(
                    x=translate_dates(clean_df["dt"]),
                    y=clean_df["isolated"],
                    name=city_name,
                    line=my_line_scheme,
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=translate_dates(clean_df["dt"]),
                    y=clean_df["isolated"],
                    name=city_name,
                )
            )
        buttons_list.append(
            dict(
                label=city_name,
                method="update",
                args=[
                    {"visible": [i == a for i in range(len(city_states_pairs))]},
                    {
                        "title": "Distanciamento social %s" % city_name,
                        "annotations": [],
                    },
                ],
            ),
        )
    if decoration:
        fig.update_layout(updatemenus=[dict(active=0, buttons=buttons_list,)])
    fig.update_layout(template="plotly_white")
    return fig


def gen_social_dist_plots(in_args, in_height=700, set_height=False):
    if type(in_args[0]) == type([]):
        is_city = True
    else:
        is_city = False
    social_dist_plot = None
    if is_city:
        if gen_social_dist_plots.cities_df is None:  # As to only load once
            gen_social_dist_plots.cities_df = pd.read_csv(cities_url, index_col=0)
        social_dist_df = gen_social_dist_plots.cities_df
        social_dist_plot = generateFigsCities(in_args, social_dist_df)
    else:  # IS STATE
        if gen_social_dist_plots.states_df is None:  # Too to only load once
            gen_social_dist_plots.states_df = pd.read_csv(states_url, index_col=0)
        social_dist_df = gen_social_dist_plots.states_df
        my_clean_df = (
            social_dist_df.reset_index()
            .pivot(index="state_name", columns="dt", values="isolated")
            .fillna(0)
            .dropna(how="all")
        )
        social_dist_plot = generateFigsStates(in_args, my_clean_df)
    social_dist_plot.update_layout(xaxis=dict(tickformat="%d/%m"))
    social_dist_plot.update_layout(yaxis=dict(tickformat=",.0%"))
    social_dist_plot.update_layout(template="plotly_white")
    social_dist_plot.update_layout(margin=dict(l=30, r=10, b=10, t=20, pad=4))
    if set_height:
        social_dist_plot.update_layout(height=in_height)
    return social_dist_plot


def translate_dates(df, simple=True, lang_frame="pt_BR.utf8"):
    if simple:
        return df
    else:
        import locale

        locale.setlocale(locale.LC_ALL, lang_frame)
        newdate = pd.to_datetime(df)
        newdate = [d.strftime("%d %b %y") for d in newdate]
        return newdate


gen_social_dist_plots.cities_df = None
gen_social_dist_plots.states_df = None


def gen_social_dist_plots_placeid(place_id, height=700):
    names = utils.get_place_names_by_id(place_id)
    if type(names) == type("sampletext"):  # IS STATE
        return gen_social_dist_plots([names], height)
    else:  # IS CITY
        return gen_social_dist_plots([names[::-1]], height)
