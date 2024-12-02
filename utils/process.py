"""Provide user with processing functions"""

import numpy as np
import pandas as pd


def preprocess_proteomics(df: pd.DataFrame, steps: list[dict]):
    """Preprocess proteomics data."""
    print("Preprocessing proteomics data")
    print(steps)
    for step in steps:
        step["fun"](df, **step["args"])


def pick_debt(df: pd.DataFrame, model: str):
    """Preprocess sleep debt data."""
    print("Preprocessing sleep debt data")
    debt = [
        col
        for col in df.columns
        if ((col[0] == "sleep_debts") and (model not in col[1]))
    ]
    df.drop(columns=debt, inplace=True)
    df.rename(
        columns={f"acute_{model}": "acute", f"chronic_{model}": "chronic"},
        level=1,
        inplace=True,
    )


def drop_samples_without_proteins(df: pd.DataFrame):
    """Drop rows with all NaN proteins"""
    proteins = [col for col in df.columns if col[0] == "proteins"]
    df.dropna(subset=proteins, how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)


def drop_proteins_without_samples(df: pd.DataFrame):
    """Drop proteins with all NaN samples"""
    proteins = [col for col in df.columns if col[0] == "proteins"]
    empty_proteins = [col for col in proteins if df[col].isna().all()]
    df.drop(columns=empty_proteins, inplace=True)


def drop_proteins_with_missing_samples(df: pd.DataFrame):
    """Drop proteins with some NaN samples"""
    proteins = [col for col in df.columns if col[0] == "proteins"]
    empty_proteins = [col for col in proteins if df[col].isna().any()]
    df.drop(columns=empty_proteins, inplace=True)


def drop_all_but_circadian_proteins(df: pd.DataFrame, aptamers: pd.DataFrame):
    """Drop proteins that are not circadian"""
    df_proteins = set(df[["proteins"]].droplevel(0, axis=1).columns)
    circadian_proteins = set(aptamers[aptamers.category == "circadian"].index)
    no_circadian = df_proteins.difference(circadian_proteins)
    proteins2drop = pd.MultiIndex.from_product([["proteins"], no_circadian])
    df.drop(columns=proteins2drop, inplace=True)


def log_normalize_proteins(df: pd.DataFrame):
    """Log normalize protein values"""
    df["proteins"] = df.proteins.astype(float).apply(np.log10)


def drop_high_cv_proteins(
    df: pd.DataFrame, aptamers: pd.DataFrame, max_cv: float = 0.15
):
    """Drop proteins with high coefficient of variation"""
    # Get the set of proteins with high CV
    cd_high_cv = aptamers["Total CV Plasma"] > max_cv
    high_cv_proteins = set(aptamers[cd_high_cv].index)
    high_cv_proteins = high_cv_proteins.intersection(df.proteins.columns)
    # Format high CV proteins
    high_cv_proteins_col = pd.MultiIndex.from_product([["proteins"], high_cv_proteins])
    # Drop high CV proteins
    df.drop(columns=high_cv_proteins_col, inplace=True)


def drop_old_samples(df: pd.DataFrame):
    """Remove samples with less than 2000 proteins"""
    cd_old = df[["proteins"]].notna().sum(axis=1) < 2000
    df.loc[cd_old] = None
    df.dropna(how="all", inplace=True)


def bridge_v40_to_v41(df: pd.DataFrame, aptamers: pd.DataFrame, min_ccc: float = 0.75):
    """Bridge v4.0 to v4.1"""
    if ("infos", "fluid") not in df.columns:
        raise ValueError("Fluid information is missing")
    # Select the samples to bridge
    cd_v40 = df.notna().sum(axis=1) < 6000
    cd_edta = df.infos.fluid == "edta"
    # Ignore bridging value for samples with low/nan CCC
    cd_no_bridge = aptamers["Plasma Lin's CCC"] < min_ccc
    cd_no_bridge |= aptamers["Plasma Lin's CCC"].isna()
    aptamers.loc[cd_no_bridge] = None
    aptamers = aptamers.reindex(df.proteins.columns, fill_value=None)
    # Bridge v4.0 to v4.1
    ratio = aptamers["Plasma Scalar v4.1 to v4.0"]
    proteins_v41 = df.loc[cd_v40 & cd_edta]["proteins"].mul(1 / ratio)
    df.loc[cd_v40 & cd_edta, "proteins"] = proteins_v41.values


def optimize_full_dataset(df: pd.DataFrame, sizes: list[list[int]], min_proteins: int):
    """Use size analysis results to find the best datasets without missing proteins."""
    if not 0 <= min_proteins <= df[["proteins"]].shape[1]:
        raise ValueError("Make sure 0 <= min_proteins <= n_proteins")
    # Find the best dataset size
    my_sizes = sizes.copy()
    n_samples, n_proteins = len(df), 0
    while n_proteins < min_proteins:
        n_samples, n_proteins = my_sizes.pop(0)
    # Select samples with less than n_proteins
    cd_samples = df[["proteins"]].notna().sum(axis=1) >= n_proteins
    # Select proteins with less than n_samples
    cd_proteins = df[["proteins"]].notna().sum(axis=0) >= n_samples
    proteins2drop = cd_proteins[~cd_proteins].index
    # Drop samples that don't have the required proteins
    cd_samples &= df.drop(columns=proteins2drop)[["proteins"]].notna().all(axis=1)
    samples2drop = cd_samples[~cd_samples].index
    # Drop samples and proteins
    df.drop(columns=proteins2drop, inplace=True)
    df.drop(index=samples2drop, inplace=True)
    df.reset_index(drop=True, inplace=True)
    if df.empty:
        raise ValueError("No samples left after optimization.")
