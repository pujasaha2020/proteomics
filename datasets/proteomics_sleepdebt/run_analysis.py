"""
This script is used to get the input data from the box and clean the data.
The cleaned data is then used to get the sleep debt data for each protocol.
get_ids_profile_drop_rows_missing_proteins:
                function that removes all rows that have no proteins. 
                and keeps only the ids and profile and infos columns.
get_ids_profile: function that keeps all the rows in the proteomics data.
             but filters only the ids and profile and infos columns.This 
             function is needed to get sleep/wake schedule for Zeitzer subjects
               that have different schedule than common subjects. removing 
               rows with missing proteins removes 
            sample id needed to calculate sleep wake time. 
            sample["2", "15", "39", "52"] are needed to get number of 
            hours they sleep and awake.
get_no_of_subjects_samples: function that gets the number of subjects
                            and samples in each study.
get_blood_collection_time: function that gets the blood collection time for
                           a subject that have the maximum count in each study.
get_mppg_ctl_csr_fd: function that gets the mppg protocol and returns 
                     the sleepdebt at clock time.
get_faa: function that gets the faa protocol and returns the 
        sleepdebt at clock time.
get_mri_day5: function that gets the mri and day5 and mri protocol 
              and returns the sleepdebt at clock time.
get_dinges_zeitzer: function that gets the dinges and zeitzer protocol and returns
                     the sleepdebt at clock time.
At the end of the scripts data from unified and adenosine models
are merged and saved to a csv file and stored in box.


"""

# pylint: disable=R0801


from datetime import date
from pathlib import Path

import pandas as pd

from box.manager import BoxManager
from datasets.proteomics_sleepdebt.day5_study import get_5day
from datasets.proteomics_sleepdebt.dinges_study import get_dinges
from datasets.proteomics_sleepdebt.faa_csrd_study import get_faa_csrd
from datasets.proteomics_sleepdebt.faa_csrn_study import get_faa_csrn
from datasets.proteomics_sleepdebt.faa_ctl_study import get_faa_ctl
from datasets.proteomics_sleepdebt.faa_tsd_study import get_faa_tsd
from datasets.proteomics_sleepdebt.mppg_csr_study import get_mppg_csr
from datasets.proteomics_sleepdebt.mppg_ctl_study import get_mppg_ctl
from datasets.proteomics_sleepdebt.mppg_fd_study import get_mppg_fd
from datasets.proteomics_sleepdebt.mri_study import get_mri
from datasets.proteomics_sleepdebt.zeitzer_study import get_zeitzer
from utils.get import get_box
from utils.save import save_to_csv

BOX_PATH = {
    "proteomics": Path("archives/data/proteomics_091224_AS.csv"),
    "csvs": Path("archives/sleep_debt/SleepDebt_Data/ligand_receptor_model/sleepdebt/"),
    "csvs_unified": Path("archives/sleep_debt/SleepDebt_Data/unified_model/sleepdebt/"),
    "csv_proteomics": Path(
        "archives/sleep_debt/SleepDebt_Data/dataset_with_sleepdebt_at_clocktime/"
    ),
    "yaml_path": Path("archives/sleep_debt/SleepDebt_Data/yaml_files/protocols.yaml"),
}
# box1 = get_box()


def get_ids_profile_drop_rows_missing_proteins(
    box1: BoxManager, path: Path = BOX_PATH["proteomics"]
) -> pd.DataFrame:
    """
    getting "ids" and  "profile" from proteomics data.
    data is filtered depending on the availability of proteomics data
    """
    file = box1.get_file(path)
    dtype = {
        ("ids", "study"): str,
        ("ids", "subject"): str,
        ("ids", "experiment"): str,
        ("ids", "sample_id"): str,
    }
    df = pd.read_csv(file, header=[0, 1], dtype=dtype, low_memory=False)

    print("shape of dataset before cleaning: ", df.shape)
    proteins_columns = [col for col in df.columns if col[0] == "proteins"]

    df_cleaned = df.dropna(subset=proteins_columns, how="all")
    print("shape of dataset after cleaning: ", df_cleaned.shape)
    ids_profile = df_cleaned[["ids", "infos", "profile"]]

    return ids_profile


def get_ids_profile(
    box1: BoxManager, path: Path = BOX_PATH["proteomics"]
) -> pd.DataFrame:
    """
    getting "ids" and  "profile" from proteomics data.
    data is filtered depending on the availability of proteomics data
    """
    file = box1.get_file(path)
    dtype = {
        ("ids", "study"): str,
        ("ids", "subject"): str,
        ("ids", "experiment"): str,
        ("ids", "sample_id"): str,
    }
    df = pd.read_csv(file, header=[0, 1], dtype=dtype, low_memory=False)

    return df


def get_no_of_subjects_samples(df_protocol: pd.DataFrame) -> list:
    """
    get the number of subjects and samples in each study
    """
    subs = df_protocol[("ids", "subject")].unique()
    print(subs)
    samples = df_protocol.shape[0]

    return [len(subs), samples]


def get_blood_collection_time(df_protocol: pd.DataFrame) -> pd.Series:
    """
    get the blood collection time for each subject
    """
    # time = (df_protocol[("profile", "mins_from_admission")] - 15840) / (60 * 24)
    subject_counts = df_protocol[("ids", "subject")].value_counts()
    print(subject_counts)

    # Find the maximum count
    max_count = subject_counts.idxmax()
    print(max_count)
    # Find the subject with the maximum count
    # max_subject_ids = subject_counts[subject_counts == max_count]
    time = df_protocol[df_protocol[("ids", "subject")] == max_count][
        ("profile", "mins_from_admission")
    ] / (60 * 24)
    # print(df_protocol[df_protocol[("ids", "subject")] == max_count].ids)

    return time


def get_mppg_ctl_csr_fd(
    df_ids_profile: pd.DataFrame, path_to_box: Path, box1: BoxManager
) -> pd.DataFrame:
    """
    get the mppg protocol
    """

    mppg_ctl_sample = get_mppg_ctl(df_ids_profile, box1, path_to_box)
    print("shape of mppg_ctl sample: ", mppg_ctl_sample.shape)

    id_8h = ["3547", "3776", "3789", "3812"]  # note: 3547 appears in both 8H and 10H
    id_10h = ["3547", "3369", "3436", "3552"]
    protemics = mppg_ctl_sample[mppg_ctl_sample.ids["subject"].isin(id_8h)]
    protemics = protemics[
        ~(
            (protemics[("ids", "experiment")] == "3547HY_1")
            | (protemics[("ids", "experiment")] == "3547HY_2")
            | (protemics[("ids", "experiment")] == "3547HY_3")
            | (protemics[("ids", "experiment")] == "3547HY_4")
        )
    ]

    sub_samples = get_no_of_subjects_samples(protemics)

    print(
        "number of subjects and samples in  mppg 8hr protocol: ",
        sub_samples[0],
        sub_samples[1],
    )
    print(
        "mppg 8h protocol, blood collected at: ",
        list(round(get_blood_collection_time(protemics), 2)),
    )
    protemics = mppg_ctl_sample[mppg_ctl_sample.ids["subject"].isin(id_10h)]

    protemics = protemics[
        ~(
            (protemics[("ids", "experiment")] == "3547HY82_1")
            | (protemics[("ids", "experiment")] == "3547HY82_2")
        )
    ]

    sub_samples = get_no_of_subjects_samples(protemics)

    print(
        "number of subjects and samples in  mppg 10hr protocol: ",
        sub_samples[0],
        sub_samples[1],
    )
    print(
        "mppg 10h protocol, blood collected at: ",
        list(round(get_blood_collection_time(protemics), 2)),
    )
    print("=================================================================")

    mppg_csr_sample = get_mppg_csr(df_ids_profile, box1, path_to_box)
    print("shape of mppg_csr sample: ", mppg_csr_sample.shape)
    id_5h = ["29W4", "3665", "3776", "3794", "3828"]
    id_56h = ["3445", "3608", "3665", "3619"]
    protemics = mppg_csr_sample[mppg_csr_sample.ids["subject"].isin(id_5h)]

    # 3665 appears in both 5H and 5.6H, so removing 5.6H experiment
    # id for 3665 info from 5H protocol.
    protemics = protemics[
        ~(
            (protemics[("ids", "experiment")] == "3665HY_1")
            | (protemics[("ids", "experiment")] == "3665HY_2")
            | (protemics[("ids", "experiment")] == "3665HY_3")
            | (protemics[("ids", "experiment")] == "3665HY_4")
        )
    ]

    sub_samples = get_no_of_subjects_samples(protemics)

    print(
        "number of subjects and samples in  mppg 5hr protocol: ",
        sub_samples[0],
        sub_samples[1],
    )
    print(
        "mppg 5h protocol, blood collected at: ",
        list(round(get_blood_collection_time(protemics), 2)),
    )

    print("==============================================================")

    protemics = mppg_csr_sample[mppg_csr_sample.ids["subject"].isin(id_56h)]

    # 3665 appears in both 5H and 5.6H, so removing 5H experiment id for 3665 info from
    # 5.6H protocol.
    protemics = protemics[
        ~(
            (protemics[("ids", "experiment")] == "3665HY82_1")
            | (protemics[("ids", "experiment")] == "3665HY82_2")
            | (protemics[("ids", "experiment")] == "3665HY82_3")
        )
    ]

    sub_samples = get_no_of_subjects_samples(protemics)

    print(
        "number of subjects and samples in  mppg 5.6hr protocol: ",
        sub_samples[0],
        sub_samples[1],
    )
    print(
        "mppg 5.6h protocol, blood collected at: ",
        list(round(get_blood_collection_time(protemics), 2)),
    )
    print("===============================================")

    mppg_fd_sample = get_mppg_fd(df_ids_profile, box1, path_to_box)
    print("shape of mppg_fd sample: ", mppg_fd_sample.shape)
    sub_samples = get_no_of_subjects_samples(mppg_fd_sample)
    print(
        "number of subjects and samples in FAA Forced Desynchrony: ",
        sub_samples[0],
        sub_samples[1],
    )
    print(
        "blood collected at: ",
        list(round(get_blood_collection_time(mppg_fd_sample), 2)),
    )
    print("===============================================")

    return pd.concat([mppg_ctl_sample, mppg_csr_sample, mppg_fd_sample])


def get_faa(
    df_ids_profile: pd.DataFrame, path_to_box: Path, box1: BoxManager
) -> pd.DataFrame:
    """
    get the faa protocol
    """

    faa_ctl_sample = get_faa_ctl(df_ids_profile, box1, path_to_box)
    print("shape of faa_ctl sample: ", faa_ctl_sample.shape)
    sub_samples = get_no_of_subjects_samples(faa_ctl_sample)
    print("number of subjects and samples in FAA ctl: ", sub_samples[0], sub_samples[1])
    print(
        "blood collected at: ",
        list(round(get_blood_collection_time(faa_ctl_sample), 2)),
    )
    print("===============================================")

    faa_tsd_sample = get_faa_tsd(df_ids_profile, box1, path_to_box)
    print("shape of faa_tsd sample: ", faa_tsd_sample.shape)
    sub_samples = get_no_of_subjects_samples(faa_tsd_sample)
    print("number of subjects and samples in FAA TSD: ", sub_samples[0], sub_samples[1])
    print(
        "blood collected at: ",
        list(round(get_blood_collection_time(faa_tsd_sample), 2)),
    )
    print("===============================================")

    faa_csrn_sample = get_faa_csrn(df_ids_profile, box1, path_to_box)
    print("shape of faa_csrn sample: ", faa_csrn_sample.shape)
    sub_samples = get_no_of_subjects_samples(faa_csrn_sample)
    print(
        "number of subjects and samples in FAA CSRN: ", sub_samples[0], sub_samples[1]
    )
    print(
        "blood collected at: ",
        list(round(get_blood_collection_time(faa_csrn_sample), 2)),
    )
    print("===============================================")

    faa_csrd_sample = get_faa_csrd(df_ids_profile, box1, path_to_box)
    print("shape of faa_csrd sample: ", faa_csrd_sample.shape)
    sub_samples = get_no_of_subjects_samples(faa_csrd_sample)
    print(
        "number of subjects and samples in FAA CSRD: ", sub_samples[0], sub_samples[1]
    )
    print(
        "blood collected at: ",
        list(round(get_blood_collection_time(faa_csrd_sample), 2)),
    )
    print("===============================================")

    return pd.concat(
        [
            faa_ctl_sample,
            faa_tsd_sample,
            faa_csrn_sample,
            faa_csrd_sample,
        ]
    )


def get_mri_day5(
    df_ids_profile: pd.DataFrame, path_to_box: Path, box1: BoxManager
) -> pd.DataFrame:
    """
    get the mri and day5 protocol
    """

    mri_sample = get_mri(df_ids_profile, box1, path_to_box)
    sub_samples = get_no_of_subjects_samples(mri_sample)
    print("shape of mri sample: ", mri_sample.shape)
    print("columns of mri sample: ", mri_sample.columns)
    print("number of subjects and samples in mri: ", sub_samples[0], sub_samples[1])
    print("blood collected at: ", list(round(get_blood_collection_time(mri_sample), 2)))
    print("===============================================")

    day5_sample = get_5day(df_ids_profile, box1, path_to_box)
    sub_samples = get_no_of_subjects_samples(day5_sample)
    print("shape of day5 sample: ", day5_sample.shape)
    print("number of subjects and samples in mri: ", sub_samples[0], sub_samples[1])
    print(
        "blood collected at: ", list(round(get_blood_collection_time(day5_sample), 2))
    )
    print("===============================================")
    return pd.concat([mri_sample, day5_sample])


def get_dinges_zeitzer(
    df_ids_profile: pd.DataFrame,
    df_ids_profile_with_all_rows: pd.DataFrame,
    path_to_box: Path,
    box1: BoxManager,
) -> pd.DataFrame:
    """
    get the dinges and zeitzer protocol
    """

    zeitzer_sample = get_zeitzer(df_ids_profile_with_all_rows, box1, path_to_box)
    print("shape of zeitzer sample: ", zeitzer_sample.shape)
    sub_samples = get_no_of_subjects_samples(zeitzer_sample)
    print("number of subjects and samples in Zeitzer: ", sub_samples[0], sub_samples[1])
    print(
        "blood collected at: ",
        list(round(get_blood_collection_time(zeitzer_sample), 2)),
    )
    print("===============================================")

    dinges_sample = get_dinges(df_ids_profile, box1, path_to_box)
    print("shape of dinges sample: ", dinges_sample.shape)
    sub_samples = get_no_of_subjects_samples(dinges_sample)
    print("number of subjects and samples in dinges: ", sub_samples[0], sub_samples[1])
    print(
        "blood collected at: ",
        list(round(get_blood_collection_time(dinges_sample), 2)),
    )

    print("done")

    return pd.concat([zeitzer_sample, dinges_sample])


if __name__ == "__main__":
    box = get_box()

    df_ids_prof_no_proteins = get_ids_profile_drop_rows_missing_proteins(box)
    df_ids_prof_proteins = get_ids_profile(box)

    # adenosine model

    dinges_zeitzer = get_dinges_zeitzer(
        df_ids_prof_no_proteins, df_ids_prof_proteins, BOX_PATH["csvs"], box
    )
    mppg = get_mppg_ctl_csr_fd(df_ids_prof_no_proteins, BOX_PATH["csvs"], box)
    # print("sample id", mppg["ids"]["sample_id"])
    mri_5day = get_mri_day5(df_ids_prof_no_proteins, BOX_PATH["csvs"], box)
    faa = get_faa(df_ids_prof_no_proteins, BOX_PATH["csvs"], box)

    df_sleep_debt_adenosine = pd.concat([dinges_zeitzer, mppg, mri_5day, faa])
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
        df_ids_prof_no_proteins, df_ids_prof_proteins, BOX_PATH["csvs_unified"], box
    )
    mppg = get_mppg_ctl_csr_fd(df_ids_prof_no_proteins, BOX_PATH["csvs_unified"], box)
    mri_5day = get_mri_day5(df_ids_prof_no_proteins, BOX_PATH["csvs_unified"], box)
    faa = get_faa(df_ids_prof_no_proteins, BOX_PATH["csvs_unified"], box)

    df_sleep_debt_unified = pd.concat([dinges_zeitzer, mppg, mri_5day, faa])
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

    save_to_csv(
        box,
        df_proteomics_with_sleep_debt,
        BOX_PATH["csv_proteomics"]
        / f"data_{split_string[1]}_{split_string[2]}_with_sleep_debt_{today}_PS.csv",
        index=False,
    )
