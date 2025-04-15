import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html

# ---- Load your data ----
# This should be replaced with your actual data loading
# For example:
# df = pd.read_csv("your_data.csv")
# Must include: 'subject_id', 'sleep_debt', 'protein_1', ..., 'protein_1000'
# Example:
# df = pd.read_csv("sleep_proteins.csv")
df = pd.read_csv(
    "/Users/pujasaha/Desktop/Git_Oct1/proteomics/hyperparameters_tuning/alpha_0.04-0.07_l1_0.1-0.11/prot_processed.csv"
)  # update this
df_pred = pd.read_csv(
    "/Users/pujasaha/Desktop/Git_Oct1/proteomics/hyperparameters_tuning/alpha_0.04-0.07_l1_0.1-0.11/data_testing.csv"
)  # update this
protein_cols = [col for col in df.columns if "-" in col]
subject_training = sorted(df["subject"].unique().tolist())
subject_testing = sorted(df_pred["subject"].unique().tolist())

fluid_types = sorted(df_pred["fluid"].unique().tolist())

# ---- Initialize app ----
app = dash.Dash(__name__)
app.title = "Sleep Debt & Protein Explorer"

# ---- Layout ----
app.layout = html.Div(
    [
        html.H1("Protein Expression and Prediction Explorer"),
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Protein Expression vs Sleep Debt"),
                        html.Label("Select Protein:"),
                        dcc.Dropdown(
                            id="protein-dropdown",
                            options=[{"label": p, "value": p} for p in protein_cols],
                            value=protein_cols[0],
                            style={"width": "400px"},
                        ),
                        html.Label("Select Subject:"),
                        dcc.Dropdown(
                            id="subject-dropdown",
                            options=[{"label": "All", "value": "All"}]
                            + [{"label": s, "value": s} for s in subject_training],
                            value="All",
                            style={"width": "400px"},
                        ),
                        dcc.Graph(id="protein-vs-sleep"),
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "vertical-align": "top",
                    },
                ),
                html.Div(
                    [
                        html.H3("Prediction vs True"),
                        html.Label("Select plasma:"),
                        dcc.Dropdown(
                            id="fluid-dropdown",
                            options=[{"label": f, "value": f} for f in fluid_types],
                            value=fluid_types[0],
                            style={"width": "400px"},
                        ),
                        dcc.Graph(id="prediction-vs-true"),
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "vertical-align": "top",
                        "margin-left": "4%",
                    },
                ),
            ]
        ),
    ]
)


# ---- Callback ----
@app.callback(
    Output("protein-vs-sleep", "figure"),
    Input("protein-dropdown", "value"),
    Input("subject-dropdown", "value"),
)
def update_plot(protein_name, subject_id):
    if subject_id == "All":
        df_filtered = df.copy()
    else:
        df_filtered = df[df["subject"] == subject_id]

    x = df_filtered["total_debt"]
    y = df_filtered[protein_name]

    fig = go.Figure()

    # Scatter
    fig.add_trace(
        go.Scatter(
            x=x, y=y, mode="markers", name="Data", marker=dict(size=8, color="blue")
        )
    )

    # Regression line using np.polyfit
    if len(x) >= 2 and not y.isnull().any():
        coeffs = np.polyfit(x, y, deg=1)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = np.polyval(coeffs, x_line)

        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                line=dict(color="red"),
                name="Linear Fit",
            )
        )

    fig.update_layout(
        title=f"{protein_name} vs Sleep Debt (Subject: {subject_id})",
        xaxis_title="Sleep Debt",
        yaxis_title="Protein Expression",
        height=500,
    )

    return fig


# ---- Callback for Prediction vs True Plot ----
@app.callback(
    Output("prediction-vs-true", "figure"),
    [Input("fluid-dropdown", "value")],
)
def update_prediction_plot(fluid_type):
    # Filter data based on selected subject and fluid
    """
    if pred_subject == "All":
        df_prediction = df_pred.copy()
    else:
        df_prediction = df_pred[df_pred["subject"] == pred_subject]
    """
    # Filter for the chosen fluid type
    df_prediction = df_pred.copy()
    df_prediction = df_prediction[df_prediction["fluid"] == fluid_type]

    # Assume that you have a column 'true_value' and that you can compute predictions on the fly.
    # For demonstration, we simulate predictions as follows:
    # Here we are just applying a simple transformation (for example purposes). Replace this with your model's predictions.
    if "true" in df_prediction.columns:
        true_values = df_prediction["true"]
    else:
        true_values = df_prediction["sleep_debt"]  # fallback example

    # Here a dummy prediction: For instance, assume predictions are true_value plus some noise.
    predictions = df_prediction["predicted"]

    fig = go.Figure()

    # Scatter plot for Prediction vs True
    fig.add_trace(
        go.Scatter(
            x=true_values,
            y=predictions,
            mode="markers",
            marker=dict(size=8, color="green"),
            name="Predictions",
        )
    )

    # Add a 45-degree reference line for perfect prediction
    min_val = min(true_values.min(), predictions.min())
    max_val = max(true_values.max(), predictions.max())
    fig.add_trace(
        go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            line=dict(color="black", dash="dash"),
            name="Perfect Prediction",
        )
    )

    fig.update_layout(
        title=f"Prediction vs True ( Fluid: {fluid_type})",
        xaxis_title="True Value",
        yaxis_title="Predicted Value",
        height=500,
    )
    return fig


# ---- Run app ----
if __name__ == "__main__":
    app.run(debug=True)
