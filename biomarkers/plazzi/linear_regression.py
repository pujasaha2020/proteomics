"""
model  to test the protein expression between two groups
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import mannwhitneyu, shapiro


def run_lm_sleep(data: pd.DataFrame, protein: str, reference: str, merge: bool) -> dict:
    """Run a linear regression for a protein"""

    # place the group you want to make reference in the first position
    studies = list(data["study"].unique())
    studies.remove(reference)
    studies.insert(0, reference)
    if merge:
        # Groups to merge
        groups_to_merge = studies[1:]
        new_group_name = "Merged"

        # Merge groups
        data["study"] = data["study"].apply(
            lambda x: new_group_name if x in groups_to_merge else x
        )
        data["study"] = pd.Categorical(
            data["study"], categories=[reference, "Merged"], ordered=False
        )

        data_dummies = pd.get_dummies(data, columns=["study"], drop_first=True)

    else:
        data["study"] = pd.Categorical(data["study"], categories=studies, ordered=False)
        data_dummies = pd.get_dummies(data, columns=["study"], drop_first=True)
    for col in data_dummies.columns:
        if col.startswith("study"):
            data_dummies[col] = data_dummies[col].astype(int)
    y = data_dummies["log_protein"]
    # x_matrix = data_dummies[
    #    [col for col in data_dummies.columns if col.startswith("study")]
    # ]
    x_matrix = data_dummies.loc[:, data_dummies.columns != "log_protein"]
    x_matrix = sm.add_constant(x_matrix)

    model = sm.OLS(y, x_matrix).fit()
    normal = check_distribution(model.resid)

    results = {
        ("ids", "seq_id"): protein,
    }

    keys = (
        ["const"]
        + [col for col in data_dummies.columns if col.startswith("study")]
        + ["Age", "Gender", "BMI"]
    )
    for key in keys:

        results[(key, "param")] = model.params[key]
        results[(key, "pvalue")] = model.pvalues[key]

    results[("dist", "normal")] = str(normal)
    # results = test_non_parametric(data, reference, results)
    return results


def check_distribution(y: pd.Series) -> bool:
    """Check the residual distribution of the data"""
    _, p = shapiro(y)
    normal = True
    if p < 0.05:
        normal = False

    return normal


def test_non_parametric(data: pd.DataFrame, reference: str, results: dict) -> dict:
    """Test the non parametric test, Mann Whitney U"""
    studies = list(data["study"].unique())
    studies.remove(reference)

    for study in studies:
        _, p_value = mannwhitneyu(
            data[data["study"] == reference]["log_protein"],
            data[data["study"] == study]["log_protein"],
        )
        results[(f"study_{study}", "param")] = "NA"
        results[(f"study_{study}", "pvalue")] = p_value
    return results
