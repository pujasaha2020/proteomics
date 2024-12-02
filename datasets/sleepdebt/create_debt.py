"""
This scripts takes model name "Adenosine" or "unified" 
and definition ("def_1", "def_2', "def_3") of acute and chronic sleep debt 
as input and runs the sleep debt model.
"""

import argparse
import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from box.manager import BoxManager
from datasets.sleepdebt.figure import (
    plot_debt_vs_time_adenosine,
    plot_debt_vs_time_unified,
)
from datasets.sleepdebt.model import adenosine, unified
from datasets.sleepdebt.protocol import Protocol
from utils.get import get_box, get_protocols, get_status
from utils.make import (
    make_parameters_dict,
    make_protocol_list,
    make_protocol_object_list,
    make_sleep_wake_tuple,
)
from utils.save import save_to_csv

BOX_PATH = {
    "plots": Path("results/sleepdebt/curves/"),
    "csvs_adenosine": Path("archives/sleepdebt/adenosine/"),
    "csvs_unified": Path("archives/sleepdebt/unified/"),
}


def create_debts(
    box: BoxManager,
    pro: Protocol,
    protocols: dict,
    params: dict,
    script_params: dict,
):
    """create debts for each protocol ands save the csv file"""
    model = script_params["model"]
    name = protocols["protocols"][pro.name]["dataset"]

    if model == "adenosine":
        df = adenosine.calculate_debt(pro, params)
        path = BOX_PATH["csvs_adenosine"] / f"{name}.csv"

    elif model == "unified":
        df = unified.calculate_debt(pro)
        df = unified.define_acute_chronic(df, pro.definition)
        path = BOX_PATH["csvs_unified"] / f"{name}.csv"

    else:
        raise ValueError("Invalid model type")
    df["status"] = df["time"].apply(lambda x: get_status(x, pro.time_sequence()))
    df = get_time_since_transition(df)

    save_to_csv(
        box,
        df,
        path,
        index=False,
    )
    return df


def get_time_since_transition(df: pd.DataFrame) -> pd.DataFrame:
    """
    creating "time since sleep -> awake" and "time since awake -> sleep" csv
    """

    # first get "time since sleep -> awake"
    transitions = df[(df["status"] == "sleep") & (df["status"].shift(1) == "awake")]
    transitions.reset_index(drop=True, inplace=True)
    # Initialize a list to store time differences
    time_diffs = []

    for _, row in df.iterrows():
        # Get the current time
        current_time = row["time"]

        # Find the closest preceding transition time
        preceding_time = transitions["time"][transitions["time"] <= current_time].max()

        # Calculate the difference if a preceding transition is found
        if pd.notna(preceding_time):
            time_diff = current_time - preceding_time
        else:
            time_diff = pd.NaT  # Not applicable if no preceding transition

        time_diffs.append(time_diff)

    # Add time differences as a new column in the data DataFrame
    df["time_since_last_sleep"] = time_diffs

    # first get "time since  awake -> sleep"
    first_row = df.loc[[0], ["time", "status"]]
    transitions = df[(df["status"] == "awake") & (df["status"].shift(1) == "sleep")]
    transitions = pd.concat([first_row, transitions]).reset_index(drop=True)

    # Initialize a list to store time differences
    time_diffs = []

    for _, row in df.iterrows():
        # Get the current time
        current_time = row["time"]

        # Find the closest preceding transition time
        preceding_time = transitions["time"][transitions["time"] <= current_time].max()

        # Calculate the difference if a preceding transition is found
        if pd.notna(preceding_time):
            time_diff = current_time - preceding_time
        else:
            time_diff = pd.NaT  # Not applicable if no preceding transition

        time_diffs.append(time_diff)

    # Add time differences as a new column in the data DataFrame
    df["time_since_last_awake"] = time_diffs

    return df


def plot_debts(
    df: pd.DataFrame,
    pro: Protocol,
    protocols: dict,
    script_params: dict,
) -> plt.Figure:
    """Get plot for the protocol"""

    model = script_params["model"]
    fig = plt.figure(figsize=(20, 10))

    ax = fig.add_subplot(111)
    if model == "adenosine":
        axis_title = "Adenosine/Receptor concentration (nM)"
        ax = plot_debt_vs_time_adenosine(pro, df, ax, protocols)

    elif model == "unified":
        axis_title = "Sleep Homeostat values % (impairment \u2192)"
        ax = plot_debt_vs_time_unified(pro, df, protocols, ax)

    else:
        raise ValueError("Invalid model type")

    fig.text(0.5, 0.05, "Time (days)", ha="center", va="center", fontsize=14)
    fig.text(
        0.06,
        0.5,
        axis_title,
        ha="center",
        va="center",
        rotation="vertical",
        fontsize=14,
    )

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=14)
    return fig


def run_protocols(
    box: BoxManager,
    protocols: dict,
    params: dict,
    script_params: dict,
):
    """Run sleep debt model for all protocols"""
    model = script_params["model"]
    defi = script_params["defi"]
    plot = script_params["plot"]
    prot_list = make_protocol_list()
    protocol_objects = make_protocol_object_list(prot_list, defi)
    for protocol in protocol_objects:
        name = protocols["protocols"][protocol.name]["dataset"]
        print(f"Running sleep debt model for {name}")
        t_ae_sl = make_sleep_wake_tuple(protocols, protocol.name)
        protocol.fill(t_ae_sl[0], t_ae_sl[1])
        df = create_debts(box, protocol, protocols, params, script_params)
        if plot:
            plot1 = plot_debts(df, protocol, protocols, script_params)

            file = io.BytesIO()
            plot1.savefig(file)
            file.seek(0)
            box.save_file(file, BOX_PATH["plots"] / f"sleep_debt_{name}_{model}.png")

            plt.close(plot1)


def run_zeitzer(box: BoxManager, params: dict, model: str, defi: int):
    """
    some of the Zeitzer subject have different sleep wake schedule.
    So calculating  sleep debt separately
    for those subjects.
    """

    def df_zeitzer(sub, t_awake_l, t_sleep_l, model) -> None:
        pro = Protocol(f"zeitzer_uncommon_{sub}", defi)
        pro.fill(t_awake_l, t_sleep_l)
        pro.time_sequence()
        if model == "adenosine":
            df = adenosine.calculate_debt(pro, params)
            path = BOX_PATH["csvs_adenosine"] / f"Zeitzer_Uncommon_{sub}.csv"

        elif model == "unified":
            df = unified.calculate_debt(pro)
            path = BOX_PATH["csvs_unified"] / f"Zeitzer_Uncommon_{sub}.csv"

        else:
            raise ValueError("Invalid model type")

        df["status"] = df["time"].apply(lambda x: get_status(x, pro.time_sequence()))
        df = get_time_since_transition(df)

        save_to_csv(
            box,
            df,
            path,
            index=False,
        )

    file = box.get_file(BOX_PATH["csvs_adenosine"] / "zeitzer_uncommon_protocol.csv")
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

        df_zeitzer(sub, t_awake_l, t_sleep_l, model)


def main(model: str, defi: int, plot: bool, zeitzer: bool):
    """
    Run sleep debt model for all protocols
    """
    box = get_box()
    protocols = get_protocols(box)
    params = make_parameters_dict(box)

    script_params = {"model": model, "defi": defi, "plot": plot, "zeitzer": zeitzer}
    run_protocols(box, protocols, params, script_params)
    if zeitzer:
        run_zeitzer(box, params, model, defi)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run sleep debt model.")
    parser.add_argument(
        "--model",
        type=str,
        help="model to run",
        default="adenosine",
    )
    # for unified model you need to give the definition of acute and chronic.
    # For adensoine model it does not matter.
    parser.add_argument(
        "--defi",
        type=int,
        help="Definition for chronic and acute sleep debt",
        default=2,
    )

    parser.add_argument(
        "--plot",
        action="store_true",
        help="if specified it will plot the sleep debt",
    )

    parser.add_argument(
        "--zeitzer",
        action="store_true",
        help="Run sleep debt model for zeitzer uncommon subjects."
        + "if not specified it will not run",
    )
    args = parser.parse_args()

    main(**vars(args))
