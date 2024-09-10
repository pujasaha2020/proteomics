# this code is  to extract sleep debt at blood collection time or  time when proteomics data were available.
#
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from box.manager import BoxManager
from utils.save import save_to_csv

"""
Zeitzer study has subjects with different sleep-wake schedules.
Most of them have a common schedule like 966 minutes of wake time, 
480 minutes of sleep time, and 540 minutes of wake time.
But some subjects have different schedules. 
"get_zeitzer_protocols()" function extracts the sleep-wake schedule for each subject.
"get_zeitzer()" function extracts the sleep debt at blood collection time or the time 
when proteomics data were available.
"""


def get_zeitzer_protocols(proteomics_data_new: pd.DataFrame) -> pd.DataFrame:
    """
    extracts the sleep-wake schedule for each subject.
    """
    sub_zeitzer = np.concat(
        [
            proteomics_data_new[proteomics_data_new[("ids", "study")] == "zeitzer_mbc"][
                ("ids", "subject")
            ].unique(),
            proteomics_data_new[proteomics_data_new[("ids", "study")] == "zeitzer_ctl"][
                ("ids", "subject")
            ].unique(),
        ]
    )
    # Initialize the dataframe
    columns = [
        "subject",
        "hours_awake",
        "hours_sleep",
        "hours_awake1",
        "dim",
        "wake_up_time",
        "sample_2",
        "sample_15",
        "sample_39",
        "sample_52",
    ]

    df_zeitzer = pd.DataFrame(columns=columns)
    df_zeitzer = df_zeitzer.astype(
        {
            "wake_up_time": "datetime64[ns]",
            "sample_2": "datetime64[ns]",
            "sample_15": "datetime64[ns]",
            "sample_39": "datetime64[ns]",
            "sample_52": "datetime64[ns]",
        }
    )
    # df_zeitzer.head()

    for i in sub_zeitzer:
        df_sub = proteomics_data_new[
            proteomics_data_new[("ids", "subject")] == i
        ].copy()

        df_sub[("ids", "sample_id")] = df_sub[("ids", "sample_id")].str.split().str[-1]

        needed_sample_ids = ["2", "15", "39", "52"]
        if not all(
            [
                sample_id in df_sub[("ids", "sample_id")].values
                for sample_id in needed_sample_ids
            ]
        ):
            print("All samples are not present")
            continue

        # Extract required values with checks
        sample_2 = df_sub[df_sub[("ids", "sample_id")] == "2"][
            ("profile", "clock_time")
        ].iloc[0]
        sample_15 = df_sub[df_sub[("ids", "sample_id")] == "15"][
            ("profile", "clock_time")
        ].iloc[0]
        sample_39 = df_sub[df_sub[("ids", "sample_id")] == "39"][
            ("profile", "clock_time")
        ].iloc[0]
        sample_52 = df_sub[df_sub[("ids", "sample_id")] == "52"][
            ("profile", "clock_time")
        ].iloc[0]

        wake_up_time = pd.to_datetime(
            df_sub[df_sub[("ids", "sample_id")] == "2"][("profile", "clock_time")].iloc[
                0
            ]
        ) - timedelta(minutes=126 + 7 * 60)

        dim = df_sub.shape[1]
        # Create a new row as a DataFrame
        new_row = pd.DataFrame(
            {
                "subject": [i],
                "dim": [dim],
                "wake_up_time": [wake_up_time],
                "sample_2": [sample_2],
                "sample_15": [sample_15],
                "sample_39": [sample_39],
                "sample_52": [sample_52],
            }
        )

        # Concatenate the new row to the existing DataFrame
        df_zeitzer = pd.concat([df_zeitzer, new_row], ignore_index=True)

    # Ensure the columns are in datetime format
    df_zeitzer["wake_up_time"] = pd.to_datetime(df_zeitzer["wake_up_time"])
    df_zeitzer["sample_15"] = pd.to_datetime(df_zeitzer["sample_15"])
    df_zeitzer["sample_39"] = pd.to_datetime(df_zeitzer["sample_39"])
    df_zeitzer["sample_52"] = pd.to_datetime(df_zeitzer["sample_52"])

    # Subtract the datetime columns
    df_zeitzer["hours_awake"] = df_zeitzer["sample_15"] - df_zeitzer["wake_up_time"]
    df_zeitzer["hours_sleep"] = df_zeitzer["sample_39"] - df_zeitzer["sample_15"]
    df_zeitzer["hours_awake1"] = df_zeitzer["sample_52"] - df_zeitzer["sample_39"]

    df_zeitzer["hours_awake"] = df_zeitzer["hours_awake"].apply(
        lambda x: x.total_seconds() / 60
    )
    df_zeitzer["hours_sleep"] = df_zeitzer["hours_sleep"].apply(
        lambda x: x.total_seconds() / 60
    )
    df_zeitzer["hours_awake1"] = df_zeitzer["hours_awake1"].apply(
        lambda x: x.total_seconds() / 60
    )
    # Replace NaN values with the column mean for specific columns
    df_zeitzer["hours_awake"] = df_zeitzer["hours_awake"].fillna(
        df_zeitzer["hours_awake"].mean()
    )
    df_zeitzer["hours_sleep"] = df_zeitzer["hours_sleep"].fillna(
        df_zeitzer["hours_sleep"].mean()
    )
    df_zeitzer["hours_awake1"] = df_zeitzer["hours_awake1"].fillna(
        df_zeitzer["hours_awake1"].mean()
    )

    df_zeitzer.head()

    # Filter for uncommon rows
    df_zeitzer_uncommon = df_zeitzer[
        ~(
            (df_zeitzer[("hours_awake")] == "966")
            & (df_zeitzer[("hours_sleep")] == "480")
            & (df_zeitzer[("hours_awake1")] == "540")
        )
    ]

    return df_zeitzer


# this code is  to extract sleep debt at blood collection time or
# time when proteomics data were available.
def get_zeitzer(
    proteomics_data_new: pd.DataFrame,
    box: BoxManager,
    path: Path,
) -> pd.DataFrame:
    """
    This function extracts the sleep debt at blood collection time or the time
    when proteomics data were available.
    """

    zeitzer_data = proteomics_data_new[
        (proteomics_data_new[("ids", "study")] == "zeitzer_mbc")
        | (proteomics_data_new[("ids", "study")] == "zeitzer_ctl")
    ].copy()
    print("shape before merging admission time", zeitzer_data.shape)

    # print("shape before merging admission time", zeitzer_data.shape)

    df_zeitzer = get_zeitzer_protocols(zeitzer_data)
    print("shape df_zeitzer protocol", df_zeitzer.shape)

    save_to_csv(
        box,
        df_zeitzer,
        path / "zeitzer_uncommon_protocol_from_python.csv",
        index=False,
    )

    # Drop rows with missing values
    df_zeitzer = df_zeitzer.dropna(subset=[("wake_up_time")])

    df_zeitzer.rename(columns={"wake_up_time": "time"}, inplace=True)
    # print(df_zeitzer.head())

    df_id_admit_date_time = pd.DataFrame(
        {
            ("ids", "subject"): df_zeitzer["subject"],
            ("profile", "time"): df_zeitzer["time"],
        }
    )

    proteins_columns = [col for col in zeitzer_data.columns if col[0] == "proteins"]

    # removed rows with proteins having all missing values
    zeitzer_data_no_proteins = zeitzer_data.dropna(subset=proteins_columns, how="all")
    zeitzer_data_no_proteins = zeitzer_data_no_proteins[["ids", "infos", "profile"]]
    print(
        "shape after removing rows with all proteins missing values",
        zeitzer_data_no_proteins.shape,
    )

    protemics_data1 = pd.merge(
        zeitzer_data_no_proteins,
        df_id_admit_date_time,
        on=[("ids", "subject")],
        how="inner",
    )

    print("shape after merging admission time", protemics_data1.shape)

    protemics_data1[("profile", "clock_time")] = pd.to_datetime(
        protemics_data1[("profile", "clock_time")]
    )
    protemics_data1 = protemics_data1.dropna(subset=[("profile", "clock_time")])

    # Calculating mins_from_admission
    protemics_data1[("profile", "mins_from_admission")] = (
        protemics_data1[("profile", "clock_time")]
        - protemics_data1[("profile", "time")]
    ).dt.total_seconds() / 60 + 15840

    protemics_data1[("profile", "mins_from_admission")] = protemics_data1[
        ("profile", "mins_from_admission")
    ].astype(int)

    # Filter for uncommon rows
    df_zeitzer_selected = df_zeitzer[
        ~(
            (df_zeitzer[("hours_awake")] == 966.0)
            & (df_zeitzer[("hours_sleep")] == 480.0)
            & (df_zeitzer[("hours_awake1")] == 540.0)
        )
    ]

    exp_id = df_zeitzer_selected["subject"].unique()
    print("number of uncommon subjects", len(exp_id))
    df_uncommon = apply_debt_uncommon_routine(protemics_data1, exp_id, box, path)
    df_zeitzer_selected = df_zeitzer[
        (
            (df_zeitzer[("hours_awake")] == 966.0)
            & (df_zeitzer[("hours_sleep")] == 480.0)
            & (df_zeitzer[("hours_awake1")] == 540.0)
        )
    ]
    exp_id = df_zeitzer_selected["subject"].unique()
    print("number of common subjects", len(exp_id))
    df_common = apply_debt_common_routine(protemics_data1, exp_id, box, path)
    zeitzer_sleepdebt = pd.concat([df_common, df_uncommon])
    print("shape after merging sleepdebt", zeitzer_sleepdebt.shape)

    return zeitzer_sleepdebt


def apply_debt_common_routine(
    df: pd.DataFrame, ids: list, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    This function calculates the sleep debt at the time of blood collection for subjects
    with common sleep-wake schedule.
    """
    file = box.get_file(path / "Zeitzer_class.csv")
    sleep_debt_zeitzer = pd.read_csv(file)
    sleep_debt_zeitzer.drop(columns=["l_debt", "s_debt"], inplace=True, errors="ignore")

    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    sleep_debt_zeitzer.columns = pd.MultiIndex.from_tuples(multi_level_columns)

    # Renaming column
    sleep_debt_zeitzer.columns = pd.MultiIndex.from_tuples(
        sleep_debt_zeitzer.set_axis(sleep_debt_zeitzer.columns.values, axis=1).rename(
            columns={("profile", "time"): ("profile", "mins_from_admission")}
        )
    )
    # filtering subjects who have same sleep-wake schedule
    filtered_df = df[df[("ids", "subject")].isin(ids)]
    print(
        "data dimension for common subject before merging sleepdebt", filtered_df.shape
    )

    # Merging data
    zeitzer_sleepdebt = pd.merge(
        left=filtered_df,
        right=sleep_debt_zeitzer,
        on=[("profile", "mins_from_admission")],
        # right_on=[('profile','time')],
        how="inner",
    )
    zeitzer_sleepdebt = zeitzer_sleepdebt.drop_duplicates()
    print(
        "data dimension for common subject after merging sleepdebt",
        zeitzer_sleepdebt.shape,
    )
    return zeitzer_sleepdebt


def apply_debt_uncommon_routine(
    df: pd.DataFrame, ids: list, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    This function calculates the sleep debt at the time of blood collection for subjects
    with uncommon sleep-wake schedule."""
    empty_df = pd.DataFrame()
    # filtering subjects who have same sleep-wake schedule
    uncommon_df = df[df[("ids", "subject")].isin(ids)]
    print(
        "data dimension for uncommon subject before merging sleepdebt",
        uncommon_df.shape,
    )

    for key in ids:
        print(key)
        file = box.get_file(path / f"Zeitzer_Uncommon_{key}_class.csv")
        sleep_debt_zeitzer = pd.read_csv(file)
        sleep_debt_zeitzer.drop(
            columns=["l_debt", "s_debt"], inplace=True, errors="ignore"
        )
        sleep_debt_zeitzer.drop(
            columns=["l_debt", "s_debt"], inplace=True, errors="ignore"
        )

        multi_level_columns = [
            ("profile", "time"),
            ("debt", "Chronic"),
            ("debt", "Acute"),
            ("debt", "status"),
        ]
        sleep_debt_zeitzer.columns = pd.MultiIndex.from_tuples(multi_level_columns)

        # Renaming column
        sleep_debt_zeitzer.columns = pd.MultiIndex.from_tuples(
            sleep_debt_zeitzer.set_axis(
                sleep_debt_zeitzer.columns.values, axis=1
            ).rename(columns={("profile", "time"): ("profile", "mins_from_admission")})
        )
        # filtering the subject specific data for before merging, as sleepdebt  are different for different subject
        # because their sleep-wake schedule is little different although they are in same protocol
        filtered_df = df[df[("ids", "subject")].str.contains(key)]
        # print("dim of subject specific data", filtered_df.shape)
        # Merging data
        zeitzer_sleepdebt = pd.merge(
            left=filtered_df,
            right=sleep_debt_zeitzer,
            on=[("profile", "mins_from_admission")],
            # right_on=[('profile','time')],
            how="inner",
        )
        # print(
        #   "data dimension for uncommon subject specific after merging sleepdebt",
        #   zeitzer_sleepdebt.shape,
        # )
        empty_df = pd.concat([empty_df, zeitzer_sleepdebt])
        empty_df = empty_df.drop_duplicates()
    print("data dimension for uncommon subject after merging sleepdebt", empty_df.shape)
    return empty_df
