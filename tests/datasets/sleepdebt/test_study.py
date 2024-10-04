"""
this test script is for testing functions in 
datasets/proteomics_sleepdebt/*_study.py
for all the study same pattern for data structuring 
was followed so only one function 
(get_faa_csrd() from "faa_csrd_study.py") is tested.
"""

import io
from pathlib import Path

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from box.manager import BoxManager
from datasets.sleepdebt.studies.faa_csrd_study import get_faa_csrd

# from utils.get import get_box

BOX_PATH = {
    "csvs": Path("archives/sleep_debt/SleepDebt_Data/ligand_receptor_model/sleepdebt/"),
    "csvs_unified": Path("archives/sleep_debt/SleepDebt_Data/unified_model/sleepdebt/"),
}


@pytest.fixture(name="input_df")
def make_input_df() -> pd.DataFrame:
    """Create a sample input dataframe for testing"""
    data_dict = {
        "subject": [
            "4164",
            "4164",
            "4203",
            "4203",
            "4203",
            "42B6",
            "42B7",
            "42B7",
        ],
        "experiment": [
            "exp1",
            "exp2",
            "exp1",
            "exp2",
            "exp3",
            "exp1",
            "exp1",
            "exp2",
        ],
        "study": ["faa_csrd"] * 8,
        "sample_id": [f"sample{i}" for i in range(1, 9)],
        "time": [
            "2022-01-01 08:35:00",
            "2022-01-02 09:35:00",
            "2022-01-01 7:35:00",
            "2022-01-02 11:35:00",
            "2022-01-03 12:35:00",
            "2022-01-01 07:10:00",
            "2022-01-01 08:00:00",
            "2022-01-02 09:00:00",
        ],
    }

    input_df = pd.DataFrame(data_dict)
    multi_columns = [
        ("ids", "subject"),
        ("ids", "experiment"),
        ("ids", "study"),
        ("ids", "sample_id"),
        ("profile", "time"),
    ]
    input_df.columns = pd.MultiIndex.from_tuples(multi_columns)

    return input_df


@pytest.fixture(name="expected_output")
def make_expected_output_df() -> pd.DataFrame:
    """Create a sample expected output dataframe for testing"""
    expected_output_dict = {
        ("ids", "subject"): [
            "4164",
            "4164",
            "4203",
            "4203",
            "4203",
            "42B6",
            "42B7",
            "42B7",
        ],
        ("ids", "experiment"): [
            "exp1",
            "exp2",
            "exp1",
            "exp2",
            "exp3",
            "exp1",
            "exp1",
            "exp2",
        ],
        ("ids", "study"): ["faa_csrd"] * 8,
        ("ids", "sample_id"): [f"sample{i}" for i in range(1, 9)],
        ("profile", "time"): [
            "2022-01-01 08:35:00",
            "2022-01-02 09:35:00",
            "2022-01-01 7:35:00",
            "2022-01-02 11:35:00",
            "2022-01-03 12:35:00",
            "2022-01-01 07:10:00",
            "2022-01-01 08:00:00",
            "2022-01-02 09:00:00",
        ],
        ("adenosine", "chronic"): [
            586.710600,
            586.344137,
            586.946793,
            586.365663,
            586.779812,
            586.833688,
            586.694373,
            586.337673,
        ],
        ("adenosine", "acute"): [
            627.579763,
            656.534175,
            611.983588,
            644.490536,
            782.131237,
            606.588119,
            633.061707,
            661.359942,
        ],
        ("adenosine", "status"): [
            "awake",
            "awake",
            "sleep",
            "awake",
            "sleep",
            "sleep",
            "awake",
            "awake",
        ],
        ("unified", "chronic"): [
            -0.162113,
            -0.181126,
            -0.136002,
            -0.193310,
            0.058317,
            -0.170746,
            -0.157154,
            -0.176086,
        ],
        ("unified", "acute"): [
            0.045201,
            0.077853,
            0.019339,
            0.062108,
            0.182065,
            0.018970,
            0.051816,
            0.084246,
        ],
        ("unified", "status"): [
            "awake",
            "awake",
            "sleep",
            "awake",
            "sleep",
            "sleep",
            "awake",
            "awake",
        ],
    }

    expected_output_df = pd.DataFrame(expected_output_dict)
    expected_output_df.columns = pd.MultiIndex.from_tuples(expected_output_df.columns)
    expected_output_df[("profile", "time")] = pd.to_datetime(
        expected_output_df[("profile", "time")]
    )
    return expected_output_df


@pytest.fixture(name="path_csv")
def load_csv_path() -> list[str]:
    """Load the path of the csv file"""
    return [
        "tests/datasets/sleepdebt/adenosine/faa_csrd_test.csv",
        "tests/datasets/sleepdebt/unified/faa_csrd_test.csv",
    ]


def test_get_study(
    mocker: MockerFixture,
    input_df: pd.DataFrame,
    expected_output: pd.DataFrame,
    path_csv: str,
):
    """test the get_study function"""
    box1 = mocker.Mock(spec=BoxManager)
    mock_path1 = Path(path_csv[0])
    mock_path2 = Path(path_csv[1])

    with open(path_csv[0], encoding="utf-8") as file:
        mock_content = file.read()

    # Ensure the mock content is not empty
    assert mock_content.strip(), "The mock CSV content is empty."

    mocker.patch.object(box1, "get_file", return_value=io.StringIO(mock_content))
    # Mock the pandas read_csv method

    output_adenosine = get_faa_csrd(input_df, box1, mock_path1)

    output_adenosine = output_adenosine.drop(
        columns=[
            ("profile", "mins_from_admission"),
            ("profile", "admission_date_time"),
            ("profile", "date"),
            ("profile", "adm_time"),
        ]
    )

    output_adenosine.rename(columns={"debt": "adenosine"}, level=0, inplace=True)
    output_adenosine.rename(
        columns={"Acute": "acute", "Chronic": "chronic"}, level=1, inplace=True
    )
    print(output_adenosine)

    with open(path_csv[1], encoding="utf-8") as file:
        mock_content = file.read()

    # Ensure the mock content is not empty
    assert mock_content.strip(), "The mock CSV content is empty."

    mocker.patch.object(box1, "get_file", return_value=io.StringIO(mock_content))
    # Mock the pandas read_csv method

    output_unified = get_faa_csrd(input_df, box1, mock_path2)
    output_unified = output_unified.drop(
        columns=[
            ("profile", "mins_from_admission"),
            ("profile", "admission_date_time"),
            ("profile", "date"),
            ("profile", "adm_time"),
        ]
    )

    output_unified.rename(columns={"debt": "unified"}, level=0, inplace=True)
    output_unified.rename(
        columns={"Acute": "acute", "Chronic": "chronic"}, level=1, inplace=True
    )

    # merging the both models

    output = pd.merge(
        left=output_adenosine,
        right=output_unified,
        on=[
            ("ids", "subject"),
            ("ids", "experiment"),
            ("ids", "study"),
            ("ids", "sample_id"),
            ("profile", "time"),
        ],
        how="inner",
        suffixes=("_adenosine", "_unified"),
    )
    output = output.round(6)
    print(output.adenosine)
    print(expected_output.adenosine)
    try:
        pd.testing.assert_frame_equal(output, expected_output)
    except AssertionError as e:
        print("DataFrames are not equal:")
        print(e)
        # Optionally, print the specific differences
        diff = output_adenosine.compare(expected_output)
        print("\nDifferences:")
        print(diff)
        raise
