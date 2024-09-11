"""Provides the steps to run the size analysis for the dataset"""

from pathlib import Path

import cvxpy as cp
import numpy as np

from box.manager import BoxManager
from utils.get import get_info_per_somalogic, get_proteomics


def prepare_size_data(box: BoxManager, path: Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Prepare the data for the size analysis
    - Load the data, assumes to have somalogic id columns
    - Info stores the proteins and the number of samples in each somalogic id
    - Presence[i][j] is 1 if somalogic id i has protein j and 0 otherwise
    - n_samples[i] is the number of samples in somalogic id i
    """
    # Load the data
    df = get_proteomics(box, path)
    proteins = df.proteins.columns.tolist()
    info = get_info_per_somalogic(df)

    # presence[i][j] is 1 if somalogic id i has protein j and 0 otherwise
    presence = np.zeros((len(info), len(proteins)))
    # n_samples[i] is the number of samples in somalogic id i
    n_samples = np.zeros(len(info))
    for i, soma_info in enumerate(info.values()):
        for p in soma_info["proteins"]:
            presence[i, proteins.index(p)] = 1
        n_samples[i] = soma_info["n_samples"]

    return presence, n_samples


def optimize_size(
    presence: np.ndarray, n_samples: np.ndarray, min_proteins: int
) -> tuple[int, np.ndarray, np.ndarray]:
    """
    Solve the MILP problem to optimize the dataset size
    - Maximize the number of samples
    - Ensure at least min_proteins proteins are present
    - Ensure no missing proteins in the selected samples
    """
    n_somalogic, n_proteins = presence.shape
    if not 0 <= min_proteins <= n_proteins:
        raise ValueError("Make sure 0 <= min_proteins <= n_proteins")
    # x_i is 1 if somalogic id i is in df and 0 otherwise
    x = cp.Variable(n_somalogic, boolean=True)
    # z_j is 1 if protein j is in df and 0 otherwise
    z = cp.Variable(n_proteins, boolean=True)
    # Maximize the number of samples in df
    objective = cp.Maximize(cp.sum(cp.multiply(n_samples, x)))
    # Ensure at least min_proteins elements in df
    constraints = [cp.sum(z) >= min_proteins]
    for j in range(n_proteins):
        # Ensure z[j] is 1 if all somalogic id selected have protein j
        constraints.append(z[j] >= 1 - (cp.sum(x - cp.multiply(presence[:, j], x))))
        for i in range(n_somalogic):
            # Ensure z[j] is 0 if somalogic i is selected in df but is missing protein j
            # Ensure x[i] is 0 if protein j is missing in somalogic i and selected in df
            if presence[i, j] == 0:
                constraints.append(z[j] + x[i] <= 1)
    # Define the problem
    problem = cp.Problem(objective, constraints)  # type: ignore
    # Solve the problem
    n = int(problem.solve(solver=cp.GLPK_MI))  # type: ignore
    return n, x.value, z.value
