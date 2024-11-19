# plot the necessary digram needed for the analysis


import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_density(variables: list, df_study: pd.DataFrame) -> plt:
    """Plot the histogram by groups"""
    # plot hist by group
    # Create subplots with one row and as many columns as there are variables
    _, axes = plt.subplots(1, 2, figsize=(15, 6))
    df_study = df_study.droplevel(0, axis=1)

    # Plot each variable's histogram in a separate subplot
    for ax, var in zip(axes, variables):

        if var == "Gender":
            sns.countplot(data=df_study, x=var, hue="study", ax=ax)
            ax.set_title(f"Histogram of {var}")
            ax.set_xlabel(var)
            ax.set_ylabel("Frequency")
            ax.set_ylim(0, df_study[var].value_counts().max())  # Adjust y-
        else:
            sns.kdeplot(
                data=df_study.dropna(subset=[var]),
                x=var,
                hue="study",
                ax=ax,
                fill=True,
                common_norm=False,
            )
            ax.set_title(f"Density of {var}")
            ax.set_xlabel(var)
            ax.set_ylabel("Density")
            ax.set_ylim(0, 0.1)

    # Adjust layout and save the figure
    plt.tight_layout()
    return plt


def plot_box(variables: list, df_study: pd.DataFrame) -> plt:
    """Plot the histogram by groups"""
    # plot hist by group
    # Create subplots with one row and as many columns as there are variables
    _, axes = plt.subplots(1, 2, figsize=(15, 6))
    df_study = df_study.droplevel(0, axis=1)

    # Plot each variable's histogram in a separate subplot
    for ax, var in zip(axes, variables):
        sns.boxplot(data=df_study, x="study", y=var, ax=ax)
        ax.set_title(f"Box plot of {var}")
        ax.set_xlabel("Study")

    # Adjust layout and save the figure
    plt.tight_layout()
    return plt


def plot_count(var: str, df_study: pd.DataFrame) -> plt:
    """Plot the count by groups"""

    _, ax = plt.subplots(1, 1, figsize=(15, 6))
    df_study = df_study.droplevel(0, axis=1)
    sns.countplot(data=df_study, x=var, hue="study")
    ax.set_title(f"count plot of {var}")
    ax.set_xlabel(var)
    ax.set_ylabel("Frequency")
    return plt
