"""Module that test if Box Manager works correctly"""

import io
import warnings
from pathlib import Path

import pandas as pd
import pytest

from box.manager import PROTECTED_FOLDERS, BoxManager


def test_root_folder():
    """Test access to Box proteomics folder"""

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        box = BoxManager()
        if not box.token_path.exists():
            pytest.skip("Box token file is not accessible, skipping box tests.")

        # Check the root folder
        assert box.proteomics.name == "proteomics"
        content = set(box.get_folder_contents(Path(".")))
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


def test_get_id():
    """Test get_id method"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        box = BoxManager()
        if not box.token_path.exists():
            pytest.skip()

        # Check root id
        path = Path(".")
        root_id = box.get_id(path, box.proteomics)
        assert root_id == "200099021915"
        # Check folder id
        path = Path("raw_data")
        folder_id = box.get_id(path, box.proteomics)
        assert folder_id == "200093011900"
        # Check file id
        path = Path("raw_data/proteins/READ_ME.txt")
        file_id = box.get_id(path, box.proteomics)
        assert file_id == "1171334247062"


def test_txt_file():
    """Test txt file upload/download/delete"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        box = BoxManager()
        if not box.token_path.exists():
            pytest.skip()
        file = io.StringIO("Hello, world!")
        path = Path("test/folder/hello.txt")

        # Deletion of non-existent path
        with pytest.raises(FileNotFoundError):
            box.delete(path)
        with pytest.raises(FileNotFoundError):
            box.delete(path.parent)

        # Create a folder with a file
        with pytest.raises(ValueError):
            box.create_folder(path)

        # Create a new folder
        box.create_folder(path.parent)
        with pytest.raises(FileNotFoundError):
            box.get_file(path)

        # Create a folder that already exists
        with pytest.raises(ValueError):
            box.create_folder(path.parent)

        # Upload the file
        box.save_file(file, path)

        # Upload a folder
        with pytest.raises(ValueError):
            box.save_file(file, path.parent)

        # Download the file
        file = box.get_file(path)
        assert file.readline() == "Hello, world!"

        # Delete the file
        box.delete(path)
        with pytest.raises(FileNotFoundError):
            box.get_file(path)

        # Check protected folders
        top_folder = Path(path.parts[0])
        PROTECTED_FOLDERS.append(str(top_folder))
        with pytest.raises(ValueError):
            box.delete(top_folder)
        PROTECTED_FOLDERS.remove(str(top_folder))

        # Delete the top folder
        box.delete(top_folder, recursive=True)
        with pytest.raises(FileNotFoundError):
            box.get_id(top_folder, box.proteomics)


def test_csv_file():
    """Test csv file upload/download/delete"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        box = BoxManager()
        if not box.token_path.exists():
            pytest.skip()
        df_upload = pd.DataFrame({"A": [1, 2], "B": [4, None], "C": ["a", "b"]})
        file = io.StringIO()
        df_upload.to_csv(file, index=False)
        file.seek(0)
        path = Path("test.csv")
        box.save_file(file, path)
        file = box.get_file(path)
        df_download = pd.read_csv(file)
        assert df_upload.equals(df_download)
        box.delete(path)
