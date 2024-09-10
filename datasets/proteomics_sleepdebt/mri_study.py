# Extracting sleep debt for proteomics data or at blood collection time.


from pathlib import Path

import pandas as pd

from box.manager import BoxManager


# Sleep debt for "mri" sample
def get_mri(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    get the sleep debt for the "mri" sample
    """
    # DataFrame with unique subjects and admission times

    sub_admission_time = {
        "3667": "7:16",
        "3701": "7:30",
        "3728": "7:58",
        "3740": "7:04",
        "3744": "7:59",
        "3752": "6:05",
        "3771": "5:51",
        "3775": "5:30",
        "3783": "7:59",
    }

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "mri"
            ]["subject"].unique(),
        }
    )
    print("number of subjects in mri", len(df_id_admit_time))

    df_id_admit_time[("profile", "time")] = df_id_admit_time[("ids", "subject")].map(
        sub_admission_time
    )
    mri_data = proteomics_data_new[proteomics_data_new.ids["study"] == "mri"]

    print("data dimension before merging admission time", mri_data.shape)

    protemics_data1 = pd.merge(
        mri_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
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
    file = box.get_file(path / "mri_class.csv")
    sleep_debt_cr3667_cr3783 = pd.read_csv(file)
    sleep_debt_cr3667_cr3783.drop(
        columns=["l_debt", "s_debt"], inplace=True, errors="ignore"
    )

    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    sleep_debt_cr3667_cr3783.columns = pd.MultiIndex.from_tuples(multi_level_columns)
    print(sleep_debt_cr3667_cr3783.head())

    # Renaming columns
    sleep_debt_cr3667_cr3783.columns = pd.MultiIndex.from_tuples(
        sleep_debt_cr3667_cr3783.set_axis(
            sleep_debt_cr3667_cr3783.columns.values, axis=1
        ).rename(columns={("profile", "time"): ("profile", "mins_from_admission")})
    )

    # Merging data
    mri_sleepdebt = pd.merge(
        left=protemics_data1,
        right=sleep_debt_cr3667_cr3783,
        on=[("profile", "mins_from_admission")],
        # right_on=[('profile','time')],
        how="inner",
    )

    print("data dimension after merging sleep debt", mri_sleepdebt.shape)
    return mri_sleepdebt
