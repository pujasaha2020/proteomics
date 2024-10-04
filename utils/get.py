"""Provide shortcuts to get relevant data"""

from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

from box.manager import BoxManager
from utils.check import check_df
from utils.process import preprocess_proteomics

# Default paths
PATH = {
    "proteomics": Path("archives/data/proteomics_091224_AS.csv"),
    "aptamers": Path("archives/data/aptamers.csv"),
    "debt": Path(
        "archives/sleepdebt/sleepdebt_data/dataset_with_sleepdebt_at_clocktime/"
        + "data_091224_AS_with_sleep_debt_2024-10-02_PS.csv"
    ),
    "protocols": Path("archives/sleepdebt/sleepdebt_data/yaml_files/protocols.yaml"),
    "parameters": Path("archives/sleepdebt/sleepdebt_data/yaml_files/parameters.yaml"),
}


def get_box() -> BoxManager:
    """Get BoxManager object"""
    box = BoxManager()
    if not box.token_path.exists():
        raise ValueError("Box token file is not accessible.")
    return box


def get_proteomics(
    box: BoxManager,
    path: Path = PATH["proteomics"],
    preprocessing: Optional[list[dict]] = None,
) -> pd.DataFrame:
    """
    Get proteomic dataset from Box.

    # Examples:

    ### Open the csv file
    >>> box = get_box()
    >>> df = get_proteomics(box)

    ### Open the csv file and preprocess it
    >>> box = get_box()
    >>> sizes = get_sizes(box)
    >>> aptamers = get_aptamers(box)
    >>> preprocessing = [
    ...     {   # Step 1
    ...         "fun": optimize_full_dataset,
    ...         "args": {"sizes": sizes, "min_proteins": 4000},
    ...     },
    ...     {   # Step 2
    ...         "fun": drop_high_cv_proteins,
    ...         "args": {"aptamers": aptamers},
    ...     },
    ...     {   # Step 3
    ...         "fun": bridge_v40_to_v41,
    ...         "args": {"aptamers": aptamers},
    ...     },
    ...     {   # Step 4
    ...         "fun": drop_proteins_with_missing_samples,
    ...         "args": {}
    ...     },
    ...     {   # Step 5
    ...         "fun": log_normalize_proteins,
    ...         "args": {}
    ...     },
    ... ]
    >>> df = get_proteomics(box, preprocessing=preprocessing)
    """
    file = box.get_file(path)
    dtype = {
        ("ids", "study"): str,
        ("ids", "subject"): str,
        ("ids", "experiment"): str,
        ("ids", "sample_id"): str,
    }
    df = pd.read_csv(file, header=[0, 1], dtype=dtype, low_memory=False)
    check_df(df, "proteomics", path)
    df[("profile", "time")] = pd.to_datetime(df.profile.time, format="mixed")
    if preprocessing:
        preprocess_proteomics(df, preprocessing)
    return df


def get_aptamers(box: BoxManager, path: Path = PATH["aptamers"]) -> pd.DataFrame:
    """Get aptamer table from Box."""
    file = box.get_file(path)
    df = pd.read_csv(file, index_col=0, low_memory=False)
    check_df(df, "aptamer", path)
    return df


def get_debt(box: BoxManager, path: Path = PATH["debt"]) -> pd.DataFrame:
    """Get debt table from Box.
    This function will be deprecated once sleep debt values are add to proteomics."""
    file = box.get_file(path)
    dtype = {
        ("ids", "study"): str,
        ("ids", "subject"): str,
        ("ids", "experiment"): str,
        ("ids", "sample_id"): str,
    }
    df = pd.read_csv(file, dtype=dtype, header=[0, 1], low_memory=False)
    check_df(df, "debt", path)
    return df


def get_info_per_somalogic(df: pd.DataFrame) -> dict[str, dict]:
    """Extract the number of samples and the proteins measured in each somalogic id."""
    n_samples = dict(df.ids.somalogic.value_counts())
    info = {}
    for somalogic, n in n_samples.items():
        soma_df = df[df.ids.somalogic == somalogic]
        full_proteins = soma_df["proteins"].notna().all(axis=0)
        proteins = set(full_proteins[full_proteins].index)
        info[somalogic] = {"proteins": proteins, "n_samples": n}
    return info


def get_sizes(box: BoxManager, path: Path = PATH["proteomics"]) -> list[list[int]]:
    """Get the size analysis results"""
    date = path.stem.split("_")[-2]
    size_path = path.parent / f"size_{date}.yaml"
    try:
        file = box.get_file(size_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Size results not available for {path}") from exc
    sizes = yaml.safe_load(file.getvalue())
    if "n_samples, n_proteins" not in sizes:
        raise ValueError("Invalid size analysis results")
    return sizes["n_samples, n_proteins"]


def get_protocols(box: BoxManager, path: Path = PATH["protocols"]) -> dict:
    """get protocols from box"""
    file = box.get_file(path)
    data = yaml.safe_load(file)
    return data


def get_parameters(box: BoxManager, path: Path = PATH["parameters"]) -> dict:
    """get protocols from box"""
    file = box.get_file(path)
    params = yaml.safe_load(file)
    return params


def get_status(t: int, time_ct: list[int]) -> str:
    """getting sleep/wake status based on time interval"""
    s = "awake"
    for i in range(1, len(time_ct), 2):
        # print(i)
        if time_ct[i] < t <= time_ct[i + 1]:
            s = "sleep"
            break
    return s


def get_title(pro, data):
    """getting title for the plot"""
    return data["protocols"][pro.name]["title"]


def get_blood_collection_time(pro, data):
    """getting blood collection time"""
    return data["protocols"][pro.name]["blood_sample_time"]


def get_ids_profile_drop_missing_proteins(
    box1: BoxManager, path: Path = PATH["proteomics"]
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
    df_cleaned.reset_index(drop=True, inplace=True)
    print("shape of dataset after cleaning: ", df_cleaned.shape)
    ids_profile = df_cleaned[["ids", "infos", "profile"]]

    return ids_profile


def get_subjects_samples(df_protocol: pd.DataFrame) -> list:
    """get the number of subjects and samples in each study"""
    subs = df_protocol[("ids", "subject")].unique()
    print(subs)
    samples = df_protocol.shape[0]

    return [len(subs), samples]


def get_time_per_subject(df_protocol: pd.DataFrame) -> pd.Series:
    """
    get the blood collection time for each subject,
    then consider subjects with the maximum number of samples.
    """
    # time = (df_protocol[("profile", "mins_from_admission")] - 15840) / (60 * 24)
    subject_counts = df_protocol[("ids", "subject")].value_counts()
    print(subject_counts)

    # Find the maximum count
    max_count = subject_counts.idxmax()
    print(max_count)
    # Find the subject with the maximum count
    time = df_protocol[df_protocol[("ids", "subject")] == max_count][
        ("profile", "mins_from_admission")
    ] / (60 * 24)
    # print(df_protocol[df_protocol[("ids", "subject")] == max_count].ids)

    return time
