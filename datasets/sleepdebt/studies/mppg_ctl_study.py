"""
This piece of code do the data processing for the "mppg ctl" sample.
It reads the sleep debt data and merge it with the proteomics data.
note: there are subjects who participated in both 8h and 10 hr protocol.
This fact is taken care of while merging the sleep debt data with the proteomics data.
"""

# pylint: disable=R0801

import io
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
        "3776": "6:02",
        "3789": "7:54",
        "3812": "9:03",
        "3547": "8:00",  # this time is for 10H protocol, will be corrected
        # for 8H protocol. Appears both in 8H and 10H protocol
        "3436": "7:53",  # 10H protocol
        "3369": "8:00",  # 10H protocol
        "3552": "7:30",  # 10H protocol
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
    ] = "7:01"

    # Adding date and admission_date_time columns
    protemics_data1[("profile", "date")] = "2022-01-01"
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
    file_8h = box.get_file(path / "mppg_ctl_8H_class.csv")

    file_10h = box.get_file(path / "mppg_ctl_10H_class.csv")

    id_8h = ["3547", "3776", "3789", "3812"]  # note: 3547 appears in both 8H and 10H
    id_10h = ["3547", "3369", "3436", "3552"]

    df_8h = apply_debt_8h(file_8h, protemics_data1, id_8h)
    df_10h = apply_debt_10h(file_10h, protemics_data1, id_10h)
    mppg_ctl_sleepdebt = pd.concat([df_8h, df_10h])

    print("data dimension after merging sleep debt ", mppg_ctl_sleepdebt.shape)
    return mppg_ctl_sleepdebt


def apply_debt_8h(file: io.StringIO, df: pd.DataFrame, sub_id: list) -> pd.DataFrame:
    """This function applies the sleep debt for 8H of sleep time"""
    df_debt = pd.read_csv(file)
    df_debt.drop(columns=["l_debt", "s_debt"], inplace=True, errors="ignore")

    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    df_debt.columns = pd.MultiIndex.from_tuples(multi_level_columns)

    # Renaming column
    df_debt.columns = pd.MultiIndex.from_tuples(
        df_debt.set_axis(df_debt.columns.values, axis=1).rename(
            columns={("profile", "time"): ("profile", "mins_from_admission")}
        )
    )

    protemics_8h = df[df.ids["subject"].isin(sub_id)]

    # 3547 appears in both 8H and 10H, so removing 10H experiment id for 3547  from 8H protocol.
    fil_protemics_data1_8h = protemics_8h[
        ~(
            (protemics_8h[("ids", "experiment")] == "3547HY_1")
            | (protemics_8h[("ids", "experiment")] == "3547HY_2")
            | (protemics_8h[("ids", "experiment")] == "3547HY_3")
            | (protemics_8h[("ids", "experiment")] == "3547HY_4")
        )
    ]

    # Merging data
    mppg8h_sleepdebt = pd.merge(
        left=fil_protemics_data1_8h,
        right=df_debt,
        on=[("profile", "mins_from_admission")],
        how="inner",
    )

    #
    print("data dimension after merging sleep debt 8H", mppg8h_sleepdebt.shape)
    return mppg8h_sleepdebt


def apply_debt_10h(file: io.StringIO, df: pd.DataFrame, sub_id: list) -> pd.DataFrame:
    """This function applies the sleep debt for 10H of sleep time"""

    df_debt = pd.read_csv(file)
    df_debt.drop(columns=["l_debt", "s_debt"], inplace=True, errors="ignore")

    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    df_debt.columns = pd.MultiIndex.from_tuples(multi_level_columns)

    # Renaming column
    df_debt.columns = pd.MultiIndex.from_tuples(
        df_debt.set_axis(df_debt.columns.values, axis=1).rename(
            columns={("profile", "time"): ("profile", "mins_from_admission")}
        )
    )

    protemics_10h = df[df.ids["subject"].isin(sub_id)]

    # 3547 appears in both 8H and 10H, so removing 8H experiment id for 3547 info from 10H protocol.

    fil_protemics_data1_10h = protemics_10h[
        ~(
            (protemics_10h[("ids", "experiment")] == "3547HY82_1")
            | (protemics_10h[("ids", "experiment")] == "3547HY82_2")
        )
    ]

    # Merging data
    mppg10h_sleepdebt = pd.merge(
        left=fil_protemics_data1_10h,
        right=df_debt,
        on=[("profile", "mins_from_admission")],
        how="inner",
    )

    #
    print("data dimension after merging sleep debt 10H", mppg10h_sleepdebt.shape)
    return mppg10h_sleepdebt
