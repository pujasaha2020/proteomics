# this model is used to predict sleep debt from proteomics data useing
# Bayesian hierarchical modeling using subject and subject-protein specific random effects

import argparse
from collections import Counter
from pathlib import Path

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm
import seaborn as sns
from sklearn.metrics import root_mean_squared_error
from sklearn.preprocessing import StandardScaler

from box.manager import BoxManager
from utils.get import get_aptamers, get_box, get_debt, get_proteomics
from utils.process import (
    bridge_v40_to_v41,
    drop_high_cv_proteins,
    drop_proteins_with_missing_samples,
    drop_samples_without_proteins,
    log_normalize_proteins,
    optimize_full_dataset,
)


def get_common_proteins_en():
    """
    get common proteins from the Elastic Net model
    """
    sig_proteins_list = []
    for i in range(1, 5):
        significant_proteins = pd.read_csv(f"coef_fold_{i}.csv", index_col=0)

        sig_proteins_list.append(
            significant_proteins["Feature"].tolist()
        )  # Append the list of significant proteins to the list

    sig_proteins_list = [
        protein for sublist in sig_proteins_list for protein in sublist
    ]

    # Count occurrences
    protein_counts = Counter(sig_proteins_list)

    # Get proteins that appear more than once
    repeated_proteins = [
        protein for protein, count in protein_counts.items() if count > 2
    ]

    return repeated_proteins


def do_normalization(data, repeated_proteins):
    """
    Normalize the data
    """
    # Step 1: Identify protein columns
    protein_cols = repeated_proteins

    # Step 2: Define function to scale within a group
    def scale_group(group):
        scaler = StandardScaler()
        group[protein_cols] = scaler.fit_transform(group[protein_cols])
        return group

    # Step 3: Apply the scaling group-wise
    data_scaled = data.groupby("fluid", group_keys=False).apply(
        scale_group, include_groups=False
    )

    return data_scaled


def bayesian_model_random_subject(data_training_scaled, repeated_proteins, model):
    """
    Bayesian hierarchical model with random intercepts for subjects
    """
    with pm.Model() as _:

        if model == "subject_protein":
            df = prepare_X_matrix(data_training_scaled, repeated_proteins, model)
            X = df[repeated_proteins].values
            y = df["s_debt"].values

        else:
            # Prepare the X matrix
            X = data_training_scaled[repeated_proteins].values
            y = data_training_scaled["s_debt"].values

        z_matrix, pair_idx, pair_key = prepare_Z_matrix(
            data_training_scaled, repeated_proteins, model
        )
        # subject_idx, subjects = pd.factorize(data_training_scaled["subject"])
        # n_subjects = len(subjects_idx.unique())

        # Priors for fixed effects
        beta = pm.Normal("beta", mu=0, sigma=1, shape=X.shape[1])
        intercept = pm.Normal("intercept", mu=0, sigma=5)

        # Feature-based mean for random effects
        # Let’s assume one intercept per subject, predicted from their protein values (z)

        if model == "subject_protein":
            gamma = pm.Normal("gamma", mu=0, sigma=1, shape=z_matrix.shape[1])
            u_mean = pm.math.dot(z_matrix, gamma)

            # Random intercepts, centered around predicted means
            tau = pm.HalfNormal("tau", sigma=1)
            u_raw = pm.Normal("u_raw", mu=0, sigma=1, shape=z_matrix.shape[0])
            u = pm.Deterministic("u", u_mean + u_raw * tau)
            # Model error
            sigma = pm.HalfNormal("sigma", sigma=1)

        else:
            n_subjects = len(pair_key)
            gamma = pm.Normal("gamma", mu=0, sigma=1, shape=X.shape[1])
            u_mean = pm.math.dot(z_matrix, gamma)

            # Random intercepts, centered around predicted means
            tau = pm.HalfNormal("tau", sigma=1)
            u_raw = pm.Normal("u_raw", mu=0, sigma=1, shape=n_subjects)
            u = pm.Deterministic("u", u_mean + u_raw * tau)
            # Model error
            sigma = pm.HalfNormal("sigma", sigma=1)

        # Expected value per observation

        mu = intercept + pm.math.dot(X, beta) + u[pair_idx]

        # Likelihood
        y_obs = pm.StudentT("y_obs", nu=3, mu=mu, sigma=sigma, observed=y)

        trace = pm.sample(1000, tune=2000, target_accept=0.95, max_treedepth=15)

    return trace


def prepare_Z_matrix(data, repeated_proteins, model):
    """
    Prepare the Z matrix for the random effects
    """

    if model == "subject_protein":
        data = prepare_X_matrix(data, repeated_proteins, model)
        subject_protein_df = data[["subject", "target_protein"]].drop_duplicates()
        # Create string labels like "subjectA_proteinX"
        pair_labels = (
            data[["subject", "target_protein"]].astype(str).agg("_".join, axis=1)
        )
        pair_idx, pair_keys = pd.factorize(pair_labels)
        # n_pair = subject_protein_df.shape[0]
        features = []
        for i, row in subject_protein_df.iterrows():
            s = row["subject"]
            p = row["target_protein"]

            # Example: take the mean expression of this protein for this subject
            sub_data = data[(data["subject"] == s)]
            mean_expr = sub_data[p].mean()

            features.append([mean_expr])  # Can add more features here

        z_matrix = np.array(features)

    else:
        pair_idx, pair_keys = pd.factorize(data["subject"])
        n_subjects = len(pair_keys)

        z_matrix = np.zeros((n_subjects, data[repeated_proteins].shape[1]))
        for i, s in enumerate(pair_keys):
            z_matrix[i] = data[data["subject"] == s][repeated_proteins].mean().values

    return z_matrix, pair_idx, pair_keys


def prepare_X_matrix(data, repeated_proteins, model):
    """
    Prepare the X matrix for the fixed effects
    """

    if model == "subject_protein":
        # Create a long-format version with one row per (subject, protein, time), keeping all features
        df = data.loc[data.index.repeat(len(repeated_proteins))].copy()
        # Reset the index
        df.reset_index(drop=True, inplace=True)
        df["target_protein"] = repeated_proteins * len(data)

        # Extract expression of the target protein as the "local" expression
        for prot in repeated_proteins:
            df.loc[df["target_protein"] == prot, "local_expression"] = df[prot]

    return df


def make_predictions(trace, data_testing_scaled, repeated_proteins, model):
    """
    Make predictions using the trained model
    """
    if model == "subject_protein":
        df = prepare_X_matrix(data_testing_scaled, repeated_proteins, model)
        X_new = df[repeated_proteins].values
        y_new = df["s_debt"].values

    else:
        # Prepare the X matrix
        X_new = data_testing_scaled[repeated_proteins].values
        y_new = data_testing_scaled["s_debt"].values

    z_matrix_new, pair_idx, pair = prepare_Z_matrix(
        data_testing_scaled, repeated_proteins, model
    )

    # Extract posterior samples
    posterior = trace.posterior

    beta_samples = (
        posterior["beta"].stack(draws=("chain", "draw")).values
    )  # shape: [n_features, n_samples]
    gamma_samples = posterior["gamma"].stack(draws=("chain", "draw")).values
    intercept_samples = posterior["intercept"].stack(draws=("chain", "draw")).values
    sigma_samples = posterior["sigma"].stack(draws=("chain", "draw")).values

    print("beta_samples shape:", beta_samples.shape)
    print("gamma_samples shape:", gamma_samples.shape)
    print("intercept_samples shape:", intercept_samples.shape)
    print("sigma_samples shape:", sigma_samples.shape)
    print("x_new shape:", X_new.shape)
    print("z_new shape:", z_matrix_new.shape)

    # Compute predicted random effect mean: u_pred = z_new @ gamma
    u_pred_samples = np.dot(
        z_matrix_new, gamma_samples
    )  # shape: [n_samples, n_subjects]

    # Compute fixed effect contribution: x_new @ beta
    fixed_pred_samples = np.dot(X_new, beta_samples)  # shape: [n_features, n_samples]
    intercept_samples = intercept_samples[:, np.newaxis]  # shape: (4000, 1)

    print("fixed_pred_samples shape:", fixed_pred_samples.shape)
    print("u_pred_samples shape:", u_pred_samples.shape)
    print("intercept_samples shape:", intercept_samples.shape)
    # Final prediction: intercept + fixed + random effect

    # Transpose to (n_samples, n_obs)
    fixed_pred_samples = fixed_pred_samples.T  # (4000, 309)
    u_pred_samples = u_pred_samples.T  # (4000, 37)

    # Index u for each row in X_test
    u_aligned = u_pred_samples[:, pair_idx]  # (4000, 309)
    y_pred_samples = intercept_samples + fixed_pred_samples + u_aligned
    print("y_pred_samples shape:", y_pred_samples.shape)

    # Summarize
    mean_pred = np.mean(y_pred_samples, axis=0)
    print("mean_pred shape:", mean_pred.shape)
    print("subject", pair.shape)
    print("target", y_new.shape)
    print("mins_from_admission", data_testing_scaled["mins_from_admission"].shape)

    df_pred = pd.DataFrame(
        {
            "subject_id": df["subject"],
            "predicted_sleep_debt": mean_pred,
            "true": y_new,
            "mins_from_admission": df["mins_from_admission"],
            # "lower_bound": ci_lower,
            # "upper_bound": ci_upper,
        }
    )

    df_pred.to_csv(
        f"/Users/pujasaha/Desktop/Git_Oct1/proteomics/BLM_result/df_pred_{model}.csv"
    )
    if model == "subject_protein":
        df_pred.drop_duplicates(
            subset=["subject_id", "true", "mins_from_admission"],
            inplace=True,
        )
        df_pred = df_pred.reset_index(drop=True)
    # print(f"Predicted sleep debt: {mean_pred:.2f}")
    # print(f"95% credible interval: [{ci_lower:.2f}, {ci_upper:.2f}]")
    return df_pred


def evaluate_model(df_pred, plot, model):
    """
    Evaluate the model"""

    rmse = root_mean_squared_error(df_pred["true"], df_pred["predicted_sleep_debt"])
    print(f"RMSE: {rmse:.2f}")

    rel_error = np.abs(
        (df_pred["predicted_sleep_debt"] - df_pred["true"]) / df_pred["true"]
    )
    print(f"Relative error: {np.mean(rel_error):.2f}")
    if plot:
        plot_true_predicted(df_pred, model)
        plot_time_debt(df_pred, model)


def plot_true_predicted(df_pred, model):
    """Plot true vs predicted sleep debt"""
    plt.figure(figsize=(6, 6))
    sns.lineplot(
        x=df_pred["mins_from_admission"],
        y=df_pred["predicted_sleep_debt"],
        hue=df_pred["subject_id"],
        data=df_pred,
    )

    plt.xlabel("Time")
    plt.ylabel("Predicted (mean)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        f"/Users/pujasaha/Desktop/Git_Oct1/proteomics/BLM_result/true_vs_predicted_sleep_debt_{model}.png"
    )

    plt.show()


def plot_time_debt(df_pred, model):
    """Plot sleep debt over time"""
    plt.figure(figsize=(10, 6))
    plt.plot(
        df_pred["mins_from_admission"],
        df_pred["true"],
        label="True",
        marker="o",
    )
    plt.plot(
        df_pred["mins_from_admission"],
        df_pred["predicted_sleep_debt"],
        label="Prediction",
        marker="x",
    )
    plt.title("True vs Prediction Over Time for ")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"/Users/pujasaha/Desktop/Git_Oct1/proteomics/BLM_result/time_trueandpred_{model}.png"
    )

    plt.show()


def prepare_data_model(
    prot: pd.DataFrame,
    debt: pd.DataFrame,
    aptamers: pd.DataFrame,
    min_proteins: int = 4000,
):
    """Prepare dataset, encode the target, and extract the fluid list"""
    # before going into too much detail, remove "mppg_fd" Forced Desynchrony samples
    sizes = [(19634, 4979)]
    print(prot.columns)

    print("shape before preprocessing:", prot.shape)
    print("Preprocessing data...")
    # not needed as I am working with selected biomarkers
    optimize_full_dataset(prot, sizes=sizes, min_proteins=min_proteins)
    print("shape before preprocessing:", prot.shape)

    drop_high_cv_proteins(prot, aptamers)
    print("shape before preprocessing:", prot.shape)

    bridge_v40_to_v41(prot, aptamers)
    print("shape before preprocessing:", prot.shape)

    drop_proteins_with_missing_samples(prot)
    print("shape before preprocessing:", prot.shape)

    log_normalize_proteins(prot)

    # Ensure type compatibility for the subject column
    prot[("ids", "subject")] = prot[("ids", "subject")].astype(str)

    # reset the index
    prot.reset_index(drop=True, inplace=True)

    print("Proteomics data shape before merging debt:", prot.shape)

    # Drop rows with missing values in the target column
    # prot_preprocessed = prot.dropna(subset=[("infos", "state")])

    debt_copy = debt[["ids", "unified", "profile"]].copy()
    debt_copy = debt_copy.droplevel(0, axis=1)
    prot = prot.droplevel(0, axis=1)

    df_final = pd.merge(
        prot,
        debt_copy[
            ["sample_id", "chronic", "acute", "l_debt", "s_debt", "mins_from_admission"]
        ],
        on="sample_id",
        how="inner",
    )

    print("Proteomics data shape after merging debt:", df_final.shape)

    # df_final["total_debt"] = df_final["chronic"] + df_final["acute"]

    # Define the "proteins" columns to keep for the prediction
    biomarkers = [col for col in df_final.columns if "-" in col]

    cols = biomarkers + [
        "fluid",
        "subject",
        "study",
        "sample_id",
        "s_debt",
        "mins_from_admission",
    ]
    full_data = df_final[cols].copy()

    # cgecking NaN in features
    print("shape of features:", full_data.shape)

    return full_data


def main(model: str, protocols: list, train: list, test: list, plot: bool):
    box = get_box()
    # get the common proteins from the Elastic Net model
    repeated_proteins = get_common_proteins_en()
    print("repeated proteins:", len(repeated_proteins))
    # get the proteomics data
    proteomics = get_proteomics(box)

    # get the sleep debt data
    sleep_debt = get_debt(box)

    # get the aptamers data
    aptamers = get_aptamers(box)

    # prepare the data for modeling
    data = prepare_data_model(proteomics, sleep_debt, aptamers, min_proteins=4000)

    print(f"Analysis data shape: {data.shape}")

    # select the data from the selected protocols
    data = data[data["study"].isin(protocols)]

    train_data = data[data["study"].isin(train)]
    test_data = data[data["study"].isin(test)]

    # normalize the data
    data_training_scaled = do_normalization(train_data, repeated_proteins)
    data_testing_scaled = do_normalization(test_data, repeated_proteins)
    print("shape of training data:", data_training_scaled.shape)
    print("shape of testing data:", data_testing_scaled.shape)
    # prepare the training and testing data
    # train_data, test_data = prepare_training_testing_data(data)

    # prepare the prior distributions
    trace = bayesian_model_random_subject(
        data_training_scaled, repeated_proteins, model
    )

    # make predictions
    df_pred = make_predictions(
        trace,
        data_testing_scaled,
        repeated_proteins,
        model,
    )

    # evaluate the model
    evaluate_model(df_pred, plot, model)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="plot sleep debt data.")
    parser.add_argument(
        "--model",
        type=str,
        help="model to run random subject or random subject-protein",
        default="subject",
    )

    parser.add_argument(
        "--protocols",
        nargs="+",
        help="list of protocols to plot",
        type=str,
        default=["mri", "5day_bsl", "5day_cr", "5day_reco"],
    )

    parser.add_argument(
        "--train",
        nargs="+",
        help="which protocol to train on",
        type=str,
        default=["mri"],
    )

    parser.add_argument(
        "--test",
        nargs="+",
        help="which protocol to test on",
        type=str,
        default=["5day_bsl", "5day_cr", "5day_reco"],
    )

    parser.add_argument(
        "--plot",
        type=bool,
        help="whether to plot the results",
        default=True,
    )

    args = parser.parse_args()

    # run the main function
    main(**vars(args))
