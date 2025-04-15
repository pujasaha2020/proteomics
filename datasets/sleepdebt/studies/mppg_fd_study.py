"""
This piece of code do the data processing for the "mppg CSR" sample.
It reads the sleep debt data and merge it with the proteomics data.
note: subjects have slightly different protocols than each other.
This fact is taken care of while merging the sleep debt data with the proteomics data.
"""

# pylint: disable=R0801

from pathlib import Path

import pandas as pd

from box.manager import BoxManager


def get_mppg_fd(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """Subject 3453, 3536, 3552: multiple experiment, 3552 also participated
    in mppg control experiment
    """
    """
    # SP1 time and date
    sub_admission_time = {
        "3453": "7:01",  # 3453HY52---> 7:01, 3453HY73 : 7:31
        "3536": "7:30",  # 3536HY52----> 7:30, 3536HY83: 7:00
        "3552": "6:31",  # 3552HY62----> 6:31, 3552HY73 : 7:31
        "2056": "8:59",
        "26P2": "6:58",
        "3557": "8:06",
    }
    sub_admission_date = {
        "3453": "2021-12-26",  # "2021-12-30",  # 3453HY52---> "2021-12-30", 3453HY73 :"2022-01-01"
        "3536": "2021-12-26",  # 3536HY52----> "2021-12-30", 3536HY83: "2022-01-01"
        "3552": "2021-12-28",  # 3552HY62----> "2022-01-01", 3552HY73 : "2022-01-01"
        "2056": "2021-12-28",
        "26P2": "2021-12-28",
        "3557": "2021-12-28",
    }
    """
    # SP7/WP8 time
    sub_admission_time = {
        "3453": "7:00",  # 3453HY52---> 7:00, 3453HY73 : 6:30
        "3536": "7:29",  # 3536HY52----> 7:29, 3536HY83: 5:59
        "3552": "6:31",  # 3552HY62----> 6:31, 3552HY73 : 6:31
        "2056": "7:59",
        "26P2": "5:58",
        "3557": "8:05",
    }

    sub_admission_date = {
        "3453": "2021-12-30",  # "2021-12-30",  # 3453HY52---> "2021-12-30", 3453HY73 :"2022-01-01"
        "3536": "2021-12-30",  # 3536HY52----> "2021-12-30", 3536HY83: "2022-01-01"
        "3552": "2022-01-01",  # 3552HY62----> "2022-01-01", 3552HY73 : "2022-01-01"
        "2056": "2022-01-01",
        "26P2": "2022-01-01",
        "3557": "2022-01-01",
    }

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "mppg_fd"
            ]["subject"].unique(),
        }
    )
    df_id_admit_time[("profile", "adm_time")] = df_id_admit_time[
        ("ids", "subject")
    ].map(sub_admission_time)

    df_id_admit_time[("profile", "date")] = df_id_admit_time[("ids", "subject")].map(
        sub_admission_date
    )

    mppg_fd_data = proteomics_data_new.loc[
        proteomics_data_new[("ids", "study")] == "mppg_fd", :
    ]

    print("data dimension before merging admission time", mppg_fd_data.shape)

    protemics_data1 = pd.merge(
        mppg_fd_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
    )

    print("data dimension after merging admission time", protemics_data1.shape)

    # changing admission time and date for subject who participated in multiple experiments.
    protemics_data1.loc[
        protemics_data1[("ids", "experiment")].isin(
            ["3453HY73_1", "3453HY73_2", "3453HY73_3", "3453HY73_4"]
        ),
        ("profile", "adm_time"),
    ] = "6:30"

    protemics_data1.loc[
        protemics_data1[("ids", "experiment")].isin(
            ["3453HY73_1", "3453HY73_2", "3453HY73_3", "3453HY73_4"]
        ),
        ("profile", "date"),
    ] = "2022-01-01"

    protemics_data1.loc[
        protemics_data1[("ids", "experiment")].isin(
            ["3536HY83_1", "3536HY83_2", "3536HY83_1"]
        ),
        ("profile", "adm_time"),
    ] = "5:59"

    protemics_data1.loc[
        protemics_data1[("ids", "experiment")].isin(
            ["3536HY83_1", "3536HY83_2", "3536HY83_1"]
        ),
        ("profile", "date"),
    ] = "2022-01-01"

    protemics_data1.loc[
        protemics_data1[("ids", "experiment")].isin(
            ["3552HY73_1", "3552HY73_2", "3552HY73_3"]
        ),
        ("profile", "adm_time"),
    ] = "6:31"

    protemics_data1[("profile", "date")] = pd.to_datetime(
        protemics_data1[("profile", "date")]
    )
    protemics_data1[("profile", "date")] = protemics_data1[
        ("profile", "date")
    ].dt.strftime("%Y-%m-%d")

    protemics_data1[("profile", "admission_date_time")] = (
        protemics_data1[("profile", "date")]
        + " "
        + protemics_data1[("profile", "adm_time")]
    )
    protemics_data1[("profile", "admission_date_time")] = pd.to_datetime(
        protemics_data1[("profile", "admission_date_time")]
    )
    # print(protemics_data1[("profile", "time")])
    protemics_data1[("profile", "time")] = protemics_data1[("profile", "time")].apply(
        lambda x: x.split(".")[0]
    )

    protemics_data1[("profile", "time")] = pd.to_datetime(
        protemics_data1[("profile", "time")]
    )

    # Calculating mins_from_admission
    protemics_data1[("profile", "mins_from_admission")] = (
        protemics_data1[("profile", "time")]
        - protemics_data1[("profile", "admission_date_time")]
    ).dt.total_seconds() / 60 + 15840

    protemics_data1[("profile", "mins_from_admission")] = protemics_data1[
        ("profile", "mins_from_admission")
    ].astype(int)
    print("shape before merging sleepdebt", protemics_data1.shape)

    return apply_debt(protemics_data1, box, path)


def apply_debt(df: pd.DataFrame, box: BoxManager, path: Path) -> pd.DataFrame:
    """
    This function calculates the sleep debt at the time of blood collection"""

    exp_id = [
        "3453HY73",
        "3557HY61",
        "2056HY75",
        "3552HY62",
        "26P2HY83",
        "3453HY52",
        "3536HY83",
        "3536HY52",
        "3552HY73",
    ]
    empty_df = pd.DataFrame()

    for key in exp_id:
        print(key)
        file = box.get_file(path / f"mppg_fd_{key}.csv")
        sleep_debt_fd = pd.read_csv(file)
        # check if  "l_debt" and "s_debt " columns are present in the dataframe
        if all(col in sleep_debt_fd.columns for col in ["l_debt", "s_debt"]):
            multi_level_columns = [
                ("profile", "time"),
                ("debt", "Chronic"),
                ("debt", "Acute"),
                ("debt", "l_debt"),
                ("debt", "s_debt"),
                ("debt", "status"),
                ("transitions", "waking_up"),
                ("transitions", "falling_asleep"),
            ]

        else:
            multi_level_columns = [
                ("profile", "time"),
                ("debt", "Chronic"),
                ("debt", "Acute"),
                ("debt", "status"),
                ("transitions", "waking_up"),
                ("transitions", "falling_asleep"),
            ]
        sleep_debt_fd.columns = pd.MultiIndex.from_tuples(multi_level_columns)

        # Renaming column
        sleep_debt_fd.columns = pd.MultiIndex.from_tuples(
            sleep_debt_fd.set_axis(sleep_debt_fd.columns.values, axis=1).rename(
                columns={("profile", "time"): ("profile", "mins_from_admission")}
            )
        )
        # filtering the subject specific data for before merging, as sleepdebt
        #  are different for different subject
        # because their sleep-wake schedule is little different although
        # they are in same protocol
        filtered_df = df[df[("ids", "experiment")].str.split("_").str[0] == key]
        print("filtered data dimension", filtered_df.shape)

        # Merging data
        fd_sleepdebt = pd.merge(
            left=filtered_df,
            right=sleep_debt_fd,
            on=[("profile", "mins_from_admission")],
            # right_on=[('profile','time')],
            how="inner",
        )
        print("dimension of filtered data after merging", fd_sleepdebt.shape)

        empty_df = pd.concat([empty_df, fd_sleepdebt])

    print("data dimension after merging admission time by exp", empty_df.shape)

    return empty_df
