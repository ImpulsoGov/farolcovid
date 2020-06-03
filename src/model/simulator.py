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


def iterate_simulation(current_state, seir_parameters, phase, initial):
    """
    Iterate over simulation phase, returning evolution and new current state.
    """

    res = entrypoint(current_state, seir_parameters, phase, initial)
    current_state = (
        res.drop("scenario", axis=1).iloc[-1].to_dict()
    )  # new initial = last date

    return res, current_state


# Get reproduction rate
def get_rt(place_type, user_input, config, bound):

    if place_type == "city_id":
        col = place_type
        endpoint = config["br"]["api"]["endpoints"]["rt_cities"]

    if place_type == "state_id":
        col = "state"
        endpoint = config["br"]["api"]["endpoints"]["rt_states"]

    rt = loader.read_data("br", config, endpoint=endpoint)
    # pegando estimacao de 10 dias atras
    rt = rt[rt["last_updated"] == (rt["last_updated"].max() - dt.timedelta(10))]

    # caso nao tenha rt, usa o rt do estado
    if (place_type == "city_id") & (user_input[place_type] not in rt[col].values):
        return get_rt("state_id", user_input, config, bound)

    cols = {"best": "Rt_low_95", "worst": "Rt_high_95"}

    if user_input["strategy"] == "isolation":  # current
        return rt[rt[col] == user_input[place_type]][cols[bound]].values[0]

    if user_input["strategy"] == "lockdown":  # smaller_rt
        return rt[rt[col] == user_input[place_type]][cols[bound]] / 2

    if user_input["strategy"] == "nothing":  # greater_rt
        return rt[rt[col] == user_input[place_type]][cols[bound]] * 2


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
        if not user_input["state_id"] and not user_input["city_id"]:
            phase["R0"] = 3
        else:
            phase["R0"] = get_rt(user_input["place_type"], user_input, config, bound)

        print(phase["R0"])

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
            print("aqui atinge a capacidade:", dday[case], case)
        else:
            print("+ 90", resource_number)
            dday[case] = -1  # change here!

    return dday


if __name__ == "__main__":
    pass
