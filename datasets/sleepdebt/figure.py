""" Plotting tools for sleep debt calculation """

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.get import get_blood_collection_time, get_title

# from scipy import signal

# pylint: disable=R0801
if TYPE_CHECKING:
    # Import only during type checking to avoid circular imports
    from datasets.sleepdebt.protocol import Protocol


# def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
def plot_debt_vs_time_adenosine(
    pro: Protocol, df: pd.DataFrame, ax, protocols: dict
) -> plt.Axes:
    """getting the plot for the sleep debt for adenosine model"""
    ax2 = ax.twinx()  # type:ignore
    ax2.plot(
        df["time"] / (60.0 * 24),
        df["Acute"],
        # label="Acute (A_tot)",
        color="red",
    )
    ax2.set_ylabel("Acute", color="red", fontsize=14)

    ax.plot(
        df["time"] / (60.0 * 24),
        df["Chronic"],
        # label="Chronic(R1_tot)",
        color="green",
    )
    ax.set_ylabel("Chronic", color="green", fontsize=14)

    ax.grid()
    ax.set_title(get_title(pro, protocols), fontsize=16)

    # ax.set_xlim(
    #    [11, df_sleep_debt["time"][len(df_sleep_debt["time"]) - 1] / (60.0 * 24)]
    # )
    ax.set_xlim((11, df["time"].iloc[-1] / (60.0 * 24)))
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

    xcoords = get_blood_collection_time(pro, protocols)
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
            ticks=np.arange(11, int(max(df["time"]) / (60.0 * 24)) + 1, 2),
            labels=np.arange(0, int(max(df["time"]) / (60.0 * 24) - 11) + 1, 2),
        )
    else:
        ax.set_xticks(
            ticks=np.arange(11, int(max(df["time"]) / (60.0 * 24)) + 1),
            labels=np.arange(0, int(max(df["time"]) / (60.0 * 24) - 11) + 1),
        )
    return ax


# def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
def plot_debt_vs_time_unified(
    pro: Protocol, df: pd.DataFrame, protocol_data: dict, ax: plt.Axes
) -> plt.Axes:
    """getting the plot for the sleep debt for unified model"""

    ax.plot(
        df["time"] / (60.0 * 24),
        df["Chronic"] * 100,
        label="Sleep debt (chronic)",
        color="black",
    )
    ax.plot(
        df["time"] / (60.0 * 24),
        (df["Acute"]) * 100,
        label="Sleep debt (acute)",
        color="red",
    )
    ax.plot(
        df["time"] / (60.0 * 24),
        df["l_debt"] * 100,
        label="Sleep debt (L)",
        color="green",
    )
    ax.plot(
        df["time"] / (60.0 * 24),
        df["s_debt"] * 100,
        label="Sleep homeostat (S)",
        color="orange",
        linestyle="--",
    )
    ax.grid()
    ax.set_xlabel("Time (days)", fontsize=12)
    ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=10)

    ax.set_xlim((11, df["time"].iloc[-1] / (60.0 * 24)))
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
        ticks=np.arange(11, int(max(df["time"]) / (60.0 * 24)) + 1),
        labels=np.arange(0, int(max(df["time"]) / (60.0 * 24) - 11) + 1),
    )

    return ax
