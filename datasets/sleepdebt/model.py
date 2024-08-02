""" Unified Model for Sleep Debt Simulation """

# import pandas as pd
import numpy as np

# Unified Model
U = 24.1
TAU_LA = 4.06 * 24 * 60  # 4.06
TAU_W = 40 * 60
TAU_S = 1 * 60  # 8/3
# s_e= U/5


def sleep_new(t, t0=0, s0=0, l0=0, fd=False):
    """debt during sleep"""
    l_t = l0 * np.exp(-(t - t0) / TAU_LA) - 2 * U * (1 - np.exp(-(t - t0) / TAU_LA))
    s_t = (
        s0 * np.exp(-(t - t0) / TAU_S)
        - 2 * U * (1 - np.exp(-(t - t0) / TAU_S))
        + (TAU_LA * (l0 + 2 * U) / (TAU_LA - TAU_S))
        * (np.exp(-(t - t0) / TAU_LA) - np.exp(-(t - t0) / TAU_S))
    )

    if fd:
        l_t = l0 * np.exp(-(t - t0) / TAU_LA) - 1.4 * U * (
            1 - np.exp(-(t - t0) / TAU_LA)
        )
        s_t = (
        s0 * np.exp(-(t - t0) / TAU_S)
        - 1.4 * U * (1 - np.exp(-(t - t0) / TAU_S))
        + (TAU_LA * (l0 + 1.4 * U) / (TAU_LA - TAU_S))
        * (np.exp(-(t - t0) / TAU_LA) - np.exp(-(t - t0) / TAU_S))
    )
    return s_t, l_t


def awake_new(t, t0=0, s0=0, l0=0):
    """debt during awake"""
    s_t = U - np.exp(-(t - t0) / TAU_W) * (U - s0)
    l_t = U - np.exp(-(t - t0) / TAU_LA) * (U - l0)
    # L_t=0

    # eff_t= (1-np.exp(-(S_t/s_e)))*100

    return s_t, l_t


def simulate_unified(t_awake, t_sleep, s0, l0, t0, forced=False):
    """Unified Model"""
    wake_times = np.linspace(t0, (t0 + t_awake), t_awake + 1)
    # print(wake_times)

    res_awake = [awake_new(i, t0=t0, s0=s0, l0=l0) for i in wake_times]
    s_awake, l_awake = list(map(list, zip(*res_awake)))

    s0 = s_awake[-1]
    # print(S0)
    l0 = l_awake[-1]
    t0 = wake_times[-1]

    sleep_times = np.linspace(t0, (t0 + t_sleep), t_sleep + 1)

    res_sleep = [sleep_new(i, t0=t0, s0=s0, l0=l0, fd=forced) for i in sleep_times]

    s_sleep, l_sleep = list(map(list, zip(*res_sleep)))

    # eff_sleep= [eff]*len(sleep_times)

    return list(wake_times) + list(sleep_times), s_awake + s_sleep, l_awake + l_sleep
