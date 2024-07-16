"""Test the figures functions"""

import matplotlib
import pytest
from pytest_mock import MockerFixture

from biomarkers.sleep.figures import plot_venn_diagram


@pytest.fixture(name="proteins")
def input_proteins() -> dict:
    """Return a dictionary with set of significant acute and chronic proteins"""
    return {"acute": ["P1", "P2", "P3"], "chronic": ["P3", "P4", "P5"]}


def test_plot_venn_diagram(mocker: MockerFixture, proteins: dict):
    """Test plot_venn_diagram function"""
    mock_venn2 = mocker.patch("biomarkers.sleep.figures.venn2")
    mock_venn3 = mocker.patch("biomarkers.sleep.figures.venn3")
    mocker.patch("biomarkers.sleep.figures.plt.show")

    # With only one set
    proteins = {"acute": ["P1", "P2", "P3"]}
    with pytest.raises(ValueError):
        plot_venn_diagram(proteins)

    # With two sets
    proteins["chronic"] = ["P3", "P4", "P5"]
    plot_venn_diagram(proteins)
    mock_venn2.assert_called_once()

    # With wrong sets
    proteins["other"] = ["P7", "P8", "P9"]
    with pytest.raises(ValueError):
        plot_venn_diagram(proteins)
    proteins.pop("other")

    # With three sets
    proteins["sleep"] = ["P2", "P4", "P6"]
    plot_venn_diagram(proteins)
    mock_venn3.assert_called_once()
