""" Plotting tools for sleep debt calculation """

import numpy as np

from scipy import signal
from scipy import interpolate
from scipy.signal import find_peaks
import yaml


file_path = "/Users/pujasaha/Desktop/duplicate/proteomics/datasets/sleepdebt/protocols.yaml"


def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
    """getting the plot for the sleep debt"""
    if definition == "def_1":
        lower_envelope = get_lower_envelope(df_sleep_debt)
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            lower_envelope * 100,
            label="Sleep debt (chronic)",
            color="black",
        )
        ax.plot(
            np.array(t) / (60.0 * 24),
            (df_sleep_debt["l"] - lower_envelope) * 100,
            label="Sleep debt (acute)",
            color="red",
        )
        ax.plot(
            np.array(t) / (60.0 * 24),
            df_sleep_debt["l"] * 100,
            label="Sleep debt (L)",
            color="green",
        )
        ax.plot(
            df_sleep_debt["time"] / (60.0 * 24),
            df_sleep_debt["s"] * 100,
            label="Sleep homeostat (S)",
            color="orange",
            linestyle="--",
        )
        ax.grid()
        ax.set_xlabel("Time (days)", fontsize=12)
        ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=10)
        df_sleep_debt["SD_Chronic"] = lower_envelope
        df_sleep_debt["SD_Acute"] = df_sleep_debt["l"] - lower_envelope

    elif definition == "def_2":
        ax.plot(
            np.array(t) / (60.0 * 24),
            df_sleep_debt["l"] * 100,
            label="Sleep debt (chronic) (L)",
            color="green",
        )
        ax.plot(
            np.array(t) / (60.0 * 24),
            df_sleep_debt["s"] * 100,
            label="Sleep homeostat (S)",
            color="orange",
            linestyle="--",
        )
        ax.plot(
            np.array(t) / (60.0 * 24),
            (df_sleep_debt["s"] - df_sleep_debt["l"]) * 100,
            label="Sleep debt (acute) (S-L)",
            color="red",
        )
        ax.grid()
        # ax.set_xlabel("Time (days)", fontsize=12)
        # ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=10)

    elif definition == "def_3":
        ax.plot(
            np.array(t) / (60.0 * 24),
            df_sleep_debt["l"] * 100,
            label="Sleep debt (chronic) (L)",
            color="green",
        )
        ax.plot(
            np.array(t) / (60.0 * 24),
            df_sleep_debt["s"] * 100,
            label="Sleep homeostat (S)",
            color="orange",
            linestyle="--",
        )
        ax.plot(
            np.array(t) / (60.0 * 24),
            (df_sleep_debt["s"] - df_sleep_debt["l"]) * 100,
            label="Sleep debt (acute) (S-L)",
            color="red",
        )
        ax.grid()
        # ax.set_xlabel("Time (days)", fontsize=10)
        # ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=12)

    else:
        print("Invalid definition")
        return None
    ax.set_title(get_title(pro), fontsize=6)

    ax.set_xlim([11, t[len(t) - 1] / (60.0 * 24)])
    for i in range(1, len(time_count), 2):
        if i == 1:
            ax.axvspan(
                time_count[i] / (60 * 24),
                time_count[i + 1] / (60 * 24),
                facecolor="grey",
                label="Sleep episodes",
                alpha=0.3,
            )
        ax.axvspan(
            time_count[i] / (60 * 24),
            time_count[i + 1] / (60 * 24),
            facecolor="grey",
            alpha=0.3,
        )
    xcoords = get_blood_collection_time(pro)
    if len(xcoords) == 0:
        pass
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
        ticks=np.arange(11, int(max(np.array(t)) / (60.0 * 24)) + 1),
        labels=np.arange(0, int(max(np.array(t)) / (60.0 * 24) - 11) + 1),
    )
    pass


def get_lower_envelope(df_sleep_debt):
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


def read_yaml(file_path):
    """read yaml file"""
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


DATA = read_yaml(file_path)


def get_title(pro):
    """getting title for the plot"""
    return DATA["protocols"][pro]["title"]


def get_blood_collection_time(pro):
    """getting blood collection time"""
    return DATA["protocols"][pro]["blood_sample_time"]