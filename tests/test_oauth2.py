"""Module that test if users has access to Box proteomics folder"""

import warnings

from box.oauth2 import get_box_folder


def test_box_access():
    """Test access to Box proteomics folder"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)

        folder = get_box_folder()
        content = set()
        for item in folder.get_items():
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
