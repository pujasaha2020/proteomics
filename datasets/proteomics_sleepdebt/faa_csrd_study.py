# Sleep debt for "FAA  CSRD" sample


from pathlib import Path

import pandas as pd

from box.manager import BoxManager


def get_faa_csrd(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    get the sleep debt for the "FAA CSRD" sample
    """
    # DataFrame with unique subjects and admission times

    sub_admission_time = {
        "4164": "5:59",
        "4203": "8:59",
        "42B6": "6:44",
        "42B7": "4:59",
    }

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "faa_csrd"
            ]["subject"].unique(),
        }
    )

    df_id_admit_time[("profile", "time")] = df_id_admit_time[("ids", "subject")].map(
        sub_admission_time
    )

    print("number of subjects in faa csrd", len(df_id_admit_time))
    faa_csrd_data = proteomics_data_new[proteomics_data_new.ids["study"] == "faa_csrd"]

    print("data dimension before merging admission time", faa_csrd_data.columns)
    protemics_data1 = pd.merge(
        faa_csrd_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
    )
    print("data dimension after merging admission time", protemics_data1.shape)
    # Adding date and admission_date_time columns
    protemics_data1[("profile", "date")] = (
        "2021-12-31"  # ["2021-12-31"] * len(protemics_data1)
    )
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

    protemics_data1[("profile", "mins_from_admission")] = protemics_data1[
        ("profile", "mins_from_admission")
    ].astype(int)
    # Reading sleep debt data
    file = box.get_file(path / "faa_csrd_class.csv")
    sleep_debt_faa_csrd = pd.read_csv(file)
    sleep_debt_faa_csrd.drop(
        columns=["l_debt", "s_debt"], inplace=True, errors="ignore"
    )
    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    sleep_debt_faa_csrd.columns = pd.MultiIndex.from_tuples(multi_level_columns)

    # Renaming column
    sleep_debt_faa_csrd.columns = pd.MultiIndex.from_tuples(
        sleep_debt_faa_csrd.set_axis(sleep_debt_faa_csrd.columns.values, axis=1).rename(
            columns={("profile", "time"): ("profile", "mins_from_admission")}
        )
    )

    # Merging data
    faa_csrd_sleepdebt = pd.merge(
        left=protemics_data1,
        right=sleep_debt_faa_csrd,
        on=[("profile", "mins_from_admission")],
        # right_on=[('profile','time')],
        how="inner",
    )

    print("shape after merging sleep debt", faa_csrd_sleepdebt.shape)
    # print("final data", faa_csrd_sleepdebt)

    timing = [17436, 18936, 17196, 18876, 20376, 17306, 17461, 18961]

    print(
        sleep_debt_faa_csrd[
            sleep_debt_faa_csrd[("profile", "mins_from_admission")].isin(timing)
        ]
    )

    return faa_csrd_sleepdebt
