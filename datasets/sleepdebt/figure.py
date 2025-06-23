"""Plotting tools for sleep debt calculation"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from utils.get import get_blood_collection_time

# from scipy import signal

# pylint: disable=R0801
if TYPE_CHECKING:
    # Import only during type checking to avoid circular imports
    from datasets.sleepdebt.protocol import Protocol


# def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
def plot_debt_vs_time_adenosine(
    pro: Protocol, df: pd.DataFrame, ax, protocols: dict
) -> tuple:
    """getting the plot for the sleep debt for adenosine model"""
    ax.plot(
        df["time"] / (60.0 * 24),
        df["Chronic"],
        label="Chronic",
        color="green",
    )
    ax2 = ax.twinx()  # type:ignore
    ax2.plot(
        df["time"] / (60.0 * 24),
        df["Acute"],
        label="Acute",
        color="red",
    )
    ax2.set_ylabel("Acute", color="red", fontsize=30)

    ax.set_ylabel("Chronic", color="green", fontsize=30)

    # ax.grid()
    # ax.set_title(get_title(pro, protocols), fontsize=16)

    # ax.set_xlim(
    #    [11, df_sleep_debt["time"][len(df_sleep_debt["time"]) - 1] / (60.0 * 24)]
    # )

    substrs = {"5H", "56H", "8H", "10H", "fd"}
    print(pro.name)

    if any(sub in pro.name for sub in substrs):
        ax.set_xlim((11, df["time"].iloc[-1] / (60.0 * 24)))
    else:
        ax.set_xlim((11, df["time"].iloc[-1] / (60.0 * 24)))
    x_min, x_max = ax.get_xlim()

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
        mid_point = (
            (pro.time_sequence()[i + 1] / (60 * 24))
            + (pro.time_sequence()[i] / (60 * 24))
        ) / 2
        if x_min <= mid_point <= x_max:
            ax.text(
                mid_point,  # X-coordinate at the middle of the grey part
                ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.2,
                f"{(
                    (pro.time_sequence()[i + 1] )
                    - (pro.time_sequence()[i])
                ):.2f} mins",
                color="black",
                ha="center",
                va="center",
                rotation="vertical",
                fontsize=10,
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

    # ax.tick_params(axis="x", which="major", labelsize=8)
    """
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
    
    """
    if any(sub in pro.name for sub in substrs):
        ax.set_xticks(
            ticks=np.arange(11, int(max(df["time"]) / (60.0 * 24)) + 1, 1),
            labels=np.arange(0, int(max(df["time"]) / (60.0 * 24) - 11) + 1, 1),
        )
    else:
        ax.set_xticks(
            ticks=np.arange(11, int(max(df["time"]) / (60.0 * 24)) + 1),
            labels=np.arange(0, int(max(df["time"]) / (60.0 * 24) - 11) + 1),
        )

    ax.tick_params(axis="both", which="major", labelsize=30)
    ax2.tick_params(axis="both", which="major", labelsize=30)
    return ax, ax2


# def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
def plot_debt_vs_time_unified(
    pro: Protocol, df: pd.DataFrame, ax: plt.Axes, protocol_data: dict, definition: int
) -> plt.Axes:
    """getting the plot for the sleep debt for unified model"""
    if definition == 1:
        ax.plot(
            df["time"] / (60.0 * 24),
            df["Chronic"],
            label="Sleep debt (chronic)",
            color="black",
        )
    else:
        ax.plot(
            df["time"] / (60.0 * 24),
            df["Chronic"],
            label="Sleep debt (chronic)/Sleep debt (L)",
            color="green",
        )
    ax.plot(
        df["time"] / (60.0 * 24),
        df["Acute"],
        label="Sleep debt (acute)",
        color="red",
    )
    if definition == 1:
        ax.plot(
            df["time"] / (60.0 * 24),
            df["l_debt"],
            label="Sleep debt (L)",
            color="green",
        )
    ax.plot(
        df["time"] / (60.0 * 24),
        df["s_debt"],
        label="Sleep homeostat (S)",
        color="orange",
        linestyle="--",
    )

    # ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=30)

    substrs = {"5H", "56H", "8H", "10H", "FD"}
    print(pro.name)

    if any(sub in pro.name for sub in substrs):
        ax.set_xlim((11, df["time"].iloc[-1] / (60.0 * 24)))
    else:
        ax.set_xlim((11, df["time"].iloc[-1] / (60.0 * 24)))

    x_min, x_max = ax.get_xlim()

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
        mid_point = (
            (pro.time_sequence()[i + 1] / (60 * 24))
            + (pro.time_sequence()[i] / (60 * 24))
        ) / 2
        if x_min <= mid_point <= x_max:
            ax.text(
                mid_point,  # X-coordinate at the middle of the grey part
                ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.2,
                f"{(
                    (pro.time_sequence()[i + 1] )
                    - (pro.time_sequence()[i])
                ):.2f} mins",
                color="black",
                ha="center",
                va="center",
                rotation="vertical",
                fontsize=15,
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

    if any(sub in pro.name for sub in substrs):
        ax.set_xticks(
            ticks=np.arange(11, int(max(df["time"]) / (60.0 * 24)) + 1, 1),
            labels=np.arange(0, int(max(df["time"]) / (60.0 * 24) - 11) + 1, 1),
        )
    else:
        ax.set_xticks(
            ticks=np.arange(11, int(max(df["time"]) / (60.0 * 24)) + 1),
            labels=np.arange(0, int(max(df["time"]) / (60.0 * 24) - 11) + 1),
        )

    ax.tick_params(axis="both", which="major", labelsize=30)

    return ax


def plot_debt_vs_time_both(
    pro: Protocol, df: pd.DataFrame, ax, protocols: dict
) -> tuple:
    """getting the plot for the sleep debt for adenosine model"""
    ax.plot(
        df["time"] / (60.0 * 24),
        df["adenosine_Chronic"],
        label="Adenosine Chronic",
        linestyle="-",
        color="green",
    )
    ax.set_ylabel("Adenosine Chronic", color="green", fontsize=14)
    ax.tick_params(axis="y", labelcolor="green")

    ax2 = ax.twinx()  # type:ignore
    ax2.plot(
        df["time"] / (60.0 * 24),
        df["adenosine_Acute"],
        label="Adenosine Acute",
        linestyle="-",
        color="red",
    )
    ax2.set_ylabel("Adenosine Acute", color="red", fontsize=14)
    ax2.tick_params(axis="y", labelcolor="red")

    ax3 = ax.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.plot(
        df["time"] / (60.0 * 24),
        df["unified_Chronic"],
        label="Unified Chronic",
        linestyle="-.",
        color="green",
    )
    ax3.set_ylabel("Unified Chronic", color="green", fontsize=14)
    ax3.tick_params(axis="y", labelcolor="green")

    ax4 = ax.twinx()
    ax4.spines["right"].set_position(("outward", 140))
    ax4.plot(
        df["time"] / (60.0 * 24),
        df["unified_Acute"] / df["unified_Acute"].sum(),
        label="Unified Acute",
        linestyle="-.",
        color="red",
    )
    ax4.set_ylabel("Unified Acute", color="red", fontsize=14)
    ax4.tick_params(axis="y", labelcolor="red")

    # Apply the formatter to the axes with scientific notation
    ax4.yaxis.set_major_formatter(FuncFormatter(decimal_formatter))

    substrs = {"5H", "56H", "8H", "10H", "fd"}
    print(pro.name)

    if any(sub in pro.name for sub in substrs):
        ax.set_xlim((11, df["time"].iloc[-1] / (60.0 * 24)))
    else:
        ax.set_xlim((11, df["time"].iloc[-1] / (60.0 * 24)))

    x_min, x_max = ax.get_xlim()
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

        mid_point = (
            (pro.time_sequence()[i + 1] / (60 * 24))
            + (pro.time_sequence()[i] / (60 * 24))
        ) / 2
        if x_min <= mid_point <= x_max:
            ax.text(
                mid_point,  # X-coordinate at the middle of the grey part
                ax.get_ylim()[0] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.2,
                f"{(
                    (pro.time_sequence()[i + 1] )
                    - (pro.time_sequence()[i])
                ):.2f} mins",
                color="black",
                ha="center",
                va="center",
                rotation="vertical",
                fontsize=10,
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

    # ax.tick_params(axis="x", which="major", labelsize=8)
    """
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
    
    """
    if any(sub in pro.name for sub in substrs):
        ax.set_xticks(
            ticks=np.arange(11, int(max(df["time"]) / (60.0 * 24)) + 1, 1),
            labels=np.arange(0, int(max(df["time"]) / (60.0 * 24) - 11) + 1, 1),
        )
    else:
        ax.set_xticks(
            ticks=np.arange(11, int(max(df["time"]) / (60.0 * 24)) + 1),
            labels=np.arange(0, int(max(df["time"]) / (60.0 * 24) - 11) + 1),
        )

    return ax, ax2, ax3, ax4


# Function to format the y-axis ticks in decimal format
def decimal_formatter(x, pos):
    return f"{x:.6f}"  # Adjust the number of decimal places as needed
