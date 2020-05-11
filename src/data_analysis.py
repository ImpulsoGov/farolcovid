import streamlit as st
import loader
import yaml
import plotly.graph_objs as go
import plotly.offline as plt
from plotly.io import to_html
import numpy as np
import pandas as pd

import utils

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

    return plot_deaths_heatmap(df_deaths, 'state')#, title='Distribuição de novas mortes nas UFs (mavg = 5 days)')

def main():

    utils.localCSS("style.css")
    utils.localCSS("icons.css")

    config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)

    df = loader.read_data('br', config, refresh_rate=1)

    st.write(
        """
        <div class="base-wrapper">
                <span class="section-header primary-span">MORTES DIÁRIAS POR ESTADO</span>
        </div>
        """
    ,  unsafe_allow_html=True)

    prepare_heatmap(df)

    # st.write('Dados atualizados para 10 de maio. Os dados dos dias mais recentes são provisórios e podem ser revisados para cima à medida que testes adicionais são processados.')

if __name__ == "__main__":
    main()