""" extract sleep debt and plot them for different protocols """

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


import plotting
import protocols
from model import simulate_unified
from plotting import get_plot

"""
from protocols import (
    protocol1,
    protocol2,
    protocol3,
    protocol4,
    protocol5,
    protocol6,
    protocol7,
    protocol8_1,
    protocol9,
    protocol10,
    protocol11,
    protocol12,
    protocol13,
)
"""


def get_interval(t, time_ct):
    """getting sleep=wake status based on time interval"""
    s = "awake"
    for i in range(1, len(time_ct), 2):
        # print(i)
        if t > time_ct[i] and t <= time_ct[i + 1]:
            s = "sleep"
            break
    return s


def get_protocol_list_as_function():
    """getting protocol list dynamically"""
    protocol_list = []
    for i in range(1, 14):  # Assuming you have 3 protocols
        if i == 8:
            for j in range(1, 2):
                function_name = f"protocol{i}_{j}"
                print(function_name)
                protocol_func = globals().get(function_name)
                print(protocol_func)
                if protocol_func:
                    protocol_list.append(protocol_func)
        else:
            function_name = f"protocol{i}"
            print(function_name)
            protocol_func = globals().get(function_name)
            print(protocol_func)
            if protocol_func:
                protocol_list.append(protocol_func)
    print(protocol_list)
    return protocol_list


def get_protocols():
    "getting protocols list as string"
    protocol_list = []
    for i in range(1, 14):  # Assuming you have 3 protocols
        if i == 8:
            for j in range(1, 2):
                function_name = f"protocol{i}_{j}"
                print(function_name)
                protocol_list.append(function_name)
        else:
            function_name = f"protocol{i}"
            print(function_name)
            protocol_list.append(function_name)
    print(protocol_list)
    return protocol_list


def read_yaml(file_path):
    """read yaml file"""
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


def construct_protocol(data, protocol_name):
    """ construct protocol from yaml file"""
    print(protocol_name)
    protocol = data['protocols'][protocol_name]
    # Construct t_awake_l
    t_awake_l = []
    for item in protocol['t_awake_l']:
        print(type(item))
        if 'repeat' in item:
            repeat_value = protocol['t_awake_l'][item]['value'] # Ensure value is an integer
            repeat_count = protocol['t_awake_l'][item]['count']  # Ensure count is an integer
            t_awake_l.extend([repeat_value] * repeat_count)                
        elif 'append' in item:
            append_value = protocol['t_awake_l'][item]  # Ensure append value is an integer
            t_awake_l.extend(append_value)  # Use append for single values
        else:
            raise ValueError(f"Invalid key in t_awake_l: {item}")
        # Construct t_sleep_l
        t_sleep_l = []
        for item in protocol['t_sleep_l']:
            if 'repeat' in item:
                repeat_value = protocol['t_sleep_l'][item]['value'] # Ensure value is an integer
                repeat_count = protocol['t_sleep_l'][item]['count']  # Ensure count is an integer
                t_sleep_l.extend([repeat_value] * repeat_count)                
            elif 'append' in item:
                append_value = protocol['t_sleep_l'][item]  # Ensure append value is an integer
                t_sleep_l.extend(append_value)  # Use append for single values
            else:
                raise ValueError(f"Invalid key in t_sleep_l: {item}")

        
    return t_awake_l, t_sleep_l


def sleep_debt(protocol_list, definition, unified=False, u=24.1):
    """plotting sleep debt for different protocols"""
    j = 1

    # Parameters for subplot grid
    rows = 2
    cols = 2
    total_plots = rows * cols

    # Initialize subplot position and figure
    i1 = 1
    fig = plt.figure(figsize=(20, 10))

    for protocol in protocol_list:
        S0 = 0
        L0 = 0
        t0 = 0
        s, l, t = [], [], []
        t_ae_sl = construct_protocol(DATA, protocol)  # protocol()
        t_awake_l = t_ae_sl[0]
        t_sleep_l = t_ae_sl[1]
        time_count = []

        for t_awake, t_sleep in zip(t_awake_l, t_sleep_l):
            FD = False
            # for FD protocol only
            if "protocol8" in protocol:
                if (t_awake + t_sleep) != 1440:
                    FD = True
                else:
                    FD = False
            if unified:
                t1, s1, l1 = simulate_unified(
                    t_awake=t_awake, t_sleep=t_sleep, s0=S0, l0=L0, t0=t0, forced=FD
                )
            s += s1
            t += t1
            l += l1
            # eff+= eff1
            S0 = s1[-1]
            L0 = l1[-1]
            t0 = t1[-1]
        print("plotting protocol", protocol)
        s = np.array(s) / u
        l = np.array(l) / u
        data = [pair for pair in zip(t, l, s)]
        df_sleep_debt = pd.DataFrame(data, columns=["time", "l", "s"])

        # sleep-awake status
        time_elapsed = 0

        time_count.append(0)
        for i in range(len(t_ae_sl[0])):
            # print(len(t_ae_sl[0]))
            time_elapsed = time_elapsed + t_awake_l[i]
            time_count.append(time_elapsed)
            time_elapsed = time_elapsed + t_sleep_l[i]
            time_count.append(time_elapsed)

        # print(time_count)
        # print(len(time_count))

        df_sleep_debt["status"] = df_sleep_debt["time"].apply(
            lambda x: get_interval(x, time_count)
        )
        if j > total_plots:
            print("plotting protocol 10-1")
            plt.savefig(f"sleep_debt_combined{i1}.png")
            fig = plt.figure(figsize=(20, 10))
            i1 = i1 + 1
            j = 1
        ax = plt.subplot(rows, cols, j)  # (rows, columns, subplot number)

        get_plot(protocol, df_sleep_debt, t, time_count, definition, ax=ax)
        # Set common x and y labels for the figure
        fig.text(0.5, 0.05, "Time (days)", ha="center", va="center")
        fig.text(
            0.06,
            0.5,
            "Sleep Homeostat values % (impairment \u2192)",
            ha="center",
            va="center",
            rotation="vertical",
        )

        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper center", ncol=3)
        j = j + 1

    plt.savefig(f"sleep_debt_combined{i1}.png")


UNIFIED = True
prot_list = get_protocols()
print(prot_list)
FILE_PATH = "/Users/pujasaha/Desktop/duplicate/proteomics/datasets/sleepdebt/protocols.yaml"
DATA = read_yaml(FILE_PATH)

# Function that makes sleep debt plot
sleep_debt(prot_list, definition="def_2", unified=UNIFIED)
