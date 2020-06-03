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
def get_rt(place_type, user_input, config, simulation_params, bound):

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
        return get_rt("state_id", user_input, config, simulation_params, bound)

    cols = {"best": "Rt_low_95", "worst": "Rt_high_95"}

    for phase in simulation_params:

        # TODO: mudar para novas flags com o front
        if simulation_params[phase]["scenario"] == "isolation":  # nothing
            simulation_params[phase]["R0"] = rt[rt[col] == user_input[place_type]][
                cols[bound]
            ].values[0]

        if simulation_params[phase]["scenario"] == "lockdown":  # smaller_rt
            simulation_params[phase]["R0"] = (
                rt[rt[col] == user_input[place_type]][cols[bound]] / 2
            )

        if simulation_params[phase]["scenario"] == "nothing":  # greater_rt
            simulation_params[phase]["R0"] = (
                rt[rt[col] == user_input[place_type]][cols[bound]] * 2
            )

    return simulation_params


def decide_scenario(user_strategy):

    if user_strategy["isolation"] < user_strategy["lockdown"]:
        return ["nothing", "isolation", "lockdown"]
    elif user_strategy["isolation"] == user_strategy["lockdown"]:  # lockdown only
        return ["nothing", "lockdown", "lockdown"]
    else:
        return ["nothing", "lockdown", "isolation"]


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

        # Get ranges with test delay
        intervals = (
            min(user_input["strategy"].values())
            + config["simulator"]["scenarios"][bound]["test_delay"],
            max(user_input["strategy"].values()) - min(user_input["strategy"].values()),
            config["simulator"]["max_days"] - max(user_input["strategy"].values()),
        )

        scenarios = decide_scenario(user_input["strategy"])
        simulation_params = {
            f"phase{i+1}": {"scenario": scenarios[i], "n_days": intervals[i]}
            for i in range(3)
        }

        # Get Rts
        if not user_input["state_id"] and not user_input["city_id"]:
            for phase in simulation_params:
                simulation_params[phase]["R0"] = 3
        else:
            simulation_params = get_rt(
                user_input["place_type"], user_input, config, simulation_params, bound
            )

        # Iterate over phases
        df_evolution = pd.DataFrame()

        for phase in simulation_params:

            if phase == "phase1":
                res, current_state = iterate_simulation(
                    user_input["population_params"],
                    config["br"]["seir_parameters"],
                    simulation_params[phase],
                    initial=True,
                )
                df_evolution = df_evolution.append(res)  # consider 1st day

            else:
                res, current_state = iterate_simulation(
                    current_state,
                    config["br"]["seir_parameters"],
                    simulation_params[phase],
                    initial=False,
                )
                df_evolution = df_evolution.append(res[1:])

        df_evolution = df_evolution[
            config["simulator"]["scenarios"][bound]["test_delay"] :
        ]
        df_evolution = df_evolution.reset_index(drop=True)
        df_evolution.index += 1
        df_evolution.index.name = "dias"

        dfs[bound] = df_evolution

    return dfs


def get_dday(dfs, col, resource_number):

    dday = dict()
    for case in ["worst", "best"]:
        df = dfs[case]

        if max(df[col]) > resource_number:
            dday[case] = df[df[col] > resource_number].index[0]
        else:
            dday[case] = -1  # change here!

    return dday


if __name__ == "__main__":
    pass
