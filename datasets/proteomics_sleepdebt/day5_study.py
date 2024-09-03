# 5day study


from pathlib import Path

import pandas as pd

from box.manager import BoxManager


# Sleep debt for "5day" sample
def get_5day(
    proteomics_data_new: pd.DataFrame, box: BoxManager, path: Path
) -> pd.DataFrame:
    """
    get the sleep debt for the "5day" sample
    """
    sub_admission_time = {
        "4276": "7:04",
        "4199": "5:59",
        "4190": "8:35",
        "4164": "5:59",
        "4133": "7:28",
        "4128": "7:01",
        "41D3": "7:31",
        "41A9": "6:42",
        "4251": "8:11",
    }

    study = ["5day_bsl", "5day_cr", "5day_reco"]

    df_id_admit_time = pd.DataFrame(
        {
            ("ids", "subject"): proteomics_data_new.ids[
                proteomics_data_new.ids["study"].isin(study)
            ]["subject"].unique(),
        }
    )
    print("number of subjects in 5day", len(df_id_admit_time))

    df_id_admit_time[("profile", "time")] = df_id_admit_time[("ids", "subject")].map(
        sub_admission_time
    )

    day5_data = proteomics_data_new[proteomics_data_new.ids["study"].isin(study)]
    print("data dimension before merging admission time", day5_data.shape)

    protemics_data1 = pd.merge(
        day5_data, df_id_admit_time, on=[("ids", "subject")], how="inner"
    )
    print("data dimension after merging admission time", protemics_data1.shape)

    # Adding date and admission_date_time columns
    protemics_data1[("profile", "date")] = "2021-12-31"
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
    file = box.get_file(path / "5day_class.csv")
    sleep_debt_day5 = pd.read_csv(file)

    multi_level_columns = [
        ("profile", "time"),
        ("debt", "Chronic"),
        ("debt", "Acute"),
        ("debt", "status"),
    ]
    sleep_debt_day5.columns = pd.MultiIndex.from_tuples(multi_level_columns)
    # print(sleep_debt_day5)

    # Renaming column
    sleep_debt_day5.columns = pd.MultiIndex.from_tuples(
        sleep_debt_day5.set_axis(sleep_debt_day5.columns.values, axis=1).rename(
            columns={("profile", "time"): ("profile", "mins_from_admission")}
        )
    )

    # print(sleep_debt_day5)
    # Merging data
    day5_sleepdebt = pd.merge(
        left=protemics_data1,
        right=sleep_debt_day5,
        on=[("profile", "mins_from_admission")],
        how="inner",
    )

    print("data dimension after merging sleep debt", day5_sleepdebt.shape)
    return day5_sleepdebt
