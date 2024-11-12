from dash import Dash, dcc, html, Input, Output, State
import json
import pandas as pd
from pandas import date_range
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# Load activity data
with open('../../data/activities.json', 'r') as f:
    data = json.load(f)

# Convert JSON data to a pandas DataFrame
df = pd.DataFrame(data)

# Convert the 'startTimeLocal' column to datetime
df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

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
    print("Metric:", selected_metric)
    print("Date range:", start_date, "-", end_date)
    print("Goal value:", goal_value)
    # Set default goal value for initial load if goal_value is None
    if goal_value is None or n_clicks == 0:
        goal_value = 500  # Default goal for initial load

    # Convert start_date and end_date to datetime for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    print("Date range in data:", df['startTimeLocal'].min(), "-", df['startTimeLocal'].max())
    print("Selected date range:", start_date, "-", end_date)

    # Filter data by date range
    mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
    filtered_df = df.loc[mask]

    print("Filtered Data:", filtered_df)
    print("Calories data:", filtered_df['calories'])

    # Ensure we have a complete date range
    all_dates = pd.date_range(start=start_date, end=end_date)
    filtered_df = filtered_df.set_index('startTimeLocal').reindex(all_dates, fill_value=0).reset_index()
    filtered_df.rename(columns={'index': 'startTimeLocal'}, inplace=True)

    # Determine bar colors based on the goal
    # Determine bar colors based on the goal
    bar_colors = [
        'green' if value >= goal_value else 'red'
        for value in filtered_df[selected_metric]
    ]

    # Create figure with bars for actual values
    fig = go.Figure()

    filtered_df['startTimeLocal'] = pd.to_datetime(filtered_df['startTimeLocal'])

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

    fig.update_layout(
        title=f"{selected_metric.capitalize()} Over Time",
        xaxis_title="Date",
        yaxis_title=selected_metric.capitalize(),
        xaxis=dict(
            tickformat="%b %d",
            dtick="D1",
            tickangle=45,
            showgrid=True,
            gridcolor="lightgrey",
            range=[start_date, end_date]  # Explicitly set the date range for the x-axis
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="lightgrey"
        ),
        barmode='group'
    )

    return fig


# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
