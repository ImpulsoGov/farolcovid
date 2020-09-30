import pandas as pd
import numpy as np
import yaml
from scipy.integrate import odeint


def prepare_states(population_params, place_specific_params, disease_params):
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

    config: dict
            General configuration files with rules to estimate implicit parameters

    Returns
    --------
    dict
           Explicit and implicit population parameters ready to be applied in the `model` function
    """

    e_perc = (disease_params["doubling_rate"] - 1) * disease_params[
        "incubation_period"
    ]  # 0.26 * 6 = 1.56

    exposed = population_params["I"] * place_specific_params["i1_percentage"] * e_perc

    initial_pop_params = {
        "S": population_params["N"]
        - population_params["R"]
        - population_params["D"]
        - population_params["I"]
        - exposed,
        "E": exposed,
        "I1": population_params["I"]
        * place_specific_params[
            "i1_percentage"
        ],  # disease_params["i2_percentage"],  # 12.5%
        "I2": population_params["I"]
        * place_specific_params[
            "i2_percentage"
        ],  # disease_params["i2_percentage"],  # 12.5%
        "I3": population_params["I"]
        * place_specific_params[
            "i3_percentage"
        ],  # disease_params["i3_percentage"],  # 2.5%
        "R": population_params["R"],
        "D": population_params["D"],
    }

    return initial_pop_params


def prepare_disease_params(
    population_params, place_specific_params, disease_params, reproduction_rate
):
    """
    Estimate non explicity SEIR model parameters

    Params
    --------
    population_params: dict
    disease_params: dict
    reproduction_rate: int

    Returns
    --------
    dict
           Explicit and implicit disease parameters ready to be applied in the `model` function
    """

    frac_severe_to_critical = place_specific_params["i3_percentage"] / (
        place_specific_params["i2_percentage"] + place_specific_params["i3_percentage"]
    )
    frac_critical_to_death = (
        place_specific_params["fatality_ratio"] / place_specific_params["i3_percentage"]
    )

    parameters = {
        "sigma": 1 / disease_params["incubation_period"],
        "gamma1": place_specific_params["i1_percentage"]
        / disease_params["mild_duration"],
        "p1": (1 - place_specific_params["i1_percentage"])
        / disease_params["mild_duration"],
        "gamma2": (1 - frac_severe_to_critical) / disease_params["severe_duration"],
        "p2": frac_severe_to_critical / disease_params["severe_duration"],
        "mu": frac_critical_to_death / disease_params["critical_duration"],
        "gamma3": (1 - frac_critical_to_death) / disease_params["critical_duration"],
    }

    # Assuming beta1 with 0.9 * R0
    parameters["beta1"] = (
        0.9
        * (1 / disease_params["mild_duration"])
        * reproduction_rate
        / population_params["N"]
    )

    # And beta2 = beta3 with 0.1 * R0
    x = (
        (1 / disease_params["mild_duration"])
        * (1 / disease_params["severe_duration"])
        * (1 / disease_params["critical_duration"])
    )
    y = (
        parameters["p1"] * (1 / disease_params["critical_duration"])
        + parameters["p1"] * parameters["p2"]
    )

    parameters["beta3"] = 0.1 * (x / y) * reproduction_rate / population_params["N"]
    parameters["beta2"] = parameters["beta3"]

    return parameters


def SEIR(y, t, model_params, initial=False):
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
    exposition_rate = (
        (model_params["beta1"] * I1)
        + (model_params["beta2"] * I2)
        + (model_params["beta3"] * I3)
    )

    # Susceptible
    dSdt = -exposition_rate * S

    # Exposed
    dEdt = exposition_rate * S - model_params["sigma"] * E

    # Infected (mild)
    dI1dt = (
        model_params["sigma"] * E - (model_params["gamma1"] + model_params["p1"]) * I1
    )

    # Infected (severe)
    dI2dt = model_params["p1"] * I1 - (model_params["gamma2"] + model_params["p2"]) * I2

    # Infected (critical)
    dI3dt = model_params["p2"] * I2 - (model_params["gamma3"] + model_params["mu"]) * I3

    # Recovered
    dRdt = (
        model_params["gamma1"] * I1
        + model_params["gamma2"] * I2
        + model_params["gamma3"] * I3
    )

    # Deaths
    dDdt = model_params["mu"] * I3

    return dSdt, dEdt, dI1dt, dI2dt, dI3dt, dRdt, dDdt


def entrypoint(
    population_params, place_specific_params, disease_params, phase, initial=False
):
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

    place_specific_params: pd.DataFrame
        Parameters for specific places (for now: fatality ratio and infection proportions)

    disease_params: dict
        Parameters of model dynamic (transmission, progression, recovery and death rates)
                                 
    phase: dict
       Scenario and days to run 
            - scenario
            - date
        

    Return
    -------
    pd.DataFrame
            Evolution of population parameters.
    """

    if initial:  # Get I1, I2, I3 & E
        population_params, disease_params = (
            prepare_states(population_params, place_specific_params, disease_params),
            prepare_disease_params(
                population_params, place_specific_params, disease_params, phase["R0"]
            ),
        )
    else:
        disease_params = prepare_disease_params(
            population_params, place_specific_params, disease_params, phase["R0"]
        )
        del population_params["N"]

    # Run model
    params = {
        "y0": list(population_params.values()),
        "t": np.linspace(0, phase["n_days"], phase["n_days"] + 1),
        "args": (disease_params, initial),
    }

    result = pd.DataFrame(
        odeint(SEIR, **params), columns=["S", "E", "I1", "I2", "I3", "R", "D"]
    )
    result["N"] = result.sum(axis=1)
    result["scenario"] = phase["scenario"]
    result.index.name = "dias"

    return result