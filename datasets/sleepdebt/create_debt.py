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
    "plots_adenosine": Path(
        "results/sleepdebt/sleepdebt_curves/ligand_receptor_model/"
    ),
    "plots_unified": Path("results/sleepdebt/sleepdebt_curves/unified_model/"),
    "csvs_adenosine": Path(
        "archives/sleep_debt/sleepdebt_data/ligand_receptor_model/sleepdebt/"
    ),
    "csvs_unified": Path("archives/sleep_debt/sleepdebt_data/unified_model/sleepdebt/"),
}


def create_debt(
    pro: Protocol,
    protocol_data: dict,
    box1: BoxManager,
    model_params: dict,
    model: str = "adenosine",
) -> plt.Figure:
    """Get plot for the protocol"""
    fig = plt.figure(figsize=(20, 10))

    ax = fig.add_subplot(111)  # 111 means 1 row, 1 column, 1st subplot
    dataset_name = protocol_data["protocols"][pro.name]["dataset"]
    if model == "adenosine":
        df_sleep_debt = adenosine.calculate_debt(pro, model_params)
        path = BOX_PATH["csvs_adenosine"] / f"{dataset_name}_class.csv"
        axis_title = "Adenosine/Receptor concentration (nM)"
        ax = plot_debt_vs_time_adenosine(pro, df_sleep_debt, ax, protocol_data)

    elif model == "unified":
        df_sleep_debt = unified.calculate_debt(pro)
        path = BOX_PATH["csvs_unified"] / f"{dataset_name}_class.csv"
        axis_title = "Sleep Homeostat values % (impairment \u2192)"
        ax, df_sleep_debt = plot_debt_vs_time_unified(
            pro, df_sleep_debt, protocol_data, ax
        )

    else:
        raise ValueError("Invalid model type")

    df_sleep_debt["status"] = df_sleep_debt["time"].apply(
        lambda x: get_status(x, pro.time_sequence())
    )

    save_to_csv(
        box1,
        df_sleep_debt,
        path,
        index=False,
    )

    # Set common x and y labels for the figure
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


def run_sleepdebt_model(
    protocol_data: dict,
    box1: BoxManager,
    model_params: dict,
    model: str = "adenosine",
    definition: str = "def_2",
):
    """Run sleep debt model for all protocols"""

    prot_list = make_protocol_list()
    protocol_objects = make_protocol_object_list(prot_list, definition)
    for protocol in protocol_objects:
        t_ae_sl = make_sleep_wake_tuple(protocol_data, protocol.name)
        protocol.fill(t_ae_sl[0], t_ae_sl[1])
        name = protocol_data["protocols"][protocol.name]["dataset"]
        plot1 = create_debt(protocol, protocol_data, box1, model_params, model)

        file = io.BytesIO()
        plot1.savefig(file)
        file.seek(0)
        if model == "adenosine":
            box1.save_file(file, BOX_PATH["plots_adenosine"] / f"sleep_debt_{name}.png")
        elif model == "unified":
            box1.save_file(file, BOX_PATH["plots_unified"] / f"sleep_debt_{name}.png")
        else:
            raise ValueError("Invalid model type")
        plt.close(plot1)


def run_zeitzer_sample(
    box1: BoxManager,
    model_params: dict,
    model: str = "adenosine",
    definition: str = "def_2",
):
    """
    some of the Zeitzer subject have different sleep wake schedule.
    So calculating  sleep debt separately
    for those subjects.
    """

    def df_zeitzer(sub, t_awake_l, t_sleep_l) -> None:
        pro = Protocol(f"zeitzer_uncommon_{sub}", definition)
        pro.fill(t_awake_l, t_sleep_l)
        pro.time_sequence()
        if model == "adenosine":
            df_sleep_debt = adenosine.calculate_debt(pro, model_params)
            path = BOX_PATH["csvs_adenosine"] / f"Zeitzer_Uncommon_{sub}_class.csv"

        elif model == "unified":
            df_sleep_debt = unified.calculate_debt(pro)
            path = BOX_PATH["csvs_unified"] / f"Zeitzer_Uncommon_{sub}_class.csv"

        else:
            raise ValueError("Invalid model type")

        df_sleep_debt["status"] = df_sleep_debt["time"].apply(
            lambda x: get_status(x, pro.time_sequence())
        )
        save_to_csv(
            box1,
            df_sleep_debt,
            path,
            index=False,
        )

    file = box1.get_file(
        BOX_PATH["csvs_adenosine"] / "zeitzer_uncommon_protocol_from_python.csv"
    )
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
        "--definition",
        type=str,
        help="Definition for chronic and acute sleep debt",
        default="def_2",
    )
    args = parser.parse_args()
    # Validate model type
    valid_models = ["adenosine", "unified"]  # Add all valid model types here
    if args.model not in valid_models:
        raise ValueError(f"Invalid model type: {args.model}.")

    box = get_box()
    data = get_protocols(box)
    params = make_parameters_dict(box)
    run_sleepdebt_model(data, box, params, **vars(args))
    # if you want to run the zeitzer sample
    run_zeitzer_sample(box, params, **vars(args))
