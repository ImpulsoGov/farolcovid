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
                "<b>{}</b><br>Data: {}<br>Percentual do máximo: {}".format(
                    yy, str(xx)[:10], round(df_to_plotly["z"][yi][xi], 2)
                )
            )

    legend = """
        O gráfico ao lado mostra a média do número de mortes<br>
        diárias dos últimos cinco dias em cada UF, desde a data da<br>
        primeira morte reportada. Para comparação, os números foram<br>
        normalizados pelo maior valor encontrado em cada UF:<br>
        <b>quanto mais vermelho, mais próximo está o valor do<br>
        maior número de mortes por dia observado na UF até hoje</b>.<br>
        <br>
        As UFs estão ordenadas pela data em que atingiram <br>
        metade do número máximo de mortes diário. Ou seja, a data<br>
        em que foi observado metade do maior número de mortes em <i>{}</i><br>
        é anterior à data das demais UFs.
        <br><br>
        Última atualização: {}
    """.format(df_heatmap['y'][-1], df_heatmap['x'][-1].replace(second=0, microsecond=0))

    fig.add_annotation(dict(font=dict(color="black",size=14),
                            x=-1.1,
                            y=1,
                            showarrow=False,
                            text=legend,
                            xref="paper",
                            yref="paper",
                            align='left'
                           ))

    st.plotly_chart(fig)

def _get_rolling_amount(grp, days):
    return grp.rolling(days, min_periods=1, on='last_updated')['deaths'].mean()

def prepare_heatmap(df, mavg_days=5):

    df_deaths = df[~df['deaths'].isnull()][['state', 'last_updated', 'deaths']]\
                                                .groupby(['state', 'last_updated'])['deaths']\
                                                .sum()\
                                                .reset_index()

    df_deaths['rolling_deaths_new'] = df_deaths.groupby('state', 
                                                    as_index=False, 
                                                    group_keys=False)\
                                           .apply(lambda x : _get_rolling_amount(x, mavg_days))

    return plot_deaths_heatmap2(df_deaths, 'state', title='Distribuição de novas mortes nas UFs (mavg = 5 days)')



def plot_heatmap(df, place_type, legend, title=None, group=None):

    if place_type == "state" or place_type == "city":
        col_date = "last_updated"
        col_deaths = "deaths"

    if place_type == "country_pt":
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

    # entender o que acontece aqui
    states_total_deaths = (
        df.groupby(place_type)[col_deaths]
        .max()
        .loc[pivot.index]
        .sort_values(ascending=False)[:30]
        .sort_values()
    )

    # Ordena por: 1. Dia do máximo, 2. Quantidade de Mortes
    sorted_index = (
        pivot.loc[states_total_deaths.index]
        .idxmax(axis=1)
        .to_frame()
        .merge(states_total_deaths.to_frame(), left_index=True, right_index=True)
        .sort_values(by=[0, col_deaths])
        .index
    )

    states_total_deaths = states_total_deaths.reindex(sorted_index)

    data = _df_to_plotly(pivot.loc[states_total_deaths.index])
    trace1 = go.Heatmap(
        data,
        hoverinfo="text",
        hovertext=_generate_hovertext(data),
        colorscale="temps",
        showscale=False,
    )

    fig = go.Figure(data=d, layout=layout)
    fig.add_annotation(dict(font=dict(color="black",size=14),
                            x=-1.1,
                            y=1,
                            showarrow=False,
                            text=legend,
                            xref="paper",
                            yref="paper",
                            align='left'
                           ))

    
    
    

    st.plotly_chart(fig)




def plot_cities_deaths_heatmap(t, state, place_type, col_time, min_deaths, title, colors='temps'):
    t = t.query(f'state =="{state}"')
    df_heatmap = var_through_time(t,place_type,col_time,'deaths',norm=True)

    city_total_deaths = [t[t['city'] ==x]['deaths'].max() for x in df_heatmap.index]
    idy = np.argsort(city_total_deaths)
    idx = np.array(city_total_deaths,dtype=np.int32)[idy] > min_deaths

    
    try:
        trace1 = go.Heatmap(_df_to_plotly(df_heatmap.iloc[idy,:].loc[idx,:].drop('0',axis=1)), 
                                        colorscale=colors,showscale=False)
    except:
        trace1 = go.Heatmap(_df_to_plotly(df_heatmap.iloc[idy,:].loc[idx,:]), 
                                        colorscale=colors,showscale=False)

    trace2 = go.Bar(x=np.array(city_total_deaths)[idy][idx],y=df_heatmap.iloc[idy,:].loc[idx,:].index,
                    xaxis="x2",yaxis="y2",orientation='h')
    d = [trace1,trace2]
    layout = go.Layout(title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            domain=[0, 0.7]
        ),
        xaxis2=dict(
            domain=[0.8, 1],
            showticklabels=True
        ),
        yaxis=dict(tickmode='linear'
        ),
        yaxis2=dict(tickmode='linear',anchor='x2'
        )
        
    )

    fig = go.Figure(data=d, layout=layout)

    legend = """


    """


    fig.add_annotation(dict(font=dict(color="black",size=14),
                            x=-1.1,
                            y=1,
                            showarrow=False,
                            text=legend,
                            xref="paper",
                            yref="paper",
                            align='left'
                           ))

    

    st.plotly_chart(fig)


def prepare_cities_heatmap(df,state, mavg_days=5):

    df_cities_deaths = df[~df['deaths'].isnull()][['state','city', 'last_updated', 'deaths']]\
                                                    .groupby(['state','city', 'last_updated'])['deaths']\
                                                    .sum()\
                                                    .reset_index()

    df_cities_deaths['rolling_deaths_new'] = df_cities_deaths.groupby('city', 
                                                        as_index=False, 
                                                        group_keys=False)\
                                               .apply(lambda x : get_rolling_amount(x,5, 'last_updated', 'deaths'))


    return  plot_cities_deaths_heatmap(df_cities_deaths,
                               state,
                               place_type='city',
                               col_time='last_updated',
                               min_deaths=70,
                               title = 'Distribuição de novas mortes municipal (mavg = 5 days)',
                               colors='temps')    

def prepare_countries_heatmap(df, mavg_days=5):

    df_deaths = df[~df['new_deaths'].isnull()][['iso_code', 'date','total_deaths', 'new_deaths']]\
                                                    .groupby(['iso_code', 'date','total_deaths'])['new_deaths']\
                                                    .sum()\
                                                    .reset_index()

    df_deaths['rolling_deaths_new'] = df_deaths.groupby('iso_code', 
                                                        as_index=False, 
                                                        group_keys=False)\
                                               .apply(get_rolling_amount)
    df_deaths = df_deaths[df_deaths['iso_code']!='OWID_WRL']
    return plot_deaths_heatmap2(df_deaths, 'iso_code', title='Distribuição de novas mortes Mundo (mavg = 5 days)')


def plot_countries_heatmap(t, place_type, min_deaths, title,save_img=False):
    
    df_heatmap = t.reset_index()\
                          .pivot(index=place_type, 
                                  columns='date', 
                                  values='rolling_deaths_new')\
                           .fillna(0)\
                           .apply(lambda x: x/x.max(), axis=1)\
                           .dropna(how='all')

    st.plotly_chart(fig, use_container_width=True)


def _generate_mvg_deaths(df, place_type, mavg_days):

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


def prepare_heatmap(df, place_type, group=None, mavg_days=5):

def var_through_time(t,place_type,col_time,var,norm=False):
    if norm:
        df_tt = t.reset_index()\
                              .pivot(index=place_type, 
                                      columns=col_time, 
                                      values=var)\
                               .fillna(0)\
                               .apply(lambda x: x/x.max(), axis=1)\
                               .dropna(how='all')
    else:
        df_tt = t.reset_index()\
                              .pivot(index=place_type, 
                                      columns=col_time, 
                                      values=var)\
                               .fillna(0)\
                               .dropna(how='all')
    # remove days with all states zero
    df_tt = df_tt.loc[:, (df_tt != 0).any(axis=0)]
    return df_tt


def data_slider(geodf, geojson, Z, cmap,txt, cbar_title, title,locmode='geojson-id'):
    data_slider = []
    
    dates = Z.columns
    ### Loop to create a list with all plots
    for date in dates:

        plot_data = dict(type = 'choropleth',
                    geojson=geojson,
                    locations =geodf.index.astype(str),
                    locationmode = locmode,
                    colorscale= cmap,
                    text= geodf[txt],
                    z=Z[date].astype(float),
                    zmin=0,zmax=Z.values.max(),
                    colorbar = {'title':cbar_title})


        data_slider.append(plot_data)


    ### create empty list for slider object:    
    steps = []
    for i in range(len(data_slider)):
        step = dict(method='restyle',
                    args=['visible', [False] * len(data_slider)],
                    label=dates[i]) # label to be displayed for each step (year)
        step['args'][1][i] = True
        steps.append(step)



    ##  I create the 'sliders' object from the 'steps' 

    sliders = [dict(active=0, pad={"t": 1}, steps=steps)]  

    layout = dict(title_text = title,
              geo = {'scope':'south america',
                    'fitbounds':"locations",
                     'visible':False},
              sliders=sliders)
    
    return data_slider, layout

def get_map(df, place_type, time_col,var, cmap, Title, cbar_title):
    
        
    df_bystate = df[~df['deaths'].isnull()][['state', 'last_updated','state_notification_rate','last_available_death_rate', 'deaths','new_deaths']]\
                                                    .groupby(['state', 'last_updated', 'state_notification_rate'])['deaths']\
                                                    .sum()\
                                                    .reset_index()

    df_bystate['rolling_deaths_new'] = df_bystate.groupby(['state','last_updated'], 
                                                        as_index=False, 
                                                        group_keys=False)\
                                            .apply(lambda x : get_rolling_amount(x,5, 'last_updated', 'deaths'))
        
    vtt = var_through_time(df_bystate,
                 place_type=place_type,
                 col_time=time_col,
                 var=var)
    
    dates = vtt.columns
    
    if place_type == 'state':
        year = 2018
        types = {
            'States': geobr.read_state(code_state='all', year=year)
        }



        df1 = types['States']
        df1 = df1.sort_values('abbrev_state').reset_index(drop=True)

        gdf = gpd.GeoDataFrame(df1[['abbrev_state','geometry']])
        jdf = json.loads(df1[['abbrev_state','geometry']].to_json())

        
        ds, layout = data_slider(geodf = gdf,
                     geojson = jdf,
                     Z = vtt[dates[-10:]],
                     cmap = cmap,
                     txt = 'abbrev_state',
                     cbar_title = cbar_title,
                     title = Title,
                     locmode='geojson-id')
        
        
    fig = dict(data = ds,layout = layout)
    st.plotly_chart(fig)


def main():
    refresh = df["data_last_refreshed"][0]

    if place_type == "city":
        df = df[df["state"] == group]

    if place_type == "city" or place_type == "state":
        df = _generate_mvg_deaths(df, place_type, mavg_days)
        col_date = "last_updated"
        col_deaths = "deaths"

    if place_type == "country_pt":
        col_date = "date"
        col_deaths = "total_deaths"

    place_max_deaths = (
        df.groupby(place_type)[[col_deaths]].max().reset_index().sort_values(col_deaths)
    )

    if place_type == "city":

        legend = """
        <div class="base-wrapper">
            O gráfico abaixo mostra a média do número de mortes
            diárias dos últimos cinco dias para os 30 municípios com mais mortes, desde a data da primeira morte reportada.
            Para comparação, os números foram normalizados pelo 
            maior valor encontrado em cada município:
            <b>quanto mais vermelho, mais próximo está o valor do
            maior número de mortes por dia observado no município
            até hoje</b>.
            <br><br>
            Os municípios estão ordenadas pelo dia que atingiu o máximo de mortes, 
            ou seja, municípios no pico de mortes aparecerão no topo. {}
            é o município com o maior número de mortos, com: <i>{}</i>
            e o estado totaliza: <i>{}</i>.
            <br><br>
            <i>Última atualização: {}</i>
        </div>
        """

    if place_type == "state":

    df = loader.read_data('br', config, endpoint=config['br']['api']['endpoints']['analysis'])
    dfc = pd.read_csv('../notebooks/data/raw/owid-covid-data.csv')
    st.write(
        """

    if place_type == "country_pt":

        legend = """
        <div class="base-wrapper">
            <span class="section-header primary-span">MORTES DIÁRIAS POR PAÍS</span>
            <br><br>
            O gráfico abaixo mostra a média do número de mortes
            diárias dos últimos cinco dias para os 30 países com mais 
            mortes, desde a data da primeira morte reportada.
            Para comparação, os números foram normalizados pelo maior
            valor encontrado em cada país:<b> quanto mais vermelho,
            mais próximo está o valor do maior número de mortes por
            dia observado na UF até hoje</b>.
            <br><br>
            Os países estão ordernados pelo dia que atingiu o máximo de mortes,
            ou seja, os países no pico de mortes aparecerão no topo. {}
            é o país com o maior número de mortos, com: <i>{}</i>
            e o mundo totaliza: <i>{}</i>.
            <br><br>
            <i>Última atualização: {}</i>
        </div>
        """

    st.write(
        legend.format(
            place_max_deaths.iloc[-1][place_type],
            place_max_deaths.max()[col_deaths],
            place_max_deaths.sum()[col_deaths],
            refresh[:10],
        ),
        unsafe_allow_html=True,
    )

    return plot_heatmap(
        df,
        place_type,
        # min_deaths=min_deaths,
        legend=legend,
        # title ="Distribuição de novas mortes nas UFs (mavg = 5 days)",
    )


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
        """
    ,  unsafe_allow_html=True)
    prepare_heatmap(df)
    get_map(df,
    place_type='state',
    time_col='last_updated',
    var='deaths',
    cmap='temps',
    Title = 'Mortos por estado',
    cbar_title='numero de mortes')

    user_uf = st.selectbox("Selecione um estado para análise:", utils.get_ufs_list())

    prepare_cities_heatmap(df,'SP')


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
