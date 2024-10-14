import pandas as pd
import statsmodels.api as sm


def run_lm_sleep(data: pd.DataFrame, protein: str, reference: str) -> dict:
    """Run a linear regression for a protein"""

    # place the group you want to make reference in the first position
    studies = list(data["study"].unique())
    studies.remove(reference)
    studies.insert(0, reference)
    data["study"] = pd.Categorical(data["study"], categories=studies, ordered=True)

    data = pd.get_dummies(data, columns=["study"], drop_first=True)
    for col in data.columns:
        if col.startswith("study"):
            data[col] = data[col].astype(int)
    y = data["log_protein"]
    x_matrix = data[[col for col in data.columns if col.startswith("study")]]
    x_matrix = sm.add_constant(x_matrix)
    model = sm.OLS(y, x_matrix).fit()

    results = {
        ("ids", "seq_id"): protein,
    }
    keys = ["const"] + [col for col in data.columns if col.startswith("study")]
    for key in keys:
        results[(key, "param")] = model.params[key]
        results[(key, "pvalue")] = model.pvalues[key]
    return results
