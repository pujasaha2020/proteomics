""" Plotting tools for sleep debt calculation """


import numpy as np

# from scipy import signal
import yaml
from utils.get import get_box, get_protocols_from_box


# def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
def get_plot(pro, df_sleep_debt, ax=None):
    """getting the plot for the sleep debt"""
    ax2 = ax.twinx()
    ax2.plot(
        df_sleep_debt["time"] / (60.0 * 24),
        df_sleep_debt["Acute"],
        label="Acute (A_tot)",
        color="red",
    )
    ax2.set_ylabel("Acute", color="red", fontsize=14)

    ax.plot(
        df_sleep_debt["time"] / (60.0 * 24),
        df_sleep_debt["Chronic"],
        label="Chronic( R1_tot)",
        color="green",
    )
    ax.set_ylabel("Chronic", color="green", fontsize=14)

    ax.grid()
    ax.set_title(get_title(pro), fontsize=8)

    ax.set_xlim(
        [0, df_sleep_debt["time"][len(df_sleep_debt["time"]) - 1] / (60.0 * 24)]
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


def read_yaml(file_path):
    """read yaml file"""
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


def get_title(pro):
    """getting title for the plot"""
    return DATA["protocols"][pro.name]["title"]


def get_blood_collection_time(pro):
    """getting blood collection time"""
    return DATA["protocols"][pro.name]["blood_sample_time"]


box = get_box()
DATA = get_protocols_from_box(box)
