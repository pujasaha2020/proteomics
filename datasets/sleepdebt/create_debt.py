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
        path = BOX_PATH["csvs_unified"] / f"def{script_params["defi"]}" / f"{name}.csv"

    else:
        raise ValueError("Invalid model type")
    df["status"] = df["time"].apply(lambda x: get_status(x, pro.time_sequence()))
    df = get_transition(df)

    save_to_csv(
        box,
        df,
        path,
        index=False,
    )
    return df


def get_transition(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get the time difference from the nearest transition time.
    """
    # Identify transitions: awake -> sleep and sleep -> awake
    transitions_w_s = df[(df["status"] == "sleep") & (df["status"].shift(1) == "awake")]
    transitions_s_w = df[(df["status"] == "awake") & (df["status"].shift(1) == "sleep")]

    # Include the first row to handle edge cases
    first_row = df.loc[[0], ["time", "status"]]
    transitions_s_w = pd.concat([first_row, transitions_s_w]).reset_index(drop=True)

    # Reset indices for transitions
    transitions_w_s = transitions_w_s["time"].reset_index(drop=True)
    transitions_s_w = transitions_s_w["time"].reset_index(drop=True)

    # Helper function to compute time differences
    def compute_diff(current_time, current_status):
        if current_status == "sleep":
            preceding_time = transitions_s_w[transitions_s_w >= current_time].min()
            lagger_time = transitions_w_s[transitions_w_s <= current_time].max()
            return current_time - preceding_time, current_time - lagger_time
        if current_status == "awake":
            preceding_time = transitions_w_s[transitions_w_s >= current_time].min()
            lagger_time = transitions_s_w[transitions_s_w <= current_time].max()
            return current_time - lagger_time, current_time - preceding_time
        return pd.NaT, pd.NaT

    # Apply the helper function row-wise
    diffs = df.apply(lambda row: compute_diff(row["time"], row["status"]), axis=1)
    df["waking_up"], df["falling_asleep"] = zip(*diffs)

    return df


def plot_debts(
    df: pd.DataFrame,
    pro: Protocol,
    protocols: dict,
    script_params: dict,
    ax: plt.Axes = None,
) -> plt.Axes:
    """Get plot for the protocols"""
    if ax is None:
        _, ax = plt.subplots(figsize=(20, 5))
    print(pro.time_sequence())
    model = script_params["model"]

    if model == "adenosine":
        ax, ax2 = plot_debt_vs_time_adenosine(pro, df, ax, protocols)
        return ax, ax2
    elif model == "unified":
        ax = plot_debt_vs_time_unified(pro, df, protocols, ax)
        return ax
    else:
        raise ValueError("Invalid model type")

    # ax.set_xlabel("Time (days)", fontsize=16)
    # ax.set_ylabel(axis_title, fontsize=14)


def run_protocols(
    box: BoxManager,
    protocols: dict,
    params: dict,
    script_params: dict,
):
    """Run sleep debt model for all protocols"""
    # model = script_params["model"]
    defi = script_params["defi"]
    plot = script_params["plot"]
    protocols_for_debt = [
        "mri",
        "5day",
        "dinges",
        "faa_ctl",
        "faa_tsd",
        "faa_csrn",
        "faa_csrd",
        "zeitzer",
        "mppg_ctl_10H_3547HY",
        "mppg_ctl_10H_3436HY",
        "mppg_ctl_10H_3369HY42",
        "mppg_ctl_10H_3552HY",
        "mppg_ctl_8H_3776HY",
        "mppg_ctl_8H_3789HY",
        "mppg_ctl_8H_3547HY82",
        "mppg_ctl_8H_3812HY83",
        "mppg_csr_5H_3794HY",
        "mppg_csr_5H_3776HY82",
        "mppg_csr_5H_3665HY82",
        "mppg_csr_5H_29W4HY83",
        "mppg_csr_5H_3828HY",
        "mppg_csr_56H_3608HY",
        "mppg_csr_56H_3445HY",
        "mppg_csr_56H_3665HY",
        "mppg_csr_56H_3619HY",
        "mppg_fd_3453HY73",
        "mppg_fd_2056HY75",
        "mppg_fd_3552HY62",
        "mppg_fd_26P2HY83",
        "mppg_fd_3453HY52",
        "mppg_fd_3536HY83",
        "mppg_fd_3536HY52",
        "mppg_fd_3552HY73",
        "mppg_fd_3557HY61",
    ]

    prot_list = make_protocol_list(protocols_for_debt)
    protocol_objects = make_protocol_object_list(prot_list, defi)

    df_protocols = {}
    for protocol in protocol_objects:
        name = protocols["protocols"][protocol.name]["dataset"]
        print(f"Running sleep debt model for {name}")
        t_ae_sl = make_sleep_wake_tuple(protocols, protocol.name)
        protocol.fill(t_ae_sl[0], t_ae_sl[1])
        df = create_debts(box, protocol, protocols, params, script_params)
        df_protocols[protocol.name] = df
    if plot:
        plot_selected_protocols(box, df_protocols, protocols, script_params)


def plot_selected_protocols(
    box: BoxManager, df_protocols: dict, protocols: dict, script_params: dict
):
    """plot selected protocols"""
    global_min_max = {
        "acute_min": min(df["Acute"].min() for df in df_protocols.values()),
        "acute_max": max(df["Acute"].max() for df in df_protocols.values()),
        "chronic_min": min(df["Chronic"].min() for df in df_protocols.values()),
        "chronic_max": max(df["Chronic"].max() for df in df_protocols.values()),
    }

    protocols_to_plot = [
        "mri",
        "5day",
        "dinges",
        "faa_ctl",
        "faa_tsd",
        "faa_csrn",
        "faa_csrd",
        "mppg_ctl_10H_3547HY",
        "mppg_ctl_8H_3776HY",
        "mppg_csr_5H_3794HY",
        "mppg_csr_56H_3608HY",
        "mppg_fd_3453HY73",
        "mppg_fd_2056HY75",
    ]

    # protocol_lists = make_protocol_list(protocols_to_plot)
    protocol_objects = make_protocol_object_list(
        make_protocol_list(protocols_to_plot), script_params["defi"]
    )

    for i in range(0, len(protocol_objects), 4):
        fig, axes = plt.subplots(
            4,
            1,
            figsize=(20, 5 * 4),
            squeeze=False,
        )  # use sharey=True to share y-axis

        for idx, protocol in enumerate(protocol_objects[i : i + 4]):
            print(f"Plotting {protocol.name}")
            t_ae_sl = make_sleep_wake_tuple(protocols, protocol.name)
            protocol.fill(t_ae_sl[0], t_ae_sl[1])
            protocol.time_sequence()
            if script_params["model"] == "adenosine":
                ax, ax2 = plot_debts(
                    df_protocols[protocol.name],
                    protocol,
                    protocols,
                    script_params,
                    axes[idx, 0],
                )
                ax.set_ylim(
                    [
                        global_min_max["chronic_min"],
                        global_min_max["chronic_max"],
                    ]
                )
                ax.set_yticks([])
                ax.set_yticklabels([])
                ax2.set_ylim(
                    [
                        global_min_max["acute_min"] - 50,
                        global_min_max["acute_max"] + 50,
                    ]
                )
                ax2.set_yticks([])
                ax2.set_yticklabels([])
            else:
                ax = plot_debts(
                    df_protocols[protocol.name],
                    protocol,
                    protocols,
                    script_params,
                    axes[idx, 0],
                )
                ax.set_ylim(
                    [
                        global_min_max["acute_min"] - 50,
                        global_min_max["acute_max"] + 50,
                    ]
                )
                ax.set_yticks([])
                ax.set_yticklabels([])
            ax.set_title(protocols["protocols"][protocol.name]["title"], fontsize=14)

        ax.set_xlabel("Time (days)", fontsize=16)

        if script_params["model"] == "adenosine":
            handles, labels = sum(
                (ax.get_legend_handles_labels() for ax in [axes[0, 0], ax2]),
                start=([], []),
            )

            fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=14)

        else:
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=14)
        file = io.BytesIO()
        fig.savefig(file)
        file.seek(0)
        box.save_file(
            file,
            BOX_PATH["plots"]
            / f"sleep_debt_{script_params["model"]}_def{script_params["defi"]}_{i}.png",
        )

        plt.close(fig)


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
            df = unified.define_acute_chronic(df, pro.definition)
            path = (
                BOX_PATH["csvs_unified"] / f"def{defi}" / f"Zeitzer_Uncommon_{sub}.csv"
            )

        else:
            raise ValueError("Invalid model type")

        df["status"] = df["time"].apply(lambda x: get_status(x, pro.time_sequence()))
        df = get_transition(df)

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


"""
handles1, labels1 = ax.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles = handles1 + handles2
labels = labels1 + labels2

if script_params["model"] == "adenosine":
    axis_title = "Adenosine/Receptor concentration (nM)"
else:
    axis_title = "Sleep Homeostat values % (impairment \u2192)"

fig.text(
    0.06,
    0.5,
    axis_title,
    ha="center",
    va="center",
    rotation="vertical",
    fontsize=14,
)
"""
