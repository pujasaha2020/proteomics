"""Tests for the process module"""

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from box.manager import BoxManager
from utils.process import bridge_v40_to_v41, drop_high_cv_proteins, drop_old_samples


@pytest.fixture(name="somalogic")
def input_somalogic() -> pd.DataFrame:
    """Return a somalogic dataframe with Total CV Plasma column"""
    data = {
        "Total CV Plasma": [0.1, 0.2, None, None],
        "Plasma Lin's CCC": [0.8, 0.7, None, 0.8],
        "Plasma Scalar v4.1 to v4.0": [1.1, 1.2, 1.3, None],
    }
    index = ["seq_id1", "seq_id2", "seq_id3", "seq_id5"]
    return pd.DataFrame(data, index=index, dtype=float)


@pytest.fixture(name="box")
def mock_box(mocker: MockerFixture) -> BoxManager:
    """Return a mocked BoxManager object"""
    box = mocker.Mock(spec=BoxManager)
    return box


################# HIGH CV #################
@pytest.fixture(name="df_high_cv")
def input_df_high_cv():
    """Return a dataframe with proteins columns"""
    data = {
        ("proteins", "seq_id1"): [1, 2, 3],
        ("proteins", "seq_id2"): [4, 5, 6],
        ("proteins", "seq_id3"): [7, 8, 9],
        ("proteins", "seq_id4"): [10, 11, 12],
    }
    return pd.DataFrame(data, dtype=float)


def test_drop_high_cv_proteins(
    mocker: MockerFixture,
    box: BoxManager,
    df_high_cv: pd.DataFrame,
    somalogic: pd.DataFrame,
):
    """Test drop_high_cv_proteins function"""
    # Patch the get_somalogic function to return the somalogic fixture data
    mocker.patch("utils.process.get_somalogic", return_value=somalogic)

    expected_data = {
        # cv < 0.15
        ("proteins", "seq_id1"): [1, 2, 3],
        # cv = None
        ("proteins", "seq_id3"): [7, 8, 9],
        # Not in somalogic
        ("proteins", "seq_id4"): [10, 11, 12],
    }
    expected_df = pd.DataFrame(expected_data, dtype=float)

    result_df = drop_high_cv_proteins(box, df_high_cv, max_cv=0.15)
    pd.testing.assert_frame_equal(result_df, expected_df)


################# OLD SAMPLES #################
@pytest.fixture(name="df_old")
def input_df_old() -> pd.DataFrame:
    """Return a dataframe with proteins columns"""
    data = {
        "sample1": [1] + 2004 * [None],
        "sample2": 2005 * [None],
        "sample3": range(2005),
    }
    protein_names = [f"seq_id{i}" for i in range(2005)]
    index = pd.MultiIndex.from_product([["proteins"], protein_names])
    return pd.DataFrame(data, index=index, dtype=float).transpose()


def test_drop_old_samples(df_old: pd.DataFrame):
    """Test drop_old_samples function"""
    expected_data = {
        "sample3": range(2005),
    }
    protein_names = [f"seq_id{i}" for i in range(2005)]
    index = pd.MultiIndex.from_product([["proteins"], protein_names])
    expected_df = pd.DataFrame(expected_data, index=index, dtype=float).transpose()

    result_df = drop_old_samples(df_old)
    pd.testing.assert_frame_equal(result_df, expected_df)


################# BRIDGE V40 TO V41 #################
@pytest.fixture(name="df_bridge")
def input_df_bridge() -> pd.DataFrame:
    """Return a dataframe for bridging v4.0 to v4.1"""
    data = {
        ("proteins", "seq_id1"): [1, None, 3, 4],
        ("proteins", "seq_id2"): [5, None, 7, 8],
        ("proteins", "seq_id3"): [9, None, 11, 12],
        ("proteins", "seq_id4"): [13, None, 15, 16],
        ("proteins", "seq_id5"): [None, None, 19, 20],
    }
    df = pd.DataFrame(data, dtype=float)
    df[("infos", "fluid")] = ["edta", "edta", "heparin", "serum"]
    return df


def test_bridge_v40_to_v41(
    mocker: MockerFixture,
    box: BoxManager,
    df_bridge: pd.DataFrame,
    somalogic: pd.DataFrame,
):
    """Test bridge_v40_to_v41 function"""
    # Patch the get_somalogic function to return the somalogic_bridge fixture data
    mocker.patch("utils.process.get_somalogic", return_value=somalogic)

    expected_data = {
        # CCC >= 0.75            --> bridge only edta
        ("proteins", "seq_id1"): [1 / 1.1, None, 3, 4],
        # CCC <  0.75            --> No bridge
        ("proteins", "seq_id2"): [None, None, 7, 8],
        # CCC = None             --> No bridge
        ("proteins", "seq_id3"): [None, None, 11, 12],
        # Not in somalogic       --> No bridge
        ("proteins", "seq_id4"): [None, None, 15, 16],
        # scalar = None  --> No bridge
        ("proteins", "seq_id5"): [None, None, 19, 20],
    }
    expected_df = pd.DataFrame(expected_data, dtype=float)
    expected_df[("infos", "fluid")] = ["edta", "edta", "heparin", "serum"]

    result_df = bridge_v40_to_v41(box, df_bridge, min_ccc=0.75)
    pd.testing.assert_frame_equal(result_df, expected_df)
