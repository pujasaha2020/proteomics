"""
This scripts gets input from get.py, gets studies from get_studies.py and 
saves the dataset with sleepdebt at specific time from both model
as csv to BOX.
"""

# pylint: disable=R0801


from datetime import date
from pathlib import Path

import pandas as pd

from datasets.sleepdebt.get_studies import (
    get_dinges_zeitzer,
    get_faa,
    get_fd,
    get_mppg_ctl_csr,
    get_mri_day5,
)
from utils.get import get_box, get_ids_profile_drop_missing_proteins, get_proteomics
from utils.save import save_to_csv

BOX_PATH = {
    "proteomics": Path("archives/data/proteomics_091224_AS.csv"),
    "csvs": Path("archives/sleepdebt/sleepdebt_data/ligand_receptor_model/sleepdebt/"),
    "csvs_unified": Path("archives/sleepdebt/sleepdebt_data/unified_model/sleepdebt/"),
    "csv_final": Path(
        "archives/sleep_debt/sleepdebt_data/dataset_with_sleepdebt_at_clocktime/"
    ),
    "yaml_path": Path("archives/sleepdebt/sleepdebt_data/yaml_files/protocols.yaml"),
}
# box1 = get_box()


if __name__ == "__main__":
    box = get_box()

    # creating a dataframe that contains, study,subject and sample count,
    # and blood collection time for subject with maximum count.
    dict_count: dict[str, list] = {
        "study": [],
        "subject_count": [],
        "sample_count": [],
        "blood_time": [],
    }

    df_ids_prof_no_proteins = get_ids_profile_drop_missing_proteins(box)
    df = get_proteomics(box)

    # adenosine model

    dinges_zeitzer = get_dinges_zeitzer(
        df_ids_prof_no_proteins, df, BOX_PATH["csvs"], box, dict_count
    )

    mppg = get_mppg_ctl_csr(df_ids_prof_no_proteins, BOX_PATH["csvs"], box, dict_count)
    print(dict_count)

    fd = get_fd(df_ids_prof_no_proteins, BOX_PATH["csvs"], box, dict_count)
    mri_5day = get_mri_day5(df_ids_prof_no_proteins, BOX_PATH["csvs"], box, dict_count)
    faa = get_faa(df_ids_prof_no_proteins, BOX_PATH["csvs"], box, dict_count)

    df_sleep_debt_adenosine = pd.concat([dinges_zeitzer, mppg, fd, mri_5day, faa])
    print("shape of all samples: ", df_sleep_debt_adenosine.shape)

    columns_to_drop = [
        ("profile", "date"),
        ("profile", "adm_time"),
        ("profile", "mins_from_admission"),
        ("profile", "admission_date_time"),
    ]
    # Drop the specified columns
    df_sleep_debt_adenosine = df_sleep_debt_adenosine.drop(columns=columns_to_drop)

    df_sleep_debt_adenosine.rename(columns={"debt": "adenosine"}, level=0, inplace=True)
    df_sleep_debt_adenosine.rename(
        columns={"Acute": "acute", "Chronic": "chronic"}, level=1, inplace=True
    )
    print("shape of all samples in adenosine system: ", df_sleep_debt_adenosine.shape)
    # unified model

    dinges_zeitzer = get_dinges_zeitzer(
        df_ids_prof_no_proteins,
        df,
        BOX_PATH["csvs_unified"],
        box,
        dict_count,
    )

    mppg = get_mppg_ctl_csr(
        df_ids_prof_no_proteins, BOX_PATH["csvs_unified"], box, dict_count
    )
    print(dict_count)

    fd = get_fd(df_ids_prof_no_proteins, BOX_PATH["csvs_unified"], box, dict_count)
    mri_5day = get_mri_day5(
        df_ids_prof_no_proteins, BOX_PATH["csvs_unified"], box, dict_count
    )
    faa = get_faa(df_ids_prof_no_proteins, BOX_PATH["csvs_unified"], box, dict_count)

    df_sleep_debt_unified = pd.concat([dinges_zeitzer, mppg, fd, mri_5day, faa])
    print("shape of all samples: ", df_sleep_debt_unified.shape)

    columns_to_drop = [
        ("profile", "date"),
        ("profile", "adm_time"),
        ("profile", "mins_from_admission"),
        ("profile", "admission_date_time"),
    ]
    # Drop the specified columns
    df_sleep_debt_unified = df_sleep_debt_unified.drop(columns=columns_to_drop)
    df_sleep_debt_unified.rename(columns={"debt": "unified"}, level=0, inplace=True)
    df_sleep_debt_unified.rename(
        columns={"Acute": "acute", "Chronic": "chronic"}, level=1, inplace=True
    )
    print("shape of all samples in unified model: ", df_sleep_debt_unified.shape)

    # Extract level 0 and level 1 column names from both DataFrames
    columns_level_0_adenosine = df_sleep_debt_adenosine.columns.get_level_values(0)
    columns_level_0_unified = df_sleep_debt_unified.columns.get_level_values(0)
    columns_level_1_adenosine = df_sleep_debt_adenosine.columns.get_level_values(1)
    columns_level_1_unified = df_sleep_debt_unified.columns.get_level_values(1)

    # Find common columns in both levels
    common_columns_level_0 = set(columns_level_0_adenosine).intersection(
        columns_level_0_unified
    )
    common_columns_level_1 = set(columns_level_1_adenosine).intersection(
        columns_level_1_unified
    )

    # Create a list of tuples for common columns in both levels
    common_columns = [
        (col0, col1)
        for col0 in common_columns_level_0
        for col1 in common_columns_level_1
    ]

    # Ensure the common columns exist in both DataFrames
    common_columns = [
        col
        for col in common_columns
        if col in df_sleep_debt_adenosine.columns
        and col in df_sleep_debt_unified.columns
    ]

    # merging the both models
    df_proteomics_with_sleep_debt = pd.merge(
        df_sleep_debt_adenosine,
        df_sleep_debt_unified,
        on=common_columns,
        how="inner",
    )

    print("shape of all samples: ", df_proteomics_with_sleep_debt.shape)
    today = date.today()
    print(today)
    input_version = BOX_PATH["proteomics"].stem
    print(input_version)
    split_string = input_version.split("_")
    # save the dataset as csv to BOX
    df_count = pd.DataFrame(dict_count)
    print(df_count)
    # df_count.drop_duplicates(inplace=True)
    # df_count.reset_index(drop=True, inplace=True)
    save_to_csv(
        box,
        df_count,
        BOX_PATH["csv_proteomics"]
        / f"count_{split_string[1]}_{split_string[2]}_{today}_PS.csv",
        index=False,
    )

    save_to_csv(
        box,
        df_proteomics_with_sleep_debt,
        BOX_PATH["csv_final"]
        / f"data_{split_string[1]}_{split_string[2]}_with_sleep_debt_{today}_PS.csv",
        index=False,
    )
