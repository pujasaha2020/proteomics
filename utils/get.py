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
    "proteomics": Path("archives/data/proteomics_071924_AS.csv"),
    "aptamers": Path("archives/data/aptamers.csv"),
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
    df[("profile", "clock_time")] = pd.to_datetime(
        df.profile.clock_time, format="mixed"
    )
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
        "study": str,
        "subject": str,
        "experiment": str,
        "sample_id": str,
    }
    df = pd.read_csv(file, dtype=dtype)
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
