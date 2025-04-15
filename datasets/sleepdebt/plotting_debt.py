# plot selected protocols

import argparse
import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from box.manager import BoxManager
from datasets.sleepdebt.figure import (
    plot_debt_vs_time_adenosine,
    plot_debt_vs_time_both,
    plot_debt_vs_time_unified,
)
from datasets.sleepdebt.protocol import Protocol
from utils.get import get_box, get_protocols
from utils.make import (
    make_protocol_list,
    make_protocol_object_list,
    make_sleep_wake_tuple,
)

PATH = {
    "plots": Path("results/sleepdebt/curves/"),
    "csvs": Path("archives/sleepdebt/adenosine/"),
    "csvs_unified_def2": Path("archives/sleepdebt/unified/def2/"),
    "csvs_unified_def1": Path("archives/sleepdebt/unified/def1/"),
}


def get_df(box: BoxManager, model: str, pro_name: str, defi: int):
    """get the model data"""
    adenosine_file = box.get_file(PATH["csvs"] / f"{pro_name}.csv")
    unified_file = box.get_file(PATH[f"csvs_unified_def{defi}"] / f"{pro_name}.csv")
    df_adenosine = pd.read_csv(adenosine_file)
    df_unified = pd.read_csv(unified_file)

    if model == "adenosine":
        return df_adenosine
    if model == "unified":
        return df_unified
    if model == "both":
        df_adenosine.rename(
            columns={"Chronic": "adenosine_Chronic", "Acute": "adenosine_Acute"},
            inplace=True,
        )

        df_unified.rename(
            columns={"Chronic": "unified_Chronic", "Acute": "unified_Acute"},
            inplace=True,
        )
        df_both = pd.merge(left=df_adenosine, right=df_unified, on="time", how="inner")

        return df_both


def plot_adenosine(
    box: BoxManager,
    protocols: list,
):
    """plot selected protocols"""
    protocol_dict = get_protocols(box)
    pro_obj_list = make_protocol_object_list(make_protocol_list(protocols), 2)

    for i in range(0, len(protocols), 4):
        fig, axes = plt.subplots(
            4,
            1,
            figsize=(40, 5 * 4),
            squeeze=False,
        )  # use sharey=True to share y-axis

        for idx, pro in enumerate(pro_obj_list[i : i + 4]):
            print(f"Plotting {pro.name}")
            df = get_df(
                box, "adenosine", protocol_dict["protocols"][pro.name]["dataset"], 2
            )
            t_ae_sl = make_sleep_wake_tuple(protocol_dict, pro.name)
            pro.fill(t_ae_sl[0], t_ae_sl[1])
            pro.time_sequence()
            ax, ax2 = plot_debt_vs_time_adenosine(pro, df, axes[idx, 0], protocol_dict)
            ax.set_title(protocol_dict["protocols"][pro.name]["title"], fontsize=24)

        ax.set_xlabel("Time (days)", fontsize=24)
        handles_labels = [ax.get_legend_handles_labels() for ax in [axes[0, 0], ax2]]
        handles = [h for hl in handles_labels for h in hl[0]]
        labels = [l for hl in handles_labels for l in hl[1]]
        fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=24)
        file = io.BytesIO()
        fig.savefig(file)
        file.seek(0)
        box.save_file(
            file,
            PATH["plots"] / f"sleep_debt_adenosine_{i}_test.png",
        )

        plt.close(fig)


def plot_unified(box: BoxManager, protocols: list, defi: int):
    """plot selected protocols"""
    protocol_dict = get_protocols(box)
    pro_obj_list = make_protocol_object_list(make_protocol_list(protocols), defi)

    for i in range(0, len(protocols), 4):
        fig, axes = plt.subplots(
            4,
            1,
            figsize=(40, 5 * 4),
            squeeze=False,
        )  # use sharey=True to share y-axis

        for idx, pro in enumerate(pro_obj_list[i : i + 4]):
            print(f"Plotting {pro.name}")
            df = get_df(
                box, "unified", protocol_dict["protocols"][pro.name]["dataset"], defi
            )
            print(df.columns)
            t_ae_sl = make_sleep_wake_tuple(protocol_dict, pro.name)
            pro.fill(t_ae_sl[0], t_ae_sl[1])
            pro.time_sequence()
            ax = plot_debt_vs_time_unified(pro, df, axes[idx, 0], protocol_dict)
            ax.set_title(protocol_dict["protocols"][pro.name]["title"], fontsize=14)

        ax.set_xlabel("Time (days)", fontsize=16)
        handles_labels = [ax.get_legend_handles_labels() for ax in [axes[0, 0]]]
        handles = [h for hl in handles_labels for h in hl[0]]
        labels = [l for hl in handles_labels for l in hl[1]]
        fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=14)
        file = io.BytesIO()
        fig.savefig(file)
        file.seek(0)
        box.save_file(
            file,
            PATH["plots"] / f"sleep_debt_unified_{i}_definition{defi}_test.png",
        )

        plt.close(fig)


def plot_both(box: BoxManager, protocols: list, defi: int):
    """plot selected protocols"""
    protocol_dict = get_protocols(box)
    pro_obj_list = make_protocol_object_list(make_protocol_list(protocols), defi)

    for i in range(0, len(protocols), 4):
        fig, axes = plt.subplots(
            4,
            1,
            figsize=(40, 5 * 4),
            squeeze=False,
        )  # use sharey=True to share y-axis

        for idx, pro in enumerate(pro_obj_list[i : i + 4]):
            print(f"Plotting {pro.name}")
            df = get_df(
                box, "both", protocol_dict["protocols"][pro.name]["dataset"], defi
            )
            print(df.columns)
            t_ae_sl = make_sleep_wake_tuple(protocol_dict, pro.name)
            pro.fill(t_ae_sl[0], t_ae_sl[1])
            pro.time_sequence()
            (ax, ax2, ax3, ax4) = plot_debt_vs_time_both(
                pro, df, axes[idx, 0], protocol_dict
            )
            ax.set_title(protocol_dict["protocols"][pro.name]["title"], fontsize=14)

        ax.set_xlabel("Time (days)", fontsize=16)
        handles_labels = [
            ax.get_legend_handles_labels() for ax in [axes[0, 0], ax2, ax3, ax4]
        ]
        handles = [h for hl in handles_labels for h in hl[0]]
        labels = [l for hl in handles_labels for l in hl[1]]
        fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=14)
        file = io.BytesIO()
        fig.savefig(file)
        file.seek(0)
        box.save_file(
            file,
            PATH["plots"] / f"sleep_debt_both_{i}_definition{defi}test.png",
        )

        plt.close(fig)


def main(protocols: list, defi: int, model: str):
    """plot selected protocols"""
    box = get_box()

    # df_unified = box.get_file(PATH[f"csvs_unified_def{defi}"] / f"{protocol}.csv")

    # script_params = {"model": model, "defi": defi}
    if model == "adenosine":
        plot_adenosine(box, protocols)
    elif model == "unified":
        plot_unified(box, protocols, defi)
    elif model == "both":
        plot_both(box, protocols, defi)
    else:
        raise ValueError("Invalid model type")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="plot sleep debt data.")
    parser.add_argument(
        "--model",
        type=str,
        help="model to run",
        default="both",
    )  # "adenosine", "unified", "both"

    # for unified model you need to give the definition of acute and chronic.
    # For adensoine model it does not matter.
    parser.add_argument(
        "--defi",
        type=int,
        help="Definition for chronic and acute sleep debt",
        default=2,
    )

    parser.add_argument(
        "--protocols",
        nargs="+",
        help="list of protocols to plot",
        type=str,
        default=["mri"],
    )
    # here are the options for the protocols, you can make a list of them and
    #  pass them as argument.
    # Note some of them are subject specific and some are same for all subjects.
    #     "mri",
    #     "5day",
    #     "dinges",
    #     "faa_ctl",
    #     "faa_tsd",
    #     "faa_csrn",
    #     "faa_csrd",
    #     "mppg_ctl_10H_3547HY",
    #     "mppg_ctl_8H_3776HY",
    #     "mppg_csr_5H_3794HY",
    #     "mppg_csr_56H_3608HY",

    #     "mppg_fd_3453HY73",
    #    "mppg_fd_3557HY61",
    #      "mppg_fd_2056HY75",
    # "mppg_fd_3552HY62",
    # "mppg_fd_26P2HY83",
    # "mppg_fd_3453HY52",
    # "mppg_fd_3536HY83",
    # "mppg_fd_3536HY52",
    # "mppg_fd_3552HY73",

    args = parser.parse_args()

    main(**vars(args))
