"""Provide user with processing functions"""

import numpy as np
import pandas as pd

from box.manager import BoxManager
from utils.get import get_somalogic


def drop_samples_without_proteins(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with all NaN proteins"""
    proteins = [col for col in df.columns if col[0] == "proteins"]
    return df.dropna(subset=proteins, how="all").reset_index(drop=True)


def log_normalize_proteins(df: pd.DataFrame) -> pd.DataFrame:
    """Log normalize protein values"""
    df["proteins"] = df.proteins.apply(np.log10)
    return df


def drop_high_cv_proteins(
    box: BoxManager, df: pd.DataFrame, max_cv: float = 0.15
) -> pd.DataFrame:
    """Drop proteins with high coefficient of variation"""
    somalogic = get_somalogic(box)
    # Get the set of proteins with high CV
    cd_high_cv = somalogic["Total CV Plasma"] > max_cv
    high_cv_proteins = set(somalogic[cd_high_cv].index)
    # Drop high CV proteins
    high_cv_proteins_col = pd.MultiIndex.from_product([["proteins"], high_cv_proteins])
    df.drop(columns=high_cv_proteins_col, inplace=True)
    return df


def drop_old_samples(df: pd.DataFrame) -> pd.DataFrame:
    """Remove samples with less than 2000 proteins"""
    cd_old = df[["proteins"]].notna().sum(axis=1) < 2000
    df.loc[cd_old] = None
    df.dropna(how="all", inplace=True)
    return df


def bridge_v40_to_v41(
    box: BoxManager, df: pd.DataFrame, min_ccc: float = 0.75
) -> pd.DataFrame:
    """Bridge v4.0 to v4.1"""
    if ("infos", "fluid") not in df.columns:
        raise ValueError("Fluid information is missing")
    somalogic = get_somalogic(box)
    # Select the samples to bridge
    cd_v40 = df.notna().sum(axis=1) < 6000
    cd_edta = df.infos.fluid == "edta"
    # Ignore bridging value for samples with low/nan CCC
    cd_no_bridge = somalogic["Plasma Lin's CCC"] < min_ccc
    cd_no_bridge |= somalogic["Plasma Lin's CCC"].isna()
    somalogic.loc[cd_no_bridge] = None
    somalogic = somalogic.reindex(df.proteins.columns, fill_value=None)
    # Bridge v4.0 to v4.1
    ratio = somalogic["Plasma Scalar v4.1 to v4.0"]
    proteins_v41 = df.loc[cd_v40 & cd_edta, "proteins"].mul(1 / ratio)
    df.loc[cd_v40 & cd_edta, "proteins"] = proteins_v41.values
    return df
