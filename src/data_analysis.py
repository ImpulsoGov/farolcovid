import streamlit as st
import loader
import yaml
import plotly.graph_objs as go
import plotly.offline as plt
from plotly.io import to_html
import plotly.io as pio
import numpy as np
import pandas as pd
import geopandas as gpd
import geobr
import json
import geojsonio
from plotly.offline import download_plotlyjs, plot, iplot
import utils


def get_rolling_amount(grp,time,data_col, col_to_roll):
    return grp.rolling(time, min_periods=1, on=data_col)[col_to_roll].mean()

def _df_to_plotly(df):
    return {'z': df.values.tolist(),
            'x': df.columns.tolist(),
            'y': df.index.tolist()}
    
def plot_deaths_heatmap(t, place_type, title=None):
    
    # group df
    df_heatmap = t.reset_index()\
                    .pivot(index=place_type, 
                            columns='last_updated', 
                            values='rolling_deaths_new')\
                    .fillna(0)\
                    .apply(lambda x: x/x.max(), axis=1)\
                    .dropna(how='all')

    # remove days with all states zero
    df_heatmap = df_heatmap.loc[:, (df_heatmap != 0).any(axis=0)]
    
    # sort by date of max value ==> first on 0.5
    d = df_heatmap.mask(df_heatmap < 0.5)
    df_heatmap['order'] = d.apply(pd.Series.first_valid_index, 1)
    # df_heatmap['order'] = df_heatmap.idxmax(axis=1)

    df_heatmap = df_heatmap.sort_values('order', ascending=False)
    del df_heatmap['order']
    
    df_heatmap = _df_to_plotly(df_heatmap)

    # style hovertext
    hovertext = list()
    for yi, yy in enumerate(df_heatmap['y']):
        hovertext.append(list())
        for xi, xx in enumerate(df_heatmap['x']):
            hovertext[-1].append('Data: {}<br />UF: {}<br />Média: {:.2f}'.format(xx, yy, df_heatmap['z'][yi][xi]))
    
    # generate fig
    fig = go.Figure(data=go.Heatmap(
                                df_heatmap,
                                colorscale='temps',
                                showscale=False,
                                text=hovertext,
                                hoverinfo='text',
                            ),
                    layout={
                        # 'autosize': True,
                        'width': 1200,
                        'height': 700, 
                        'margin': {'l': 600, 't': 0}
                    }
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


def prepare_country_heatmap(df, mavg_days=5):

    df_deaths = df[~df['new_deaths'].isnull()][['iso_code', 'date','total_deaths', 'new_deaths']]\
                                                .groupby(['iso_code', 'date','total_deaths'])['new_deaths']\
                                                .sum()\
                                                .reset_index()

    df_deaths['rolling_deaths_new'] = df_deaths.groupby('iso_code', 
                                                    as_index=False, 
                                                    group_keys=False)\
                                           .apply(lambda x : get_rolling_amount(x,5, 'date', 'new_deaths'))
    
    df_deaths = df_deaths[df_deaths['iso_code']!='OWID_WRL']

    return plot_countries_heatmap(df_deaths, 'iso_code', 1000, title='Distribuição de novas mortes por países (mavg = 5 days)')


def plot_countries_heatmap(t, place_type, min_deaths, title):
    
    df_heatmap = t.reset_index()\
                          .pivot(index=place_type, 
                                  columns='date', 
                                  values='rolling_deaths_new')\
                           .fillna(0)\
                           .apply(lambda x: x/x.max(), axis=1)\
                           .dropna(how='all')

    # remove days with all states zero
    df_heatmap = df_heatmap.loc[:, (df_heatmap != 0).any(axis=0)]
    print(len(df_heatmap))
    states_total_deaths = [t[t['iso_code'] ==x]['total_deaths'].max() for x in df_heatmap.index]
    idy = np.argsort(states_total_deaths)
    idx = np.array(states_total_deaths,dtype=np.int32)[idy] > min_deaths
    states_total_deaths = np.array(states_total_deaths)


    trace1 = go.Heatmap(_df_to_plotly(df_heatmap.iloc[idy,:].loc[idx,:]), 
                                        colorscale='temps',showscale=False)


    trace2 = go.Bar(x=states_total_deaths[idy][idx],y=df_heatmap.iloc[idy,:].loc[idx,:].index,
                    xaxis="x2",yaxis="y2",orientation='h')
        
    d = [trace1,trace2]
    layout = go.Layout(title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        # autosize= True,
        width= 1200,
        height= 700, 
        margin= {'l': 600, 't': 0},
        xaxis=dict(
            domain=[0, 0.8]
        ),
        xaxis2=dict(
            domain=[0.85, 1]
        ),
        yaxis=dict(tickmode='linear'
        ),
        yaxis2=dict(tickmode='linear',anchor='x2'
        )
        )

    legend = """

        O gráfico ao lado mostra a média do número de mortes<br>
        diárias dos últimos cinco dias para cada País com mais de {}, desde a data da<br>
        primeira morte reportada. Para comparação, os números foram<br>
        normalizados pelo maior valor encontrado em cada UF:<br>
        <b>quanto mais vermelho, mais próximo está o valor do<br>
        maior número de mortes por dia observado na UF até hoje</b>.<br>
        <br>
        As UFs estão ordenadas pelo número de mortos total, <br>
        ou seja, os estados com mais mortes nominais. Os Estados Unidos são o País <br>
        com o maior número de mortos, onde vitimou mais de <i>{}</i> pessoas. <br>
        Última atualização: {}
    """.format(min_deaths,
               states_total_deaths.max(),
               df_heatmap.columns[-1])


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


def plot_deaths_heatmap2(t, place_type, title):
    
    df_heatmap = t.reset_index()\
                          .pivot(index=place_type, 
                                  columns='last_updated', 
                                  values='rolling_deaths_new')\
                           .fillna(0)\
                           .apply(lambda x: x/x.max(), axis=1)\
                           .dropna(how='all')

    # remove days with all states zero
    df_heatmap = df_heatmap.loc[:, (df_heatmap != 0).any(axis=0)]
    print(len(df_heatmap))
    states_total_deaths = [t[t['state'] ==x]['deaths'].max() for x in df_heatmap.index]
    idy = np.argsort(states_total_deaths) 
    
    trace1 = go.Heatmap(_df_to_plotly(df_heatmap.iloc[idy,:]), 
                                    colorscale='temps')

    states_total_deaths = np.array(states_total_deaths)
    trace2 = go.Bar(x=states_total_deaths[idy],y=df_heatmap.iloc[idy,:].index,
                    xaxis="x2",yaxis="y2",orientation='h')
    d = [trace1,trace2]
    layout = go.Layout(title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        # autosize= True,
        width= 1200,
        height= 700, 
        margin= {'l': 600, 't': 0},
        xaxis=dict(
            domain=[0, 0.8]
        ),
        xaxis2=dict(
            domain=[0.85, 1]
        ),
        yaxis=dict(tickmode='linear'
        ),
        yaxis2=dict(tickmode='linear',anchor='x2'
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
        As UFs estão ordenadas pelo número de mortos total, <br>
        ou seja, os estados com mais mortes nominais. São Paulo, <br>
        é o estado com o maior número de mortos, com: <i>{}</i>. <br>
        e o Brasil totaliza: <i>{}</i>.
        <br><br>
        Última atualização: {}
    """.format(states_total_deaths.max(),states_total_deaths.sum(), df_heatmap.columns[-1])


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

    # remove days with all states zero
    df_heatmap = df_heatmap.loc[:, (df_heatmap != 0).any(axis=0)]
    print(len(df_heatmap))
    states_total_deaths = [t[t['iso_code'] ==x]['total_deaths'].max() for x in df_heatmap.index]
    idy = np.argsort(states_total_deaths)
    idx = np.array(states_total_deaths,dtype=np.int32)[idy] > min_deaths
    states_total_deaths = np.array(states_total_deaths)


    trace1 = go.Heatmap(_df_to_plotly(df_heatmap.iloc[idy,:].loc[idx,:]), 
                                        colorscale='temps',showscale=False)


    trace2 = go.Bar(x=states_total_deaths[idy][idx],y=df_heatmap.iloc[idy,:].loc[idx,:].index,
                    xaxis="x2",yaxis="y2",orientation='h')
        
    d = [trace1,trace2]
    layout = go.Layout(title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        # autosize= True,
        width= 1200,
        height= 700, 
        margin= {'l': 600, 't': 0},
        xaxis=dict(
            domain=[0, 0.8]
        ),
        xaxis2=dict(
            domain=[0.85, 1]
        ),
        yaxis=dict(tickmode='linear'
        ),
        yaxis2=dict(tickmode='linear',anchor='x2'
        )
        )

    legend = """

        O gráfico ao lado mostra a média do número de mortes<br>
        diárias dos últimos cinco dias para cada País com mais de {}, desde a data da<br>
        primeira morte reportada. Para comparação, os números foram<br>
        normalizados pelo maior valor encontrado em cada país:<br>
        <b>quanto mais vermelho, mais próximo está o valor do<br>
        maior número de mortes por dia observado na UF até hoje</b>.<br>
        <br>
        As UFs estão ordenadas pelo número de mortos total, <br>
        ou seja, os estados com mais mortes nominais. Os Estados Unidos são o País <br>
        com o maior número de mortos, onde vitimou mais de <i>{}</i> pessoas. <br>
        Última atualização: {}
    """.format(min_deaths,
               states_total_deaths.max(),
               df_heatmap.columns[-1])


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

    utils.localCSS("style.css")
    utils.localCSS("icons.css")

    config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)

    df = loader.read_data('br', config, endpoint=config['br']['api']['endpoints']['analysis'])
    dfc = pd.read_csv('../notebooks/data/raw/owid-covid-data.csv')
    st.write(
        """
        <div class="base-wrapper">
                <span class="section-header primary-span">MORTES DIÁRIAS POR PAÍS COM MAIS DE 1000 MORTOS</span>
        </div>
        """
    ,  unsafe_allow_html=True)

    prepare_country_heatmap(dfc)

    st.write(
        """
        <div class="base-wrapper">
                <span class="section-header primary-span">MORTES DIÁRIAS POR ESTADO</span>
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


    prepare_cities_heatmap(df,'SP')


    # st.write('Dados atualizados para 10 de maio. Os dados dos dias mais recentes são provisórios e podem ser revisados para cima à medida que testes adicionais são processados.')

if __name__ == "__main__":
    main()
