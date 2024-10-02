""" Plotting tools for sleep debt calculation """

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate
from scipy.signal import find_peaks

from utils.get import get_blood_collection_time, get_title

# from scipy import signal

# pylint: disable=R0801
if TYPE_CHECKING:
    # Import only during type checking to avoid circular imports
    from datasets.sleepdebt.class_def import Protocol


# def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
def plot_debt_vs_time_adenosine(
    pro: Protocol, df_sleep_debt: pd.DataFrame, ax, data
) -> plt.Axes:
    """getting the plot for the sleep debt"""
    ax2 = ax.twinx()  # type:ignore
    ax2.plot(
        df_sleep_debt["time"] / (60.0 * 24),
        df_sleep_debt["Acute"],
        # label="Acute (A_tot)",
        color="red",
    )
    ax2.set_ylabel("Acute", color="red", fontsize=14)

    ax.plot(
        df_sleep_debt["time"] / (60.0 * 24),
        df_sleep_debt["Chronic"],
        # label="Chronic(R1_tot)",
        color="green",
    )
    ax.set_ylabel("Chronic", color="green", fontsize=14)

    ax.grid()
    ax.set_title(get_title(pro, data), fontsize=16)

    # ax.set_xlim(
    #    [11, df_sleep_debt["time"][len(df_sleep_debt["time"]) - 1] / (60.0 * 24)]
    # )
    ax.set_xlim((11, df_sleep_debt["time"].iloc[-1] / (60.0 * 24)))
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

    xcoords = get_blood_collection_time(pro, data)
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

    if pro.name in ("protocol5", "protocol6"):
        ax.set_xticks(
            ticks=np.arange(11, int(max(df_sleep_debt["time"]) / (60.0 * 24)) + 1, 2),
            labels=np.arange(
                0, int(max(df_sleep_debt["time"]) / (60.0 * 24) - 11) + 1, 2
            ),
        )
    else:
        ax.set_xticks(
            ticks=np.arange(11, int(max(df_sleep_debt["time"]) / (60.0 * 24)) + 1),
            labels=np.arange(0, int(max(df_sleep_debt["time"]) / (60.0 * 24) - 11) + 1),
        )
    return ax


# def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
def plot_debt_vs_time_unified(
    pro: Protocol, df_sleep_debt: pd.DataFrame, protocol_data: dict, ax: plt.Axes
) -> tuple:
    """getting the plot for the sleep debt"""

    if pro.definition == "def_1":
        lower_envelope = plot_lower_envelope(df_sleep_debt)
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
    ax.set_title(get_title(pro, protocol_data), fontsize=6)

    ax.set_xlim((11, df_sleep_debt["time"].iloc[-1] / (60.0 * 24)))
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
    xcoords = get_blood_collection_time(pro, protocol_data)
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


def plot_lower_envelope(df_sleep_debt: pd.DataFrame) -> np.ndarray:
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
