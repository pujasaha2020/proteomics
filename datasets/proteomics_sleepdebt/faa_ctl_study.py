# FAA ctl study

from pathlib import Path

import pandas as pd

from box.manager import BoxManager


# Sleep debt for "FAA ctl" sample
def get_faa_ctl(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    get the sleep debt for the "FAA ctrl" sample
    """
    # DataFrame with unique subjects and admission times

    sub_admission_time = {
        "4202": "5:59",
        "4261": "4:58",
        "42D6": "7:24",
        "42G3": "6:59",
        "4339": "6:00",
    }

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"] == "faa_ctl"
            ]["subject"].unique(),
        }
    )

    df_id_admit_time[("profile", "time")] = df_id_admit_time[("ids", "subject")].map(
        sub_admission_time
    )
    # df_id_admit_time = df_id_admit_time.dropna()

    print("number of subjects in faa ctl", len(df_id_admit_time))

    faa_ctl_data = proteomics_data_new[proteomics_data_new.ids["study"] == "faa_ctl"]
    print("data dimension before merging admission time", faa_ctl_data.shape)

    protemics_data1 = pd.merge(
        faa_ctl_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
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
    print(protemics_data1[("profile", "mins_from_admission")].max())
    protemics_data1[("profile", "mins_from_admission")] = protemics_data1[
        ("profile", "mins_from_admission")
    ].astype(int)

    # Reading sleep debt data
    file = box.get_file(path / "faa_ctl_class.csv")
    sleep_debt_faa_ctl = pd.read_csv(file)
    sleep_debt_faa_ctl.drop(columns=["l_debt", "s_debt"], inplace=True, errors="ignore")

    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    sleep_debt_faa_ctl.columns = pd.MultiIndex.from_tuples(multi_level_columns)
    print(sleep_debt_faa_ctl)

    # Renaming column
    sleep_debt_faa_ctl.columns = pd.MultiIndex.from_tuples(
        sleep_debt_faa_ctl.set_axis(sleep_debt_faa_ctl.columns.values, axis=1).rename(
            columns={("profile", "time"): ("profile", "mins_from_admission")}
        )
    )

    # Merging data
    faa_ctl_sleepdebt = pd.merge(
        left=protemics_data1,
        right=sleep_debt_faa_ctl,
        on=[("profile", "mins_from_admission")],
        # right_on=[('profile','time')],
        how="inner",
    )

    print("data dimension after merging sleep debt", faa_ctl_sleepdebt.shape)
    return faa_ctl_sleepdebt
