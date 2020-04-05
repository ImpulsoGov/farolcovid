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

def run_simulation(population_params, simulation_params):
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
            
    simulation_params: dict
            Simulation parameters for each phase (from user input):
                - phase1:
                    - scenario
                    - date
                - phase2:
                    - scenario
                    - date
        
                    
    Return
    ------
    
    pd.Dataframe
        States evolution over phases
        
    """
    
    scenario_parameters = yaml.load(open('./configs/scenario_parameters.yaml', 'r'), Loader=yaml.FullLoader)
    model_parameters    = yaml.load(open('./configs/model_parameters.yaml', 'r'), Loader=yaml.FullLoader)

    model_params = model_parameters['br']['seir_parameters'] # for now with country = br
    
    dfs = {'worst': np.nan, 'best': np.nan}
    
    # Run worst scenario
    for bound in dfs.keys():
    
        # Get R0s
        simulation_params = get_r0(scenario_parameters, simulation_params, bound)

        # Iterate over phases
        df_evolution = pd.DataFrame()
        
        for phase in simulation_params:

            if phase == 'phase1':
                res, current_state = iterate_simulation(population_params, model_params, 
                                                        simulation_params[phase], initial=True)

            else:
                res, current_state = iterate_simulation(current_state, model_params, 
                                                        simulation_params[phase], initial=False)
            df_evolution = df_evolution.append(res[1:])

        df_evolution = df_evolution.reset_index(drop=True)
        df_evolution.index += 1
        df_evolution.index.name = 'dias'
        
        dfs[bound] = df_evolution
    
    return dfs

if __name__ == '__main__':
    pass