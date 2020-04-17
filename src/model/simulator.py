import pandas as pd
import numpy as np
import plotly.express as px
import yaml
from scipy.integrate import odeint
from tqdm import tqdm
import sys
# sys.path.insert(0,'.')
# from seir import entrypoint
from model.seir import entrypoint

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
    elif user_strategy['isolation'] == user_strategy['lockdown']: # lockdown only
        return ['nothing', 'lockdown', 'lockdown']
    else:
        return ['nothing', 'lockdown', 'isolation']

def run_simulation(population_params, strategy_params, default_params):
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
                df_evolution = df_evolution.append(res) # consider 1st day

            else:
                res, current_state = iterate_simulation(current_state, 
                                                        default_params['br']['seir_parameters'], 
                                                        simulation_params[phase], initial=False)
                df_evolution = df_evolution.append(res[1:])

        df_evolution = df_evolution[default_params['simulator']['scenarios'][bound]['test_delay']:]
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
            dday[case] = -1 # change here!
    
    return dday

import plotly.graph_objects as go

def plot_fig(t, cols):
    
    fig = go.Figure()
    for col in t.columns:
        i_type = col.split('_')[0]

        if 'best' in col:
            fig.add_trace(go.Scatter(x=t.index, y=t[col].astype(int), name=cols[i_type]['name'], showlegend=False, fill=None, 
                                     hovertemplate=None, #'%{y:.0f} no dia %{x}', 
                                     mode='lines', line=dict(color=cols[i_type]['color'], width=3)))

        else:
            fig.add_trace(go.Scatter(x=t.index, y=t[col].astype(int), name=cols[i_type]['name'], fill='tonexty',
                                     hovertemplate=None, #'%{y:.0f} no dia %{x}',
                                     mode='lines', line=dict(color=cols[i_type]['color'], width=3)))
    
    for i_type in cols.keys():
        fig.add_trace(go.Scatter(x=t.index, y=[cols[i_type]['capacity'] for i in t.index], name=cols[i_type]['resource_name'],
                                showlegend=False, hovertemplate=None, mode='lines',
                                line=dict(color=cols[i_type]['color'], width=6, dash="dash")))

    fig.update_layout(#title="<b>EVOLUÇÃO DIÁRIA DA DEMANDA HOSPITALAR</b>", titlefont=dict(size=24, family='Oswald, sans-serif'), 
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    legend_orientation="h", legend=dict(x=0, y=-.2, font=dict(size=18, family='Oswald, sans-serif')),
                    hovermode="x", 
                    autosize=False, width=1000, height=800)
    
    fig.update_xaxes(title="dias", tickfont=dict(size=16, family='Oswald, sans-serif'),
                    # titletext=dict(xref='paper', x=0),
                    titlefont=dict(size=18, family='Oswald, sans-serif'), 
                    showline=True, linewidth=2, linecolor='black', showgrid=False)

    fig.update_yaxes(gridwidth=1, gridcolor='#d7d8d9', tickfont=dict(size=16, family='Oswald, sans-serif'),)
    
    return fig

def run_evolution(user_input, config):
    
    dfs = run_simulation(user_input['population_params'], user_input['strategy'], config)
    
    cols = {'I2': {'name': 'Demanda por leitos', 'color': '#F2C94C', 
                  'resource_name': 'Capacidade de leitos', 'capacity': user_input['n_beds']}, 
            'I3': {'name': 'Demanda por ventiladores', 'color': '#0097A7',
                  'resource_name': 'Capacidade de ventiladores', 'capacity': user_input['n_ventilators']}}

    # Create graph
    t = dfs['best'][cols.keys()].join(dfs['worst'][cols.keys()], lsuffix='_best', rsuffix='_worst').sort_index(axis=1)    
    
    dday_beds = get_dday(dfs,'I2', user_input['n_beds'])   
    dday_ventilators = get_dday(dfs, 'I3', user_input['n_ventilators'])
    
    fig = plot_fig(t, cols)
    
    return fig, dday_beds, dday_ventilators

if __name__ == '__main__':
    pass