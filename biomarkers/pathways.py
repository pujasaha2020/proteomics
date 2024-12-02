"""This module contains functions to run pathway analysis"""

import pandas as pd
from gprofiler import GProfiler

# Initialize g:Profiler
gp = GProfiler(return_dataframe=True)


def run_pathway_analysis(
    genes: dict[str, list[str]], background: list[str], max_pvalue
) -> pd.DataFrame:
    """Run pathway analysis on the candidate genes"""
    # Run pathway analysis
    enrichment_results = gp.profile(
        organism="hsapiens",  # Human
        query=genes,
        significance_threshold_method="fdr",
        user_threshold=max_pvalue,
        background=background,
        sources=["GO:BP", "GO:MF", "GO:CC"],  # "REAC", "KEGG"],
        # use only GO:BP,
        # GO:CC , GO:MF : molecular function with up and down regulated,
        # plot for all pathways up and down regulated
    )
    return enrichment_results
