# adenosine model


import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

# from box.manager import BoxManager
from datasets.sleepdebt.class_def import Protocol


def ode_chronic(_, y: list, status: int, model_params: dict) -> list:
    """
    Differential equations for Adenosine and R1 receptor sleep debt.
    """
    # k2 = model_params["k1"] * model_params["kd1"]
    gamma = model_params["au_i"] / (
        model_params["au_i"] + model_params["kd1"]
    )  # target receptor occupancy setting at 0, will be calculated from au_i and kd1
    beta = 300 / (model_params["kd2"] + 300)

    term = y[0] + y[1] + (model_params["kd1"] / (1 - beta))
    discriminant = term**2 - 4 * y[0] * y[1]

    if discriminant < 0:
        raise ValueError(f"Encountered negative discriminant: {discriminant}")

    a1b = 0.5 * (term - np.sqrt(discriminant))
    # Au = y[0] - A1b - params[4]
    # Ru = y[1] - A1b

    # if(t==0):
    # print("*gamma*", a1b/y[1])

    dy1 = status * (1 / model_params["chi_s"]) * (model_params["mu_s"] - y[0]) + (
        1 - status
    ) * (1 / model_params["chi_w"]) * (model_params["mu_w"] - y[0])
    dy2 = (1 / model_params["lambda1"]) * (a1b - (y[1] * gamma))

    return [dy1, dy2]


def calculate_debt(protocol: Protocol, model_params: dict) -> pd.DataFrame:
    """
    Calculate sleep debt for a given protocol from Adenosine model
    """
    atot_i = 727.8  # mu_s + .6237*(mu_w-mu_s) #727.8
    # A_mean = mu_s + 0.302*(mu_w-mu_s)
    r1tot_i = 586.66  # (A_mean/gamma) - (kd1/((1-gamma)*(1-beta))) #586.3

    print("Initial values", atot_i, r1tot_i)
    t0 = 0
    r1tot, atot, t = [], [], []
    for t_awake, t_sleep in zip(protocol.t_awake_l, protocol.t_sleep_l):
        t_range = np.linspace(t0, t0 + t_awake, ((t0 + t_awake) - t0) + 1)
        status = 0
        sol_atot = solve_ivp(
            ode_chronic,
            [t0, t0 + t_awake],
            [atot_i, r1tot_i],
            method="RK45",
            t_eval=t_range,
            args=(status, model_params),
            rtol=1e-6,
            atol=1e-9,
        )

        # sol_R1tot= solve_ivp(func_R1tot, [t0, t0+t_awake],
        #  [Atot_i, R1tot_i], method= 'RK45',t_eval=t_range)
        t.append(sol_atot.t)
        r1tot.append(sol_atot.y[1])
        r1tot_i = sol_atot.y[1][-1]
        atot_i = sol_atot.y[0][-1]
        atot.append(sol_atot.y[0])
        t0 = int(sol_atot.t[-1])

        t_range = np.linspace(t0, t0 + t_sleep, ((t0 + t_sleep) - t0) + 1)
        status = 1
        sol_atot = solve_ivp(
            ode_chronic,
            [t0, t0 + t_sleep],
            [atot_i, r1tot_i],
            method="RK45",
            t_eval=t_range,
            args=(status, model_params),
            rtol=1e-6,
            atol=1e-9,
        )

        # sol_R1tot= solve_ivp(func_R1tot, [t0, t0+t_sleep]
        # , [Atot_i,R1tot_i], method= 'RK45',t_eval=t_range)

        t.append(sol_atot.t)
        r1tot.append(sol_atot.y[1])
        r1tot_i = sol_atot.y[1][-1]
        atot_i = sol_atot.y[0][-1]
        atot.append(sol_atot.y[0])
        t0 = int(sol_atot.t[-1])

    df_debt = pd.DataFrame({"time": [], "Chronic": [], "Acute": []})
    df_debt["time"] = [item for sublist in t for item in sublist]

    df_debt["Acute"] = [item for sublist in atot for item in sublist]
    df_debt["Chronic"] = [item for sublist in r1tot for item in sublist]

    return df_debt
