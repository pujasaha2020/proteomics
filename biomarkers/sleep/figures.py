"""Provides the plotting functions for sleep biomarkers analysis"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib_venn import venn3  # type: ignore


def plot_sample_per_subject_per_study(df: pd.DataFrame):
    """Plot the number of samples per subject per study"""
    studies = df.study.unique()
    plt.figure()
    for study in studies:
        df[df.study == study].groupby("subject").size().hist(label=study, alpha=0.5)
    plt.axvline(6, color="r", linestyle="--", label="significant")
    plt.legend(bbox_to_anchor=(0.5, -0.2), loc="center", ncol=len(studies) // 3 + 1)
    plt.title("Number of samples per subject")
    plt.ylim([0, 10])
    plt.show()


def plot_specificity_vs_sensitivity(results: pd.DataFrame, max_pvalue: float) -> dict:
    """Plot specificity vs sensitivity"""
    # Compute the number of proteins for each p-value
    max_candidates = np.logspace(-4, 0, 100)
    max_candidates = np.hstack((max_candidates, np.array([max_pvalue])))
    max_candidates.sort()
    my_max_idx = np.argwhere(max_candidates == max_pvalue)[0, 0]
    data: dict[str, list[int]] = {"acute": [], "chronic": []}  # , "sleep": []}
    for candidate in max_candidates:
        buffer = {}
        for key, val in data.items():
            buffer[key] = results[results[(key, "pvalue_fdr")] < candidate].index
            val.append(len(buffer[key]))

        # draw venn diagram
        if candidate == max_pvalue:
            proteins = buffer.copy()

    my_colors = {"acute": "tab:red", "chronic": "tab:green", "sleep": "tab:purple"}
    plt.figure()
    plt.title(r"Specificity VS Sensibility")
    for key, val in data.items():
        label = f"{key.capitalize()} ({val[my_max_idx]})"
        plt.plot(max_candidates, val, label=label, color=my_colors[key])
    plt.axvline(x=max_pvalue, ls="--", c="k", label=r"$p_{max}$" + f"={max_pvalue}")
    plt.ylabel("Number of proteins")
    plt.xlabel(r"$p_{fdr}$")
    plt.xscale("log")
    plt.legend()
    plt.show()
    return proteins


def plot_venn_diagram(proteins: dict):
    """Plot a venn diagram"""
    plt.figure()
    plt.title("Venn diagram of significant proteins")
    my_sets = list(map(set, proteins.values()))
    my_labels = list(map(str.capitalize, proteins.keys()))
    venn3(my_sets, my_labels)
    plt.show()
