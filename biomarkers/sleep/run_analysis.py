"""Run LME model: log(protein) ~ 1 + acute + chronic + sleep + (1 |subject)"""

import argparse
import time
from pathlib import Path

import pandas as pd
from tqdm.contrib.concurrent import process_map

from biomarkers.pathways import run_pathway_analysis
from biomarkers.sleep.steps import postprocess_results, preprocess_data, run_lme_sleep
from utils.get import get_aptamers, get_box, get_debt, get_proteomics
from utils.save import save_to_csv


def process_results(result: pd.DataFrame) -> pd.DataFrame:
    """Process the results of the LME models"""

    first_3cols = result.columns.get_level_values(0).str.contains("Unnamed")
    df_not_first_3cols = result.loc[:, ~first_3cols]
    df_not_first_3cols = df_not_first_3cols.drop(df_not_first_3cols.index[0])
    df_not_first_3cols.reset_index(drop=True, inplace=True)
    df_first3 = result.loc[:, first_3cols]
    df_first3.columns = df_first3.iloc[0]
    df_first3 = df_first3.drop(df_first3.index[0])
    df_first3 = df_first3.reset_index(drop=True)
    multi_level_columns = [
        ("ids", "seq_id"),
        ("ids", "protein"),
        ("ids", "gene"),
    ]
    df_first3.columns = pd.MultiIndex.from_tuples(multi_level_columns)
    result = pd.concat([df_first3, df_not_first_3cols], axis=1)

    return result


def rerun_sleep_analysis(
    path: Path, plot: bool, min_group_size: int, max_pvalue: float, debt_model: str
):
    """Rerun the mixed model analysis with significant proteins from the first run"""

    box = get_box()
    file = box.get_file(path)
    result = pd.read_csv(file, header=[0, 1], low_memory=False)
    result = process_results(result)

    sig_proteins = result.loc[
        (result["acute"]["pvalue_fdr"] < 0.05 or result["chronic"]["param"] > 0),
        :,
    ]
    proteins_up = sig_proteins.loc[
        (sig_proteins["acute"]["param"] > 0 or sig_proteins["chronic"]["param"] > 0),
        ("ids", "seq_id"),
    ]
    proteins_down = sig_proteins.loc[
        (sig_proteins["acute"]["param"] < 0 or sig_proteins["chronic"]["param"] < 0),
        ("ids", "seq_id"),
    ]
    df = get_proteomics(box)
    selected_columns = pd.IndexSlice["proteins", proteins_up]

    df_up = df.loc[:, selected_columns]
    selected_columns = pd.IndexSlice["proteins", proteins_down]
    df_down = df.loc[:, selected_columns]

    debts = get_debt(box)
    aptamers = get_aptamers(box)
    t.append(time.time())
    print(f"Data loaded in {t[-1] - t[-2]:.2f} seconds")

    # Process data
    print("Preprocessing  up regulated protein data...")
    data = preprocess_data(
        df_up,
        debts,
        min_group_size,
        plot,
        debt_model,
    )
    t.append(time.time())
    print(f"Data preprocessed in {t[-1] - t[-2]:.2f} seconds")

    # Run the LME models
    print("Running LME models...")
    results = process_map(run_lme_sleep, data.values(), chunksize=10)
    results = pd.DataFrame.from_records(results, index=data.keys())
    results.columns = pd.MultiIndex.from_tuples(results.columns)
    t.append(time.time())
    print(f"LME models run in {t[-1] - t[-2]:.2f} seconds")

    # Postprocess the results
    print("Postprocessing results...")
    results = postprocess_results(results, aptamers, max_pvalue, plot)
    t.append(time.time())
    print(f"Results postprocessed in {t[-1] - t[-2]:.2f} seconds")

    return df


def run_sleep_analysis(
    path: Path, plot: bool, min_group_size: int, max_pvalue: float, debt_model: str
) -> pd.DataFrame:
    """Identify sleep biomarker with linear mixed effect models"""

    print(80 * "=")
    print("Running sleep analysis")
    print(80 * "=")

    # Get data
    print("Getting data...")
    t = [time.time()]
    box = get_box()
    df = get_proteomics(box)
    debts = get_debt(box)
    aptamers = get_aptamers(box)
    t.append(time.time())
    print(f"Data loaded in {t[-1] - t[-2]:.2f} seconds")

    # Process data
    print("Preprocessing data...")
    data = preprocess_data(
        df,
        debts,
        min_group_size,
        plot,
        debt_model,
    )
    t.append(time.time())
    print(f"Data preprocessed in {t[-1] - t[-2]:.2f} seconds")

    # Run the LME models
    print("Running LME models...")
    results = process_map(run_lme_sleep, data.values(), chunksize=10)
    results = pd.DataFrame.from_records(results, index=data.keys())
    results.columns = pd.MultiIndex.from_tuples(results.columns)
    t.append(time.time())
    print(f"LME models run in {t[-1] - t[-2]:.2f} seconds")

    # Postprocess the results
    print("Postprocessing results...")
    results = postprocess_results(results, aptamers, max_pvalue, plot)
    t.append(time.time())
    print(f"Results postprocessed in {t[-1] - t[-2]:.2f} seconds")

    # Run the pathway analysis
    print("Running pathway analysis...")
    genes = {}
    for key in ["acute", "chronic", "sleep"]:
        sig = df[(key, "pvalue_fdr")] < max_pvalue
        genes[key] = list(results[sig].index.get_level_values("gene"))
    background = results.index.get_level_values("gene")
    pathways = run_pathway_analysis(genes, background, max_pvalue)
    t.append(time.time())
    print(f"Pathway analysis done in {t[-1] - t[-2]:.2f} seconds")

    # Save the results
    if path.suffix:
        print(f"Saving results to {path}...")
        save_to_csv(box, results, path, index=True)
        pathway_path = path.parent / f"{path.stem}_pathways.csv"
        save_to_csv(box, pathways, pathway_path)
        t.append(time.time())
        print(f"Results saved in {t[-1] - t[-2]:.2f} seconds")

    # rerun the mixed effect model with the significant proteins in "Acute" and "Chronic" groups
    results = rerun_sleep_analysis(path, df, min_group_size, max_pvalue)

    t.append(time.time())
    print(80 * "=")
    print(f"Sleep analysis done in {t[-1] - t[0]:.2f} seconds")
    print(80 * "=")
    return results


if __name__ == "__main__":

    # Parse the arguments
    parser = argparse.ArgumentParser(description="Run sleep biomarker analysis.")
    parser.add_argument(
        "--path",  # proteomics/results/sleepdebt/sleepdebt_biomarker
        type=str,
        default="",
        help="Path where results are saved. If not specified, nothing is saved.",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot several figures.",
    )
    parser.add_argument(
        "--min_group_size",
        type=int,
        default=6,
        help="Minimum group size to included in the analysis. (see figures)",
    )
    parser.add_argument(
        "--max_pvalue",
        type=float,
        default=0.05,
        help="Maximum p-value to consider a protein significant. (see figures)",
    )
    parser.add_argument(
        "--debt_model",
        type=str,
        default="adenosine",
        help="Model to run. (see figures)",
    )

    args = parser.parse_args()
    args.path = Path(args.path)
    run_sleep_analysis(**vars(args))
