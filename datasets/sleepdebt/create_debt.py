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

    # drop duplicates, duplicates arise due to the edge case of the time difference, i.e
    # last value of awake is same as first value of sleep and vice versa.
    df = df.drop_duplicates(subset=["time"], keep="first")
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


def run_protocols(
    box: BoxManager,
    protocols: dict,
    params: dict,
    script_params: dict,
):
    """Run sleep debt model for all protocols"""
    # model = script_params["model"]
    defi = script_params["defi"]
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

    for protocol in protocol_objects:
        name = protocols["protocols"][protocol.name]["dataset"]
        print(f"Running sleep debt model for {name}")
        t_ae_sl = make_sleep_wake_tuple(protocols, protocol.name)
        protocol.fill(t_ae_sl[0], t_ae_sl[1])
        protocol.time_sequence()
        if name == "mppg_csr_56H_3665HY":
            print(protocol.time_sequence())
        create_debts(box, protocol, protocols, params, script_params)


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
        df = df.drop_duplicates(subset=["time"], keep="first")

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


def main(model: str, defi: int, zeitzer: bool):
    """
    Run sleep debt model for all protocols
    """
    box = get_box()
    protocols = get_protocols(box)
    params = make_parameters_dict(box)

    script_params = {"model": model, "defi": defi, "zeitzer": zeitzer}
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
        "--zeitzer",
        action="store_true",
        help="Run sleep debt model for zeitzer uncommon subjects."
        + "if not specified it will not run",
    )
    args = parser.parse_args()

    main(**vars(args))
