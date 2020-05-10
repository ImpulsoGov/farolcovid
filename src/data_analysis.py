import streamlit as st
import loader
import yaml
import plotly.graph_objs as go

def _df_to_plotly(df):
    return {'z': df.values.tolist(),
            'x': df.columns.tolist(),
            'y': df.index.tolist()}
    
def plot_deaths_heatmap(t, place_type, title):
    
    df_heatmap = t.reset_index()\
                          .pivot(index=place_type, 
                                  columns='last_updated', 
                                  values='rolling_deaths_new')\
                           .fillna(0)\
                            # TODO: order by date of max value
                           .sort_values(by=[t['last_updated'].max()])\
                           .apply(lambda x: x/x.max(), axis=1)\
                           .dropna(how='all')

    # remove days with all states zero
    df_heatmap = df_heatmap.loc[:, (df_heatmap != 0).any(axis=0)]
    
    fig = go.Figure(data=go.Heatmap(_df_to_plotly(df_heatmap), 
                                    colorscale='temps'), 
                    layout={'width': 600,
                            'height': 800,
                            'title': title})
    
    # fig['layout']['yaxis']['autorange'] = "reversed"  
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

    return plot_deaths_heatmap(df_deaths, 'state', title='Distribuição de novas mortes nas UFs (mavg = 5 days)')

def main():

    config = yaml.load(open('configs/config.yaml', 'r'), Loader = yaml.FullLoader)

    df = loader.read_data('br', config, refresh_rate=1)
    prepare_heatmap(df)

if __name__ == "__main__":
    main()