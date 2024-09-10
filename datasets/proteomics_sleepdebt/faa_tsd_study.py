"""
This piece of code do the data processing for the "FAA tsd" sample.
 It reads the sleep debt data and merge it with the proteomics data.
"""

# pylint: disable=R0801

from pathlib import Path

import pandas as pd

from box.manager import BoxManager


def get_faa_tsd(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    get the sleep debt for the "FAA tsd" sample
    """
    # DataFrame with unique subjects and admission times

    sub_admission_time = {
        "3796": "8:02",
        "4131": "7:59",
        "4147": "10:03",
        "4148": "5:43",
        "4216": "7:59",
        "4228": "8:00",
        "4260": "6:00",
        "42A1": "5:01",
        "42D4": "8:00",
        "4315": "6:04",
        "4381": "6:58",
    }

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "faa_tsd"
            ]["subject"].unique(),
        }
    )

    df_id_admit_time[("profile", "time")] = df_id_admit_time[("ids", "subject")].map(
        sub_admission_time
    )

    print("number of subjects in faa tsd", df_id_admit_time)
    faa_tsd_data = proteomics_data_new[proteomics_data_new.ids["study"] == "faa_tsd"]

    print("data dimension before merging admission time", faa_tsd_data.shape)
    protemics_data1 = pd.merge(
        faa_tsd_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
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

    protemics_data1[("profile", "clock_time")] = pd.to_datetime(
        protemics_data1[("profile", "clock_time")]
    )
    # Calculating mins_from_admission
    protemics_data1[("profile", "mins_from_admission")] = (
        protemics_data1[("profile", "clock_time")]
        - protemics_data1[("profile", "admission_date_time")]
    ).dt.total_seconds() / 60 + 15840
    # Get rows with NaN in the specific column
    nan_rows = protemics_data1[
        protemics_data1[("profile", "mins_from_admission")].isna()
    ]

    # Display the rows
    print(nan_rows[("profile", "mins_from_admission")])
    protemics_data1[("profile", "mins_from_admission")] = protemics_data1[
        ("profile", "mins_from_admission")
    ].astype(int)

    # Reading sleep debt data
    file = box.get_file(path / "faa_tsd_class.csv")
    sleep_debt_faa_tsd = pd.read_csv(file)
    sleep_debt_faa_tsd.drop(columns=["l_debt", "s_debt"], inplace=True, errors="ignore")

    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    sleep_debt_faa_tsd.columns = pd.MultiIndex.from_tuples(multi_level_columns)
    # print(sleep_debt_faa_tsd)

    # Renaming column
    sleep_debt_faa_tsd.columns = pd.MultiIndex.from_tuples(
        sleep_debt_faa_tsd.set_axis(sleep_debt_faa_tsd.columns.values, axis=1).rename(
            columns={("profile", "time"): ("profile", "mins_from_admission")}
        )
    )

    # Merging data
    faa_tsd_sleepdebt = pd.merge(
        left=protemics_data1,
        right=sleep_debt_faa_tsd,
        on=[("profile", "mins_from_admission")],
        # right_on=[('profile','time')],
        how="inner",
    )

    print("shape after merging sleep debt", faa_tsd_sleepdebt.shape)
    return faa_tsd_sleepdebt
