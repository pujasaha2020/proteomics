"""Module that test if get functions work correctly"""

from pathlib import Path

import pytest

from box.manager import BoxManager
from utils.get import get_box, get_debt, get_proteomics, get_somalogic

# Apply the filterwarnings marker to all tests in this file
pytestmark = pytest.mark.filterwarnings("ignore:Package 'boxsdk'*:DeprecationWarning")


def test_get_box():
    """Test get_box function"""
    box = get_box()
    assert isinstance(box, BoxManager)


def test_get_proteomics():
    """Test get_proteomics function"""
    box = get_box()
    # Test with default path
    get_proteomics(box)
    # Test with wrong path
    wrong_path = Path("archives/data/somasupp.csv")
    with pytest.raises(AssertionError):
        get_proteomics(box, wrong_path)


def test_get_somalogic():
    """Test get_somalogic function"""
    box = get_box()
    # Test with default path
    get_somalogic(box)
    # Test with wrong path
    wrong_path = Path("archives/data/proteomics_051124_AS.csv")
    with pytest.raises(AssertionError):
        get_somalogic(box, wrong_path)


def test_get_debt():
    """Test get_debt function"""
    box = get_box()
    # Test with default path
    get_debt(box)
    # Test with wrong path
    wrong_path = Path("archives/data/somasupp.csv")
    with pytest.raises(AssertionError):
        get_debt(box, wrong_path)
