"""Module providing a function to optimize hyperparameters"""

# cSpell: disable
import time
from pathlib import Path

# Core Libraries
# Plotting Libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore

# Machine Learning Libraries
import sklearn  # type: ignore
from sklearn.linear_model import ElasticNet, Ridge  # type: ignore
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV  # type: ignore
from sklearn.model_selection import cross_validate
from sklearn.pipeline import make_pipeline  # type: ignore
from sklearn.preprocessing import FunctionTransformer  # type: ignore

# Custom Libraries
from utils.accessory_functions import Params  # plot_cv_indices,
from utils.accessory_functions import (  # distribution_analysis,; na_analysis,; plot_study_characteristics,
    Config,
    OrderedGroupKFold,
    WeightedZScoreNormalizer,
    get_jobs,
    prepare_data_model,
    prepare_training_testing_data,
)
from utils.get import get_aptamers, get_box, get_debt, get_proteomics

# Steps :
# 1. Get the data
# 2. Preprocess and inspect the data
# 3. Run the model
# 4. Postprocess the results
# 5. Save the results


def plot_grid_heatmap(scores_matrix, cfg, combination_path):
    """Plot the heatmap of the hyperparameter tuning results."""
    plt.figure(figsize=(10, 8))
    sns.heatmap(scores_matrix, annot=True, fmt=".3f", cmap="viridis", cbar=True)
    plt.title("Hyperparameter Tuning Results")
    plt.xlabel("L1 Ratio")
    plt.ylabel("alpha Value")
    if cfg.save:
        plt.savefig(combination_path / "hyperparameter_tuning_heatmap.png")

    if cfg.plot:
        plt.show()


def plot_top_coefficients(top_coef_df, cfg, combination_path):
    """Plot the top 10 coefficients of the best model."""
    plt.figure(figsize=(10, 6))
    plt.barh(top_coef_df["Feature"].astype(str), top_coef_df["Coefficient"], color="b")
    plt.xlabel("Coefficient Value")
    plt.title("Top 10 Most Important Features in Logistic Regression")
    plt.gca().invert_yaxis()
    if cfg.plot:
        plt.show()
    if cfg.save:
        plt.savefig(combination_path / "best_model_coef.png")


def extract_top_coefficients(cv_results_zscore, data_training):
    """Extract the top coefficients from the best model in cross-validation results."""
    # Initialize variables to store the best model's coefficients
    best_score = -np.inf
    best_coef_df = None
    data_training = data_training.drop(columns=["fluid", "subject"], errors="ignore")

    # Loop over all estimators from the cross-validation results
    for i, model in enumerate(cv_results_zscore["estimator"]):
        # Access the logistic regression model from the pipeline
        lr_model = model.best_estimator_.named_steps["elasticnet"]

        non_zero_coefs = lr_model.coef_[lr_model.coef_ != 0]
        print(f"Fold {i+1}: {len(non_zero_coefs)} non-zero coefficients")
        # Calculate the score for the model to determine the best model
        current_score = model.best_score_

        # If the current model has the highest score, store its coefficients
        if current_score > best_score:
            best_score = current_score
            feature_names = data_training.columns
            coefficients = lr_model.coef_
            best_coef_df = pd.DataFrame(
                {"Feature": feature_names, "Coefficient": coefficients}
            )
            best_coef_df["Absolute Coefficient"] = best_coef_df["Coefficient"].abs()

    # Sort the coefficients and get the top 10 if best_coef_df is not None
    top_coef_df = best_coef_df.sort_values(
        by="Absolute Coefficient", ascending=False
    ).head(10)

    return best_coef_df, top_coef_df


def hyperparameters_tuning(
    path: Path = Path("hyperparameters_tuning"),
    parameters: Params = Params(),
    cfg: Config = Config(),
):
    """hyperparameter tuning for the Elastic Net model of sleep prediction.
    Config object is used to control the behavior of saving, plotting, and exploring.
    Parameters object is used to control the sizes, min_proteins, alphas, and l1_r."""

    # Create the base path if it doesn't exist
    path.mkdir(parents=True, exist_ok=True)

    # Create a unique directory name for each combination
    combination_path = (
        path
        / f"alpha_{parameters.alphas[0]}-{parameters.alphas[len(parameters.alphas)-1]}_l1_{parameters.l1_r[0]}-{parameters.l1_r[len(parameters.l1_r)-1]}"
    )
    combination_path.mkdir(parents=True, exist_ok=True)

    print(f"Running model for alpha={parameters.alphas}" f"l1={parameters.l1_r}")

    # 2 Preprocess and inspect the data
    #
    box = get_box()
    # get proteomics+other from box
    prot = get_proteomics(box)
    # get sleep debt from box
    debt = get_debt(box)
    # get aptamers from box
    aptamers = get_aptamers(box)

    # prepare data for the model evaluation and training
    full_dataset = prepare_data_model(
        prot,
        debt,
        aptamers,
        sizes=parameters.sizes,
        min_proteins=parameters.min_proteins,
    )

    # Save the preprocessed data to a CSV file
    full_dataset.to_csv(combination_path / "prot_processed.csv", index=False)
    # fig, ax = plt.subplots()
    """
    if cfg.explore:
        print("Missing Values Analysis")
        na_analysis(prot_preprocessed, cfg, combination_path)
        print("Distribution Analysis")
        distribution_analysis(prot_preprocessed, cfg, combination_path)
        print("Plotting Study Characteristics")
        plot_study_characteristics(prot_preprocessed, cfg, combination_path)
        print("Plotting CV Indices")
        # plot_cv_indices(
        #    parameters.method(n_splits=5), data_prot, target, group, study, n_splits=5
        # )
    """
    #  3 Run the model :

    # CV strategy: Stratified Group K Fold (Limited data + individual variations)
    # In each fold :
    #   Normalize protein expression based on a robust to outlier method: RobustScaler
    #   Train model (Elastic-Net) to predict the sleep status.

    print("Running Model...")

    # Split the data into training and testing sets
    # training will go in the pipeline
    # need more investigations how to choose the test set

    data_training, target_training, data_testing, target_testing, groups = (
        prepare_training_testing_data(full_dataset)
    )

    data_training.to_csv(combination_path / "data_training.csv", index=False)
    target_testing.to_csv(combination_path / "target_training.csv", index=False)
    data_testing.to_csv(combination_path / "data_testing.csv", index=False)
    target_testing.to_csv(combination_path / "target_testing.csv", index=False)

    data_training = data_training.drop(
        columns=["study", "sample_id", "s_debt", "mins_from_admission"], errors="ignore"
    )

    testing_info = data_testing[["study", "sample_id", "s_debt", "mins_from_admission"]]
    data_testing = data_testing.drop(
        columns=["study", "sample_id", "s_debt", "mins_from_admission"], errors="ignore"
    )

    # Enable the metadata routing
    sklearn.set_config(enable_metadata_routing=True)

    # Define a custom normalizer that takes the plasma and group into account.
    # Use weighted_zscore_normalization instead of zscore_normalization
    lr_zscore = make_pipeline(
        WeightedZScoreNormalizer(),
        ElasticNet(max_iter=8000),
    )

    cv_in = OrderedGroupKFold(n_splits=parameters.n_splits_in_out[0])
    cv_out = OrderedGroupKFold(n_splits=parameters.n_splits_in_out[1])
    # Define GridSearchCV with the weighted Z-score normalization
    grid_search_zscore = GridSearchCV(
        lr_zscore,
        param_grid={
            "elasticnet__alpha": parameters.alphas,
            "elasticnet__l1_ratio": parameters.l1_r,
        },
        cv=cv_in,  # Internal CV
        n_jobs=get_jobs(),
        scoring=parameters.scoring,
    )
    # Run nested cross-validation with weighted Z-score normalization
    cv_results_zscore = cross_validate(
        grid_search_zscore,
        data_training,
        target_training,
        cv=cv_out,  # Outer CV
        scoring=parameters.scoring,
        return_train_score=True,
        return_estimator=True,
        n_jobs=get_jobs(),
        error_score="raise",
        verbose=10,
        params={"groups": groups},
    )

    # 4 Postprocess the results
    # Assuming you have run cross-validation with return_estimator=True

    # Collect results from each GridSearchCV in the cross-validation
    mean_test_scores = [est.cv_results_ for est in cv_results_zscore["estimator"]][0][
        "mean_test_score"
    ]
    print(type(mean_test_scores))
    print("Mean Test Scores from outer CV:", cv_results_zscore["test_score"])

    best_params_per_fold = [est.best_params_ for est in cv_results_zscore["estimator"]]
    print("Best Parameters per Fold:", best_params_per_fold)

    # evaluate model performance on unknown samples
    best_idx = np.argmax(cv_results_zscore["test_score"])
    best_model = cv_results_zscore["estimator"][best_idx]
    target_test_pred = best_model.predict(data_testing)

    mse = mean_squared_error(target_testing, target_test_pred)
    variance = np.var(target_testing, ddof=0)  # population variance
    relative_mse = mse / variance

    print("Mean Squared Error:", mse)
    print("Relative MSE:", relative_mse)

    print("Relative MSE:", relative_mse)

    relative_error = abs((target_testing - target_test_pred) / target_testing)
    print("Relative Error:", relative_error)

    print("mean Relative Error:", np.median(relative_error))

    data_testing["predicted"] = target_test_pred
    data_testing["relative_error"] = relative_error
    data_testing["true"] = target_testing

    data_testing_with_prediction = pd.concat([data_testing, testing_info], axis=1)

    # Reshape the mean test scores to match the grid structure
    scores_matrix = pd.DataFrame(
        mean_test_scores.reshape(
            len(
                parameters.alphas
                if isinstance(parameters.alphas, list)
                else [parameters.alphas]
            ),
            len(
                parameters.l1_r
                if isinstance(parameters.l1_r, list)
                else [parameters.l1_r]
            ),
        ),
        index=parameters.alphas,
        columns=parameters.l1_r,
    )

    # Plot the heatmap
    plot_grid_heatmap(scores_matrix, cfg, combination_path)

    # Call the function to extract top coefficients

    best_coef_df, top_coef_df = extract_top_coefficients(
        cv_results_zscore, data_training
    )

    # Call the function to plot the top coefficients
    plot_top_coefficients(top_coef_df, cfg, combination_path)

    # Save the results
    if cfg.save:
        pd.DataFrame(cv_results_zscore).to_csv(
            combination_path / "cv_results_zscore.csv"
        )
        scores_matrix.to_csv(combination_path / "scores_matrix.csv")
        pd.DataFrame(best_coef_df).to_csv(combination_path / "best_coef_df.csv")
        top_coef_df.to_csv(combination_path / "top_coef_df.csv")
        data_testing_with_prediction.to_csv(
            combination_path / "data_testing_with_prediction.csv", index=False
        )

    return cv_results_zscore, scores_matrix, best_coef_df, top_coef_df


if __name__ == "__main__":
    config = Config(save=True, plot=True, explore=False)

    params = Params(
        alphas=[round(x, 3) for x in np.linspace(0.04, 0.07, 20)],
        l1_r=[round(x, 3) for x in np.linspace(0.1, 0.11, 20)],
        n_splits_in_out=[3, 5],
        scoring="neg_mean_squared_error",
    )
    print(params.__dict__)
    # Uncomment the line below to run the hyperparameter tuning
    hyperparameters_tuning(cfg=config, parameters=params)
