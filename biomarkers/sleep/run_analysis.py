"""Run LME model: log(protein) ~ 1 + acute + chronic + sleep + (1 |subject)"""

import argparse
import time
from pathlib import Path

import pandas as pd
from tqdm.contrib.concurrent import process_map

from biomarkers.sleep.steps import postprocess_results, preprocess_data, run_lme_sleep
from utils.get import get_aptamers, get_box, get_debt, get_proteomics
from utils.save import save_to_csv


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

    # Save the results
    if path.suffix:
        print(f"Saving results to {path}...")
        save_to_csv(box, results, path, index=True)
        t.append(time.time())
        print(f"Results saved in {t[-1] - t[-2]:.2f} seconds")

    t.append(time.time())
    print(80 * "=")
    print(f"Sleep analysis done in {t[-1] - t[0]:.2f} seconds")
    print(80 * "=")
    return results


if __name__ == "__main__":

    # Parse the arguments
    parser = argparse.ArgumentParser(description="Run sleep biomarker analysis.")
    parser.add_argument(
        "--path",
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
