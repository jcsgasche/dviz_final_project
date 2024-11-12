from dash import Dash, dcc, html, Input, Output, State
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Load activity data
with open('../../data/activities.json', 'r') as f:
    data = json.load(f)

# Convert JSON data to a pandas DataFrame
df = pd.DataFrame(data)

# Calculate the last full month’s date range
today = datetime.today()
first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
last_day_last_month = today.replace(day=1) - timedelta(days=1)

# Initialize Dash app
app = Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Interactive Fitness Activity Bar Chart"),

    # Dropdown for metric selection
    html.Label("Select Metric:"),
    dcc.Dropdown(
        id='metric-selector',
        options=[
            {'label': 'Calories', 'value': 'calories'},
            {'label': 'Steps', 'value': 'steps'},
            {'label': 'Duration', 'value': 'duration'}
        ],
        value='calories'
    ),

    # Date range picker with last full month as default
    html.Label("Select Time Frame:"),
    dcc.DatePickerRange(
        id='date-range',
        start_date=first_day_last_month.date(),
        end_date=last_day_last_month.date()
    ),

    # Input for goal setting
    html.Label("Set Goal Value:"),
    dcc.Input(id="goal-input", type="number", value=500, placeholder="Enter goal value"),
    html.Button("Set Goal", id="set-goal-button", n_clicks=0),

    # Graph for visualization
    dcc.Graph(id='line-chart')
])

# Callback to update chart with new goal
@app.callback(
    Output('line-chart', 'figure'),
    [Input('metric-selector', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('set-goal-button', 'n_clicks')],
    [State('goal-input', 'value')]
)
def update_chart(selected_metric, start_date, end_date, n_clicks, goal_value):
    # Set default goal value for initial load if goal_value is None
    if goal_value is None or n_clicks == 0:
        goal_value = 500  # Default goal for initial load

    # Filter data by date range
    mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
    filtered_df = df.loc[mask]

    # Determine bar colors based on the goal
    bar_colors = [
        'green' if value >= goal_value else 'red'
        for value in filtered_df[selected_metric]
    ]

    # Create figure with bars for actual values
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=filtered_df['startTimeLocal'],
        y=filtered_df[selected_metric],
        marker_color=bar_colors,
        name='Actual'
    ))

    # Add a line for the goal across the entire date range
    fig.add_trace(go.Scatter(
        x=[start_date, end_date],  # Ensure the goal line spans the full width
        y=[goal_value, goal_value],
        mode='lines',
        name='Goal',
        line=dict(color='blue', dash='dash')
    ))

    # Update layout with daily tick interval on x-axis
    fig.update_layout(
        title=f"{selected_metric.capitalize()} Over Time",
        xaxis_title="Date",
        yaxis_title=selected_metric.capitalize(),
        xaxis=dict(
            tickformat="%b %d",  # Format each tick as 'Nov 01'
            dtick="D1",          # Set tick spacing to every day
            tickangle=-45,       # Rotate date labels for clarity
            showgrid=True,       # Show vertical grid lines
            gridcolor="LightGray" # Set grid line color for better visibility
        ),
        yaxis=dict(
            showgrid=True          # Show horizontal grid lines
        ),
        bargap=0.1,               # Slight gap between bars
        barmode='group'
    )

    return fig


# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
