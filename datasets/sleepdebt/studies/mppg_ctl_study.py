"""
This piece of code do the data processing for the "mppg ctl" sample.
It reads the sleep debt data and merge it with the proteomics data.
note: there are subjects who participated in both 8h and 10 hr protocol.
This fact is taken care of while merging the sleep debt data with the proteomics data.
"""

# pylint: disable=R0801


from pathlib import Path

import pandas as pd

from box.manager import BoxManager


def get_mppg_ctl(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    get the sleep debt for the "mppg_ctl" sample, it includes both
    sleep time of 8H and 10H
    """
    sub_admission_time = {
        "3776": "7:02",  # "6:02",
        "3789": "8:54",  # "7:54",
        "3812": "10:03",  # "9:03",
        "3547": "8:00",  # "8:00",  # this time is for 10H protocol, will be corrected
        # for 8H protocol. Appears both in 8H and 10H protocol
        "3436": "7:53",  # "7:53",  # 10H protocol
        "3369": "8:00",  # "8:00",  # 10H protocol
        "3552": "7:30",  # "7:30",  # 10H protocol
    }

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "mppg_ctl"
            ]["subject"].unique(),
        }
    )

    df_id_admit_time[("profile", "adm_time")] = df_id_admit_time[
        ("ids", "subject")
    ].map(sub_admission_time)

    mppg_ctl_data = proteomics_data_new[proteomics_data_new.ids["study"] == "mppg_ctl"]
    print("data dimension before merging admission time", mppg_ctl_data.shape)

    protemics_data1 = pd.merge(
        mppg_ctl_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
    )
    print("data dimension after merging admission time", protemics_data1.shape)

    # correcting the admission "time" for 3547 8 TIB subject
    protemics_data1.loc[
        (protemics_data1[("ids", "experiment")] == "3547HY82_1")
        | (protemics_data1[("ids", "experiment")] == "3547HY82_2"),
        ("profile", "adm_time"),
    ] = "8:01"  # "7:01"

    # Adding date and admission_date_time columns
    protemics_data1[("profile", "date")] = "2021-12-28"  # "2022-01-01"
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

    protemics_data1[("profile", "time")] = pd.to_datetime(
        protemics_data1[("profile", "time")]
    )

    # Calculating mins_from_admission
    protemics_data1[("profile", "mins_from_admission")] = (
        (
            protemics_data1[("profile", "time")]
            - protemics_data1[("profile", "admission_date_time")]
        ).dt.total_seconds()
        / 60
    ) + 15840
    protemics_data1[("profile", "mins_from_admission")] = protemics_data1[
        ("profile", "mins_from_admission")
    ].astype(int)

    # Reading sleep debt data
    # file_8h = box.get_file(path / "mppg_ctl_8H.csv")

    # file_10h = box.get_file(path / "mppg_ctl_10H.csv")

    # id_8h = ["3547", "3776", "3789", "3812"]  # note: 3547 appears in both 8H and 10H
    # id_10h = ["3547", "3369", "3436", "3552"]

    exp_id_10h = ["3547HY", "3436HY", "3369HY42", "3552HY"]
    exp_id_8h = ["3776HY", "3789HY", "3547HY82", "3812HY83"]

    debt_8h = merge_debt(protemics_data1, box, path, exp_id_8h, protocol="8H")
    debt_10h = merge_debt(protemics_data1, box, path, exp_id_10h, protocol="10H")
    mppg_ctl_sleepdebt = pd.concat([debt_8h, debt_10h])
    print("data dimension after merging sleep debt ", mppg_ctl_sleepdebt.shape)
    return mppg_ctl_sleepdebt


def merge_debt(
    df: pd.DataFrame, box: BoxManager, path: Path, ids: list, protocol: str
) -> pd.DataFrame:
    """This function merges the sleep debt data with the proteomics data
    for the given protocol"""
    empty_df = pd.DataFrame()

    for key in ids:
        print(key)
        file = box.get_file(path / f"mppg_ctl_{protocol}_{key}.csv")
        sleep_debt_fd = pd.read_csv(file)
        sleep_debt_fd.drop(columns=["l_debt", "s_debt"], inplace=True, errors="ignore")

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
        # Merging data
        ctl_sleepdebt = pd.merge(
            left=filtered_df,
            right=sleep_debt_fd,
            on=[("profile", "mins_from_admission")],
            # right_on=[('profile','time')],
            how="inner",
        )
        empty_df = pd.concat([empty_df, ctl_sleepdebt])

    return empty_df
