import pandas as pd
import numpy as np
import yaml
from scipy.integrate import odeint
from tqdm import tqdm

def prepare_states(population_params, model_params):
    """
    Estimate non explicity population initial states

    Params
    --------
    population_param: dict
           Explicit population parameters:
                    - N: population
                    - I: infected
                    - R: recovered
                    - D: deaths

    model_params: dict
            Parameters of model dynamic (transmission, progression, recovery and death rates)

    Returns
    --------
    dict
           Explicit and implicit population parameters ready to be applied in the `model` function
    """
    
    e_perc = (model_params['doubling_rate'] - 1) * model_params['incubation_period'] # 0.26 * 6 = 1.56
    exposed = population_params['I'] * model_params['i1_percentage'] * e_perc
       
    initial_pop_params = {
        'S': population_params['N'] - population_params['R'] - population_params['D'] - population_params['I'] - exposed,
        'E': exposed,
        'I1': population_params['I'] * model_params['i1_percentage'], # 85.5%
        'I2': population_params['I'] * model_params['i2_percentage'], # 12.5%
        'I3': population_params['I'] * model_params['i3_percentage'], # 2.5%
        'R': population_params['R'],
        'D': population_params['D']
    }
    
    return initial_pop_params

def prepare_params(population_params, disease_params, reproduction_rate=3):
    """
    Estimate non explicity disease parameters

    Params
    --------
    population_param: dict
           Explicit population parameters:
                    - N: population
                    - I: infected
                    - R: recovered
                    - D: deaths

    model_params: dict
            Parameters of model dynamic (transmission, progression, recovery and death rates)

    Returns
    --------
    dict
           Explicit and implicit disease parameters ready to be applied in the `model` function
    """

    frac_severe_to_critical = disease_params['i3_percentage'] / (disease_params['i2_percentage'] + disease_params['i3_percentage'])
    frac_critical_to_death = disease_params['fatality_ratio'] / disease_params['i3_percentage']
    
    parameters = {'sigma': 1 / disease_params['incubation_period'],
                  'gamma1': disease_params['i1_percentage'] / disease_params['mild_duration'],
                  'p1': (1 - disease_params['i1_percentage']) / disease_params['mild_duration'],
                  'gamma2': (1 - frac_severe_to_critical) / disease_params['severe_duration'],
                  'p2': frac_severe_to_critical / disease_params['severe_duration'], 
                  'mu': frac_critical_to_death / disease_params['critical_duration'], 
                  'gamma3': (1 - frac_critical_to_death) / disease_params['critical_duration'], 
                 }
    
    # Assuming beta1 with 0.9 * R0
    parameters['beta1'] = 0.9 * (1 / disease_params['mild_duration']) * reproduction_rate / population_params['N']
    
    # And beta2 = beta3 with 0.1 * R0
    x = (1 / disease_params['mild_duration']) * (1 / disease_params['severe_duration']) * (1 / disease_params['critical_duration'])
    y = parameters['p1'] * (1/disease_params['critical_duration']) + parameters['p1'] * parameters['p2']
    
    parameters['beta3'] = 0.1 * (x / y) * reproduction_rate / population_params['N']
    parameters['beta2'] = parameters['beta3']  
    
    return parameters


def SEIR(y, t, model_params):
    """
    The SEIR model differential equations.
    
    Params
    --------
    y: dict
         Population parameters:
              - S: susceptible
              - E: exposed
              - I_1: infected mild
              - I_2: infected severe
              - I_3: infected critical
              - R: recovered
              - D: deaths
            
    model_params: dict
           Parameters of model dynamic (transmission, progression, recovery and death rates)

    Return
    -------
    pd.DataFrame
            Evolution of population parameters.
    """

    S, E, I1, I2, I3, R, D = y
    
    # Exposition of susceptible rate
    exposition_rate = (model_params['beta1'] * I1) + (model_params['beta2'] * I2) + (model_params['beta3'] * I3)
    
    # Susceptible
    dSdt = - exposition_rate * S
    
    # Exposed
    dEdt = exposition_rate * S - model_params['sigma'] * E
    
    # Infected (mild)
    dI1dt = model_params['sigma'] * E - (model_params['gamma1'] + model_params['p1']) * I1
    
    # Infected (severe)
    dI2dt = model_params['p1'] * I1 - (model_params['gamma2'] + model_params['p2']) * I2
    
    # Infected (critical)
    dI3dt = model_params['p2'] * I2 - (model_params['gamma3'] + model_params['mu']) * I3
    
    # Recovered
    dRdt = model_params['gamma1'] * I1 + model_params['gamma2'] * I2 + model_params['gamma3'] * I3
    
    # Deaths
    dDdt = model_params['mu'] * I3
     
    return dSdt, dEdt, dI1dt, dI2dt, dI3dt, dRdt, dDdt


def entrypoint(population_params, model_params, initial=False, reproduction_rate=3, n_days=90):
    """
    Function to receive user input and run model.
    
    Params
    --------
    population_params: dict
         Population parameters:
              - S: susceptible
              - E: exposed
              - I_1: infected mild
              - I_2: infected severe
              - I_3: infected critical
              - R: recovered
              - D: deaths

    model_params: dict
            Parameters of model dynamic (transmission, progression, recovery and death rates)
                                 
    reproduction_rate: int
            Basic reproduction rate of the disease.
            
    n_days: int
            Number of days to model.

    Return
    -------
    pd.DataFrame
            Evolution of population parameters.
    """
    
    if initial: # Get I1, I2, I3 & E
        population_params, model_params = prepare_states(population_params, model_params), prepare_params(population_params, model_params)
    
    # Run model
    params = {'y0': list(y.values()),
              't': np.linspace(0, n_days, n_days+1), 
              'args': (model_params,)}
    
    result = pd.DataFrame(odeint(SEIR, **params), columns=['S', 'E' ,'I1', 'I2', 'I3', 'R', 'D'])
    result.index.name = 'dias'
    
    return result


if __name__ == '__main__':
    
    model_parameters = yaml.load(open('model_parameters.yaml', 'r'), Loader=yaml.FullLoader)
    user_params = {'N': 10000, # 'city' => filter N (total pop) + I, D (brasil.io cases)
                   'I': 1000,
                   'R': 0,
                   'D': 10}
    seir_params = model_parameters['brazil']['seir_parameters']
    result = entrypoint(user_params, seir_params, initial=True, reproduction_rate=3, n_days=90)