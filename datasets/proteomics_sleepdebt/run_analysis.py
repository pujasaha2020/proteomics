# run_analysis.py

from pathlib import Path

import pandas as pd

from box.manager import BoxManager
from datasets.proteomics_sleepdebt.day5_study import get_5day
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
    "proteomics": Path("archives/data/proteomics_071924_AS.csv"),
    "csvs": Path("archives/sleep_debt/SleepDebt_Data/ligand_receptor_model/sleepdebt/"),
    "csv_proteomics": Path(
        "archives/sleep_debt/SleepDebt_Data/ligand_receptor_model/proteomics_with_sleepdebt"
    ),
}


def get_ids_profile_drop_rows_missing_proteins(
    box: BoxManager, path: Path = BOX_PATH["proteomics"]
):
    """
    getting "ids" and  "profile" from proteomics data.
    data is filtered depending on the availability of proteomics data
    """
    file = box.get_file(path)
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


def get_ids_profile(box: BoxManager, path: Path = BOX_PATH["proteomics"]):
    """
    getting "ids" and  "profile" from proteomics data.
    data is filtered depending on the availability of proteomics data
    """
    file = box.get_file(path)
    dtype = {
        ("ids", "study"): str,
        ("ids", "subject"): str,
        ("ids", "experiment"): str,
        ("ids", "sample_id"): str,
    }
    df = pd.read_csv(file, header=[0, 1], dtype=dtype, low_memory=False)

    return df


if __name__ == "__main__":
    box1 = get_box()
    df_ids_profile = get_ids_profile_drop_rows_missing_proteins(box1)
    df_ids_profile_with_proteomics = get_ids_profile(box1)

    mri_sample = get_mri(df_ids_profile, box1, BOX_PATH["csvs"])
    print("shape of mri sample: ", mri_sample.shape)
    print("columns of mri sample: ", mri_sample.columns)
    print("===============================================")
    """
    day5_sample = get_5day(df_ids_profile, box1, BOX_PATH["csvs"])
    print("shape of day5 sample: ", day5_sample.shape)
    print("===============================================")

    mppg_ctl_sample = get_mppg_ctl(df_ids_profile, box1, BOX_PATH["csvs"])
    print("shape of mppg_ctl sample: ", mppg_ctl_sample.shape)
    print("===============================================")

    mppg_csr_sample = get_mppg_csr(df_ids_profile, box1, BOX_PATH["csvs"])
    print("shape of mppg_csr sample: ", mppg_csr_sample.shape)
    print("===============================================")

    faa_ctl_sample = get_faa_ctl(df_ids_profile, box1, BOX_PATH["csvs"])
    print("shape of faa_ctl sample: ", faa_ctl_sample.shape)
    print("===============================================")
    faa_tsd_sample = get_faa_tsd(df_ids_profile, box1, BOX_PATH["csvs"])
    print("shape of faa_tsd sample: ", faa_tsd_sample.shape)
    print("===============================================")

    faa_csrn_sample = get_faa_csrn(df_ids_profile, box1, BOX_PATH["csvs"])
    print("shape of faa_csrn sample: ", faa_csrn_sample.shape)
    print("===============================================")

    faa_csrd_sample = get_faa_csrd(df_ids_profile, box1, BOX_PATH["csvs"])
    print("shape of faa_csrd sample: ", faa_csrd_sample.shape)
    print("===============================================")

    mppg_fd_sample = get_mppg_fd(df_ids_profile, box1, BOX_PATH["csvs"])
    print("shape of mppg_fd sample: ", mppg_fd_sample.shape)
    print("===============================================")

    zeitzer_sample = get_zeitzer(df_ids_profile_with_proteomics, box1, BOX_PATH["csvs"])
    print("shape of zeitzer sample: ", zeitzer_sample.shape)
    print("===============================================")

    print("done")
    df_proteomics_with_sleep_debt = pd.concat(
        mri_sample,
        day5_sample,
        mppg_ctl_sample,
        mppg_csr_sample,
        faa_ctl_sample,
        faa_tsd_sample,
        faa_csrn_sample,
        faa_csrd_sample,
        mppg_fd_sample,
        zeitzer_sample,
    )
    print("shape of all samples: ", df_proteomics_with_sleep_debt.shape)

    # save the dataset as csv to BOX
    save_to_csv(
        box1,
        df_proteomics_with_sleep_debt,
        BOX_PATH["csvs_proteomics"] / "proteomics_with_sleep_debt.csv",
        index=False,
    )
    """
