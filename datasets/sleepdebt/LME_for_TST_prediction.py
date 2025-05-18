# THis scripts predicts TST for two subjects in FD where SP ends at 27th night


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from patsy import dmatrix  # pylint: disable=no-name-in-module
from statsmodels.regression.mixed_linear_model import MixedLM

# preparing the dataset for the analysis


def prepare_lme_data(subject):
    """
    Prepare the dataset for the analysis.
    """
    # Load the data
    mppg = pd.read_excel(
        "/Users/pujasaha/Desktop/SleepDebt/TST_data_from_Jean/"
        + "MPPG_P1_Sleep_Analysis_03-19-19_for_Puja_2024-11-21.xlsx",
        sheet_name=subject,
    )

    # prepare dataframe
    data = pd.DataFrame(
        {
            "subject": subject,
            "night": np.arange(1, len(mppg) + 1),
            "TST": mppg["Total Sleep Time (TST) mins RECALC"].astype(float),
        }
    )
    return data


def plot_TST_night(df):
    """
    Plot TST vs night for the given dataframe.
    """
    # Basic line plot
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="night", y="TST", hue="subject", marker="o")

    plt.title("Sleep Duration Over Nights by Subject")
    plt.xlabel("Night")
    plt.ylabel("Sleep Duration (hours)")
    plt.legend(title="Subject", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("TST_over_nights.png")
    plt.show()


def predict_from_lme(df_all, predict_df):
    """
    Predict TST for the new nights using the LME model.
    """

    model = smf.mixedlm("TST ~ night", df_all, groups=df_all["subject"], re_formula="1")
    result = model.fit()
    print(result.summary())
    print(result.random_effects)

    # LME does not estimate the TST for new nights using the random effects for that subject,
    # only considers the fixed effects.
    # So manually extract the random effects for the subjects in the prediction dataset
    # and add them to the fixed effects to get the predicted TST for the new nights.

    # Extract fixed effects
    beta = result.fe_params  # contains 'Intercept' and 'night'
    # Subject-specific predictions
    predictions = []
    for subject in predict_df["subject"].unique():
        # Subject-specific data
        predict_df_sub = predict_df[predict_df["subject"] == subject].copy()
        nights = predict_df_sub["night"]

        # Get random effects (intercept and slope)
        re = result.random_effects[subject]
        print(beta["Intercept"], beta["night"], re["Group"])
        intercept = beta["Intercept"] + re["Group"]
        print(intercept)
        slope = beta["night"]
        print(slope)

        # Predicted TST = intercept + slope * night
        predict_df_sub["predicted_TST"] = intercept + (slope * nights)
        print(predict_df_sub["predicted_TST"])
        predictions.append(predict_df_sub)

    # Combine
    predict_df_with_re = pd.concat(predictions, ignore_index=True)
    print(predict_df_with_re)

    predict_df_with_re = predict_df_with_re.rename(columns={"predicted_TST": "TST"})
    df_new_all = pd.concat([df_all, predict_df_with_re], ignore_index=True)

    return df_new_all


def plot_spline(df_all, model_result):

    # Generate a smooth sequence of nights to plot the spline
    night_grid = pd.DataFrame(
        {"night": np.linspace(df["night"].min(), df["night"].max(), 100)}
    )

    # Create spline basis for the grid
    spline_basis = dmatrix(
        "bs(night, df=4, degree=3, include_intercept=False)",
        data=night_grid,
        return_type="dataframe",
    )
    fixed_pred = model_result.predict(exog=spline_basis)

    # Plot raw data
    plt.figure(figsize=(10, 6))
    plt.scatter(df_all["night"], df_all["TST"], alpha=0.4, label="Observed Data")

    # Plot spline fit
    plt.plot(
        night_grid["night"], fixed_pred, color="red", label="Spline Fit (Fixed Effects)"
    )

    plt.xlabel("Night")
    plt.ylabel("Sleep Duration (hrs)")
    plt.title("Spline Fit to Sleep Duration Over Nights (All Subjects)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("spline_fit.png")
    plt.show()


def predict_from_spline(df_all, predict_df):
    """
    Predict TST for the new nights using the spline model.
    """
    # Fit a spline model to the data
    # This is a placeholder for the actual spline fitting and prediction
    # You can use statsmodels or any other library to fit a spline model
    spline_basis = dmatrix(
        "bs(night, df=4, degree=3, include_intercept=False)",
        data=df_all,
        return_type="dataframe",
    )
    # Join the spline features to your original DataFrame
    df_spline = df_all.join(spline_basis)

    # Fit a mixed model: fixed effects = spline terms, random effects = subject intercept
    model = MixedLM(
        endog=df_spline["TST"],
        exog=df_spline[spline_basis.columns],
        groups=df_spline["subject"],
    )
    result = model.fit()
    print(result.summary())

    new_spline_basis = dmatrix(
        "bs(night, df=4, degree=3, include_intercept=False)",
        data=predict_df,
        return_type="dataframe",
    )

    # Predict using the fixed effects (excluding subject random effects)
    fixed_pred = result.predict(exog=new_spline_basis)
    print(fixed_pred)

    # plot_spline(df_all, result)

    predictions = []
    for subject in predict_df["subject"].unique():
        predict_df_sub = predict_df[predict_df["subject"] == subject].copy()

        # Get subject's random intercept
        random_intercept = result.random_effects[subject][
            0
        ]  # assuming only random intercept

        # Combine
        predict_df_sub["predicted_TST"] = fixed_pred + random_intercept

        print(predict_df_sub["predicted_TST"])
        predictions.append(predict_df_sub)

    # Combine
    predict_df_with_re = pd.concat(predictions, ignore_index=True)
    print(predict_df_with_re)

    predict_df_with_re = predict_df_with_re.rename(columns={"predicted_TST": "TST"})
    df_new_all = pd.concat([df_all, predict_df_with_re], ignore_index=True)
    print(df_new_all)
    return df_new_all


subjects_mppg_fd = [
    "3453HY73",
    "2056HY75",
    "3552HY62",
    "26P2HY83",  # SP27
    "3453HY52",
    "3536HY83",  # SP27
    "3536HY52",
    "3552HY73",
]

df = pd.concat([prepare_lme_data(subj) for subj in subjects_mppg_fd], ignore_index=True)

# making training and prediction dataset
# Training data: all data from subjects with full 36 nights + first 27 nights from the incomplete subjects
# drop rows with missing values in TST
df = df.dropna(subset=["TST"])


# Prediction data: Nights 28–38 for the incomplete subjects
subjects = ["26P2HY83", "3536HY83"]
nights_missing = np.arange(28, 37)
pre_df = pd.DataFrame(
    [(s, n) for s in subjects for n in nights_missing], columns=["subject", "night"]
)


# df_with_prediction = predict_from_lme(df, pre_df)
df_with_prediction = predict_from_spline(df, pre_df)

# Plotting the predicted TST
plot_TST_night(df_with_prediction)
"""
# plot predicted TST Vs true TST for different subjects
plt.figure(figsize=(10, 6))
plt.scatter(
    df_with_prediction["TST"],
    df_with_prediction["predicted_TST"],
    c="blue",
    marker="o",
    alpha=0.4,
    label="Predicted Data",
)
plt.plot(
    [df_with_prediction["TST"].min(), df_with_prediction["TST"].max()],
    [df_with_prediction["TST"].min(), df_with_prediction["TST"].max()],
    color="red",
    linestyle="--",
    label="Perfect Prediction",
)
plt.xlabel("True TST (hrs)")
plt.ylabel("Predicted TST (hrs)")
plt.title("Predicted vs True TST")
plt.legend()
plt.tight_layout()
plt.savefig("predicted_vs_true_TST.png")
plt.show()


# Save the predicted TST to a CSV file
# Plotting the predicted TST
plot_TST_night(df_with_prediction)
"""
