"""
script to run the adenosine model for sleep debt calculation
get_protocols(): get the list of protocols, currently we have 13 of them in protocols.yaml.
construct_protocol(): construct the sleep and wake time list for each protocol. 
                      t_awake_l and t_sleep_l are list of sleep and wake
                        duration respectively.
get_status(): get the status of the individual, whether he is awake or asleep
              based on the time interval.
ode_chronic(): differential equations for Adenosine and R1 receptor concentration.
calculate_debt(): calculate sleep debt for a given protocol object from Adenosine model.
                  this functions call ode_chronic() to solve the differential
                  equations using solve_ivp().This function uses Protocol 
                  class to get the time sequence for sleep/awake duration.
Protocol class: class to represent a protocol, it has name, t_awake_l and t_sleep_l as attributes.
                fill(): fill the protocol with t_awake_l and t_sleep_l
                time_sequence(): get time sequence for sleep-awake status
                plot(): get plot for the protocol, calls get_plot() from plotting.py
protocol_object_list(): create list of protocol objects     
run_sleepdebt_model(): run sleep debt model for all the protocols.  
                       It calls get_protocols(), construct_protocol(),
                       Protocol class, calculate_debt() and Protocol.plot(). 
At the end of the scripts all the parameters are defined.
Some of the parameters are being read from "parameters.yaml" file. 
Rest of them are calculated from the parameters read from the yaml file.                            
"""

# pylint: disable=R0801

import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

# from box.manager import BoxManager
from datasets.sleepdebt.adenosine_model.plotting import get_plot
from utils.get import get_box, get_parameters_from_box, get_protocols_from_box
from utils.save import save_to_csv

BOX_PATH = {
    "plots": Path("results/sleep_debt/sleepDebt_curves/ligand_receptor_model/"),
    "csvs": Path("archives/sleep_debt/SleepDebt_Data/ligand_receptor_model/sleepdebt/"),
}


def get_protocols() -> list:
    "getting protocols list as string"
    protocol_list = []
    for i in range(1, 14):  # Assuming you have 3 protocols
        if i == 8:
            for j in range(1, 10):
                function_name = f"protocol{i}_{j}"
                # print(function_name)
                protocol_list.append(function_name)
        else:
            function_name = f"protocol{i}"
            # print(function_name)
            protocol_list.append(function_name)
    # print(protocol_list)
    return protocol_list


def construct_protocol(data, protocol_name) -> tuple:
    """construct protocol from yaml file"""
    print(protocol_name)
    protocol = data["protocols"][protocol_name]

    # Construct t_awake_l
    t_awake_l = []
    for item in protocol["t_awake_l"]:
        # print(type(item))
        if "repeat" in item:
            repeat_value = protocol["t_awake_l"][item][
                "value"
            ]  # Ensure value is an integer
            repeat_count = protocol["t_awake_l"][item][
                "count"
            ]  # Ensure count is an integer
            t_awake_l.extend([repeat_value] * repeat_count)

        elif "append" in item:
            append_value = protocol["t_awake_l"][
                item
            ]  # Ensure append value is an integer
            t_awake_l.extend(append_value)  # Use append for single values

        else:
            raise ValueError(f"Invalid key in t_awake_l: {item}")

    # Construct t_sleep_l
    t_sleep_l = []
    for item in protocol["t_sleep_l"]:
        if "repeat" in item:
            repeat_value = protocol["t_sleep_l"][item][
                "value"
            ]  # Ensure value is an integer
            repeat_count = protocol["t_sleep_l"][item][
                "count"
            ]  # Ensure count is an integer
            t_sleep_l.extend([repeat_value] * repeat_count)
        elif "append" in item:
            append_value = protocol["t_sleep_l"][
                item
            ]  # Ensure append value is an integer
            t_sleep_l.extend(append_value)  # Use append for single values
        else:
            raise ValueError(f"Invalid key in t_sleep_l: {item}")

    return t_awake_l, t_sleep_l


def get_status(t: int, time_ct: list[int]) -> str:
    """getting sleep/wake status based on time interval"""
    s = "awake"
    for i in range(1, len(time_ct), 2):
        # print(i)
        if time_ct[i] < t <= time_ct[i + 1]:
            s = "sleep"
            break
    return s


def ode_chronic(_, y: list, status: int) -> list:
    """
    Differential equations for Adenosine and R1 receptor sleep debt.
    """

    term = y[0] + y[1] + kd1 / (1 - beta)
    discriminant = term**2 - 4 * y[0] * y[1]

    if discriminant < 0:
        raise ValueError(f"Encountered negative discriminant: {discriminant}")

    a1b = 0.5 * (term - np.sqrt(discriminant))
    # Au = y[0] - A1b - params[4]
    # Ru = y[1] - A1b

    # if(t==0):
    # print("*gamma*", a1b/y[1])

    dy1 = status * (1 / chi_s) * (MU_S - y[0]) + (1 - status) * (1 / chi_w) * (
        MU_W - y[0]
    )
    dy2 = (1 / lambda1) * (a1b - (y[1] * gamma))

    return [dy1, dy2]


class Protocol:
    """
    Class to represent a protocol
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.t_awake_l: list[int] = []
        self.t_sleep_l: list[int] = []

    def fill(self, t_awake_l, t_sleep_l) -> None:
        """
        Fill the protocol with t_awake_l and t_sleep_l
        """
        self.t_awake_l = t_awake_l
        self.t_sleep_l = t_sleep_l

    def time_sequence(self) -> list[int]:
        """
        Get time count for sleep-awake status
        """
        # sleep-awake status
        time_elapsed = 0
        time_count = []
        time_count.append(0)
        for i, _ in enumerate(self.t_awake_l):
            # print(i)
            # print(self.t_awake_l[i])
            time_elapsed = time_elapsed + self.t_awake_l[i]
            time_count.append(time_elapsed)
            time_elapsed = time_elapsed + self.t_sleep_l[i]
            time_count.append(time_elapsed)

        return time_count

    def plot(self) -> plt.Figure:
        """
        Get plot for the protocol
        """
        fig = plt.figure(figsize=(20, 10))

        ax = fig.add_subplot(111)  # 111 means 1 row, 1 column, 1st subplot

        df_sleep_debt = calculate_debt(self)

        df_sleep_debt["status"] = df_sleep_debt["time"].apply(
            lambda x: get_status(x, self.time_sequence())
        )

        dataset_name = DATA["protocols"][self.name]["dataset"]
        save_to_csv(
            box,
            df_sleep_debt,
            BOX_PATH["csvs"] / f"{dataset_name}_class.csv",
            index=False,
        )

        ax = get_plot(self, df_sleep_debt, ax=ax)
        # Set common x and y labels for the figure
        fig.text(0.5, 0.05, "Time (days)", ha="center", va="center", fontsize=14)
        fig.text(
            0.06,
            0.5,
            "Adenosine/Receptor concentration (nM)",
            ha="center",
            va="center",
            rotation="vertical",
            fontsize=14,
        )

        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=14)
        return fig


def calculate_debt(protocol: Protocol) -> pd.DataFrame:
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
            args=(status,),
            rtol=1e-8,  # Relative tolerance
            atol=1e-10,  # Absolute tolerance
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
            args=(status,),
            rtol=1e-8,  # Relative tolerance
            atol=1e-10,  # Absolute tolerance
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


def protocol_object_list(protocol_list) -> list[Protocol]:
    """
    Create protocol objects
    """
    return [Protocol(name) for name in protocol_list]


def run_sleepdebt_model() -> None:
    """
    Run sleep debt model
    """
    # j = 1

    # Parameters for subplot grid
    # rows = 2
    # cols = 2
    # total_plots = rows * cols
    # Initialize subplot position and figure
    # i1 = 1
    # fig = plt.figure(figsize=(20, 10))

    prot_list = get_protocols()
    protocol_objects = protocol_object_list(prot_list)
    for protocol in protocol_objects:
        t_ae_sl = construct_protocol(DATA, protocol.name)
        protocol.fill(t_ae_sl[0], t_ae_sl[1])
        name = DATA["protocols"][protocol.name]["dataset"]
        local_file_path = f"sleep_debt_adenosine_{name}.png"
        plot1 = protocol.plot()
        plot1.savefig(local_file_path)

        file = io.BytesIO()
        plot1.savefig(file)
        file.seek(0)

        # Upload the figure to Box
        box.save_file(file, BOX_PATH["plots"] / f"sleep_debt_adenosine_{name}.png")
        plt.close(plot1)

        # j = j + 1


def zeitzer_sample() -> None:
    """
    some of the Zeitzer subject have different sleep wake schedule.
      So calculating  sleep debt separately
    for those subjects.
    """

    def df_zeitzer(sub, t_awake_l, t_sleep_l) -> None:
        pro = Protocol(f"zeitzer_uncommon_{sub}")
        pro.fill(t_awake_l, t_sleep_l)
        pro.time_sequence()
        df_sleep_debt = calculate_debt(pro)
        df_sleep_debt["status"] = df_sleep_debt["time"].apply(
            lambda x: get_status(x, pro.time_sequence())
        )
        save_to_csv(
            box,
            df_sleep_debt,
            BOX_PATH["csvs"] / f"Zeitzer_Uncommon_{sub}_class.csv",
            index=False,
        )

    file = box.get_file(BOX_PATH["csvs"] / "zeitzer_uncommon_protocol_from_python.csv")
    df_zeitzer_uncommon = pd.read_csv(file)
    subject = df_zeitzer_uncommon["subject"].unique()

    for sub in subject:
        hr_awake = int(
            df_zeitzer_uncommon.loc[
                df_zeitzer_uncommon["subject"] == sub, "hours_awake"
            ].values[0]
        )
        hr_sleep = int(
            df_zeitzer_uncommon.loc[
                df_zeitzer_uncommon["subject"] == sub, "hours_sleep"
            ].values[0]
        )
        hr_awake1 = int(
            df_zeitzer_uncommon.loc[
                df_zeitzer_uncommon["subject"] == sub, "hours_awake1"
            ].values[0]
        )
        n_rest = 11  # 11

        t_awake_l = n_rest * [16 * 60] + [hr_awake] + [hr_awake1]
        t_sleep_l = n_rest * [8 * 60] + [hr_sleep] + [480]

        df_zeitzer(sub, t_awake_l, t_sleep_l)


box = get_box()
DATA = get_protocols_from_box(box)
adenosine = get_parameters_from_box(box)
au_i = adenosine["parameters"]["set1"]["au_i"]
kd1 = max(adenosine["parameters"]["set1"]["kd1"], 1)
kd1 = min(adenosine["parameters"]["set1"]["kd1"], 10)

kd2 = max(adenosine["parameters"]["set1"]["kd2"], 100)
kd2 = min(adenosine["parameters"]["set1"]["kd2"], 10000)
k1 = adenosine["parameters"]["set1"]["k1"]
k2 = adenosine["parameters"]["set1"]["k1"] * kd1
gamma = au_i / (
    au_i + kd1
)  # target receptor occupancy setting at 0, will be calculated from au_i and kd1
beta = adenosine["parameters"]["set1"]["beta"]
if beta == 0:
    beta = 300 / (kd2 + 300)
param3 = max(adenosine["parameters"]["set1"]["param3"], 0)
param3 = min(adenosine["parameters"]["set1"]["param3"], 1)

chi_w = adenosine["parameters"]["set1"][
    "chi_w"
]  # time constant for exponential decay during wake (h)
chi_s = adenosine["parameters"]["set1"][
    "chi_s"
]  # time constant for exponential decay during sleep (h)
lambda1 = adenosine["parameters"]["set1"]["lambdas"] * 60  # 306, 291
# A_tot= au_i*(au_i + kd1+ 600*(1-beta))/((kd1 + au_i)* (1-beta))
MU_S = 596.4  # param3*A_tot
MU_W = 869.5  # (A_tot - param3*0.65)/0.36


if __name__ == "__main__":
    run_sleepdebt_model()
    zeitzer_sample()
