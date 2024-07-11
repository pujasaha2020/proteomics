"""Provide shortcuts to get relevant data"""

from pathlib import Path

import pandas as pd

from box.manager import BoxManager
from utils.checks import check_debt, check_proteomics, check_somalogic

# Default paths
PATH = {
    "proteomics": Path("archives/data/proteomics_051124_AS.csv"),
    "somalogic": Path("archives/data/somasupp.csv"),
    "debt": Path(
        "archives/sleep_debt/SleepDebt_Data/proteomic_with_sleepdebt_mri_5day_mppg_"
        + "dinges_faa_FD_Zeitzer_030124AS_062524PS.csv"
    ),
}


def get_box() -> BoxManager:
    """Get BoxManager object"""
    box = BoxManager()
    if not box.token_path.exists():
        raise ValueError("Box token file is not accessible.")
    return box


def get_proteomics(box: BoxManager, path: Path = PATH["proteomics"]) -> pd.DataFrame:
    """Get proteomic dataset from Box"""
    file = box.get_file(path)
    dtype = {
        ("ids", "study"): str,
        ("ids", "subject"): str,
        ("ids", "experiment"): str,
        ("ids", "sample_id"): str,
    }
    df = pd.read_csv(file, header=[0, 1], dtype=dtype, low_memory=False)
    try:
        check_proteomics(df)
    except AssertionError as e:
        raise AssertionError(f"{path} does not meet expected format.") from e
    df[("profile", "clock_time")] = pd.to_datetime(
        df.profile.clock_time, format="mixed"
    )
    return df


def get_somalogic(box: BoxManager, path: Path = PATH["somalogic"]) -> pd.DataFrame:
    """Get somalogic table from Box"""
    file = box.get_file(path)
    df = pd.read_csv(file, index_col=0, low_memory=False)
    try:
        check_somalogic(df)
    except AssertionError as e:
        raise AssertionError(f"{path} does not meet expected format.") from e
    return df


def get_debt(box: BoxManager, path: Path = PATH["debt"]) -> pd.DataFrame:
    """Get debt table from Box.
    This function will be deprecated once sleep debt values are add to proteomics."""
    file = box.get_file(path)
    dtype = {
        "study": str,
        "subject": str,
        "experiment": str,
        "sample_id": str,
    }
    df = pd.read_csv(file, dtype=dtype)
    try:
        check_debt(df)
    except AssertionError as e:
        raise AssertionError(f"{path} does not meet expected format.") from e
    return df
