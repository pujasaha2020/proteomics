"""Module that test if get functions work correctly"""

import io
from pathlib import Path

import pandas as pd
import pytest
import yaml
from pytest_mock import MockFixture

from box.manager import BoxManager
from datasets.sleepdebt.protocol import Protocol
from utils.get import (
    get_aptamers,
    get_box,
    get_debt,
    get_info_per_somalogic,
    get_proteomics,
    get_sizes,
    get_status,
)
from utils.make import make_sleep_wake_tuple

# Apply the filterwarnings marker to all tests in this file
pytestmark = pytest.mark.filterwarnings("ignore:Package 'boxsdk'*:DeprecationWarning")
TOKEN_PATH = Path("box/tokens.yaml")


def test_get_box():
    """Test get_box function"""
    if not TOKEN_PATH.exists():
        with pytest.raises(ValueError):
            get_box()
    else:
        box = get_box()
        assert isinstance(box, BoxManager)


def test_get_proteomics():
    """Test get_proteomics function"""
    if not TOKEN_PATH.exists():
        pytest.skip("Box token file is not accessible, skipping box tests.")
    box = get_box()
    # Test with default path
    get_proteomics(box)
    # Test with wrong path
    wrong_path = Path("archives/data/somasupp.csv")
    with pytest.raises(AssertionError):
        get_proteomics(box, wrong_path)


def test_get_aptamers():
    """Test get_aptamers function"""
    if not TOKEN_PATH.exists():
        pytest.skip("Box token file is not accessible, skipping box tests.")
    box = get_box()
    # Test with default path
    get_aptamers(box)
    # Test with wrong path
    wrong_path = Path("archives/data/proteomics_051124_AS.csv")
    with pytest.raises(AssertionError):
        get_aptamers(box, wrong_path)


def test_get_debt():
    """Test get_debt function"""
    if not TOKEN_PATH.exists():
        pytest.skip("Box token file is not accessible, skipping box tests.")
    box = get_box()
    # Test with default path
    get_debt(box)
    # Test with wrong path
    wrong_path = Path("archives/data/somasupp.csv")
    with pytest.raises(AssertionError):
        get_debt(box, wrong_path)


############# INFO PER SOMALOGIC ################
@pytest.fixture(name="df")
def input_df() -> pd.DataFrame:
    """Return a dataframe with NaN values"""
    data = {
        ("ids", "somalogic"): ["A", "B", "B", "C", "C", "C", None],
        ("proteins", "1"): [1.0, 2.0, 3.0, None, None, None, None],
        ("proteins", "2"): [1.0, None, None, 4.0, 5.0, 6.0, None],
        ("proteins", "3"): [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, None],
        ("proteins", "4"): [None, None, None, None, None, None, None],
    }
    return pd.DataFrame(data)


def test_get_info_per_somalogic(df: pd.DataFrame):
    """Test get_info_per_somalogic function"""
    expected_info = {
        "A": {"proteins": {"1", "2", "3"}, "n_samples": 1},
        "B": {"proteins": {"1", "3"}, "n_samples": 2},
        "C": {"proteins": {"2", "3"}, "n_samples": 3},
    }
    info = get_info_per_somalogic(df)
    assert info == expected_info


############# GET SIZE ################
def test_get_sizes(mocker: MockFixture):
    """Test get_sizes function"""
    expected_sizes = [[1, 1], [2, 2]]
    box = mocker.Mock(spec=BoxManager)

    # Right format
    file = io.StringIO()
    yaml.dump({"n_samples, n_proteins": expected_sizes}, file)
    file.seek(0)
    box.get_file.return_value = file
    sizes = get_sizes(box)
    assert sizes == expected_sizes

    # Wrong format
    file = io.StringIO()
    yaml.dump({"wrong format": expected_sizes}, file)
    file.seek(0)
    box.get_file.return_value = file
    with pytest.raises(ValueError):
        get_sizes(box)

    # Wrong path
    box.get_file.side_effect = FileNotFoundError
    with pytest.raises(FileNotFoundError):
        get_sizes(box)


########GET STATUS########


# Function to read a YAML file
def read_yaml(file_path):
    """This function reads a yaml file and returns the data"""
    with open(file_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data


@pytest.fixture(name="input_yaml_construct_protocol")
def get_toy_protocol():
    """This function reads the yaml file and returns the data"""
    file_path = "tests/utils/test_protocol.yaml"
    return read_yaml(file_path)


@pytest.fixture(name="protocol")
def define_protocol(input_yaml_construct_protocol: dict):
    """
    This function defines the protocol
    """
    protocol = Protocol("protocol1", "def_2")
    t_ae_sl = make_sleep_wake_tuple(input_yaml_construct_protocol, protocol.name)

    protocol.fill(t_ae_sl[0], t_ae_sl[1])
    return protocol


@pytest.fixture(name="expected_output_get_status")
def output_from_get_status():
    """This function returns the expected output from get_status"""
    return pd.DataFrame(
        {"time": [200, 970, 1552], "status": ["awake", "sleep", "awake"]}
    )


def test_get_status(protocol: Protocol, expected_output_get_status: pd.DataFrame):
    """
    This function tests the function get_status in the
    adenosine_model.py
    """
    status = expected_output_get_status["time"].apply(
        lambda x: get_status(x, protocol.time_sequence())
    )
    assert status.equals(
        expected_output_get_status["status"]
    ), "The actual output does not match the expected output."
