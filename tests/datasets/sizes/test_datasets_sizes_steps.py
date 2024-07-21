""" Test the function to """

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from box.manager import BoxManager
from datasets.sizes.steps import optimize_size, prepare_size_data


@pytest.fixture(name="info")
def input_info() -> dict:
    """Return a dataframe with NaN values"""
    # fmt: off
    data = {
        "A": {"proteins": {"1", "2", "3", "4", "5"      }, "n_samples": 5},
        "B": {"proteins": {          "3", "4", "5", "6" }, "n_samples": 5},
        "C": {"proteins": {"1", "2", "3", "4",          }, "n_samples": 10},
        "D": {"proteins": {"1"                          }, "n_samples": 20},
        "E": {"proteins": {               "4",      "6" }, "n_samples": 100},
    }
    # fmt: on
    return data


@pytest.fixture(name="presence")
def input_presence():
    """Return the corresponding presence matrix"""
    data = np.array(
        [
            [1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 0],
            [1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 1],
        ]
    )
    return data


@pytest.fixture(name="n_samples")
def input_n_samples():
    """Return the corresponding n_samples array"""
    return np.array([5, 5, 10, 20, 100])


def test_prepare_size_data(
    mocker: MockerFixture, info: dict, presence: np.ndarray, n_samples: np.ndarray
):
    """Test prepare_size_data function"""
    box = mocker.Mock(spec=BoxManager)
    mock_df = mocker.Mock(spec=pd.DataFrame)
    mock_proteins = mocker.Mock(spec=pd.DataFrame)
    mock_proteins.columns.tolist.return_value = ["1", "2", "3", "4", "5", "6"]
    mock_df.proteins = mock_proteins
    mocker.patch("datasets.sizes.steps.get_proteomics", return_value=mock_df)
    mocker.patch("datasets.sizes.steps.get_info_per_somalogic", return_value=info)
    results_presence, results_n_samples = prepare_size_data(box, Path("path"))
    assert np.all(results_presence == presence)
    assert np.all(results_n_samples == n_samples)


def test_optimize_size(presence: np.ndarray, n_samples: np.ndarray):
    """Test optimize_size function"""

    # min_proteins < 0
    with pytest.raises(ValueError):
        optimize_size(presence, n_samples, -1)

    #  0 <= min_proteins <= n_proteins
    expected_data: list[dict[str, Any]] = [
        {
            "min_proteins": 0,
            "results": {
                "somalogic": [1, 1, 1, 1, 1],
                "proteins": [0, 0, 0, 0, 0, 0],
            },
        },
        {
            "min_proteins": 1,
            "results": {
                "somalogic": [1, 1, 1, 0, 1],
                "proteins": [0, 0, 0, 1, 0, 0],
            },
        },
        {
            "min_proteins": 2,
            "results": {
                "somalogic": [0, 1, 0, 0, 1],
                "proteins": [0, 0, 0, 1, 0, 1],
            },
        },
        {
            "min_proteins": 3,
            "results": {
                "somalogic": [1, 0, 1, 0, 0],
                "proteins": [1, 1, 1, 1, 0, 0],
            },
        },
        {
            "min_proteins": 4,
            "results": {
                "somalogic": [1, 0, 1, 0, 0],
                "proteins": [1, 1, 1, 1, 0, 0],
            },
        },
        {
            "min_proteins": 5,
            "results": {
                "somalogic": [1, 0, 0, 0, 0],
                "proteins": [1, 1, 1, 1, 1, 0],
            },
        },
        {
            "min_proteins": 6,
            "results": {
                "somalogic": [0, 0, 0, 0, 0],
                "proteins": [1, 1, 1, 1, 1, 1],
            },
        },
    ]

    for expected in expected_data:
        n, x, z = optimize_size(presence, n_samples, expected["min_proteins"])
        assert n == n_samples @ expected["results"]["somalogic"]
        assert np.all(x == expected["results"]["somalogic"])
        assert np.all(z == expected["results"]["proteins"])

    # min_proteins > n_proteins
    with pytest.raises(ValueError):
        optimize_size(presence, n_samples, 7)
