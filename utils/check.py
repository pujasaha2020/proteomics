"""Check functions for dataframes"""

from pathlib import Path

import pandas as pd


def check_df(df: pd.DataFrame, what: str, path: Path):
    """Ensure dataframe is correctly formatted"""
    if what not in {"proteomics", "aptamer", "debt"}:
        raise ValueError(f"Unknown dataframe type: {what}")
    check_fun = {
        "proteomics": check_proteomics,
        "aptamer": check_aptamers,
        "debt": check_debt,
    }
    try:
        check_fun[what](df)
    except AssertionError as e:
        raise AssertionError(f"{path} does not meet expected format.") from e


def check_proteomics(df: pd.DataFrame):
    """Ensure proteomic dataframe is correctly formatted"""
    expected_toplevel_val = {
        "circadian_phases",
        "ids",
        "infos",
        "profile",
        "proteins",
    }
    true_toplevel_val = set(df.columns.get_level_values(0).unique())
    assert expected_toplevel_val.issubset(true_toplevel_val)
    required_columns = {
        ("profile", "clock_time"),
        ("ids", "study"),
        ("ids", "subject"),
        ("ids", "experiment"),
        ("ids", "sample_id"),
        ("infos", "fluid"),
        ("infos", "state"),
    }
    assert required_columns.issubset(df.columns)


def check_aptamers(df: pd.DataFrame):
    """Ensure aptamers dataframe is correctly formatted"""
    # Check index
    assert df.index.name == "SeqId"
    # Check columns
    required_columns = {
        "Total CV Plasma",
        "Plasma Lin's CCC",
        "Plasma Scalar v4.1 to v4.0",
    }
    assert required_columns.issubset(df.columns)


def check_debt(df: pd.DataFrame):
    """Ensure debt dataframe is correctly formatted"""
    required_columns = {
        "study",
        "subject",
        "experiment",
        "sample_id",
        "status",
        "s",
        "l",
    }
    assert required_columns.issubset(df.columns)
