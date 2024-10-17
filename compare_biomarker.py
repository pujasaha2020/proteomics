# sleepdebt  biomarker from both models
from pathlib import Path

import pandas as pd

from utils.get import get_box
from utils.save import save_to_csv

PATH = {
    "adenosine_biomarker": Path(
        "results/sleepdebt/sleepdebt_biomarker/result_biomarker_Oct8th.csv"
    ),
    "unified_biomarker": Path(
        "results/sleepdebt/sleepdebt_biomarker/result_biomarker_Oct17th_Unified.csv"
    ),
    "proteins": Path("archives/miscellenous/protein_names.csv"),
    "aptamers": Path("archives/data/aptamers.csv"),
    "biomarker_results": Path("results/sleepdebt/sleepdebt_biomarker"),
}


def process_result(df: pd.DataFrame) -> pd.DataFrame:
    """Process the biomarker results"""
    first_3cols = df.columns.get_level_values(0).str.contains("Unnamed")
    df_not_first_3cols = df.loc[:, ~first_3cols]
    df_not_first_3cols = df_not_first_3cols.drop(df_not_first_3cols.index[0])
    df_not_first_3cols.reset_index(drop=True, inplace=True)
    df_first3 = df.loc[:, first_3cols]
    df_first3.columns = df_first3.iloc[0]
    df_first3 = df_first3.drop(df_first3.index[0])
    df_first3 = df_first3.reset_index(drop=True)
    multi_level_columns = [
        ("ids", "seq_id"),
        ("ids", "protein"),
        ("ids", "gene"),
    ]
    df_first3.columns = pd.MultiIndex.from_tuples(multi_level_columns)
    df_new = pd.concat([df_first3, df_not_first_3cols], axis=1)
    return df_new


def make_comparison(df1: pd.DataFrame, df2: pd.DataFrame):
    """Make comparison between the two biomarker results"""

    adenosine_protein = df1.loc[df1["acute"]["pvalue_fdr"] < 0.05, :][
        ["ids", "infos", "acute"]
    ]
    unified_protein = df2.loc[df2["acute"]["pvalue_fdr"] < 0.05, :][
        ["ids", "infos", "acute"]
    ]
    adenosine_protein = adenosine_protein.rename({"acute": "acute_adenosine"}, axis=1)
    unified_protein = unified_protein.rename({"acute": "acute_unified"}, axis=1)
    print("adenosine <0.05 selection acute ", adenosine_protein.shape)
    print("unified <0.05 selection acute", unified_protein.shape)

    common_seq_ids_acute = pd.merge(
        adenosine_protein,
        unified_protein,
        on=[("ids", "seq_id")],
    )
    print("common protein in acute", common_seq_ids_acute.shape)

    adenosine_protein = df1.loc[df1["chronic"]["pvalue_fdr"] < 0.05, :][
        ["ids", "infos", "chronic"]
    ]
    unified_protein = df2.loc[df2["chronic"]["pvalue_fdr"] < 0.05, :][
        ["ids", "infos", "chronic"]
    ]
    adenosine_protein = adenosine_protein.rename(
        {"chronic": "chronic_adenosine"}, axis=1
    )
    unified_protein = unified_protein.rename({"chronic": "chronic_unified"}, axis=1)
    print("adenosine <0.05 selection chronic ", adenosine_protein.shape)
    print("unified <0.05 selection chronic", unified_protein.shape)
    common_seq_ids_chronic = pd.merge(
        adenosine_protein,
        unified_protein,
        on=[("ids", "seq_id")],
    )
    print("common protein in chronic", common_seq_ids_chronic.shape)

    return common_seq_ids_acute, common_seq_ids_chronic


def get_protein_names(box1) -> pd.DataFrame:
    """Get the list of proteins"""
    file1 = box1.get_file(PATH["proteins"])
    df = pd.read_csv(file1, low_memory=False)
    df = df.drop(df.index[0:2])
    df = df.reset_index(drop=True)
    df.rename(columns={"Unnamed: 0": "seq_id"}, inplace=True)
    df = df[["seq_id", "UniProt", "TargetFullName.1"]]
    multi_level_columns = [
        ("ids", "seq_id"),
        ("prot", "UniProt"),
        ("target", "TargetFullName"),
    ]
    df.columns = pd.MultiIndex.from_tuples(multi_level_columns)

    file2 = box1.get_file(PATH["aptamers"])
    df_aptamers = pd.read_csv(file2, low_memory=False)
    df_aptamers = df_aptamers[["SeqId", "Target Name"]]
    df_aptamers.rename(
        columns={"SeqId": "seq_id", "Target Name": "TargetName"}, inplace=True
    )
    multi_level_columns = [
        ("ids", "seq_id"),
        ("target", "TargetName"),
    ]
    df_aptamers.columns = pd.MultiIndex.from_tuples(multi_level_columns)

    df = df_aptamers.merge(df, on=[("ids", "seq_id")], how="left")

    return df


if __name__ == "__main__":
    box = get_box()
    file = box.get_file(PATH["adenosine_biomarker"])
    df_adenosine = pd.read_csv(file, header=[0, 1], low_memory=False)
    df_adenosine = process_result(df_adenosine)
    print(df_adenosine.head())
    file = box.get_file(PATH["unified_biomarker"])

    df_unified = pd.read_csv(file, header=[0, 1], low_memory=False)
    df_unified = process_result(df_unified)
    print(df_unified.head())
    acute, chronic = make_comparison(df_adenosine, df_unified)
    df_protein = get_protein_names(box)

    acute = acute.merge(df_protein, on=[("ids", "seq_id")], how="left")
    chronic = chronic.merge(df_protein, on=[("ids", "seq_id")], how="left")
    print(acute.shape)
    print(chronic.shape)

    acute = acute[["ids", "target", "acute_adenosine", "acute_unified"]]
    chronic = chronic[["ids", "target", "chronic_adenosine", "chronic_unified"]]

    save_to_csv(
        box, acute, PATH["biomarker_results"] / "common_proteins_acute.csv", index=False
    )
    save_to_csv(
        box,
        chronic,
        PATH["biomarker_results"] / "common_proteins_chronic.csv",
        index=False,
    )
