"""Tests for the biomarker sleep steps module"""

import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockerFixture
from statsmodels.regression.mixed_linear_model import MixedLM  # type: ignore
from statsmodels.regression.mixed_linear_model import MixedLMResults  # type: ignore

from biomarkers.sleep.steps import postprocess_results, preprocess_data, run_lme_sleep


@pytest.fixture(name="df")
def input_df() -> pd.DataFrame:
    """Return a somalogic dataframe with Total CV Plasma column"""
    df = pd.DataFrame(
        {
            ("proteins", "P1"): [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, None, 8.0],
            ("proteins", "P2"): 9 * [None],
            ("info", "sample_id"): [0, 1, 2, 3, 4, 5, 6, 7, 8],
            ("info", "state"): 4 * ["sleep", "wake"] + [None],
            ("info", "subject"): 6 * ["A"] + 3 * ["B"],
            ("info", "fluid"): 9 * ["edta"],
        }
    )
    return df


@pytest.fixture(name="debts")
def input_debts() -> pd.DataFrame:
    """Return a dataframe with debts information"""
    debts = pd.DataFrame(
        {
            "sample_id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "l": [0.1, 0.2, 0.3, 0.4, None, 0.6, 0.7, 0.8, 0.9],
            "s": [0.5, 0.6, 0.7, None, 0.9, 1.0, 1.1, 1.2, 1.3],
        }
    )
    return debts


################## PREPROCESS ###################
def test_preprocess_data(mocker: MockerFixture, df: pd.DataFrame, debts: pd.DataFrame):
    """Test preprocess_data function"""

    # Patch log_normalize_proteins function
    mocker.patch(
        "biomarkers.sleep.steps.log_normalize_proteins", side_effect=lambda x: x
    )

    expected_data = {
        "P1": pd.DataFrame(
            {
                "log_protein": [1.0, 2.0, 3.0],
                "acute": [0.5, 0.6, 0.7],
                "chronic": [0.1, 0.2, 0.3],
                "sleep": [0.0, 1.0, 0.0],
                "subject": 3 * ["A"],
                "fluid": 3 * ["edta"],
            }
        ),
    }
    # Test missing s or l in A, merge on sample_id
    data = preprocess_data(df, debts, min_group_size=3, plot=False)
    assert expected_data.keys() == data.keys()
    pd.testing.assert_frame_equal(data["P1"], expected_data["P1"])

    expected_data = {
        "P1": pd.DataFrame(
            {
                "log_protein": [1.0, 2.0, 3.0, 6.0],
                "acute": [0.5, 0.6, 0.7, 1.0],
                "chronic": [0.1, 0.2, 0.3, 0.6],
                "sleep": [0.0, 1.0, 0.0, 1.0],
                "subject": 3 * ["A"] + ["B"],
                "fluid": 4 * ["edta"],
            }
        ),
    }
    # Test missing state and missing protein in B
    data = preprocess_data(df, debts, min_group_size=1, plot=False)
    assert expected_data.keys() == data.keys()
    pd.testing.assert_frame_equal(data["P1"], expected_data["P1"])

    # Min group size too high
    with pytest.raises(ValueError):
        preprocess_data(df, debts, min_group_size=4, plot=False)

    # Mix fluid type within A
    df[("info", "fluid")] = 3 * ["edta"] + 6 * ["heparin"]
    with pytest.raises(ValueError):
        preprocess_data(df, debts, min_group_size=1, plot=False)


##################### LME #######################
@pytest.fixture(name="data")
def input_data() -> pd.DataFrame:
    """Return a dataframe with log_protein, acute, chronic, sleep, and subject columns"""
    data = pd.DataFrame(
        {
            "log_protein": [2.0, 2.5, 3.0, 3.5],
            "acute": [1, 0, 1, 0],
            "chronic": [0, 1, 0, 1],
            "sleep": [1, 0, 1, 0],
            "subject": ["A", "A", "B", "B"],
        }
    )
    return data


def test_run_lme_sleep(mocker: MockerFixture, data: pd.DataFrame):
    """Test run_lme_sleep function"""
    # Mock the statsmodels MixedLM.fit method
    mock_model = mocker.Mock(spec=MixedLM)
    mock_results = mocker.Mock(spec=MixedLMResults)
    mock_results.converged = True
    mock_results.cov_re = pd.DataFrame([[0.1]])
    mock_results.params = pd.Series({"acute": 0.5, "chronic": -0.3, "sleep": 0.2})
    mock_results.pvalues = pd.Series({"acute": 0.04, "chronic": 0.05, "sleep": 0.01})
    mocker.patch(
        "biomarkers.sleep.steps.sm.MixedLM.from_formula", return_value=mock_model
    )
    mocker.patch.object(mock_model, "fit", return_value=mock_results)
    mocker.patch.object(
        mock_results,
        "conf_int",
        return_value=pd.DataFrame(
            {0: [0.1, -0.4, 0.1], 1: [0.9, -0.2, 0.3]},
            index=["acute", "chronic", "sleep"],
        ),
    )

    results = run_lme_sleep(data)

    expected_results = {
        ("infos", "#samples"): 4,
        ("infos", "#subjects"): 2,
        ("infos", "converge"): True,
        ("infos", "group_var"): np.float64(0.1),
        ("acute", "param"): np.float64(0.5),
        ("acute", "pvalue"): np.float64(0.04),
        ("acute", "[0.025"): np.float64(0.1),
        ("acute", "0.975]"): np.float64(0.9),
        ("chronic", "param"): np.float64(-0.3),
        ("chronic", "pvalue"): np.float64(0.05),
        ("chronic", "[0.025"): np.float64(-0.4),
        ("chronic", "0.975]"): np.float64(-0.2),
        ("sleep", "param"): np.float64(0.2),
        ("sleep", "pvalue"): np.float64(0.01),
        ("sleep", "[0.025"): np.float64(0.1),
        ("sleep", "0.975]"): np.float64(0.3),
    }

    assert results == expected_results


################# POSTPROCESS ###################
@pytest.fixture(name="results")
def input_results() -> pd.DataFrame:
    """Fixture for results DataFrame"""
    return pd.DataFrame(
        {
            ("infos", "converge"): [True, False, True],
            ("acute", "pvalue"): [0.01, 0.05, 0.02],
            ("chronic", "pvalue"): [0.02, 0.06, 0.03],
            ("sleep", "pvalue"): [0.03, 0.07, 0.04],
        },
        index=[1, 2, 3],
    )


@pytest.fixture(name="somalogic")
def input_somalogic() -> pd.DataFrame:
    """Fixture for somalogic DataFrame"""
    return pd.DataFrame(
        {
            "seq_id": [1, 2, 3],
            "Target Name": ["P1", "P2", "P3"],
            "Entrez Gene Name": ["Gene1", "Gene2", "Gene3"],
        }
    ).set_index("seq_id")


def test_postprocess_results(
    mocker: MockerFixture, results: pd.DataFrame, somalogic: pd.DataFrame
):
    """Test postprocess_results function"""
    max_pvalue = 0.05
    plot = False

    # Patch multipletests function
    mocker.patch(
        target="biomarkers.sleep.steps.multipletests",
        side_effect=lambda pvals, alpha, method: (None, pvals, None, None),
    )

    # Expected results after dropping non-converged models
    expected_results = pd.DataFrame(
        {
            ("infos", "converge"): [True, True],
            ("acute", "pvalue"): [0.01, 0.02],
            ("acute", "pvalue_fdr"): [0.01, 0.02],
            ("chronic", "pvalue"): [0.02, 0.03],
            ("chronic", "pvalue_fdr"): [0.02, 0.03],
            ("sleep", "pvalue"): [0.03, 0.04],
            ("sleep", "pvalue_fdr"): [0.03, 0.04],
        },
        index=pd.MultiIndex.from_frame(
            pd.DataFrame(
                {
                    "seq_id": [1, 3],
                    "protein": ["P1", "P3"],
                    "gene": ["Gene1", "Gene3"],
                }
            )
        ),
    )

    final_results = postprocess_results(results, somalogic, max_pvalue, plot)
    pd.testing.assert_frame_equal(final_results, expected_results)
