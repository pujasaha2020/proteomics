# plot the necessary digram needed for the analysis


import matplotlib.pyplot as plt
import pandas as pd


def plot_box(
    data: pd.DataFrame,
    proteins,
) -> None:
    """Plot the box plot"""
    fig, ax = plt.subplots(figsize=(10, 6))
    data.boxplot(ax=ax)
    plt.title(title)
    plt.savefig(path)
    plt.close()


def plot_hist(variable: str, data: pd.DataFrame) -> None:
    """Plot the histogram"""
    fig, ax = plt.subplots(figsize=(10, 6))
    data[variable].hist(ax=ax, bins=30)
    plt.title(title)
    plt.savefig(path)
    plt.close()
