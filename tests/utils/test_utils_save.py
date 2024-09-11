"""Tests for the save module"""

from pathlib import Path

import pandas as pd
import pytest
import yaml
from pytest_mock import MockerFixture

from box.manager import BoxManager
from utils.save import save_to_csv, save_to_yaml


@pytest.fixture(name="box")
def mock_box(mocker: MockerFixture) -> BoxManager:
    """Return a mocked BoxManager object"""
    box = mocker.Mock(spec=BoxManager)
    return box


###################### CSV ######################
def test_save_to_csv(mocker: MockerFixture, box: BoxManager):
    """Test save_to_csv function"""
    # Patch the save_file function
    mock_save_file = mocker.patch.object(box, "save_file")

    # Create a sample DataFrame
    df = pd.DataFrame({"column1": [1, 2], "column2": [3, 4]})

    # Use an invalid path (not a .csv file)
    for invalid_path in [Path("test.txt"), Path("test")]:
        with pytest.raises(ValueError):
            save_to_csv(box, df, invalid_path)

    # Use the save_to_csv function
    path = Path("test.csv")
    save_to_csv(box, df, path, index=False)
    mock_save_file.assert_called_once()
    saved_file, saved_path = mock_save_file.call_args[0]

    # Ensure the saved path is correct
    assert saved_path == path

    # Read the CSV content from the StringIO object
    saved_file.seek(0)
    saved_df = pd.read_csv(saved_file)

    # Verify that the DataFrame was saved correctly
    pd.testing.assert_frame_equal(df, saved_df)


###################### YML ######################
def test_save_to_yaml(mocker, box: BoxManager):
    """Test save_to_yaml function"""
    # Patch the save_file function
    mock_save_file = mocker.patch.object(box, "save_file")

    # Create a sample dictionary
    data = {"name": "Alice", "age": 25}

    # Use an invalid path (not a .yaml or .yml file)
    for invalid_path in [Path("test.txt"), Path("test")]:
        with pytest.raises(ValueError):
            save_to_yaml(box, data, invalid_path)

    # Use the save_to_yaml function
    path = Path("test.yaml")
    save_to_yaml(box, data, path)
    mock_save_file.assert_called_once()
    saved_file, saved_path = mock_save_file.call_args[0]

    # Ensure the saved path is correct
    assert saved_path == path

    # Read the YAML content from the StringIO object
    saved_file.seek(0)
    saved_data = yaml.safe_load(saved_file)

    # Verify that the dictionary was saved correctly
    assert data == saved_data
