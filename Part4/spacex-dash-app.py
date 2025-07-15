# spacex-dash-app.py

import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Build list of launch sites for the dropdown
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site}
    for site in sorted(spacex_df['Launch Site'].unique())
]

# App layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True,
        style={'width': '80%', 'padding': '3px', 'margin': 'auto'}
    ),
    html.Br(),

    # Success pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'margin-left': '10%'}),
    # Payload range slider — track argument removed
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={
            int(min_payload): str(int(min_payload)),
            int((min_payload + max_payload) / 2): str(int((min_payload + max_payload) / 2)),
            int(max_payload): str(int(max_payload))
        },
        value=[min_payload, max_payload],
        tooltip={"placement": "bottom", "always_visible": True},
        updatemode='mouseup',
        allowCross=False,
        pushable=500
    ),

    html.Br(),
    # Payload vs. launch outcome scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# Callback to update pie chart based on selected site
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # All sites: count of successful launches per site
        df = spacex_df[spacex_df['class'] == 1]  # successes only
        fig = px.pie(
            df,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Single site: success vs. failed counts
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = df['class'].value_counts().rename(index={0: 'Failure', 1: 'Success'})
        fig = px.pie(
            names=outcome_counts.index,
            values=outcome_counts.values,
            title=f'Success vs. Failure for site {selected_site}'
        )
    return fig


# Callback to update scatter chart based on site and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # filter by payload mass
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    # further filter by site if not ALL
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    # scatter: payload vs. success, colored by booster version
    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload vs. Launch Outcome',
        labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'}
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
