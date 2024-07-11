"""Check functions for dataframes"""

import pandas as pd


def check_proteomics(df: pd.DataFrame):
    """Ensure proteomics dataframe is correctly formatted"""
    expected_toplevel_val = {
        "circadian_phases",
        "ids",
        "infos",
        "profile",
        "proteins",
        "usage",
    }
    true_toplevel_val = set(df.columns.get_level_values(0).unique())
    assert expected_toplevel_val == true_toplevel_val
    required_columns = {
        ("profile", "clock_time"),
        ("ids", "study"),
        ("ids", "subject"),
        ("ids", "experiment"),
        ("ids", "sample_id"),
        ("infos", "fluid"),
    }
    assert required_columns.issubset(df.columns)


def check_somalogic(df: pd.DataFrame):
    """Ensure somalogic dataframe is correctly formatted"""
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
