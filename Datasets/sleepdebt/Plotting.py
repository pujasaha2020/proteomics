import matplotlib.pyplot as ax
import numpy as np
from scipy import interpolate
from scipy.signal import find_peaks


def get_plot(pro, df_sleep_debt, t, time_count, definition, ax=None):
    if definition == "def_1":
        lower_envelope = get_lower_envelope(df_sleep_debt)
        ax.plot(
            np.array(t) / (60.0 * 24),
            lower_envelope * 100,
            label="Sleep debt (chronic)",
            color="black",
        )
        ax.plot(
            np.array(t) / (60.0 * 24),
            (np.array(l) - lower_envelope) * 100,
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
            np.array(t) / (60.0 * 24),
            df_sleep_debt["s"] * 100,
            label="Sleep homeostat (S)",
            color="orange",
            linestyle="--",
        )
        ax.grid()
        ax.set_xlabel("Time (days)", fontsize=12)
        ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=10)
        df_sleep_debt["SD_Chronic"] = lower_envelope
        df_sleep_debt["SD_Acute"] = (
            df_sleep_debt["l"] - lower_envelope
        )  # np.array(l)-ynew
        # df_sleep_debt.to_csv("/Users/pujasaha/Desktop/SleepDebt/data_with_sleepdebt/MPPG_Control_8H_Unified.csv", index=False)

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
        #ax.set_xlabel("Time (days)", fontsize=12)
        #ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=10)

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
        #ax.set_xlabel("Time (days)", fontsize=10)
        #ax.set_ylabel("Sleep Homeostat values % (impairment \u2192)", fontsize=12)

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


    ax.tick_params(axis='both', which='major', labelsize=8)  # Adjust the font size as needed
    ax.set_xticks(ticks= np.arange(11, int(max(np.array(t)) / (60.0 * 24))+1 ), labels=np.arange(0, int(max(np.array(t)) / (60.0 * 24) - 11)+1))
    pass


def get_lower_envelope(df_sleep_debt):
    peaks, _ = find_peaks(df_sleep_debt["l"])
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


def get_title(exp):
    pro = exp.__name__
    if pro == "protocol1":
        return "One night of 8 hr sleep, 36 hr Constant Routine (CR). n=152#9."
    elif pro == "protocol2":
        return "Two nights of 9hr sleep/night, 39 hr Constant Routine (CR), 12 hr recovery sleep. n=374#9. "
    elif pro == "protocol3":
        return "Control sample: 8 hr of normal sleep schedule. n=21#3 "
    elif pro == "protocol4":
        return "Control sample : 10 hr of normal sleep schedule. n=26#4 "
    elif pro == "protocol5":
        return "Two days of 8 hr sleep/night, 21days of 5 hr sleep at night (Chronic Sleep Restriction). n=96#5 "
    elif pro == "protocol6":
        return "Two days of 10 hr sleep/night, 21days of 5.6 hr sleep at night (Chronic Sleep Restriction). n= 53#4"
    elif pro == "protocol7":
        return "Two baseline nights of 10 hr sleep, five nights of 4 hr sleep, one recovery night of 8 hr sleep "
    elif pro == "protocol9":
        return "10 days protocol: 12 hr and 10 hr sleep on two baselines nights then 8 hr of sleep throughout. n=69#5 "
    elif pro == "protocol10":
        return "10 days protocol: 12 hr and 10 hr sleep on two baselines nights, Total Sleep Deprivation (TSD) on 3rd and 4th night, 2 recovery nights of 10 hr Sleep.n=140#11"
    elif pro == "protocol11":
        return "10 days protocol: 12 hr and 10 hr sleep on two baselines nights,\n  Chronic Sleep Restriction Night (CSRN) five nights with 6 hr sleep, 2 recovery nights of 10 hr Sleep. n=69#5 "
    elif pro == "protocol12":
        return "10 days protocol: 12 hr and 10 hr sleep on two baselines nights, \n  Chronic Sleep Restriction Day (CSRD) five days with 6 hr sleep, 2 recovery nights of 10 hr Sleep.n=54#4"
    elif pro == "protocol13":
        return "Approximately 16 hours awake followed by 8 hr sleep and again  approximately 8 hr awake. "
    elif pro == "protocol8_1":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol8_2":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22. "
    elif pro == "protocol8_3":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22. "
    elif pro == "protocol8_4":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol8_5":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol8_6":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol8_7":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol8_8":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol8_9":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol9:
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol10":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol11":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    elif pro == "protocol12":
        return "Forced Desynchrony 11hr 40 min asleep and 16hr 20min awake. n=22."
    
    else:
        return ""


def get_blood_collection_time(exp):
    pro = exp.__name__
    if pro == "protocol1":
        return [
            12.08,
            12.16,
            12.25,
            12.33,
            12.41,
            12.50,
            12.58,
            12.66,
            12.75,
            12.83,
            12.91,
            13.00,
            13.08,
            13.16,
            13.25,
            13.33,
            13.41,
        ]
    elif pro == "protocol2":
        return [
            12.04,
            12.12,
            12.20,
            12.29,
            12.37,
            12.45,
            12.54,
            12.58,
            12.62,
            12.66,
            12.70,
            12.75,
            12.79,
            12.87,
            12.96,
            13.04,
            13.12,
            13.20,
            13.29,
            13.37,
            13.45,
            13.54,
            13.58,
            13.62,
            13.66,
            13.71,
            13.75,
            13.79,
            13.87,
            13.96,
            14.04,
            14.12,
            14.21,
            14.29,
            14.37,
            14.46,
            14.54,
            14.62,
            14.71,
            14.79,
            14.87,
            14.96,
            15.04,
            15.12,
            15.21,
            15.29,
        ]
    elif pro == "protocol3":
        return [11.53, 11.74, 11.95, 12.03, 12.20, 12.37, 12.53]
    elif pro == "protocol4":
        return [11.60, 11.76, 11.94, 12.10, 12.26, 12.43, 12.60]
    elif pro == "protocol5":
        return [
            11.53,
            11.72,
            11.91,
            12.03,
            12.20,
            12.37,
            18.53,
            18.70,
            18.99,
            19.03,
            19.21,
            19.37,
            19.54,
            40.53,
            40.70,
            41.03,
            41.20,
            41.37,
            41.53,
        ]
    elif pro == "protocol6":
        return [
            11.60,
            11.76,
            11.93,
            12.10,
            12.28,
            12.43,
            12.59,
            18.59,
            18.93,
            19.10,
            19.26,
            19.43,
            40.59,
            40.76,
            40.93,
            41.10,
            41.26,
            41.43,
            41.59,
        ]
    elif pro == "protocol7":
        return [13,14,15]
    elif pro == "protocol9":
        return [
            12.55,
            12.72,
            12.89,
            13.05,
            13.22,
            13.39,
            17.55,
            17.72,
            17.89,
            18.05,
            18.22,
            18.39,
            18.55,
        ]
    elif pro == "protocol10":
        return [
            12.55,
            12.72,
            12.89,
            13.05,
            13.22,
            13.39,
            14.55,
            14.72,
            14.89,
            15.05,
            15.22,
            15.39,
            15.55,
        ]
    elif pro == "protocol11":
        return [
            12.55,
            12.72,
            12.89,
            13.05,
            13.22,
            13.39,
            13.55,
            13.89,
            17.72,
            17.89,
            18.05,
            18.22,
            18.39,
            18.55,
        ]
    elif pro == "protocol12":
        return [
            12.55,
            12.72,
            12.89,
            13.05,
            13.22,
            13.39,
            13.55,
            13.72,
            17.72,
            17.89,
            18.05,
            18.22,
            18.39,
            18.55,
        ]
    elif pro == "protocol13":
        return []
    elif pro == "protocol8_1":
        return [
            11.53,
            11.74,
            11.86,
            12.03,
            12.20,
            12.36,
            12.53,
            19.49,
            19.66,
            19.82,
            20.01,
            20.16,
            20.32,
            20.49,
            20.66,
            36.01,
            36.17,
            36.35,
            36.50,
            36.67,
            36.84,
            37.01,
        ]
    elif pro == "protocol8_2":
        return [
            11.53,
            11.74,
            11.86,
            12.03,
            12.20,
            12.36,
            12.53,
            19.49,
            19.66,
            19.82,
            20.01,
            20.16,
            20.32,
            20.49,
            20.66,
            36.01,
            36.17,
            36.35,
            36.50,
            36.67,
            36.84,
            37.01,
        ]
    elif pro == "protocol8_3":
        return [
            11.53,
            11.70,
            11.87,
            12.03,
            12.36,
            12.53,
            19.49,
            19.66,
            19.83,
            19.99,
            20.16,
            20.32,
            20.49,
            20.66,
            35.98,
            36.15,
            36.32,
            36.48,
            36.65,
            36.82,
            36.99,
            40.98,
            41.15,
            41.32,
            41.48,
            41.65,
            41.82,
            41.98,
        ]
    elif pro == "protocol8_4":
        return [
            11.53,
            11.74,
            11.86,
            12.03,
            12.20,
            12.36,
            12.53,
            19.49,
            19.66,
            19.82,
            20.01,
            20.16,
            20.32,
            20.49,
            20.66,
            36.01,
            36.17,
            36.35,
            36.50,
            36.67,
            36.84,
            37.01,
        ]
    elif pro == "protocol8_5":
        return [
            11.53,
            11.74,
            11.86,
            12.03,
            12.20,
            12.36,
            12.53,
            19.49,
            19.66,
            19.82,
            20.01,
            20.16,
            20.32,
            20.49,
            20.66,
            36.01,
            36.17,
            36.35,
            36.50,
            36.67,
            36.84,
            37.01,
        ]
    elif pro == "protocol8_6":
        return [
            11.53,
            11.74,
            11.86,
            12.03,
            12.20,
            12.36,
            12.53,
            19.49,
            19.66,
            19.82,
            20.01,
            20.16,
            20.32,
            20.49,
            20.66,
            36.01,
            36.17,
            36.35,
            36.50,
            36.67,
            36.84,
            37.01,
        ]
    elif pro == "protocol8_7":
        return [
            11.53,
            11.74,
            11.86,
            12.03,
            12.20,
            12.36,
            12.53,
            19.49,
            19.66,
            19.82,
            20.01,
            20.16,
            20.32,
            20.49,
            20.66,
            36.01,
            36.17,
            36.35,
            36.50,
            36.67,
            36.84,
            37.01,
        ]
    elif pro == "protocol8_8":
        return [
            11.53,
            11.74,
            11.86,
            12.03,
            12.20,
            12.36,
            12.53,
            19.49,
            19.66,
            19.82,
            20.01,
            20.16,
            20.32,
            20.49,
            20.66,
            36.01,
            36.17,
            36.35,
            36.50,
            36.67,
            36.84,
            37.01,
        ]
    elif pro == "protocol8_9":
        return [
            11.53,
            11.74,
            11.86,
            12.03,
            12.20,
            12.36,
            12.53,
            19.49,
            19.66,
            19.82,
            20.01,
            20.16,
            20.32,
            20.49,
            20.66,
            36.01,
            36.17,
            36.35,
            36.50,
            36.67,
            36.84,
            37.01,
        ]
    else :
        return []
