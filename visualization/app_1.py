import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html
from plotly.subplots import make_subplots

# Example data (replace this with your real data)
df = pd.read_csv(
    "/Users/pujasaha/Desktop/Git_Oct1/proteomics/hyperparameters_tuning/alpha_0.04-0.07_l1_0.1-0.11/prot_processed.csv"
)  # update this
df_prediction = pd.read_csv(
    "/Users/pujasaha/Desktop/Git_Oct1/proteomics/hyperparameters_tuning/alpha_0.04-0.07_l1_0.1-0.11/data_testing_with_prediction_May8th_resample.csv"
)  # update thi
protein_cols = [col for col in df.columns if "-" in col]

studies = df["study"].unique().tolist()
# extract studied in test data
studies_pre = df_prediction["study"].unique().tolist()
subjects = df["subject"].unique().tolist()
fluids = df["fluid"].unique().tolist()
subject_testing = df_prediction["subject"].unique().tolist()

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Protein and Prediction Explorer"

# Layout with Tabs
app.layout = html.Div(
    [
        html.H1("Elastic Net Model Visualizations"),
        dcc.Tabs(
            id="tabs",
            value="tab-protein",
            children=[
                dcc.Tab(label="Protein, Sleep Debt vs Time", value="tab-protein"),
                dcc.Tab(label="Prediction vs True", value="tab-prediction"),
                dcc.Tab(label="Prediction and True vs Time", value="tab-time"),
            ],
        ),
        html.Div(id="tab-content"),
    ]
)


# Tab switch logic
@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_content(tab):
    if tab == "tab-protein":
        return html.Div(
            [
                html.Label("Select Study:"),
                dcc.Dropdown(
                    id="study-dropdown",
                    options=[{"label": s, "value": s} for s in studies],
                    value=studies[0],
                    style={"width": "400px"},
                ),
                html.Label("Select Subject:"),
                dcc.Dropdown(id="subject-dropdown", style={"width": "400px"}),
                html.Label("Select Protein:"),
                dcc.Dropdown(
                    id="protein-dropdown",
                    options=[{"label": p, "value": p} for p in protein_cols],
                    value=protein_cols[0],
                    style={"width": "400px"},
                ),
                dcc.Graph(id="protein-vs-sleep"),
                html.Label("Study Lookup for Selected Subject:"),
                html.Div(
                    id="study-lookup-result1",
                    style={"marginTop": "20px", "fontWeight": "bold"},
                ),
            ]
        )
    elif tab == "tab-prediction":
        return html.Div(
            [
                html.Label("Select Test Subject:"),
                dcc.Dropdown(
                    id="pred-subject-dropdown",
                    options=[{"label": "All", "value": "All"}]
                    + [{"label": s, "value": s} for s in subject_testing],
                    value="All",
                    style={"width": "400px"},
                ),
                html.Label("Select Fluid:"),
                dcc.Dropdown(
                    id="fluid-dropdown",
                    options=[{"label": f, "value": f} for f in fluids],
                    value=fluids[0],
                    style={"width": "400px"},
                ),
                dcc.Graph(id="prediction-vs-true"),
                dcc.Graph(id="relativeerror-vs-true"),
            ]
        )

    elif tab == "tab-time":
        return html.Div(
            [
                html.Label("Select Study:"),
                dcc.Dropdown(
                    id="pred-study-dropdown",
                    options=[{"label": s, "value": s} for s in studies_pre],
                    value=studies[0],
                    style={"width": "400px"},
                ),
                html.Label("Select Test Subject:"),
                dcc.Dropdown(id="pred-subject-dropdown", style={"width": "400px"}),
                html.Label("Select Fluid:"),
                dcc.Dropdown(
                    id="fluid-dropdown",
                    options=[{"label": f, "value": f} for f in fluids],
                    value=fluids[0],
                    style={"width": "400px"},
                ),
                dcc.Graph(id="predictionandtrue-vs-time"),
                html.Label("Study Lookup for Selected Subject:"),
                html.Div(
                    id="study-lookup-result2",
                    style={"marginTop": "20px", "fontWeight": "bold"},
                ),
            ]
        )


# Update subject dropdown based on selected study
@app.callback(
    Output("subject-dropdown", "options"),
    Output("subject-dropdown", "value"),
    Input("study-dropdown", "value"),
)
def update_subjects(study):
    filtered_subjects = sorted(df[df["study"] == study]["subject"].unique())
    options = [{"label": s, "value": s} for s in filtered_subjects]
    value = "All"
    return options, value


@app.callback(
    Output("pred-subject-dropdown", "options"),
    Output("pred-subject-dropdown", "value"),
    Input("pred-study-dropdown", "value"),
    State("pred-subject-dropdown", "value"),
)
def update_pred_subjects(study, current_subject):
    filtered_subjects = sorted(
        df_prediction[df_prediction["study"] == study]["subject"].unique()
    )

    options = [{"label": "All", "value": "All"}] + [
        {"label": s, "value": s} for s in filtered_subjects
    ]

    if current_subject in filtered_subjects or current_subject == "All":
        value = current_subject
    else:
        value = "All"
    return options, value


# Protein vs Sleep Debt plot
@app.callback(
    Output("protein-vs-sleep", "figure"),
    Output("study-lookup-result1", "children"),
    Input("study-dropdown", "value"),
    Input("protein-dropdown", "value"),
    Input("subject-dropdown", "value"),
)
def update_plot(study, protein_name, subject_id):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df_filtered = df[(df["subject"] == subject_id) & (df["study"] == study)]

    time = df_filtered["mins_from_admission"]

    fig.add_trace(
        go.Scatter(
            x=(time - 15840) / (60 * 24),  # replace with your actual time column
            y=df_filtered[protein_name],
            mode="markers",
            name=f"{protein_name} (Subject {subject_id})",
            marker=dict(size=7),
        ),
        secondary_y=False,
    )
    fig.update_yaxes(showgrid=False, secondary_y=False)
    # Y2: sleep debt
    fig.add_trace(
        go.Scatter(
            x=(time - 15840) / (60 * 24),
            y=df_filtered["s_debt"],
            mode="markers",
            name=f"Sleep Debt (Subject {subject_id})",
            marker=dict(size=6, symbol="diamond"),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(showgrid=False, secondary_y=True)
    """
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
    """
    # Update layout
    fig.update_layout(
        title=f"{protein_name} & Sleep Debt Over Time (Subject {subject_id})",
        xaxis_title="Time",
    )

    fig.update_yaxes(title_text="Protein Expression", secondary_y=False)
    fig.update_yaxes(title_text="Sleep Debt", secondary_y=True)

    # Lookup study
    study = df_filtered[df_filtered["subject"] == subject_id]["study"].unique()
    if len(study) == 0:
        study_text = f"No study found for subject {subject_id}."
    else:
        study_text = f"Subject {subject_id} belongs to: {', '.join(study)}"

    return fig, study_text


# Prediction vs True plot
@app.callback(
    Output("prediction-vs-true", "figure"),
    Output("relativeerror-vs-true", "figure"),
    Input("pred-subject-dropdown", "value"),
    Input("fluid-dropdown", "value"),
)
def update_prediction_plot(pred_subject, fluid_type):
    # Filter data based on selected subject and fluid
    fig1 = go.Figure()
    fig2 = go.Figure()
    if pred_subject == "All":

        for sid in df_prediction["subject"].unique():
            df_s = df_prediction[df_prediction["subject"] == sid]
            df_s = df_s[df_s["fluid"] == fluid_type]
            true_values = df_s["true"]

            predictions = df_s["predicted"]
            relative_error = df_s["relative_error"]

            fig1.add_trace(
                go.Scatter(
                    x=true_values,
                    y=predictions,
                    mode="markers",
                    name=f"Subject {sid}",
                    marker=dict(size=7),
                    legendgroup=str(sid),
                    showlegend=True,
                )
            )
            fig2.add_trace(
                go.Scatter(
                    x=true_values,
                    y=relative_error,
                    mode="markers",
                    name=f"Subject {sid}",
                    marker=dict(size=7),
                    legendgroup=str(sid),
                    showlegend=True,
                )
            )

        fig1.add_trace(
            go.Scatter(
                x=[-0.1, 0.6],
                y=[-0.1, 0.6],
                mode="lines",
                line=dict(color="black", dash="dash"),
                name="Perfect Prediction",
            )
        )

    else:
        # Filter for the chosen subject
        df_pred = df_prediction[
            (df_prediction["subject"] == pred_subject)
            & (df_prediction["fluid"] == fluid_type)
        ]
        # Filter for the chosen subject

        true_values = df_pred["true"]

        predictions = df_pred["predicted"]
        relative_error = df_pred["relative_error"]

        # Scatter plot for Prediction vs True
        fig1.add_trace(
            go.Scatter(
                x=true_values,
                y=predictions,
                mode="markers",
                marker=dict(size=8),
                name="Predictions",
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=true_values,
                y=relative_error,
                mode="markers",
                marker=dict(size=8),
                name="Predictions",
            )
        )

        # Add a 45-degree reference line for perfect prediction
        min_val = min(true_values.min(), predictions.min())
        max_val = max(true_values.max(), predictions.max())
        fig1.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode="lines",
                line=dict(color="black", dash="dash"),
                name="Perfect Prediction",
            )
        )

    fig1.update_layout(
        title=f"Prediction vs True ( Fluid: {fluid_type})",
        xaxis_title="True Value",
        yaxis_title="Predicted Value",
        height=500,
    )
    fig2.update_layout(
        title=f"relative error vs True ( Fluid: {fluid_type})",
        xaxis_title="True Value",
        yaxis_title="relative error",
        height=500,
    )

    return fig1, fig2


# Prediction vs True plot
@app.callback(
    Output("predictionandtrue-vs-time", "figure"),
    Output("study-lookup-result2", "children"),
    Input("pred-study-dropdown", "value"),
    Input("pred-subject-dropdown", "value"),
    Input("fluid-dropdown", "value"),
    prevent_initial_call=True,
)
def update_time_plot(study, pred_subject, fluid_type):
    """
    Update the prediction plot based on selected subject and fluid type.
    """
    # Filter data based on selected subject and fluid

    fig3 = go.Figure()

    if pred_subject == "All":
        df_study = df_prediction[df_prediction["study"] == study]
        for sid in df_study["subject"].unique():
            df_s = df_study[df_study["subject"] == sid]
            df_s = df_s[df_s["fluid"] == fluid_type]
            true_values = df_s["true"]
            predictions = df_s["predicted"]
            time = df_s["mins_from_admission"]

            fig3.add_trace(
                go.Scatter(
                    x=(time - 15840) / (60 * 24),
                    y=predictions,
                    mode="markers",
                    name=f"Subject {sid}",
                    marker=dict(size=7),
                    legendgroup=str(sid),
                    showlegend=True,
                )
            )
            fig3.add_trace(
                go.Scatter(
                    x=(time - 15840) / (60 * 24),
                    y=true_values,  # or any second y variable
                    mode="lines+markers",
                    name=f"Subject {sid} True",
                    marker=dict(size=7),
                    legendgroup=str(sid),
                    showlegend=True,
                )
            )
        fig3.update_layout(
            title=f"Prediction vs Time All subjects in {study}",
            xaxis_title="Time in days",
            yaxis_title="prediction",
            height=500,
        )

    else:

        # Filter for the chosen subject
        df_pred = df_prediction[
            (df_prediction["subject"] == pred_subject)
            & (df_prediction["fluid"] == fluid_type)
            & (df_prediction["study"] == study)
        ]
        # Filter for the chosen subject

        true_values = df_pred["true"]

        predictions = df_pred["predicted"]
        time = df_pred["mins_from_admission"]

        fig3.add_trace(
            go.Scatter(
                x=(time - 15840) / (60 * 24),
                y=predictions,
                mode="markers",
                name="prediction",
                marker=dict(size=7, color="green", symbol="circle"),
            )
        )
        # Plot y2
        fig3.add_trace(
            go.Scatter(
                x=(time - 15840) / (60 * 24),
                y=true_values,  # or any second y variable
                mode="markers",
                name="True",
                marker=dict(size=7, color="green", symbol="square"),
            )
        )

        fig3.update_layout(
            title=f"Prediction and True vs Time ( Fluid: {fluid_type})",
            xaxis_title="Time in days",
            yaxis_title="Values",
            height=500,
        )

    # Lookup study
    study = df_prediction[df_prediction["subject"] == pred_subject]["study"].unique()
    if len(study) == 0:
        study_text = f"No study found for subject {pred_subject}."
    else:
        study_text = f"Subject {pred_subject} belongs to: {', '.join(study)}"

    return fig3, study_text


if __name__ == "__main__":
    app.run(debug=True)
