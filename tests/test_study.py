# this test script is for testing functions in datasets/proteomics_sleepdebt/*_study.py
# for all the study same pattern for data structuring was followed so only one function is tested.

from pathlib import Path

import pandas as pd

from datasets.proteomics_sleepdebt.faa_csrd_study import get_faa_csrd
from utils.get import get_box

BOX_PATH = {
    "csvs": Path("archives/sleep_debt/SleepDebt_Data/ligand_receptor_model/sleepdebt/"),
    "csvs_unified": Path("archives/sleep_debt/SleepDebt_Data/unified_model/sleepdebt/"),
}


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
    "clock_time": [
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
    ("profile", "clock_time"),
]
input_df.columns = pd.MultiIndex.from_tuples(multi_columns)


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
    ("profile", "clock_time"): [
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
expected_output_df[("profile", "clock_time")] = pd.to_datetime(
    expected_output_df[("profile", "clock_time")]
)


def test_get_study():
    """
    test the get_study function
    """
    box1 = get_box()
    output_adenosine = get_faa_csrd(input_df, box1, BOX_PATH["csvs"])

    output_adenosine = output_adenosine.drop(
        columns=[
            ("profile", "mins_from_admission"),
            ("profile", "admission_date_time"),
            ("profile", "date"),
            ("profile", "time"),
        ]
    )

    output_adenosine.rename(columns={"debt": "adenosine"}, level=0, inplace=True)
    output_adenosine.rename(
        columns={"Acute": "acute", "Chronic": "chronic"}, level=1, inplace=True
    )

    output_unified = get_faa_csrd(input_df, box1, BOX_PATH["csvs_unified"])
    output_unified = output_unified.drop(
        columns=[
            ("profile", "mins_from_admission"),
            ("profile", "admission_date_time"),
            ("profile", "date"),
            ("profile", "time"),
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
            ("profile", "clock_time"),
        ],
        how="inner",
        suffixes=("_adenosine", "_unified"),
    )
    output = output.round(6)
    print(output)
    print(expected_output_df)
    """
    # Compare the DataFrames
    diff = output.compare(expected_output_df)
    print("Differences between output and expected DataFrame:")
    print(diff)

    print("Data types in Output DataFrame:")
    print(output.dtypes)

    print("Data types in Expected Output DataFrame:")
    print(expected_output_df.dtypes)

    # Check for floating point precision issues
    if output.shape != expected_output_df.shape:
        print("Shapes are different")
        return False
    for col in output.columns:
        if output[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
            if not np.allclose(output[col], expected_output_df[col], atol=1e-8):
                print(f"Column {col} differs")
                return False
        else:
            if not output[col].equals(expected_output_df[col]):
                print(f"Column {col} differs")
                return False

    # Check indexes
    print("Indexes in Output DataFrame:")
    print(output.index)
    
    print("Indexes in Expected Output DataFrame:")
    print(expected_output_df.index)
    """
    pd.testing.assert_frame_equal(output, expected_output_df)
    # assert output.equals(
    #    expected_output_df
    # ), "The actual output does not match the expected output."


test_get_study()
