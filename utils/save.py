""" Provides shortcuts to save various type of file"""

import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yaml

from box.manager import BoxManager


def save_to_csv(box: BoxManager, df: pd.DataFrame, path: Path, **kwargs):
    """Save the results to a CSV file"""
    if path.suffix != ".csv":
        raise ValueError(f"{path} is not a csv file.")
    file = io.StringIO()
    df.to_csv(file, **kwargs)
    file.seek(0)
    box.save_file(file, path)


def save_to_yaml(box: "BoxManager", data: dict, path: Path, **kwargs):
    """Save the dictionary to a YAML file."""
    if path.suffix not in [".yaml", ".yml"]:
        raise ValueError(f"{path} is not a YAML file.")
    file = io.StringIO()
    yaml.dump(data, file, **kwargs)
    file.seek(0)
    box.save_file(file, path)
