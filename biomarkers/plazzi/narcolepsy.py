"""
This study compares the protein expression across four different groups
"study_plazzi_nt1" : narcolpesy type 1 ( with cataplexy)
"study_plazzi_nt2" : narcolpesy type 2 ( without cataplexy)
"study_plazzi_ih"  : idiopathic hypersomnia
"control"    : control group
"""

import argparse
import io
from functools import partial
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.multitest import multipletests  # type: ignore
from tqdm.contrib.concurrent import process_map

from biomarkers.plazzi.figures import plot_box, plot_count, plot_density
from biomarkers.plazzi.linear_regression import (
    MSL_protein_with_no_nt1,
    MSL_protein_with_nt1,
    SOREM_protein_with_no_nt1,
    SOREM_protein_with_nt1,
    run_lm_sleep,
)
from box.manager import BoxManager
from utils.get import get_box
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


############## DO NOT USE THIS FUNCTION for GWAS PCA ######################
def prepare_pca_data(df: pd.DataFrame, protein: str, pc_comp: int) -> pd.DataFrame:
    """Prepare the data for PCA of proteins"""
    proteins_columns = df.filter(like="-").columns
    columns_to_drop = df.columns.difference(proteins_columns)
    columns_to_drop = [protein, *columns_to_drop]

    x_data = df.drop(
        columns_to_drop, axis=1
    ).dropna()  # Features (protein expressions, without the
    # protein of interest), rows with missing values are removed

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_data)
    pca = PCA(n_components=pc_comp)  # We want to reduce to 4 dimensions
    pcs = pca.fit_transform(x_scaled)
    explained_variance = pca.explained_variance_ratio_

    pcs_df = pd.DataFrame(
        data=pcs, columns=[f"PC{i}" for i in range(1, pc_comp + 1)], index=x_data.index
    )
    df_with_pcs = df.merge(pcs_df, left_index=True, right_index=True, how="left")
    dict_pcs_variance = dict(
        zip([f"PC{i}" for i in range(1, pc_comp + 1)], explained_variance)
    )
    return (dict_pcs_variance, df_with_pcs)


###########################################################
def prepare_lm_data(
    protein: str, df: pd.DataFrame, pc_comp: int
) -> tuple[str, pd.DataFrame]:
    """Prepare the data for linear regression"""
    # dict_pcs_variance, df = prepare_pca_data(df, protein, pc_comp)
    # pcs = [f"PC{i}" for i in range(1, pc_comp + 1)]
    relevant_cols = [protein, "study", "Age", "Gender", "BMI", "MSL", "#SOREM"] + [
        col for col in df.columns if col.startswith("PC")
    ][0:pc_comp]

    data = df[relevant_cols].dropna(subset=relevant_cols, how="any")
    data.reset_index(drop=True, inplace=True)
    data.rename(columns={protein: "log_protein"}, inplace=True)
    return (protein, data)


def preprocess_sample(
    df_proteomics: pd.DataFrame, box: BoxManager, plot: bool
) -> pd.DataFrame:
    """Get the data for the analysis"""
    studies = ["plazzi_nt2", "plazzi_ctl", "plazzi_ih", "plazzi_nt1", "plazzi_seds"]
    print(df_proteomics[("ids", "study")].unique())
    df_study = df_proteomics.loc[df_proteomics["ids"]["study"].isin(studies), :]
    print("shape of study data after study selection", df_study.shape)
    drop_samples_without_proteins(df_study)
    print("shape after dropping samples without protein", df_study.shape)
    drop_proteins_without_samples(df_study)
    print("shape after dropping proteins without sample", df_study.shape)
    drop_proteins_with_missing_samples(df_study)
    print("shape after dropping proteins with any sample missing", df_study.shape)
    # log_normalize_proteins(df_study)
    if plot:
        # plot the variables in different groups
        density = plot_density(["Age", "BMI"], df_study)
        file = io.BytesIO()
        density.savefig(file)
        file.seek(0)
        box.save_file(file, PATH["plazzi_results"] / "variables_density.png")
        boxplot = plot_box(["Age", "BMI"], df_study)
        file = io.BytesIO()
        boxplot.savefig(file)
        file.seek(0)
        box.save_file(file, PATH["plazzi_results"] / "variables_box.png")
        countplot = plot_count("Gender", df_study)
        file = io.BytesIO()
        countplot.savefig(file)
        file.seek(0)
        box.save_file(file, PATH["plazzi_results"] / "variables_count.png")

    return df_study


def postprocess_results(box: BoxManager, results: pd.DataFrame, reference: str) -> dict:
    """Postprocess the results"""
    results.columns = pd.MultiIndex.from_tuples(results.columns)
    for key in results.columns.levels[0]:
        if (key, "pvalue") in results.columns:
            results[(key, "pvalue_fdr")] = multipletests(
                results[(key, "pvalue")], alpha=0.05, method="fdr_bh"
            )[1]
    df_protein = get_protein_names(box)
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
    desired_columns = [
        "ids",
        "target",
        "prot",
        test_grp,
        "Age",
        "Gender",
        "BMI",
        "PC1",
        "PC2",
        "PC3",
        "PC4",
        "PC5",
    ]

    # Keep only the columns that exist in the DataFrame
    columns_to_use = [col for col in desired_columns if col in results.columns]

    #   Subset the DataFrame
    results = results[columns_to_use]
    return results


def plot_significant_proteins(
    box: BoxManager,
    result_by_group: dict,
    dict_protein_data: dict,
):
    """make box plot the significant proteins"""
    df_protein = get_protein_names(box)

    sig_proteins = []
    for key, value in result_by_group.items():
        seq_id = value.loc[value[(key, "pvalue_fdr")] < 0.05, ("ids", "seq_id")]
        sig_proteins.extend(seq_id)
        print(f"No of significant proteins for {key}  is {len(seq_id)}")

    # remove duplicates
    sig_proteins = list(set(sig_proteins))
    print("number of significant proteins", len(sig_proteins))
    # how many plots to make
    if len(sig_proteins) / 4 == 0:
        no_canvas = len(sig_proteins) // 4
    else:
        no_canvas = len(sig_proteins) // 4 + 1

    for i in range(no_canvas):
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = np.array(axes)
        remove_protein = []
        for j, protein in enumerate(sig_proteins):
            print(protein)
            remove_protein.append(protein)
            data = dict_protein_data[protein]
            sns.boxplot(x="study", y="log_protein", data=data, ax=axes[j // 2, j % 2])

            axes[j // 2, j % 2].set_title(
                df_protein.loc[
                    df_protein["ids"]["seq_id"] == protein, ("target", "TargetName")
                ].values[0]
            )
            if j == 3:
                plt.tight_layout()
                file = io.BytesIO()
                fig.savefig(file)
                box.save_file(
                    file, PATH["plazzi_results"] / f"significant_proteins_{i}.png"
                )
                file.seek(0)
                sig_proteins = [x for x in sig_proteins if x not in remove_protein]
                break


def run_analysis(
    reference: str,
    plot: bool,
    pc_comp: int,
    merge: bool,
) -> None:
    """Run the analysis"""
    print("running analysis using reference:", reference)
    box = get_box()
    dtype = {
        ("ids", "study"): str,
        ("ids", "subject"): str,
        ("ids", "experiment"): str,
        ("ids", "sample_id"): str,
        ("ids", "somalogic"): str,
        ("ids_1", "BMI"): float,
        ("ids_1", "Age"): float,
        ("ids_1", "Gender"): str,
        ("latency", "MSL"): float,
        ("latency", "#SOREM"): float,
    }
    df_proteomics = pd.read_csv(
        "/Users/pujasaha/Desktop/Narcolepsy/GWAS_PCA_proteomics.csv",
        header=[0, 1],
        dtype=dtype,
        low_memory=False,
    )
    df_study = preprocess_sample(df_proteomics, box, plot)
    print("shape of the final dataset for this study", df_study.shape)
    print("number of study", df_study[("ids", "study")].nunique())
    print("number of subjects", df_study[("ids", "subject")].nunique())
    print(
        "number of subjects per study",
        df_study.groupby([("ids", "study")]).nunique()[[("ids", "subject")]],
    )

    # get the protein columns only

    proteins = df_study.proteins.columns
    df_study = df_study.droplevel(0, axis=1)

    # impute "Age, "Gender" and "BMI" with mean of the group
    df_study["Age"] = df_study.groupby("study")["Age"].transform(
        lambda x: x.fillna(x.mean())
    )
    print(df_study.loc[df_study["study"] == "plazzi_nt1", ["Gender"]])
    print(df_study["sample_id"].dtypes)
    gender_dict = {
        "19678": "M",
        "19681": "M",
        "19667": "M",
        "19708": "M",
        # "20133": "M",
        "DbID11461": "M",
        "21-405": "F",
        "18665": "F",
    }
    df_study["Gender"] = df_study["Gender"].fillna(
        df_study["sample_id"].astype(str).map(gender_dict)
    )

    print(df_study.loc[df_study["study"] == "plazzi_nt1", ["Gender"]])

    df_study["BMI"] = df_study.groupby("study")["BMI"].transform(
        lambda x: x.fillna(x.mean())
    )
    df_study["Gender"] = df_study["Gender"].map({"M": 1, "F": 0})

    # replace Nan in MSL and SOREM with
    df_study["#SOREM"] = df_study.groupby("study")["#SOREM"].transform(
        lambda x: x.fillna(x.median())
    )

    # replace MSL with median of the group
    df_study["MSL"] = df_study.groupby("study")["MSL"].transform(
        lambda x: x.fillna(x.median())
    )

    dict_protein_data = dict(
        map(lambda p: prepare_lm_data(p, df_study, pc_comp), proteins)
    )
    print("number of proteins", dict(list(dict_protein_data.items())[:3]))
    """
    # Prepare a list of tuples with data and reference
    run_lm_sleep_with_ref = partial(run_lm_sleep, reference=reference, merge=merge)

    results = process_map(
        run_lm_sleep_with_ref,
        dict_protein_data.values(),
        dict_protein_data.keys(),
        chunksize=4,
    )
    results = pd.DataFrame.from_records(results)
    result_by_group = postprocess_results(box, results, reference)
    for test_grp, value in result_by_group.items():
        save_to_csv(
            box,
            value,
            PATH["plazzi_results"]
            / f"biomarker_{test_grp}_{reference}_adjusted_for_GWAS_pca.csv",
            index=False,
        )

    """

    results_MSL_protein = process_map(
        MSL_protein_with_nt1,
        dict_protein_data.values(),
        dict_protein_data.keys(),
        chunksize=4,
    )
    results_MSL_protein = pd.DataFrame.from_records(results_MSL_protein)
    results_MSL_protein.columns = pd.MultiIndex.from_tuples(results_MSL_protein.columns)
    # result_by_group = postprocess_results(box, results_MSL_protein, reference)
    save_to_csv(
        box,
        results_MSL_protein,
        PATH["plazzi_results"]
        / "biomarker_with_nt1_MSL_protein_correlation_adjusted_for_GWAS_pca.csv",
        index=False,
    )

    results_MSL_protein = process_map(
        MSL_protein_with_no_nt1,
        dict_protein_data.values(),
        dict_protein_data.keys(),
        chunksize=4,
    )
    results_MSL_protein = pd.DataFrame.from_records(results_MSL_protein)
    results_MSL_protein.columns = pd.MultiIndex.from_tuples(results_MSL_protein.columns)

    # result_by_group = postprocess_results(box, results_MSL_protein, reference)
    save_to_csv(
        box,
        results_MSL_protein,
        PATH["plazzi_results"]
        / "biomarker_Nont1_MSL_protein_correlation_adjusted_for_GWAS_pca.csv",
        index=False,
    )
    results_SOREM_protein = process_map(
        SOREM_protein_with_nt1,
        dict_protein_data.values(),
        dict_protein_data.keys(),
        chunksize=4,
    )
    results_SOREM_protein = pd.DataFrame.from_records(results_SOREM_protein)
    results_SOREM_protein.columns = pd.MultiIndex.from_tuples(
        results_SOREM_protein.columns
    )
    # result_by_group = postprocess_results(box, results_SOREM_protein, reference)
    save_to_csv(
        box,
        results_SOREM_protein,
        PATH["plazzi_results"]
        / "biomarker_with_nt1_SOREM_protein_correlation_adjusted_for_GWAS_pca.csv",
        index=False,
    )

    results_SOREM_protein = process_map(
        SOREM_protein_with_no_nt1,
        dict_protein_data.values(),
        dict_protein_data.keys(),
        chunksize=4,
    )
    results_SOREM_protein = pd.DataFrame.from_records(results_SOREM_protein)
    results_SOREM_protein.columns = pd.MultiIndex.from_tuples(
        results_SOREM_protein.columns
    )
    # result_by_group = postprocess_results(box, results_SOREM_protein, reference)
    save_to_csv(
        box,
        results_SOREM_protein,
        PATH["plazzi_results"]
        / "biomarker_with_Nont1_SOREM_protein_correlation_adjusted_for_GWAS_pca.csv",
        index=False,
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run Plazzi study.")
    # decide which group to use as reference:
    # "plazzi_nt1", "plazzi_nt2", "plazzi_ih", "plazzi_sih", "plazzi_ctl"
    parser.add_argument(
        "--reference",
        type=str,
        help="group as reference",
        default="plazzi_ctl",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="plot the significant proteins, nothing will be plotted if False",
    )
    parser.add_argument(
        "--pc_comp",
        type=int,
        help="number of pca components of GWAS to use",
        default=5,
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="merge all groups except reference.",
    )

    args = parser.parse_args()
    run_analysis(**vars(args))
