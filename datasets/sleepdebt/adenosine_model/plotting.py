""" Plotting tools for sleep debt calculation """

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.get import get_box, get_protocols_from_box

# from scipy import signal

# pylint: disable=R0801
if TYPE_CHECKING:
    # Import only during type checking to avoid circular imports
    from datasets.sleepdebt.unified_model.sleepdebt_calculation import Protocol


# def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
def get_plot(pro: Protocol, df_sleep_debt: pd.DataFrame, ax) -> plt.Axes:
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
    ax.set_title(get_title(pro), fontsize=16)

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


def get_title(pro):
    """getting title for the plot"""
    return DATA["protocols"][pro.name]["title"]


def get_blood_collection_time(pro):
    """getting blood collection time"""
    return DATA["protocols"][pro.name]["blood_sample_time"]


box = get_box()
DATA = get_protocols_from_box(box)
