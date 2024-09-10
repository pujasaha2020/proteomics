"""
This piece of code do the data processing for the "FAA CSRN" sample.
 It reads the sleep debt data and merge it with the proteomics data.
"""

# pylint: disable=R0801

from pathlib import Path

import pandas as pd

from box.manager import BoxManager


def get_faa_csrn(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    get the sleep debt for the "FAA CSRN" sample
    """
    # DataFrame with unique subjects and admission times

    sub_admission_time = {
        "41D4": "5:29",
        "4211": "7:25",
        "4217": "7:01",
        "42H5": "8:01",
        "4348": "7:02",
    }

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "faa_csrn"
            ]["subject"].unique(),
        }
    )

    df_id_admit_time[("profile", "time")] = df_id_admit_time[("ids", "subject")].map(
        sub_admission_time
    )

    print("number of subjects in faa csrn", len(df_id_admit_time))
    faa_csrn_data = proteomics_data_new[proteomics_data_new.ids["study"] == "faa_csrn"]

    print("data dimension before merging admission time", faa_csrn_data.shape)
    protemics_data1 = pd.merge(
        faa_csrn_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
    )
    print("data dimension after merging admission time", protemics_data1.shape)
    # Adding date and admission_date_time columns
    protemics_data1[
        ("profile", "date")
    ] = "2021-12-31"  # ["2021-12-31"] * len(protemics_data1)
    protemics_data1[("profile", "date")] = pd.to_datetime(
        protemics_data1[("profile", "date")]
    )
    protemics_data1[("profile", "date")] = protemics_data1[
        ("profile", "date")
    ].dt.strftime("%Y-%m-%d")

    protemics_data1[("profile", "admission_date_time")] = (
        protemics_data1[("profile", "date")]
        + " "
        + protemics_data1[("profile", "time")]
    )
    protemics_data1[("profile", "admission_date_time")] = pd.to_datetime(
        protemics_data1[("profile", "admission_date_time")]
    )
    # print(protemics_data1[("profile", "clock_time")])
    protemics_data1[("profile", "clock_time")] = protemics_data1[
        ("profile", "clock_time")
    ].apply(lambda x: x.split(".")[0])

    protemics_data1[("profile", "clock_time")] = pd.to_datetime(
        protemics_data1[("profile", "clock_time")]
    )

    # Calculating mins_from_admission
    protemics_data1[("profile", "mins_from_admission")] = (
        protemics_data1[("profile", "clock_time")]
        - protemics_data1[("profile", "admission_date_time")]
    ).dt.total_seconds() / 60 + 15840
    # print(protemics_data1[('profile','mins_from_admission')].max())
    # protemics_data1[('profile','mins_from_admission')] = protemics_data1[('profile','mins_from_admission')].astype(int)
    protemics_data1[("profile", "mins_from_admission")] = protemics_data1[
        ("profile", "mins_from_admission")
    ].astype(int)

    # Reading sleep debt data
    file = box.get_file(path / "faa_csrn_class.csv")
    sleep_debt_faa_csrn = pd.read_csv(file)
    sleep_debt_faa_csrn.drop(
        columns=["l_debt", "s_debt"], inplace=True, errors="ignore"
    )

    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    sleep_debt_faa_csrn.columns = pd.MultiIndex.from_tuples(multi_level_columns)

    # Renaming column
    sleep_debt_faa_csrn.columns = pd.MultiIndex.from_tuples(
        sleep_debt_faa_csrn.set_axis(sleep_debt_faa_csrn.columns.values, axis=1).rename(
            columns={("profile", "time"): ("profile", "mins_from_admission")}
        )
    )

    # Merging data
    faa_csrn_sleepdebt = pd.merge(
        left=protemics_data1,
        right=sleep_debt_faa_csrn,
        on=[("profile", "mins_from_admission")],
        # right_on=[('profile','time')],
        how="inner",
    )

    print("shape after merging sleep debt", faa_csrn_sleepdebt.shape)
    return faa_csrn_sleepdebt
