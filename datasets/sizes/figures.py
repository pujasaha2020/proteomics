"""Provides the plotting functions for size analysis"""

import matplotlib.pyplot as plt


def plot_size_analysis(n_samples: list, n_proteins: list):
    """Plot the optimization of the dataset size"""
    plt.figure()
    plt.step([1] + n_proteins, [n_samples[0]] + n_samples, marker="o")
    plt.xlabel("Number of proteins")
    plt.ylabel("Number of samples")
    plt.title("Optimization of the dataset size")
    x_margin = 0.05 * (n_proteins[-2] - n_proteins[0])
    plt.xlim(n_proteins[0] - x_margin, n_proteins[-2] + x_margin)
    y_margin = 0.05 * (n_samples[0] - n_samples[-2])
    plt.ylim(n_samples[-2] - y_margin, n_samples[0] + y_margin)
    plt.show()
