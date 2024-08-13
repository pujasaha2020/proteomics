"""Tests for the process module"""

import numpy as np
import pandas as pd
import pytest

from utils.process import (
    bridge_v40_to_v41,
    drop_all_but_circadian_proteins,
    drop_high_cv_proteins,
    drop_old_samples,
    drop_proteins_with_missing_samples,
    drop_proteins_without_samples,
    drop_samples_without_proteins,
    log_normalize_proteins,
    optimize_full_dataset,
)


@pytest.fixture(name="aptamers")
def input_aptamers() -> pd.DataFrame:
    """Return a aptamer dataframe with Total CV Plasma column"""
    data = {
        "Total CV Plasma": [0.1, 0.2, None, None, 0.2],
        "Plasma Lin's CCC": [0.8, 0.7, None, 0.8, 0.9],
        "Plasma Scalar v4.1 to v4.0": [1.1, 1.2, 1.3, None, None],
        "category": ["circadian", None, "rhythmic", "circadian", None],
    }
    index = ["1", "2", "3", "5", "6"]
    return pd.DataFrame(data, index=index)


#################### HIGH CV ####################
def test_drop_high_cv_proteins(aptamers: pd.DataFrame):
    """Test drop_high_cv_proteins function"""
    data = {
        ("proteins", "1"): [1, 2, 3],
        ("proteins", "2"): [4, 5, 6],
        ("proteins", "3"): [7, 8, 9],
        ("proteins", "4"): [10, 11, 12],
    }
    df = pd.DataFrame(data, dtype=float)
    expected_data = {
        # cv < 0.15
        ("proteins", "1"): [1, 2, 3],
        # cv = None
        ("proteins", "3"): [7, 8, 9],
        # Not in aptamers
        ("proteins", "4"): [10, 11, 12],
    }
    expected_df = pd.DataFrame(expected_data, dtype=float)
    drop_high_cv_proteins(df, aptamers, max_cv=0.15)
    pd.testing.assert_frame_equal(df, expected_df)


################## OLD SAMPLES ##################
def test_drop_old_samples():
    """Test drop_old_samples function"""
    data = {
        "sample1": [1] + 2004 * [None],
        "sample2": 2005 * [None],
        "sample3": range(2005),
    }
    protein_names = [f"{i}" for i in range(2005)]
    index = pd.MultiIndex.from_product([["proteins"], protein_names])
    df = pd.DataFrame(data, index=index, dtype=float).transpose()

    expected_data = {
        "sample3": range(2005),
    }
    protein_names = [f"{i}" for i in range(2005)]
    index = pd.MultiIndex.from_product([["proteins"], protein_names])
    expected_df = pd.DataFrame(expected_data, index=index, dtype=float).transpose()
    drop_old_samples(df)
    pd.testing.assert_frame_equal(df, expected_df)


############### BRIDGE V40 TO V41 ###############
def test_bridge_v40_to_v41(aptamers: pd.DataFrame):
    """Test bridge_v40_to_v41 function"""
    data = {
        ("proteins", "1"): [1, None, 3, 4],
        ("proteins", "2"): [5, None, 7, 8],
        ("proteins", "3"): [9, None, 11, 12],
        ("proteins", "4"): [13, None, 15, 16],
        ("proteins", "5"): [None, None, 19, 20],
    }
    df = pd.DataFrame(data, dtype=float)
    df[("infos", "fluid")] = ["edta", "edta", "heparin", "serum"]
    expected_data = {
        # CCC >= 0.75            --> bridge only edta
        ("proteins", "1"): [1 / 1.1, None, 3, 4],
        # CCC <  0.75            --> No bridge
        ("proteins", "2"): [None, None, 7, 8],
        # CCC = None             --> No bridge
        ("proteins", "3"): [None, None, 11, 12],
        # Not in aptamers        --> No bridge
        ("proteins", "4"): [None, None, 15, 16],
        # scalar = None          --> No bridge
        ("proteins", "5"): [None, None, 19, 20],
    }
    expected_df = pd.DataFrame(expected_data, dtype=float)
    expected_df[("infos", "fluid")] = ["edta", "edta", "heparin", "serum"]
    bridge_v40_to_v41(df, aptamers, min_ccc=0.75)
    pd.testing.assert_frame_equal(df, expected_df)


########## DROP SAMPLES WITHOUT PROTEINS ########
########## DROP PROTEINS WITHOUT SAMPLES ########
################## LOG NORMALIZE ################
@pytest.fixture(name="df")
def input_df() -> pd.DataFrame:
    """Return a dataframe without proteins columns"""
    data = {
        ("proteins", "1"): [None, 2.0, 3.0],
        ("proteins", "2"): [None, None, None],
        ("proteins", "3"): [None, None, 9.0],
        ("infos", "age"): [15, 10, 20],
    }
    return pd.DataFrame(data)


def test_drop_samples_without_proteins(df: pd.DataFrame):
    """Test drop_samples_without_proteins function"""
    expected_data = {
        ("proteins", "1"): [2.0, 3.0],
        ("proteins", "2"): [None, None],
        ("proteins", "3"): [None, 9.0],
        ("infos", "age"): [10, 20],
    }
    expected_df = pd.DataFrame(expected_data)
    result_df = df.copy()
    drop_samples_without_proteins(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_drop_proteins_without_samples(df: pd.DataFrame):
    """Test drop_proteins_without_samples function"""
    expected_data = {
        ("proteins", "1"): [None, 2, 3],
        ("proteins", "3"): [None, None, 9],
        ("infos", "age"): [15, 10, 20],
    }
    expected_df = pd.DataFrame(expected_data)
    result_df = df.copy()
    drop_proteins_without_samples(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_log_normalize_proteins(df: pd.DataFrame):
    """Test log_normalize_proteins function"""
    expected_data = {
        ("proteins", "1"): [None, np.log10(2), np.log10(3)],
        ("proteins", "2"): [np.nan, np.nan, np.nan],
        ("proteins", "3"): [None, None, np.log10(9)],
        ("infos", "age"): [15, 10, 20],
    }
    expected_df = pd.DataFrame(expected_data)
    result_df = df.copy()
    log_normalize_proteins(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


############ DROP PROTEINS WITHOUT SAMPLES ############
######### DROP ALL BUT CIRCADIAN PROTEINS #############


@pytest.fixture(name="df_1")
def input_df_1() -> pd.DataFrame:
    """Return a dataframe without proteins columns"""
    data = {
        ("proteins", "1"): [None, 2, 3],
        ("proteins", "2"): [None, None, None],
        ("proteins", "3"): [None, None, 9],
        ("proteins", "4"): [1, 2, 3],
        ("infos", "age"): [15, 10, 20],
    }
    return pd.DataFrame(data)


def test_drop_proteins_with_missing_samples(df_1: pd.DataFrame):
    """Test drop_proteins_without_samples function"""
    expected_data = {
        ("proteins", "4"): [1, 2, 3],
        ("infos", "age"): [15, 10, 20],
    }
    expected_df = pd.DataFrame(expected_data)
    result_df = df_1.copy()
    drop_proteins_with_missing_samples(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_drop_all_but_circadian_proteins(df_1: pd.DataFrame, aptamers: pd.DataFrame):
    """Test drop_all_but_circadian_proteins function"""
    expected_data = {
        ("proteins", "1"): [None, 2, 3],
        ("infos", "age"): [15, 10, 20],
    }
    expected_df = pd.DataFrame(expected_data)
    result_df = df_1.copy()
    drop_all_but_circadian_proteins(result_df, aptamers)
    pd.testing.assert_frame_equal(result_df, expected_df)


########## OPTIMIZE FULL DATASET ########
def test_optimize_full_dataset():
    """Test optimize_full_dataset function"""
    data = {
        ("ids", "subject"): ["A", "B", "B", "C", "C", None],
        ("proteins", "1"): [1.0, 2.0, None, None, None, None],
        ("proteins", "2"): [1.0, 2.0, None, None, None, None],
        ("proteins", "3"): [1.0, 2.0, None, 4.0, 5.0, None],
        ("proteins", "4"): [None, None, None, None, None, 6.0],
    }
    df = pd.DataFrame(data)
    sizes = [[4, 1], [2, 3], [0, 4]]

    # min_proteins < 0
    with pytest.raises(ValueError):
        optimize_full_dataset(df, sizes, min_proteins=-1)

    # 0 <= min_proteins <= 3
    expected_data = [
        {
            "min_proteins": 1,
            "results": {
                ("ids", "subject"): ["A", "B", "C", "C"],
                ("proteins", "3"): [1.0, 2.0, 4.0, 5.0],
            },
        },
        {
            "min_proteins": 2,
            "results": {
                ("ids", "subject"): ["A", "B"],
                ("proteins", "1"): [1.0, 2.0],
                ("proteins", "2"): [1.0, 2.0],
                ("proteins", "3"): [1.0, 2.0],
            },
        },
        {
            "min_proteins": 3,
            "results": {
                ("ids", "subject"): ["A", "B"],
                ("proteins", "1"): [1.0, 2.0],
                ("proteins", "2"): [1.0, 2.0],
                ("proteins", "3"): [1.0, 2.0],
            },
        },
    ]
    for expected in expected_data:
        expected_df = pd.DataFrame(expected["results"])
        result_df = df.copy()
        optimize_full_dataset(result_df, sizes, expected["min_proteins"])
        pd.testing.assert_frame_equal(result_df, expected_df)

    # min_proteins > 3
    with pytest.raises(ValueError):
        optimize_full_dataset(df, sizes, 4)
    with pytest.raises(ValueError):
        optimize_full_dataset(df, sizes, 5)
