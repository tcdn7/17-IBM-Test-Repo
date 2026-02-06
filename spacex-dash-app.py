# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),

        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id="site-dropdown",
            options=(
                [{"label": "All Sites", "value": "ALL"}]
                + [
                    {"label": site, "value": site}
                    for site in sorted(spacex_df["Launch Site"].unique())
                ]
            ),
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),
        html.Br(),

        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),

        html.P("Payload range (Kg):"),

        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload],
            marks={0: "0", 2500: "2500", 5000: "5000", 7500: "7500", 10000: "10000"},
        ),
        html.Br(),

        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        # For ALL sites: show total successful launches by site (sum of class==1)
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Successful Launches By Site",
        )
        return fig
    else:
        # For a specific site: show Success vs Failed counts
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        outcome_counts = (
            filtered_df["class"]
            .value_counts()
            .rename_axis("class")
            .reset_index(name="count")
        )
        outcome_counts["Outcome"] = outcome_counts["class"].map({1: "Success", 0: "Failed"})

        fig = px.pie(
            outcome_counts,
            values="count",
            names="Outcome",
            title=f"Total Success vs Failed Launches for site {entered_site}",
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs,
# `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low) & (spacex_df["Payload Mass (kg)"] <= high)
    ]

    if entered_site != "ALL":
        df = df[df["Launch Site"] == entered_site]

    title_site = "All Sites" if entered_site == "ALL" else entered_site
    fig = px.scatter(
        df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=f"Correlation between Payload and Success for {title_site}",
    )
    return fig

# Run the app
if __name__ == "__main__":
    app.run()
