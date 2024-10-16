"""
This study compares the protein expression across four different groups
"study_plazzi_nt1" : narcolpesy type 1 ( with cataplexy)
"study_plazzi_nt2" : narcolpesy type 2 ( without cataplexy)
"study_plazzi_ih"  : idiopathic hypersomnia
"control"    : control group
"""

import argparse
from functools import partial
from pathlib import Path

import pandas as pd
from statsmodels.stats.multitest import multipletests  # type: ignore
from tqdm.contrib.concurrent import process_map

from biomarkers.plazzi.linear_regression import run_lm_sleep
from box.manager import BoxManager
from utils.get import get_box, get_proteomics
from utils.process import (
    drop_proteins_with_missing_samples,
    drop_proteins_without_samples,
    drop_samples_without_proteins,
    log_normalize_proteins,
)
from utils.save import save_to_csv

PATH = {
    "proteins": Path("archives/miscellenous/protein_names.csv"),
    "aptamers": Path("archives/data/aptamers.csv"),
    "plazzi_results": Path("results/plazzi_study/"),
}


def get_protein_names(box) -> pd.DataFrame:
    """Get the list of proteins"""
    file = box.get_file(PATH["proteins"])
    df_protein = pd.read_csv(file, low_memory=False)
    df_protein = df_protein.drop(df_protein.index[0:2])
    df_protein = df_protein.reset_index(drop=True)
    df_protein.rename(columns={"Unnamed: 0": "seq_id"}, inplace=True)
    df_protein = df_protein[["seq_id", "UniProt", "TargetFullName.1"]]
    multi_level_columns = [
        ("ids", "seq_id"),
        ("prot", "UniProt"),
        ("target", "TargetFullName"),
    ]
    df_protein.columns = pd.MultiIndex.from_tuples(multi_level_columns)

    file = box.get_file(PATH["aptamers"])
    df_aptamers = pd.read_csv(file, low_memory=False)
    df_aptamers = df_aptamers[["SeqId", "Target Name"]]
    df_aptamers.rename(
        columns={"SeqId": "seq_id", "Target Name": "TargetName"}, inplace=True
    )
    multi_level_columns = [
        ("ids", "seq_id"),
        ("target", "TargetName"),
    ]
    df_aptamers.columns = pd.MultiIndex.from_tuples(multi_level_columns)

    df_protein = df_aptamers.merge(df_protein, on=[("ids", "seq_id")], how="left")

    return df_protein


def prepare_lm_data(protein: str, df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """Prepare the data for linear regression"""
    relevant_cols = [protein, "study"]
    data = df[relevant_cols].dropna(subset=relevant_cols, how="any")
    data.reset_index(drop=True, inplace=True)
    data.rename(columns={protein: "log_protein"}, inplace=True)
    return (protein, data)


def preprocess_sample(df_proteomics: pd.DataFrame) -> pd.DataFrame:
    """Get the data for the analysis"""
    studies = ["plazzi_nt2", "plazzi_ctl", "plazzi_ih", "plazzi_nt1"]
    df_study = df_proteomics.loc[df_proteomics["ids"]["study"].isin(studies), :]
    print("shape of study data after study selection", df_study.shape)
    drop_samples_without_proteins(df_study)
    print("shape after dropping samples without protein", df_study.shape)
    drop_proteins_without_samples(df_study)
    print("shape after dropping proteins without sample", df_study.shape)
    drop_proteins_with_missing_samples(df_study)
    print("shape after dropping proteins with any sample missing", df_study.shape)
    log_normalize_proteins(df_study)
    return df_study


def postprocess_results(
    box: BoxManager, results: pd.DataFrame, reference: str
) -> pd.DataFrame:
    """Postprocess the results"""
    results.columns = pd.MultiIndex.from_tuples(results.columns)
    for key in results.columns.levels[0]:
        if (key, "pvalue") in results.columns:
            results[(key, "pvalue_fdr")] = multipletests(
                results[(key, "pvalue")], alpha=0.05, method="fdr_bh"
            )[1]
    df_protein = get_protein_names(box)
    print(df_protein.head)
    results = results.merge(df_protein, on=[("ids", "seq_id")], how="left")

    # Reindex the columns to ensure the new columns are in the desired order
    new_columns = []
    for col in results.columns.levels[0]:
        for sub_col in results.columns.levels[1]:
            if (col, sub_col) in results.columns:
                new_columns.append((col, sub_col))

    results = results.reindex(columns=pd.MultiIndex.from_tuples(new_columns))

    results.insert(0, ("ids", "seq_id"), results.pop(("ids", "seq_id")))
    results.insert(1, ("prot", "UniProt"), results.pop(("prot", "UniProt")))
    results.insert(
        2, ("target", "TargetFullName"), results.pop(("target", "TargetFullName"))
    )
    results.insert(3, ("target", "TargetName"), results.pop(("target", "TargetName")))
    results.head()

    study_col = [
        col for col in results.columns.get_level_values(0) if col.startswith("study")
    ]
    result_by_group = {}
    for test_grp in [study for study in study_col if study != f"study_{reference}"]:
        result_by_group[test_grp] = compare_groups(results, test_grp)
    return result_by_group


def compare_groups(results: pd.DataFrame, test_grp: str) -> pd.DataFrame:
    """Compare the groups"""
    results.sort_values(by=[(test_grp, "pvalue_fdr")], inplace=True, ascending=True)
    results.reset_index(drop=True, inplace=True)
    results = results[["ids", "target", test_grp]]

    return results


def run_analysis(reference: str):
    """Run the analysis"""
    print("running analysis using reference:", reference)
    box = get_box()
    df_proteomics = get_proteomics(box)
    df_study = preprocess_sample(df_proteomics)
    print("shape of the final dataset for this study", df_study.shape)
    print("number of study", df_study[("ids", "study")].nunique())
    print("number of subjects", df_study[("ids", "subject")].nunique())
    print(
        "number of subjects per study",
        df_study.groupby([("ids", "study")]).nunique()[[("ids", "subject")]],
    )

    # get the protein columns only
    df_protein = df_study["proteins"]
    proteins = df_protein.columns
    df_study = df_study.droplevel(0, axis=1)

    print(proteins)
    dict_protein_data = dict(map(lambda p: prepare_lm_data(p, df_study), proteins))

    # Prepare a list of tuples with data and reference
    run_lm_sleep_with_ref = partial(run_lm_sleep, reference=reference)

    results = process_map(
        run_lm_sleep_with_ref,
        dict_protein_data.values(),
        dict_protein_data.keys(),
        chunksize=4,
    )
    results = pd.DataFrame.from_records(results)
    result_by_group = postprocess_results(box, results, reference)
    for key, value in result_by_group.items():
        save_to_csv(
            box,
            value,
            PATH["plazzi_results"] / f"biomarker_{key}_{reference}.csv",
            index=False,
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run Plazzi study.")
    # decide which group to use as reference:
    # "plazzi_nt1", "plazzi_nt2", "plazzi_ih", "plazzi_ctl"
    parser.add_argument(
        "--reference",
        type=str,
        help="group as reference",
        default="plazzi_ctl",
    )

    args = parser.parse_args()
    run_analysis(**vars(args))
