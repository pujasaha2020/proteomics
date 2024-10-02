# get_studies
"""
get_mppg_ctl_csr_fd: function that gets the mppg protocol and returns 
                     the sleepdebt at clock time.
get_faa: function that gets the faa protocol and returns the 
        sleepdebt at clock time.
get_mri_day5: function that gets the mri and day5 and mri protocol 
              and returns the sleepdebt at clock time.
get_dinges_zeitzer: function that gets the dinges and zeitzer protocol and returns
                     the sleepdebt at clock time.
"""
from pathlib import Path

import pandas as pd

from box.manager import BoxManager
from datasets.sleepdebt.studies.day5_study import get_5day
from datasets.sleepdebt.studies.dinges_study import get_dinges
from datasets.sleepdebt.studies.faa_csrd_study import get_faa_csrd
from datasets.sleepdebt.studies.faa_csrn_study import get_faa_csrn
from datasets.sleepdebt.studies.faa_ctl_study import get_faa_ctl
from datasets.sleepdebt.studies.faa_tsd_study import get_faa_tsd
from datasets.sleepdebt.studies.mppg_csr_study import get_mppg_csr
from datasets.sleepdebt.studies.mppg_ctl_study import get_mppg_ctl
from datasets.sleepdebt.studies.mppg_fd_study import get_mppg_fd
from datasets.sleepdebt.studies.mri_study import get_mri
from datasets.sleepdebt.studies.zeitzer_study import get_zeitzer
from utils.get import get_subjects_samples, get_time_per_subject


def get_mppg_ctl_csr(
    df_ids_profile: pd.DataFrame,
    path_to_box: Path,
    box1: BoxManager,
    dict_count: pd.DataFrame,
) -> tuple:
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

    sub_samples = get_subjects_samples(protemics)

    blood_time = round(get_time_per_subject(protemics), 2)
    dict_count = fill_count_dict(dict_count, "mppg_8h", sub_samples, list(blood_time))

    protemics = mppg_ctl_sample[mppg_ctl_sample.ids["subject"].isin(id_10h)]

    protemics = protemics[
        ~(
            (protemics[("ids", "experiment")] == "3547HY82_1")
            | (protemics[("ids", "experiment")] == "3547HY82_2")
        )
    ]

    sub_samples = get_subjects_samples(protemics)

    blood_time = round(get_time_per_subject(protemics), 2)
    dict_count = fill_count_dict(dict_count, "mppg_10h", sub_samples, list(blood_time))

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

    sub_samples = get_subjects_samples(protemics)
    blood_time = round(get_time_per_subject(protemics), 2)
    dict_count = fill_count_dict(dict_count, "mppg_5h", sub_samples, list(blood_time))

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

    sub_samples = get_subjects_samples(protemics)

    blood_time = round(get_time_per_subject(protemics), 2)
    dict_count = fill_count_dict(dict_count, "mppg_56h", sub_samples, list(blood_time))

    print("===============================================")
    return (pd.concat([mppg_ctl_sample, mppg_csr_sample]), dict_count)


def get_fd(
    df_ids_profile: pd.DataFrame,
    path_to_box: Path,
    box1: BoxManager,
    dict_count: pd.DataFrame,
) -> tuple:
    """
    get forced desynchrony protocol
    """

    mppg_fd_sample = get_mppg_fd(df_ids_profile, box1, path_to_box)
    print("shape of mppg_fd sample: ", mppg_fd_sample.shape)
    sub_samples = get_subjects_samples(mppg_fd_sample)
    print(
        "number of subjects and samples in FAA Forced Desynchrony: ",
        sub_samples[0],
        sub_samples[1],
    )
    print(
        "blood collected at: ",
        list(round(get_time_per_subject(mppg_fd_sample), 2)),
    )

    blood_time = round(get_time_per_subject(mppg_fd_sample), 2)
    dict_count = fill_count_dict(dict_count, "mppg_fd", sub_samples, list(blood_time))

    print("===============================================")

    return (mppg_fd_sample, dict_count)


def get_faa(
    df_ids_profile: pd.DataFrame,
    path_to_box: Path,
    box1: BoxManager,
    dict_count: pd.DataFrame,
) -> tuple:
    """
    get the faa protocol
    """

    faa_ctl_sample = get_faa_ctl(df_ids_profile, box1, path_to_box)
    print("shape of faa_ctl sample: ", faa_ctl_sample.shape)
    sub_samples = get_subjects_samples(faa_ctl_sample)
    blood_time = round(get_time_per_subject(faa_ctl_sample), 2)
    dict_count = fill_count_dict(dict_count, "faa_ctl", sub_samples, list(blood_time))

    print("===============================================")

    faa_tsd_sample = get_faa_tsd(df_ids_profile, box1, path_to_box)
    print("shape of faa_tsd sample: ", faa_tsd_sample.shape)
    sub_samples = get_subjects_samples(faa_tsd_sample)

    sub_samples = get_subjects_samples(faa_tsd_sample)
    blood_time = round(get_time_per_subject(faa_tsd_sample), 2)
    dict_count = fill_count_dict(dict_count, "faa_tsd", sub_samples, list(blood_time))

    print("===============================================")

    faa_csrn_sample = get_faa_csrn(df_ids_profile, box1, path_to_box)
    print("shape of faa_csrn sample: ", faa_csrn_sample.shape)
    sub_samples = get_subjects_samples(faa_csrn_sample)
    blood_time = round(get_time_per_subject(faa_csrn_sample), 2)
    dict_count = fill_count_dict(dict_count, "faa_csrn", sub_samples, list(blood_time))

    print("===============================================")

    faa_csrd_sample = get_faa_csrd(df_ids_profile, box1, path_to_box)
    print("shape of faa_csrd sample: ", faa_csrd_sample.shape)
    sub_samples = get_subjects_samples(faa_csrd_sample)
    blood_time = round(get_time_per_subject(faa_csrd_sample), 2)
    dict_count = fill_count_dict(dict_count, "faa_csrd", sub_samples, list(blood_time))

    print("===============================================")

    return (
        pd.concat(
            [
                faa_ctl_sample,
                faa_tsd_sample,
                faa_csrn_sample,
                faa_csrd_sample,
            ]
        ),
        dict_count,
    )


def get_mri_day5(
    df_ids_profile: pd.DataFrame,
    path_to_box: Path,
    box1: BoxManager,
    dict_count: pd.DataFrame,
) -> tuple:
    """
    get the mri and day5 protocol
    """

    mri_sample = get_mri(df_ids_profile, box1, path_to_box)
    sub_samples = get_subjects_samples(mri_sample)
    print("shape of mri sample: ", mri_sample.shape)
    blood_time = round(get_time_per_subject(mri_sample), 2)
    dict_count = fill_count_dict(dict_count, "mri", sub_samples, list(blood_time))

    print("===============================================")

    day5_sample = get_5day(df_ids_profile, box1, path_to_box)
    sub_samples = get_subjects_samples(day5_sample)
    print("shape of day5 sample: ", day5_sample.shape)
    blood_time = round(get_time_per_subject(day5_sample), 2)
    dict_count = fill_count_dict(dict_count, "5day", sub_samples, list(blood_time))

    print("===============================================")
    return (pd.concat([mri_sample, day5_sample]), dict_count)


def get_dinges_zeitzer(
    df_ids_profile: pd.DataFrame,
    df: pd.DataFrame,
    path_to_box: Path,
    box1: BoxManager,
    dict_count: dict,
) -> pd.DataFrame:
    """
    get the dinges and zeitzer protocol
    """

    zeitzer_sample = get_zeitzer(df, box1, path_to_box)
    print("shape of zeitzer sample: ", zeitzer_sample.shape)
    sub_samples = get_subjects_samples(zeitzer_sample)
    blood_time = round(get_time_per_subject(zeitzer_sample), 2)
    dict_count = fill_count_dict(dict_count, "Zeitzer", sub_samples, list(blood_time))

    print("===============================================")

    dinges_sample = get_dinges(df_ids_profile, box1, path_to_box)
    print("shape of dinges sample: ", dinges_sample.shape)
    sub_samples = get_subjects_samples(dinges_sample)
    blood_time = round(get_time_per_subject(dinges_sample), 2)
    dict_count = fill_count_dict(dict_count, "Dinges", sub_samples, list(blood_time))

    return (pd.concat([zeitzer_sample, dinges_sample]), dict_count)


def fill_count_dict(
    dict_count: dict, name: str, sub_sample: list, blood_time: list
) -> dict:
    """
    fill the count dictionary with missing values
    """

    dict_count["study"].append(name)
    dict_count["subject_count"].append(sub_sample[0])
    dict_count["sample_count"].append(sub_sample[1])
    dict_count["blood_time"].append(blood_time)

    return dict_count
