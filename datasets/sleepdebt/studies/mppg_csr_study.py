"""
This piece of code do the data processing for the "mppg CSR" sample.
It reads the sleep debt data and merge it with the proteomics data.
note: there are subjects who participated in both 5h and 5.6 hr protocol.
This fact is taken care of while merging the sleep debt data with the proteomics data.
"""

# pylint: disable=R0801

import io
from pathlib import Path

import pandas as pd

from box.manager import BoxManager


def get_mppg_csr(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    get the sleep debt for the "mppg_CSR" sample,
    it includes both sleep time of 5H and 5.6H
    """
    sub_admission_time = {
        "3794": "6:02",  # "5:02",  # 5H
        "3776": "5:28",  # 5H
        "3665": "7:33",  # "6:33",  # 5H time. appears in both
        # 5 H and 5.6 H. Will be corrected for 5.6H.
        "29W4": "9:01",  # "8:01",  # 5H
        "3828": "8:20",  # "7:20",  # 5H
        "3608": "9:04",  # "9:04",  # 5.6H
        "3619": "9:01",  # 5.6H
        "3445": "6:10",  # "6:10",  # 5.6H
    }

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "mppg_csr"
            ]["subject"].unique(),
        }
    )

    df_id_admit_time[("profile", "adm_time")] = df_id_admit_time[
        ("ids", "subject")
    ].map(sub_admission_time)

    mppg_csr_data = proteomics_data_new[proteomics_data_new.ids["study"] == "mppg_csr"]
    print("data dimension before merging admission time", mppg_csr_data.shape)

    protemics_data1 = pd.merge(
        mppg_csr_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
    )
    print("data dimension after merging admission time", protemics_data1.shape)

    # correcting the admission "time" for 3665 5.6H TIB subject
    protemics_data1.loc[
        (protemics_data1[("ids", "experiment")] == "3665HY_1")
        | (protemics_data1[("ids", "experiment")] == "3665HY_2"),
        ("profile", "adm_time"),
    ] = "7:02"

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

    exp_id_5h = ["3794HY", "3776HY82", "3665HY82", "29W4HY83", "3828HY"]
    exp_id_56h = ["3608HY", "3445HY", "3665HY", "3619HY"]

    debt_5h = merge_debt(protemics_data1, box, path, exp_id_5h, protocol="5H")
    debt_56h = merge_debt(protemics_data1, box, path, exp_id_56h, protocol="56H")
    mppg_ctl_sleepdebt = pd.concat([debt_5h, debt_56h])
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
        file = box.get_file(path / f"mppg_csr_{protocol}_{key}.csv")
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
        fd_sleepdebt = pd.merge(
            left=filtered_df,
            right=sleep_debt_fd,
            on=[("profile", "mins_from_admission")],
            # right_on=[('profile','time')],
            how="inner",
        )
        empty_df = pd.concat([empty_df, fd_sleepdebt])

    return empty_df
