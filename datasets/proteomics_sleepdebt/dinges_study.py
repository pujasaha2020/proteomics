# Dinges sample

from pathlib import Path

import pandas as pd

from box.manager import BoxManager


# Sleep debt for "mri" sample
def get_dinges(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    get the sleep debt for the "dinges" sample
    """
    # DataFrame with unique subjects and admission times

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "dinges"
            ]["subject"].unique(),
        }
    )

    print("number of subjects in dinges", len(df_id_admit_time))

    df_id_admit_time[("profile", "time")] = "8:00"
    dinges_data = proteomics_data_new[proteomics_data_new.ids["study"] == "dinges"]

    print("data dimension before merging admission time", dinges_data.shape)

    protemics_data1 = pd.merge(
        dinges_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
    )
    print("data dimension after merging admission time", protemics_data1.shape)

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
    protemics_data1[("profile", "mins_from_admission")] = protemics_data1[
        ("profile", "mins_from_admission")
    ].astype(int)

    # Reading sleep debt data
    file = box.get_file(path / "dinges_class.csv")
    sleep_debt_dinges = pd.read_csv(file)
    sleep_debt_dinges.drop(columns=["l_debt", "s_debt"], inplace=True, errors="ignore")

    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    sleep_debt_dinges.columns = pd.MultiIndex.from_tuples(multi_level_columns)
    print(sleep_debt_dinges.head())

    # Renaming columns
    sleep_debt_dinges.columns = pd.MultiIndex.from_tuples(
        sleep_debt_dinges.set_axis(sleep_debt_dinges.columns.values, axis=1).rename(
            columns={("profile", "time"): ("profile", "mins_from_admission")}
        )
    )

    # Merging data
    dinges_sleepdebt = pd.merge(
        left=protemics_data1,
        right=sleep_debt_dinges,
        on=[("profile", "mins_from_admission")],
        # right_on=[('profile','time')],
        how="inner",
    )

    print("data dimension after merging sleep debt", dinges_sleepdebt.shape)
    return dinges_sleepdebt
