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
import loader
import datetime as dt
import math


def iterate_simulation(current_state, seir_parameters, phase, initial):
    """
    Iterate over simulation phase, returning evolution and new current state.
    """

    res = entrypoint(current_state, seir_parameters, phase, initial)
    current_state = (
        res.drop("scenario", axis=1).iloc[-1].to_dict()
    )  # new initial = last date

    return res, current_state


def get_rt(user_input, bound):
    """
    Get reproduction rate from scenario choice.
    """

    rules = {
        "estavel": lambda x: x,  # cenario estavel
        "positivo": lambda x: x / 2,  # cenario positivo
        "negativo": lambda x: x * 2,  # cenario negativo
    }

    # # Caso tenha Rt
    # if user_input["Rt"]["is_valid"] != "nan":
    #     return rules[user_input["strategy"]](user_input["Rt"][bound])
    # Caso não tenha Rt, usa o Rt do estado
    # else:
    return rules[user_input["strategy"]](user_input["rt_values"][bound])


def run_simulation(user_input, config):
    """
    Run simulation phases and return hospital demand.
    
    Parameters
    ----------
    user_input["population_params"]: str
            Explicit population parameters:
                    - N: population
                    - I: infected
                    - R: recovered
                    - D: deaths
            
    user_input["strategy"]: dict
            Simulation parameters for each phase (from user input):
                - scenario: date
                    
    Return
    ------
    
    pd.Dataframe
        States evolution over phases
        
    """

    dfs = {"worst": np.nan, "best": np.nan}

    # Run worst scenario
    for bound in dfs.keys():

        phase = {"scenario": "projection_current_rt", "n_days": 90}

        # Get Rts
        phase["R0"] = get_rt(user_input, bound)

        res = entrypoint(
            user_input["population_params"],
            config["br"]["seir_parameters"],
            phase=phase,
            initial=True,
        )

        res = res.reset_index(drop=True)
        res.index += 1
        res.index.name = "dias"

        dfs[bound] = res

    return dfs


def get_dday(dfs, col, resource_number):

    dday = dict()
    for case in ["worst", "best"]:
        df = dfs[case]

        if max(df[col]) > resource_number:
            dday[case] = df[df[col] > resource_number].index[0]

        else:
            dday[case] = 91

    return dday


def get_dmonth(dfs, col, resource_number):

    dday = get_dday(dfs, col, resource_number)

    for bound, v in dday.items():
        if v == 91:
            dday[bound] = 3
        else:
            dday[bound] = math.ceil(v / 30)

    return dday


if __name__ == "__main__":
    pass
