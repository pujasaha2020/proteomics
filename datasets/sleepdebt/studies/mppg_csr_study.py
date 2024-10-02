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
    get the sleep debt for the "mppg_CSR" sample, it includes both sleep time of 5H and 5.6H
    """
    sub_admission_time = {
        "3794": "5:02",  # 5H
        "3776": "5:28",  # 5H
        "3665": "6:33",  # 5H time. appears in both 5 H and 5.6 H. Will be corrected for 5.6H.
        "29W4": "8:01",  # 5H
        "3828": "7:20",  # 5H
        "3608": "9:04",  # 5.6H
        "3619": "9:01",  # 5.6H
        "3445": "6:10",  # 5.6H
    }

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "mppg_csr"
            ]["subject"].unique(),
        }
    )
    print("number of subjects in mppg csr", len(df_id_admit_time))

    df_id_admit_time[("profile", "adm_time")] = df_id_admit_time[
        ("ids", "subject")
    ].map(sub_admission_time)

    mppg_csr_data = proteomics_data_new[proteomics_data_new.ids["study"] == "mppg_csr"]
    print("data dimension before merging admission time", mppg_csr_data.shape)

    protemics_data1 = pd.merge(
        mppg_csr_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
    )
    print("data dimension after merging admission time", protemics_data1.shape)

    # correcting the admission "time" for 3547 8 TIB subject
    protemics_data1.loc[
        (protemics_data1[("ids", "experiment")] == "3665HY_1")
        | (protemics_data1[("ids", "experiment")] == "3665HY_2"),
        ("profile", "adm_time"),
    ] = "7:02"

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
    file_5h = box.get_file(path / "mppg_tsd_5H_class.csv")

    file_56h = box.get_file(path / "mppg_tsd_5.6H_class.csv")
    id_5h = ["29W4", "3665", "3776", "3794", "3828"]
    id_56h = ["3445", "3608", "3665", "3619"]

    df_5h = apply_debt_5h(file_5h, protemics_data1, id_5h)
    df_56h = apply_debt_56h(file_56h, protemics_data1, id_56h)

    mppg_csr_sleepdebt = pd.concat([df_5h, df_56h])
    print("total shape after merging sleepdebt ", mppg_csr_sleepdebt.shape)
    return mppg_csr_sleepdebt


def apply_debt_5h(file: io.StringIO, df: pd.DataFrame, sub_id: list) -> pd.DataFrame:
    """
    This function applies the sleep debt for 5H of sleep time
    """
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

    protemics_5h = df[df.ids["subject"].isin(sub_id)]

    # 3665 appears in both 5H and 5.6H, so removing 5.6H experiment id for 3665 info from
    # 5H protocol.
    fil_protemics_data1_5h = protemics_5h[
        ~(
            (protemics_5h[("ids", "experiment")] == "3665HY_1")
            | (protemics_5h[("ids", "experiment")] == "3665HY_2")
            | (protemics_5h[("ids", "experiment")] == "3665HY_3")
            | (protemics_5h[("ids", "experiment")] == "3665HY_4")
        )
    ]
    print("shape of 5H dim", fil_protemics_data1_5h.shape)
    # Merging data
    mppg5h_sleepdebt = pd.merge(
        left=fil_protemics_data1_5h,
        right=df_debt,
        on=[("profile", "mins_from_admission")],
        how="inner",
    )

    #
    print("data dimension after merging sleep debt 5H", mppg5h_sleepdebt.shape)
    return mppg5h_sleepdebt


def apply_debt_56h(file: io.StringIO, df: pd.DataFrame, sub_id: list) -> pd.DataFrame:
    """
    This function applies the sleep debt for 5.6H of sleep time
    """
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

    protemics_56h = df[df.ids["subject"].isin(sub_id)]

    # 3665 appears in both 5H and 5.6H, so removing 5H experiment id for 3665 info from
    # 5.6H protocol.
    fil_protemics_data1_56h = protemics_56h[
        ~(
            (protemics_56h[("ids", "experiment")] == "3665HY82_1")
            | (protemics_56h[("ids", "experiment")] == "3665HY82_2")
            | (protemics_56h[("ids", "experiment")] == "3665HY82_3")
        )
    ]
    print("shape of 5.6H dim", fil_protemics_data1_56h.shape)
    # Merging data
    mppg56h_sleepdebt = pd.merge(
        left=fil_protemics_data1_56h,
        right=df_debt,
        on=[("profile", "mins_from_admission")],
        how="inner",
    )

    #
    print("data dimension after merging sleep debt 56H", mppg56h_sleepdebt.shape)
    return mppg56h_sleepdebt
