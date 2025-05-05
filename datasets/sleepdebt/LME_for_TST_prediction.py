# THis scripts predicts TST for two subjects in FD where SP ends at 27th night


import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

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
    df = pd.DataFrame(
        {
            "subject": subject,
            "night": np.arange(1, len(mppg) + 1),
            "TST": mppg["Total Sleep Time (TST) mins RECALC"].astype(float),
        }
    )
    return df


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

df_all = pd.concat(
    [prepare_lme_data(subj) for subj in subjects_mppg_fd], ignore_index=True
)

# making training and prediction dataset
# Training data: all data from subjects with full 36 nights + first 27 nights from the incomplete subjects
# drop rows with missing values in TST
df_all = df_all.dropna(subset=["TST"])


# Prediction data: Nights 28–38 for the incomplete subjects
subjects = ["26P2HY83", "3536HY83"]
nights = np.arange(28, 37)
predict_df = pd.DataFrame(
    [(s, n) for s in subjects for n in nights], columns=["subject", "night"]
)

import statsmodels.formula.api as smf

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
