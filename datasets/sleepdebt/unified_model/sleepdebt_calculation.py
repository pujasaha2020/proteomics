"""
Re-writing the sleep debt calculation script avoiding 
functions with too many arguments. Using "Protocol" class.
"""

# pylint: disable=R0801

import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from box.manager import BoxManager
from datasets.sleepdebt.unified_model.model import simulate_unified
from datasets.sleepdebt.unified_model.plotting import get_plot
from utils.get import get_box, get_protocols_from_box
from utils.save import save_to_csv

BOX_PATH = {
    "plots": Path("results/sleep_debt/sleepDebt_curves/unified_model/"),
    "csvs": Path("archives/sleep_debt/SleepDebt_Data/unified_model/sleepdebt/"),
}

'''
def read_yaml(file_path):
    """read yaml file"""
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


DATA = read_yaml(FILE_PATH)
'''


def get_status(t: int, time_ct: list[int]) -> str:
    """getting sleep=wake status based on time interval"""
    s = "awake"
    for i in range(1, len(time_ct), 2):
        # print(i)
        if time_ct[i] < t <= time_ct[i + 1]:
            s = "sleep"
            break
    return s


def get_protocols() -> list[str]:
    "getting protocols list as string"
    protocol_list = []
    for i in range(12, 13):  # Assuming you have 3 protocols
        if i == 8:
            for j in range(1, 10):
                function_name = f"protocol{i}_{j}"
                print(function_name)
                protocol_list.append(function_name)
        else:
            function_name = f"protocol{i}"
            print(function_name)
            protocol_list.append(function_name)
    print(protocol_list)
    return protocol_list


def construct_protocol(protocol_data: dict, protocol_name: str) -> tuple:
    """construct protocol from yaml file"""
    print(protocol_name)
    protocol = protocol_data["protocols"][protocol_name]
    # Construct t_awake_l
    t_awake_l = []
    for item in protocol["t_awake_l"]:
        print(type(item))
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


class Protocol:
    """
    Class to represent a protocol
    """

    def __init__(self, name: str, definition: str):
        self.name = name
        self.t_awake_l: list[int] = []
        self.t_sleep_l: list[int] = []
        self.definition = definition

    def fill(self, t_awake_l, t_sleep_l):
        """
        Fill the protocol with t_awake_l and t_sleep_l
        """
        self.t_awake_l = t_awake_l
        self.t_sleep_l = t_sleep_l

    def time_sequence(self):
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


def plot_debt(pro: Protocol, protocol_data: dict, box1: BoxManager) -> plt.Figure:
    """
    Get plot for the protocol
    """
    fig = plt.figure(figsize=(20, 10))

    ax = fig.add_subplot(111)  # 111 means 1 row, 1 column, 1st subplot

    df_sleep_debt = calculate_debt(pro)
    # data = list(result)  # [pair for pair in list(result)]

    # df_sleep_debt = pd.DataFrame(data, columns=["time", "l", "s"])
    df_sleep_debt["status"] = df_sleep_debt["time"].apply(
        lambda x: get_status(x, pro.time_sequence())
    )

    dataset_name = protocol_data["protocols"][pro.name]["dataset"]

    ax, df = get_plot(pro, df_sleep_debt, protocol_data, ax=ax)
    save_to_csv(
        box1,
        df,
        BOX_PATH["csvs"] / f"{dataset_name}_class.csv",
        index=False,
    )
    # Set common x and y labels for the figure
    fig.text(0.5, 0.05, "Time (days)", ha="center", va="center", fontsize=14)
    fig.text(
        0.06,
        0.5,
        "Sleep Homeostat values % (impairment \u2192)",
        ha="center",
        va="center",
        rotation="vertical",
        fontsize=14,
    )

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3)
    return fig


def calculate_debt(protocol: Protocol) -> pd.DataFrame:
    """
    Calculate sleep debt for a given protocol from Unified model
    """
    up = 24.1
    unified = True
    initial_values = np.zeros(3)
    s, t, l = [], [], []
    s1, t1, l1 = [], [], []

    for t_awake, t_sleep in zip(protocol.t_awake_l, protocol.t_sleep_l):
        fd = False
        # for FD protocol only
        if "protocol8" in protocol.name:
            fd = (t_awake + t_sleep) > 1440
        if unified:
            t1, s1, l1 = simulate_unified(
                t_awake=t_awake,
                t_sleep=t_sleep,
                s0=initial_values[0],
                l0=initial_values[1],
                t0=initial_values[2],
                forced=fd,
            )
        s += s1
        t += t1
        l += l1

        initial_values[:] = [s1[-1], l1[-1], t1[-1]]

    s = np.array(s) / up
    l = np.array(l) / up

    df_debt = pd.DataFrame({"time": [], "Chronic": [], "Acute": []})
    df_debt["time"] = t  # [item for sublist in t for item in sublist]

    df_debt["l_debt"] = l  # [item for sublist in l for item in sublist]
    df_debt["s_debt"] = s  # [item for sublist in s for item in sublist]

    return df_debt


def protocol_object_list(protocol_list) -> list[Protocol]:
    """
    Create protocol objects
    """
    def_name = "def_2"
    return [Protocol(name, def_name) for name in protocol_list]


def run_sleepdebt_model(box1: BoxManager, protocol_data: dict) -> None:
    """
    Run sleep debt model
    """

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
        t_ae_sl = construct_protocol(protocol_data, protocol.name)
        # print(t_ae_sl[0])
        protocol.fill(t_ae_sl[0], t_ae_sl[1])
        # print(protocol.t_awake_l)
        name = protocol_data["protocols"][protocol.name]["dataset"]
        plot1 = plot_debt(protocol, protocol_data, box1)
        file = io.BytesIO()
        plot1.savefig(file)
        file.seek(0)
        # Upload the figure to Box
        box1.save_file(file, BOX_PATH["plots"] / f"sleep_debt_unified_{name}.png")
        plt.close(plot1)


def zeitzer_sample(box1: BoxManager) -> None:
    """
    some of the Zeitzer subject have different sleep wake schedule.
    So calculating  sleep debt separately
    for those subjects.
    """

    def df_zeitzer(sub, t_awake_l, t_sleep_l) -> None:
        pro = Protocol(f"zeitzer_uncommon_{sub}", "def_2")
        pro.fill(t_awake_l, t_sleep_l)
        pro.time_sequence()
        df_sleep_debt = calculate_debt(pro)
        df_sleep_debt["status"] = df_sleep_debt["time"].apply(
            lambda x: get_status(x, pro.time_sequence())
        )
        save_to_csv(
            box1,
            df_sleep_debt,
            BOX_PATH["csvs"] / f"Zeitzer_Uncommon_{sub}_class.csv",
            index=False,
        )

    file = box1.get_file(BOX_PATH["csvs"] / "zeitzer_uncommon_protocol_from_python.csv")
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


if __name__ == "__main__":
    box = get_box()
    data = get_protocols_from_box(box)
    run_sleepdebt_model(box, data)
    # zeitzer_sample(box)
