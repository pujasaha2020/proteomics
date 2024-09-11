""" Plotting tools for sleep debt calculation """

# pylint: disable=R0801

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# from scipy import signal
from scipy import interpolate
from scipy.signal import find_peaks

from utils.get import get_box, get_protocols_from_box

if TYPE_CHECKING:
    # Import only during type checking to avoid circular imports
    from datasets.sleepdebt.unified_model.sleepdebt_calculation import Protocol


# def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
def get_plot(pro: Protocol, df_sleep_debt: pd.DataFrame, ax: plt.Axes) -> tuple:
    """getting the plot for the sleep debt"""

    if pro.definition == "def_1":
        lower_envelope = get_lower_envelope(df_sleep_debt)
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            lower_envelope * 100,
            label="Sleep debt (chronic)",
            color="black",
        )
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            (df_sleep_debt["l_debt"] - lower_envelope) * 100,
            label="Sleep debt (acute)",
            color="red",
        )
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            df_sleep_debt["l_debt"] * 100,
            label="Sleep debt (L)",
            color="green",
        )
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            df_sleep_debt["s_debt"] * 100,
            label="Sleep homeostat (S)",
            color="orange",
            linestyle="--",
        )
        ax.grid()
        ax.set_xlabel("Time (days)", fontsize=12)
        ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=10)
        new = df_sleep_debt.copy()
        new["Chronic"] = lower_envelope
        new["Acute"] = df_sleep_debt["l"] - lower_envelope

    elif pro.definition == "def_2":
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            df_sleep_debt["l_debt"] * 100,
            label="Sleep debt (chronic) (L)",
            color="green",
        )
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            df_sleep_debt["s_debt"] * 100,
            label="Sleep homeostat (S)",
            color="orange",
            linestyle="--",
        )
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            (df_sleep_debt["s_debt"] - df_sleep_debt["l_debt"]) * 100,
            label="Sleep debt (acute) (S-L)",
            color="red",
        )
        ax.grid()
        new = df_sleep_debt.copy()
        new["Chronic"] = df_sleep_debt["l_debt"]
        new["Acute"] = df_sleep_debt["s_debt"] - df_sleep_debt["l_debt"]

        # ax.set_xlabel("Time (days)", fontsize=12)
        # ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=10)

    elif pro.definition == "def_3":
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            df_sleep_debt["l_debt"] * 100,
            label="Sleep debt (chronic) (L)",
            color="green",
        )
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            df_sleep_debt["s_debt"] * 100,
            label="Sleep homeostat (S)",
            color="orange",
            linestyle="--",
        )
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            (df_sleep_debt["s_debt"] - df_sleep_debt["l_debt"]) * 100,
            label="Sleep debt (acute) (S-L)",
            color="red",
        )
        ax.grid()
        new = df_sleep_debt.copy()
        new["Chronic"] = df_sleep_debt["l_debt"]
        new["Acute"] = df_sleep_debt["s_debt"] - df_sleep_debt["l_debt"]
        # ax.set_xlabel("Time (days)", fontsize=10)
        # ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=12)

    else:
        print("Invalid definition")
    ax.set_title(get_title(pro), fontsize=6)

    ax.set_xlim(
        [11, df_sleep_debt["time"][len(df_sleep_debt["time"]) - 1] / (60.0 * 24)]
    )
    for i in range(1, len(pro.time_sequence()), 2):
        if i == 1:
            ax.axvspan(
                pro.time_sequence()[i] / (60 * 24),
                pro.time_sequence()[i + 1] / (60 * 24),
                facecolor="grey",
                label="Sleep episodes",
                alpha=0.3,
            )
        ax.axvspan(
            pro.time_sequence()[i] / (60 * 24),
            pro.time_sequence()[i + 1] / (60 * 24),
            facecolor="grey",
            alpha=0.3,
        )
    xcoords = get_blood_collection_time(pro)
    if len(xcoords) == 0:
        print("No blood collection time")
    else:
        ax.axvline(
            x=xcoords[0],
            linestyle="dashed",
            color="blue",
            label="Blood collected",
            alpha=0.4,
        )

        for xc in xcoords[1 : (len(xcoords))]:
            ax.axvline(x=xc, linestyle="dashed", color="blue", alpha=0.4)

    ax.tick_params(
        axis="both", which="major", labelsize=8
    )  # Adjust the font size as needed
    ax.set_xticks(
        ticks=np.arange(11, int(max(df_sleep_debt["time"]) / (60.0 * 24)) + 1),
        labels=np.arange(0, int(max(df_sleep_debt["time"]) / (60.0 * 24) - 11) + 1),
    )

    return ax, new


def get_lower_envelope(df_sleep_debt: pd.DataFrame) -> np.array:
    """getting lower envelope for definition 1"""
    # peaks, _ = find_peaks(df_sleep_debt["l"])
    trough_index, _ = find_peaks(-df_sleep_debt["l"])

    time_trough = [0]
    trough = [0]
    for i in trough_index:
        time_trough.append(df_sleep_debt["time"][i])
        trough.append(df_sleep_debt["l"][i])

    time_trough.append(df_sleep_debt.iloc[len(df_sleep_debt[["time"]]) - 1, 0])
    trough.append(df_sleep_debt.iloc[len(df_sleep_debt[["time"]]) - 1, 1])

    f = interpolate.interp1d(time_trough, trough)

    xnew = df_sleep_debt[
        "time"
    ]  # np.array(df_sleep_debt.iloc[:, 0]) #df_sleep_debt[["time"]]
    ynew = f(xnew)  # use interpolation function returned by `interp1d`
    return ynew


def get_title(pro: Protocol) -> str:
    """getting title for the plot"""
    return DATA["protocols"][pro.name]["title"]


def get_blood_collection_time(pro: Protocol) -> list:
    """getting blood collection time"""
    return DATA["protocols"][pro.name]["blood_sample_time"]


box = get_box()
DATA = get_protocols_from_box(box)
