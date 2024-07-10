"""Module that test if Box Manager works correctly"""

import warnings
from pathlib import Path

import pandas as pd
import pytest

from box.manager import BoxManager


def test_box_manager():
    """Test access to Box proteomics folder"""

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        box = BoxManager()
        if not box.token_path.exists():
            pytest.skip("Box token file is not accessible, skipping box tests.")

        # Test the content of the proteomics folder
        content = set()
        for item in box.proteomics.get_items():
            content.add(item.name)
        true_content = {
            "archives",
            "doc",
            "official",
            "raw_data",
            "results",
            "readme.docx",
            "READ_ME.txt",
        }
        assert content == true_content
        assert box.proteomics.name == "proteomics"

        # Test a folder id
        path = Path("raw_data")
        folder_id = box.get_id(path, box.proteomics)
        assert folder_id == "200093011900"
        # Test a file id
        path = Path("raw_data/proteins/READ_ME.txt")
        file_id = box.get_id(path, box.proteomics)
        assert file_id == "1171334247062"

        # Test a file.txt
        path = Path("raw_data/proteins/READ_ME.txt")
        file = box.get_file(path)
        true_beginning = "Last editor"
        beginning = file.readline()[: len(true_beginning)]
        assert beginning == true_beginning
        # Test a file.csv
        path = Path("archives/data/somasupp.csv")
        file = box.get_file(path)
        df = pd.read_csv(file)
        assert df.shape == (7289, 11)
        subset_cols = {"SeqId", "Target Name", "UniProt ID"}
        assert subset_cols.issubset(df.columns)
