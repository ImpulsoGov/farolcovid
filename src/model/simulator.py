import pandas as pd
import numpy as np
import plotly.express as px
import yaml
from scipy.integrate import odeint
from tqdm import tqdm
import sys
sys.path.insert(0,'.')
# from seir import entrypoint
from seir import entrypoint

default_params = yaml.load(open('./configs/config.yaml', 'r'), Loader=yaml.FullLoader)

def iterate_simulation(current_state, seir_parameters, phase, initial):
    """
    Iterate over simulation phase, returning evolution and new current state.
    """
    
    res = entrypoint(current_state, seir_parameters, phase, initial)
    current_state = res.drop('scenario', axis=1).iloc[-1].to_dict() # new initial = last date
    
    return res, current_state

# Get reproduction rate
def get_r0(scenario_parameters, simulation_params, bound):
    
    for phase in simulation_params:
        simulation_params[phase]['R0'] = scenario_parameters[bound][simulation_params[phase]['scenario']]['R0']

    return simulation_params

def decide_scenario(user_strategy):
    
    if user_strategy['isolation'] < user_strategy['lockdown']:
        return ['nothing', 'isolation', 'lockdown']
    else:
        return ['nothing', 'lockdown', 'isolation']

def run_simulation(population_params, strategy_params):
    """
    Run simulation phases and return hospital demand.
    
    Parameters
    ----------
    population_params: str
            Explicit population parameters:
                    - N: population
                    - I: infected
                    - R: recovered
                    - D: deaths
            
    strategy_params: dict
            Simulation parameters for each phase (from user input):
                - scenario: date
                    
    Return
    ------
    
    pd.Dataframe
        States evolution over phases
        
    """
    
    dfs = {'worst': np.nan, 'best': np.nan}
    
    # Run worst scenario
    for bound in dfs.keys():
        
        # Get ranges with test delay
        intervals = (min(strategy_params.values()) + default_params['simulator']['scenarios'][bound]['test_delay'],
                     max(strategy_params.values()) - min(strategy_params.values()),
                     default_params['simulator']['max_days'] - max(strategy_params.values()))
        
        scenarios = decide_scenario(strategy_params)
        simulation_params = {f'phase{i+1}': {'scenario': scenarios[i], 'n_days': intervals[i]} for i in range(3)}
    
        # Get R0s
        simulation_params = get_r0(default_params['simulator']['scenarios'], simulation_params, bound)

        # Iterate over phases
        df_evolution = pd.DataFrame()
        
        for phase in simulation_params:

            if phase == 'phase1':
                res, current_state = iterate_simulation(population_params, 
                                                        default_params['br']['seir_parameters'], 
                                                        simulation_params[phase], initial=True)

            else:
                res, current_state = iterate_simulation(current_state, 
                                                        default_params['br']['seir_parameters'], 
                                                        simulation_params[phase], initial=False)
            df_evolution = df_evolution.append(res[1:])

        df_evolution = df_evolution.reset_index(drop=True)
        df_evolution.index += 1
        df_evolution.index.name = 'dias'
        
        dfs[bound] = df_evolution
    
    return dfs


def get_dday(dfs,col,resource_number):
    
    dday = dict()
    for case in ['worst', 'best']:
        df = dfs[case]
        
        if max(df[col]) > resource_number:
            dday[case] = df[df[col] > resource_number].index[0]
        else:
            dday[case] = 666 # change here!
    
    return dday

import plotly.graph_objects as go

def plot_fig(t, cols):
    
    fig = go.Figure()
    for col in t.columns:
        i_type = col.split('_')[0]

        if 'best' in col:
            fig.add_trace(go.Scatter(x=t.index, y=t[col], name=cols[i_type]['name'], showlegend=False, fill=None, 
                                     hovertemplate=None, #'%{y:.0f} no dia %{x}', 
                                     mode='lines', line=dict(color=cols[i_type]['color'], width=3)))

        else:
            fig.add_trace(go.Scatter(x=t.index, y=t[col], name=cols[i_type]['name'], fill='tonexty',
                                     hovertemplate=None, #'%{y:.0f} no dia %{x}',
                                     mode='lines', line=dict(color=cols[i_type]['color'], width=3)))

    fig.update_layout(template='plotly_white', title_text='Evolução da demanda hospitalar', 
                      legend_orientation="h", legend=dict(x=0, y=-.2, font=dict(size=14)),
                      hovermode='x')
    
    fig.update_xaxes(title=t.index.name, titlefont=dict(size=12), showline=True, 
                     linewidth=2, linecolor='black', showgrid=False)
    fig.update_yaxes(gridwidth=1, gridcolor='#e6e6e6')
    
    return fig

def run_evolution(user_input):
    
    dfs = run_simulation(user_input['population_params'], user_input['strategy'])
    
    cols = {'I2': {'name': 'Demanda por leitos', 'color': '#f4511e'}, 
            'I3': {'name': 'Demanda por ventiladores', 'color': '#ff8f00'}}

    # Create graph
    t = dfs['best'][cols.keys()].join(dfs['worst'][cols.keys()], lsuffix='_best', rsuffix='_worst').sort_index(axis=1)    
    fig = plot_fig(t, cols)
    
    dday_beds = get_dday(dfs,'I2', user_input['n_beds'])   
    dday_ventilators = get_dday(dfs, 'I3', user_input['n_ventilators'])
    
    return fig, dday_beds, dday_ventilators

if __name__ == '__main__':
    pass