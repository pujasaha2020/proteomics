# cSpell: disable
"""Module that contains accessory functions for model and hyperparameters tuning"""
import os

# import random
import time
from pathlib import Path
from typing import List, Optional

# import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
from openpyxl.styles import numbers
from sklearn.base import RegressorMixin  # type: ignore
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.model_selection import BaseCrossValidator  # type: ignore
from sklearn.model_selection._split import GroupsConsumerMixin  # type: ignore
from sklearn.preprocessing import RobustScaler  # type: ignore
from sklearn.utils import resample
from sklearn.utils.validation import _num_samples, indexable  # type: ignore

from utils.get import get_box
from utils.process import (
    bridge_v40_to_v41,
    drop_high_cv_proteins,
    drop_proteins_with_missing_samples,
    log_normalize_proteins,
    optimize_full_dataset,
)


class Config:  # pylint: disable=too-few-public-methods
    """Configuration class to control the behavior of the models/tuning."""

    def __init__(
        self, save=False, plot=True, explore=True, cache_dir="cache_directory", **kwargs
    ):
        self.save = save
        self.plot = plot
        self.explore = explore
        self.cache_dir = Path(cache_dir)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def display(self):
        """Display the configuration settings, including dynamically added attributes."""
        print("Configuration Settings:")
        for key, value in self.__dict__.items():
            print(f"{key}: {value}")


def select_features_before_modeling():
    """Select features before model training"""
    # This function is a placeholder for feature selection logic
    # You can implement your own feature selection method here

    box = get_box()
    file = box.get_file(Path("results/sleepdebt/biomarkers/unified/lme.csv"))
    df_biomarkers = pd.read_csv(file)

    # the column names are a real mess here or I do not know how to
    # handle them, so trying to fix it somehow
    # first 3 columns are  "seq_id", "pritein", "gene"
    first_3cols = df_biomarkers.columns.get_level_values(0).str.contains("Unnamed")
    df_1st3cols = df_biomarkers.loc[:, first_3cols]
    df_1st3cols = df_1st3cols.drop(df_1st3cols.index[0])
    df_1st3cols.reset_index(drop=True, inplace=True)
    df_1st3cols.columns = df_1st3cols.iloc[0]
    df_1st3cols = df_1st3cols.drop(df_1st3cols.index[0])
    df_1st3cols.reset_index(drop=True, inplace=True)

    # next 4 columns are #samples, #subjects, converge, group_var
    df_2nd_4cols = df_biomarkers.columns.get_level_values(0).str.contains("infos")
    df_2nd_4cols = df_biomarkers.loc[:, df_2nd_4cols]
    df_2nd_4cols.columns = df_2nd_4cols.iloc[0]
    df_2nd_4cols = df_2nd_4cols.drop(df_2nd_4cols.index[0:2])
    df_2nd_4cols.reset_index(drop=True, inplace=True)

    # acute columns
    acute_cols = df_biomarkers.columns.get_level_values(0).str.contains("acute")
    df_acute = df_biomarkers.loc[:, acute_cols]
    df_acute.columns = df_acute.iloc[0]
    df_acute = df_acute.drop(df_acute.index[0:2])
    df_acute.reset_index(drop=True, inplace=True)
    df_acute.columns = ["acute_" + col for col in df_acute.columns]

    # chronic columns
    chronic_cols = df_biomarkers.columns.get_level_values(0).str.contains("chronic")
    df_chronic = df_biomarkers.loc[:, chronic_cols]
    df_chronic.columns = df_chronic.iloc[0]
    df_chronic = df_chronic.drop(df_chronic.index[0:2])
    df_chronic.reset_index(drop=True, inplace=True)
    df_chronic.columns = ["chronic_" + col for col in df_chronic.columns]
    df_biomarkers = pd.concat([df_1st3cols, df_2nd_4cols, df_acute, df_chronic], axis=1)

    df_biomarkers["acute_pvalue_fdr"] = df_biomarkers["acute_pvalue_fdr"].astype(float)
    df_biomarkers["chronic_pvalue_fdr"] = df_biomarkers["chronic_pvalue_fdr"].astype(
        float
    )

    acute_proteins = df_biomarkers.loc[
        df_biomarkers["acute_pvalue_fdr"] < 0.05, "seq_id"
    ]
    chronic_proteins = df_biomarkers.loc[
        df_biomarkers["chronic_pvalue_fdr"] < 0.05, "seq_id"
    ]

    biomarkers = list(set(acute_proteins.to_list() + chronic_proteins.to_list()))

    return biomarkers


class ResampleRegressor(BaseEstimator, RegressorMixin):
    """
    A custom regressor that resamples the data to balance the target variable
    before fitting a base estimator. It oversamples the tails of the distribution
    to create a more balanced dataset for regression tasks.
    """

    def __init__(
        self, base_estimator, low_thresh=0.2, high_thresh=0.8, upsample_ratio=1.0
    ):
        self.base_estimator = base_estimator
        self.low_thresh = low_thresh
        self.high_thresh = high_thresh
        self.upsample_ratio = (
            upsample_ratio  # 1.0 = balance with common; >1.0 = oversample more
        )

    def get_params(self, deep=True):
        params = super().get_params(deep=deep)
        if deep and hasattr(self.base_estimator, "get_params"):
            base_params = self.base_estimator.get_params(deep=deep)
            for key, value in base_params.items():
                params[f"base_estimator__{key}"] = value
        return params

    def set_params(self, **params):
        base_estimator_params = {}
        for key in list(params.keys()):
            if key.startswith("base_estimator__"):
                base_key = key.replace("base_estimator__", "")
                base_estimator_params[base_key] = params.pop(key)
        if base_estimator_params:
            self.base_estimator.set_params(**base_estimator_params)
        super().set_params(**params)
        return self

    def fit(self, X, y):
        # Combine X and y
        df = pd.DataFrame(X).copy()
        df["s_debt"] = y

        # Compute thresholds
        low_val = df["s_debt"].quantile(self.low_thresh)
        high_val = df["s_debt"].quantile(self.high_thresh)

        # Identify rare and common samples
        low_rare = df[df["s_debt"] < low_val]
        high_rare = df[df["s_debt"] > high_val]
        common = df[(df["s_debt"] >= low_val) & (df["s_debt"] <= high_val)]

        # Number of samples to upsample to
        n_samples = int(
            self.upsample_ratio * len(common) // 2
        )  # divide by 2 to split between low/high

        # Upsample both tails
        low_upsampled = resample(
            low_rare,
            replace=True,
            n_samples=min(n_samples, len(low_rare)),
            random_state=42,
        )
        high_upsampled = resample(
            high_rare,
            replace=True,
            n_samples=min(n_samples, len(high_rare)),
            random_state=42,
        )

        # Combine resampled data
        df_resampled = pd.concat([common, low_upsampled, high_upsampled]).reset_index(
            drop=True
        )
        X_resampled = df_resampled.drop(columns="s_debt")
        y_resampled = df_resampled["s_debt"]

        if hasattr(self.base_estimator, "fit"):
            self.model_ = clone(self.base_estimator)
            self.model_.fit(X_resampled, y_resampled)
        else:
            raise ValueError("Base estimator does not support fit()")

        return self

    def predict(self, X):
        return self.model_.predict(X)


class WeightedZScoreNormalizer(BaseEstimator, TransformerMixin):
    call_counter = 0  # Class-level counter to track number of fit calls

    def __init__(self, verbose=True):
        self.verbose = verbose
        self.scalers = {}

    def fit(self, X, y=None):
        # WeightedZScoreNormalizer.call_counter += 1
        # call_id = WeightedZScoreNormalizer.call_counter
        """
        if self.verbose:
            print(f"\n[Fit Call {call_id}] START")
            print(
                f"[Fit Call {call_id}] BEFORE DROP → shape: {X.shape}, columns: {list(X.columns[:5])}..."
            )
        """
        X = X.copy()

        try:
            plasmas = X["fluid"].loc[X.index]
            groups = X["subject"].loc[X.index]
        except KeyError as e:
            raise

        X = X.drop(columns=["fluid", "subject"], errors="ignore")

        if groups is not None:
            group_counts = groups.value_counts()
            group_weights = 1.0 / group_counts
            group_weights *= len(groups) / group_weights.sum()
            sample_weights = groups.map(group_weights)
        else:
            sample_weights = pd.Series(1.0, index=X.index)

        for plasma in np.unique(plasmas):
            mask = plasmas == plasma

            X_plasma = X.loc[mask]
            weights_plasma = sample_weights[mask]

            weighted_mean = np.average(X_plasma, weights=weights_plasma, axis=0)
            weighted_mean = pd.Series(weighted_mean, index=X_plasma.columns)

            weighted_var = np.average(
                (X_plasma - weighted_mean) ** 2, weights=weights_plasma, axis=0
            )
            weighted_std = pd.Series(np.sqrt(weighted_var), index=X_plasma.columns)

            self.scalers[plasma] = {
                "mean": weighted_mean,
                "std": weighted_std,
            }

        return self

    def transform(self, X, y=None):
        X = X.copy()
        plasmas = X["fluid"].loc[X.index]
        X = X.drop(columns=["fluid", "subject"], errors="ignore")
        X_scaled = X.copy()

        for plasma in np.unique(plasmas):
            mask = plasmas == plasma
            mean = self.scalers[plasma]["mean"]
            std = self.scalers[plasma]["std"]
            X_scaled.loc[mask] = (X.loc[mask] - mean) / std

        return X_scaled


def weighted_zscore_normalization(X, plasma_types, groups=None):
    """
    Normalize the data using the z-score normalization method for each plasma type,
    with weighting by group (subject) to prevent subjects with more samples from dominating.

    Parameters:
    -----------
    X : pandas DataFrame
        The data to normalize
    plasma_types : pandas Series
        The plasma type for each sample
    groups : pandas Series, optional
        The group (subject) for each sample

    Returns:
    --------
    X_scaled : pandas DataFrame
        The normalized data
    """
    X_scaled = X.copy()
    indices_to_subset = X_scaled.index
    plasma_subset = plasma_types.loc[indices_to_subset]

    # Calculate weights based on groups if provided
    if groups is not None:
        groups_subset = groups.loc[indices_to_subset]
        # Count samples per group
        group_counts = groups_subset.value_counts()
        # Calculate inverse weights (less weight for groups with more samples)
        group_weights = 1.0 / group_counts
        # Normalize weights to sum to the number of samples
        group_weights = group_weights * len(X) / group_weights.sum()
        # Create a weight for each sample based on its group
        sample_weights = groups_subset.map(group_weights)
    else:
        sample_weights = pd.Series(1.0, index=indices_to_subset)

    # For each plasma type, perform weighted normalization
    for plasma in np.unique(plasma_types):
        mask = plasma_subset == plasma
        if mask.sum() == 0:
            print(f"No samples for plasma type {plasma}")
            continue

        # Get samples and weights for this plasma type
        X_plasma = X_scaled[mask]
        weights_plasma = np.asarray(sample_weights[mask])

        # Calculate weighted mean and std

        weighted_mean = np.average(
            X_plasma.values, weights=np.asarray(weights_plasma), axis=0
        )
        weighted_var = np.average(
            (X_plasma.to_numpy() - np.asarray(weighted_mean)) ** 2,
            weights=weights_plasma,
            axis=0,
        )
        weighted_std = np.sqrt(weighted_var)

        # Avoid division by zero
        weighted_std = np.where(weighted_std == 0, 1.0, weighted_std)

        # Apply normalization
        X_scaled[mask] = (X_plasma - weighted_mean) / weighted_std

    return X_scaled


class OrderedGroupKFold(GroupsConsumerMixin, BaseCrossValidator):
    """K-fold iterator variant with non-overlapping groups and ordered group IDs."""

    def __init__(self, n_splits=2):
        self.n_splits = n_splits

    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits

    def _iter_test_indices(self, X=None, y=None, groups=None):
        if groups is None:
            raise ValueError("The `groups` parameter is required.")
        if len(groups) == 0:
            return

        # Count occurrences of each group and sort them in descending order
        unique_groups, group_counts = np.unique(groups, return_counts=True)
        sorted_groups = unique_groups[np.argsort(-group_counts)]

        # Initialize empty folds
        folds = [[] for _ in range(self.n_splits)]

        # Distribute the sorted groups into the folds
        for i, group in enumerate(sorted_groups):
            fold_index = i % self.n_splits
            fold_indices = np.where(groups == group)[0]
            folds[fold_index].extend(fold_indices)

        # Yield test indices for each fold
        for fold in folds:
            yield np.array(fold)

    def split(self, X, y=None, groups=None):
        X, y, groups = indexable(X, y, groups)
        if _num_samples(X) == 0:
            return iter([])  # Return an empty iterator if there are no samples
        indices = np.arange(_num_samples(X))
        for test_index in self._iter_test_indices(X, y, groups):
            train_index = indices[np.logical_not(np.isin(indices, test_index))]
            yield train_index, test_index


class Params:  # pylint: disable=too-few-public-methods
    """Parameters class to control the behavior of the models/tuning."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        sizes: Optional[List[tuple[int, int]]] = None,
        min_proteins: int = 3000,
        alphas: list[float] = [0.1],
        l1_r: list[float] = [0.1],
        n_splits_in_out: Optional[List[int]] = None,
        method=OrderedGroupKFold,
        scoring: str = "f1_weighted",
        **kwargs,
    ):
        self.sizes = sizes if sizes is not None else [(19124, 4000)]
        self.min_proteins = min_proteins
        self.alphas = alphas if alphas is not None else [0.1, 0.06]
        self.l1_r = l1_r if l1_r is not None else [0.5, 0.99]
        self.n_splits_in_out = (
            n_splits_in_out if n_splits_in_out is not None else [3, 5]
        )
        self.method = method
        self.scoring = scoring
        for key, value in kwargs.items():
            setattr(self, key, value)

    def display(self):
        """Display the configuration settings, including dynamically added attributes."""
        print("Configuration Settings:")
        for key, value in self.__dict__.items():
            print(f"{key}: {value}")


# Calculate sleep, wake counts, and total samples
def calculate_sleep_wake_count(group):
    sleep_count = (group[("infos", "state")] == 0).sum()
    wake_count = (group[("infos", "state")] == 1).sum()
    total_sample = sleep_count + wake_count

    return pd.Series(
        {
            "sleep_count": sleep_count,
            "wake_count": wake_count,
            "sample_total": total_sample,
        }
    )


# Analysis of NaN values in a proteomics DataFrame
def na_analysis(
    df: pd.DataFrame,
    cfg: Config,
    combination_path,
    name_of_prot_col: str = "proteins",
):
    """Analyze NaN values proteins in the DataFrame"""
    # Create a boolean DataFrame indicating NaN values
    nan_df = df[name_of_prot_col].isna()

    print("df created")
    if not nan_df.any().any():
        print("No NaN values found in the DataFrame.")
        return nan_df

    # Create the heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(
        nan_df,
        cbar=False,
        cmap="viridis",
        yticklabels=df[name_of_prot_col].index,
        xticklabels=df[name_of_prot_col].columns,
    )

    # Set labels and title
    plt.xlabel("Proteins")
    plt.ylabel("Samples")
    plt.title("NaN Values in Protein Columns by Sample")
    print("heatmap created")
    # Show the plot
    if cfg.save:
        print("hello")
        plt.savefig(combination_path / "na_analysis.png")

    return nan_df


# Analysis of the distribution of proteins in a DataFrame
def distribution_analysis(
    df: pd.DataFrame,
    cfg,
    combination_path,
    name_of_prot_col: str = "proteins",
    bins=2000,
):
    """Analyze the distribution of proteins in the DataFrame"""

    # Calculate the mean of each column in "proteins"
    mean_values = df[(name_of_prot_col)].mean()

    # Plot the distribution of mean values
    plt.figure(figsize=(10, 8))
    plt.hist(mean_values, bins=bins)
    plt.ylabel("Frequency")
    plt.title("Distribution of Mean Values for Proteins")
    # plt.figure(figsize=(10, 6))
    # plt.xlim(0, 50000)  # Clip values in the x axis from 0 to 5k
    # plt.xscale("log")  # Use a logarithmic scale for the y axis
    if cfg.save:
        plt.savefig(combination_path / "distribution_analysis.png")
    plt.close()


def plot_study_characteristics(prot: pd.DataFrame, cfg, combination_path):
    """Plot the number of sleep and wake samples for each study and subject."""
    # Sort the DataFrame by the number of samples per subject
    # Group by the specified columns
    order = (
        prot.groupby([("ids", "subject")])
        .size()
        .sort_values(ascending=False)
        .index.tolist()
    )

    # Reindex based on this order
    prot = prot.set_index([("ids", "subject")]).loc[order].reset_index()

    # Group by study and subject and apply the function
    grouped = prot.groupby([("ids", "subject")])

    result = (
        grouped.apply(calculate_sleep_wake_count)
        .sort_values(by="sample_total", ascending=False)
        .reset_index()
    )
    print("this is the result:", result)
    # Plotting the bars
    result.plot(
        x=("ids", "subject"),
        y=["sleep_count", "wake_count"],
        kind="bar",
        figsize=(14, 4),
        width=0.8,
        color=["blue", "lightblue"],  # Colors for sleep_count and wake_count
    )
    plt.xlabel("Study and Subject", fontsize=10, labelpad=10)
    plt.ylabel("Number of samples", fontsize=10, labelpad=10)
    # Modify x-axis label font size
    plt.xticks(fontsize=6)

    # Define colors for the study background

    # Create and combine legends
    handles, labels = plt.gca().get_legend_handles_labels()
    # Add legend to the plot
    second_legend = plt.legend(
        handles=handles[:2],
        labels=labels[:2],
        title="Sleep Status",
        loc="upper left",
        ncol=1,
    )
    plt.gca().add_artist(second_legend)
    if cfg.save:
        plt.savefig(combination_path / "study_characteristics.png")
    plt.close()


def visualize_groups(group, classes, study):

    groups = pd.factorize(group)[0]

    group_colors = ["blue" if i % 2 == 0 else "lightblue" for i in groups]

    classes_colors = ["blue" if i % 2 == 0 else "lightblue" for i in classes]

    studies = pd.factorize(study)[0]

    studies_colors = ["blue" if i % 2 == 0 else "lightblue" for i in studies]

    # Visualize dataset groups
    fig, ax = plt.subplots(figsize=(16, 8))
    # plt.figure(figsize=(16, 8))
    ax.scatter(
        range(len(groups)),
        [0.5] * len(groups),
        c=studies_colors,
        marker="_",
        lw=50,
    )
    ax.scatter(
        range(len(groups)),
        [3.5] * len(groups),
        c=group_colors,
        marker="_",
        lw=50,
    )
    ax.scatter(
        range(len(groups)),
        [6.5] * len(groups),
        c=classes_colors,
        marker="_",
        lw=50,
    )
    ax.set(
        ylim=[-1, 8],
        yticks=[0.5, 3.5, 6.5],
        yticklabels=["Studies", "Groups", "Class"],
        xlabel="Sample index",
    )


"""
def plot_cv_indices(cv, X, y, group, study, n_splits, lw=10):

    _, ax = plt.subplots()
    cmap_data = plt.cm.Paired
    cmap_cv = plt.cm.coolwarm

    group = pd.factorize(group)[0]

    group_colors = ["blue" if i % 2 == 0 else "lightblue" for i in group]

    classes_colors = ["blue" if i % 2 == 0 else "lightblue" for i in y]

    studies = pd.factorize(study)[0]

    studies_colors = ["blue" if i % 2 == 0 else "lightblue" for i in studies]

    # Create a sample plot for indices of a cross-validation object.

    use_groups = "Group" in type(cv).__name__
    groups = group if use_groups else None

    # Generate the training/testing visualizations for each CV split
    for ii, (tr, tt) in enumerate(cv.split(X=X, y=y, groups=groups)):
        # Fill in indices with the training/test groups
        indices = np.array([np.nan] * len(X))
        indices[tt] = 1
        indices[tr] = 0

        # Visualize the results
        ax.scatter(
            range(len(indices)),
            [ii] * len(indices),
            c=indices,
            marker="_",
            lw=lw,
            cmap=cmap_cv,
            vmin=-0.2,
            vmax=1.2,
        )

    # Plot the data classes and groups at the end
    ax.scatter(
        range(len(group)),
        [ii + 1.5] * len(group),
        c=classes_colors,
        marker="_",
        lw=lw,
    )
    ax.scatter(
        range(len(group)),
        [ii + 3.5] * len(group),
        c=studies_colors,
        marker="_",
        lw=lw,
    )
    ax.scatter(
        range(len(group)),
        [ii + 2.5] * len(group),
        c=group_colors,
        marker="_",
        lw=lw,
    )

    # Formatting
    yticklabels = list(range(n_splits)) + ["state", "ids", "study"]
    ax.set(
        yticks=np.arange(n_splits + 3) + 0.5,
        yticklabels=yticklabels,
        xlabel="Sample index",
        ylabel="CV iteration",
        ylim=[n_splits + 4, -1],
        xlim=[0, 1300],
    )
    ax.set_title("{}".format(type(cv).__name__), fontsize=15)
    return ax
"""


def zscore_normalization(X, plasma_types):  # type: ignore
    """Normalize the data using the z-score normalization method for each plasma type"""
    # Assuming plasma_types is a pandas Series or array-like with the same length as X
    X_scaled = X.copy()
    indices_to_subset = X_scaled.index

    # Subset plasma using these indices
    plasma_subset = plasma_types.loc[indices_to_subset]

    # Be careful, the function is sensible to the number of plasma types in folds :
    # implement a error test if a fold has only one plasma type

    for plasma in np.unique(plasma_types):
        mask = plasma_subset == plasma
        if mask.sum() == 0:
            print("this group is only EDTA or Heparin")
        scaler = RobustScaler()
        X_scaled[mask] = scaler.fit_transform(X[mask])
    return X_scaled


def prepare_data_model(
    prot: pd.DataFrame,
    debt: pd.DataFrame,
    aptamers: pd.DataFrame,
    sizes: list,
    min_proteins: int,
):
    """Prepare dataset, encode the target, and extract the fluid list"""

    # before going into too much detail, remove "mppg_fd" Forced Desynchrony samples

    prot = prot[prot[("ids", "study")] != "mppg_fd"]

    print("shape before preprocessing:", prot.shape)
    t = [time.time()]
    print("Preprocessing data...")
    # not needed as I am working with selected biomarkers
    optimize_full_dataset(prot, sizes=sizes, min_proteins=min_proteins)
    print("shape before preprocessing:", prot.shape)

    drop_high_cv_proteins(prot, aptamers)
    print("shape before preprocessing:", prot.shape)

    bridge_v40_to_v41(prot, aptamers)
    print("shape before preprocessing:", prot.shape)

    drop_proteins_with_missing_samples(prot)
    print("shape before preprocessing:", prot.shape)

    log_normalize_proteins(prot)

    # Ensure type compatibility for the subject column
    prot[("ids", "subject")] = prot[("ids", "subject")].astype(str)

    # reset the index
    prot.reset_index(drop=True, inplace=True)

    print("Proteomics data shape before merging debt:", prot.shape)

    # Drop rows with missing values in the target column
    # prot_preprocessed = prot.dropna(subset=[("infos", "state")])

    debt_copy = debt[["ids", "unified", "profile"]].copy()
    debt_copy = debt_copy.droplevel(0, axis=1)
    prot = prot.droplevel(0, axis=1)

    df_final = pd.merge(
        prot,
        debt_copy[
            ["sample_id", "chronic", "acute", "l_debt", "s_debt", "mins_from_admission"]
        ],
        on="sample_id",
        how="inner",
    )

    print("Proteomics data shape after merging debt:", df_final.shape)

    # df_final["total_debt"] = df_final["chronic"] + df_final["acute"]

    # Define the "proteins" columns to keep for the prediction
    biomarkers = [col for col in df_final.columns if "-" in col]

    cols = biomarkers + [
        "fluid",
        "subject",
        "study",
        "sample_id",
        "s_debt",
        "mins_from_admission",
    ]
    full_data = df_final[cols].copy()

    # cgecking NaN in features
    print("shape of features:", full_data.shape)

    t.append(time.time())
    print(f"Data prep in {t[-1] - t[0]:.2f} seconds")

    return full_data


def prepare_training_testing_data(full_dataset: pd.DataFrame) -> pd.DataFrame:
    """Prepare training and testing data for modeling"""
    # carefully choose the testing dataset
    # I used the OrderedGroupKFold to split the dataset
    # took one fold for testing and the rest for training
    # the split is done by subject
    # and the training and testing data are not overlapping

    cv_testing = OrderedGroupKFold(n_splits=5)
    traing_index, test_index = next(
        cv_testing.split(
            X=full_dataset,
            y=None,
            groups=full_dataset["subject"],
        )
    )
    data_testing = full_dataset.iloc[test_index]
    data_testing.reset_index(drop=True, inplace=True)
    data_training = full_dataset.iloc[traing_index]
    data_training.reset_index(drop=True, inplace=True)

    groups = data_training["subject"]
    target_training = data_training["s_debt"]

    target_testing = data_testing["s_debt"]

    print("shape of training data:", data_training.shape)
    print("shape of testing data:", data_testing.shape)
    print("shape of target training data:", target_training.shape)
    print("shape of target testing data:", target_testing.shape)
    return data_training, target_training, data_testing, target_testing, groups


def get_jobs():
    """Get the number of jobs to use for parallel processing"""
    n_cores = os.cpu_count()
    if n_cores is None:
        n_cores = 1
    # Set n_jobs to use all but one core
    n_jobs = n_cores - 1 if n_cores > 1 else 1
    return n_jobs


def save_dataframe(df: pd.DataFrame, output_file: str) -> None:
    """
    Save the DataFrame to an Excel or CSV file with proper formatting.

    Parameters:
    df (pd.DataFrame): The DataFrame to save.
    output_file (str): The output file path. The file extension determines the format (Excel or CSV).
    """
    file_extension = Path(output_file).suffix

    if file_extension == ".xlsx":
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            # Write DataFrame to Excel
            df.to_excel(writer, index=False, sheet_name="Sheet1")
            worksheet = writer.sheets["Sheet1"]

            # Get numeric columns
            numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns

            # Iterate through columns
            for idx, column in enumerate(worksheet.columns):
                max_length = 0
                column_name = column[0].column_letter
                column_header = worksheet[f"{column_name}1"].value  # Get header name

                # Apply number formatting if it's a numeric column
                if column_header in numeric_cols:
                    for cell in column[1:]:  # Skip header row
                        cell.number_format = numbers.FORMAT_NUMBER_00
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                else:
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                # Adjust column width
                adjusted_width = min(max_length + 2, 60)
                worksheet.column_dimensions[column_name].width = adjusted_width

    elif file_extension == ".csv":
        df.to_csv(output_file, index=False)
    else:
        raise ValueError("Unsupported file extension. Please use .xlsx or .csv")
