"""Solve MILP problems to optimize (n_samples, n_proteins)"""

import argparse
import time
from pathlib import Path

from tqdm import tqdm

from datasets.sizes.figures import plot_size_analysis
from datasets.sizes.steps import optimize_size, prepare_size_data
from utils.get import PATH, get_box
from utils.save import save_to_yaml


def run_size_analysis(path: Path, plot: bool) -> list[list[int]]:
    """Solve MILP problems to optimize (n_samples, n_proteins)"""

    print(80 * "=")
    print("Running size analysis")
    print(80 * "=")

    # Initialization
    print("Initialization...")
    t = [time.time()]
    box = get_box()
    presence, n_samples = prepare_size_data(box, path)
    min_proteins = 0
    total_proteins = presence.shape[1]
    size = []
    t.append(time.time())
    print(f"Initialization done in {t[-1] - t[-2]:.2f} seconds")

    # Increase the number of proteins required in the dataset
    pbar = tqdm(total=total_proteins, desc="Optimizing dataset's sizes")
    while min_proteins <= total_proteins:
        n, _, z = optimize_size(presence, n_samples, min_proteins)
        p = int(sum(z))
        size.append([n, p])
        pbar.update(p + 1 - min_proteins)
        # Next iteration
        min_proteins = p + 1

    # save the result as yaml
    print("Saving the results...")
    yaml_path = path.parent / f"size_{path.stem.split('_')[-2]}.yaml"
    save_to_yaml(box, {"n_samples, n_proteins": size}, yaml_path)
    t.append(time.time())
    print(f"Results saved in {t[-1] - t[-2]:.2f} seconds")

    # Plot the results
    if plot:
        plot_size_analysis(*map(list, zip(*size)))

    t.append(time.time())
    print(80 * "=")
    print(f"Size analysis done in {t[-1] - t[0]:.2f} seconds")
    print(80 * "=")
    return size


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Solve MILP problems to optimize (n_samples, n_proteins)"
    )
    parser.add_argument(
        "--path",
        type=str,
        nargs="?",
        help="Path to the proteomics dataset",
        default="archives/data/proteomics_071924_AS.csv",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot the results (n_samples, n_proteins).",
    )
    args = parser.parse_args()
    if args.path is None:
        args.path = PATH["proteomics"]
    else:
        args.path = Path(args.path)
    run_size_analysis(**vars(args))
