""" Provides the steps to run the analysis for the sleep biomarker """

import warnings

import pandas as pd
import statsmodels.api as sm  # type: ignore
from statsmodels.stats.multitest import multipletests  # type: ignore

from biomarkers.sleep.figures import (
    plot_sample_per_subject_per_study,
    plot_specificity_vs_sensitivity,
    plot_venn_diagram,
)
from utils.process import drop_samples_without_proteins, log_normalize_proteins

# Suppress specific warning
warnings.filterwarnings("ignore", category=sm.tools.sm_exceptions.ConvergenceWarning)


def preprocess_data(
    df: pd.DataFrame, debts: pd.DataFrame, min_group_size: int, plot: bool
) -> dict[str, pd.DataFrame]:
    """
    Preprocess the data for the LME model:
    - Drop samples without proteins
    - Log normalize the proteins
    - Merge the debts information
    - Drop samples with missing debts information
    - Drop subjects with less than min_group_size samples
    - Drop proteins with only missing values
    - Prepare the data for the LME model
    """
    proteins = [col[1] for col in df.columns if col[0] == "proteins"]
    df = drop_samples_without_proteins(df)
    df = log_normalize_proteins(df)
    df = df.droplevel(0, axis=1)
    df = df.merge(debts[["sample_id", "l", "s"]], on="sample_id", how="left")
    df["sleep"] = (df["state"] == "sleep").astype(int)
    df.rename(columns={"s": "acute", "l": "chronic"}, inplace=True)
    df.dropna(subset=["acute", "chronic", "sleep"], how="any", inplace=True)
    if plot:
        plot_sample_per_subject_per_study(df)
    non_significant = df.groupby("subject").size() < min_group_size
    df.drop(df.loc[df["subject"].map(non_significant)].index, inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    proteins = list(set(proteins).intersection(df.columns))
    return dict(map(lambda p: prepare_lme_data(df, p), proteins))


def prepare_lme_data(df: pd.DataFrame, protein: str) -> tuple[str, pd.DataFrame]:
    """
    Prepare the data for the LME model
    - Drop missing values
    - Reset the index
    - Rename the protein column
    - Check if the fluid type is consistent
    """
    relevant_cols = [protein, "acute", "chronic", "sleep", "subject", "fluid"]
    data = df[relevant_cols].dropna(subset=relevant_cols, how="any")
    data.reset_index(drop=True, inplace=True)
    data.rename(columns={protein: "log_protein"}, inplace=True)
    plasma_check = data.groupby("subject")["fluid"].nunique() == 1
    if not plasma_check.all():
        raise ValueError("A subject has different fluid type")
    return (protein, data)


def run_lme_sleep(data: pd.DataFrame) -> dict:
    """Run a linear mixed effect model for a protein"""
    # Fit the model
    model = sm.MixedLM.from_formula(
        "log_protein ~ 1 + acute + chronic + sleep",
        data,
        groups=data["subject"],
        re_formula="1",
    ).fit()
    # Extract relevant results
    results = {
        ("infos", "#samples"): len(data),
        ("infos", "#subjects"): data.subject.nunique(),
        ("infos", "converge"): model.converged,
    }
    for key in ["acute", "chronic", "sleep"]:
        results[(key, "param")] = model.params[key]
        results[(key, "pvalue")] = model.pvalues[key]
        results[(key, "[0.025")] = model.conf_int().loc[key, 0]
        results[(key, "0.975]")] = model.conf_int().loc[key, 1]
    return results


def postprocess_results(
    results: pd.DataFrame, somalogic: pd.DataFrame, max_pvalue: float, plot: bool
) -> pd.DataFrame:
    """
    Postprocess the results
    - Drop non-converged models
    - Perform Benjamini-Hochberg adjustment
    - Format the results
    """
    # Drop non-converged models
    results.drop(results[~results.infos.converge].index, inplace=True)
    results = results.loc[results.infos.converge]
    # Perform Benjamini-Hochberg adjustment
    for key in ["acute", "chronic", "sleep"]:
        p, p_fdr = (key, "pvalue"), (key, "pvalue_fdr")
        results[p_fdr] = multipletests(results[p], alpha=max_pvalue, method="fdr_bh")[1]
    if plot:
        proteins = plot_specificity_vs_sensitivity(results, max_pvalue)
        plot_venn_diagram(proteins)
    # Format the results
    names = {"index": "seq_id", "Target Name": "protein", "Entrez Gene Name": "gene"}
    results.index = (
        somalogic.loc[results.index]
        .reset_index()
        .rename(columns=names)
        .set_index(list(names.values()))
        .index
    )
    results = results[["infos", "acute", "chronic", "sleep"]]
    return results
