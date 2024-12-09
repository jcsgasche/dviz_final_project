# modules/charts/barchart.py
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import dash
import json

def get_default_goals():
    """Return default goals for each metric"""
    return {
        'calories': 500,
        'steps': 10000,
        'duration': 60,  # minutes
        'averageHR': 140,
        'maxHR': 180,
        'aerobicTrainingEffect': 3,
        'anaerobicTrainingEffect': 1,
        'distance': 5,  # km
        'averageSpeed': 10,  # km/h
        'maxSpeed': 15,  # km/h
        'movingDuration': 45,  # minutes
        'moderateIntensityMinutes': 30,
        'vigorousIntensityMinutes': 20,
        'elevationGain': 100,  # meters
        'elevationLoss': 100,  # meters
        'maxElevation': 500,  # meters
        'totalSets': 15,
        'totalReps': 150,
        'activeSets': 15,
        'waterEstimated': 500,  # ml
        'minTemperature': 15,  # °C
        'maxTemperature': 25,  # °C
    }

def create_barchart_layout(first_day_last_month, last_day_last_month):
    return html.Div([

        html.H1("Goal/Reached Dashboard"),

        create_metric_controls(first_day_last_month, last_day_last_month),
        dcc.Graph(id="activity-graph"),

        # Store components for data persistence
        dcc.Store(id='stored-data'),
        dcc.Store(id='stored-goals', data=get_default_goals()),

        # Goals management section
        html.Div([
            html.H3("Metric Goals", style={'marginTop': '20px'}),
            html.Div(id='current-goals-display'),  # Will be populated with current goals
            html.Button("Reset Goals to Default", id='reset-goals-button', n_clicks=0)
        ])
    ])

METRIC_OPTIONS = [
    {'label': 'Active Sets', 'value': 'activeSets'},
    {'label': 'Aerobic Training Effect', 'value': 'aerobicTrainingEffect'},
    {'label': 'Anaerobic Training Effect', 'value': 'anaerobicTrainingEffect'},
    {'label': 'Average Heart Rate', 'value': 'averageHR'},
    {'label': 'Average Speed', 'value': 'averageSpeed'},
    {'label': 'Calories', 'value': 'calories'},
    {'label': 'Distance (km)', 'value': 'distance'},
    {'label': 'Duration (minutes)', 'value': 'duration'},
    {'label': 'Elevation Gain', 'value': 'elevationGain'},
    {'label': 'Elevation Loss', 'value': 'elevationLoss'},
    {'label': 'Max Elevation', 'value': 'maxElevation'},
    {'label': 'Max Heart Rate', 'value': 'maxHR'},
    {'label': 'Max Speed', 'value': 'maxSpeed'},
    {'label': 'Max Temperature', 'value': 'maxTemperature'},
    {'label': 'Min Temperature', 'value': 'minTemperature'},
    {'label': 'Moderate Intensity Minutes', 'value': 'moderateIntensityMinutes'},
    {'label': 'Moving Duration', 'value': 'movingDuration'},
    {'label': 'Steps', 'value': 'steps'},
    {'label': 'Total Reps', 'value': 'totalReps'},
    {'label': 'Total Sets', 'value': 'totalSets'},
    {'label': 'Vigorous Intensity Minutes', 'value': 'vigorousIntensityMinutes'},
    {'label': 'Water Loss (ml)', 'value': 'waterEstimated'},
]

# Sort METRIC_OPTIONS by label
METRIC_OPTIONS = sorted(METRIC_OPTIONS, key=lambda x: x['label'])

# Create a dictionary for easy lookup of labels by metric value
METRIC_LABEL_MAP = {opt['value']: opt['label'] for opt in METRIC_OPTIONS}

def create_metric_controls(first_day_last_month, last_day_last_month):
    return html.Div([
        html.Div([
            html.Label("Select Metric:"),
            dcc.Dropdown(
                id='metric-selector',
                options=METRIC_OPTIONS,  # Use the sorted list here
                value='calories'
            )
        ], style={'width': '50%', 'marginBottom': '20px'}),

        html.Div([
            html.Label("Select Time Frame:"),
            dcc.DatePickerRange(
                id='date-range',
                start_date=first_day_last_month.date(),
                end_date=last_day_last_month.date()
            )
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Label("Quick Goal Setting:"),
            dcc.Input(
                id={'type': 'goal-input', 'metric': 'quick-set'},
                type="number",
                placeholder="Enter goal value",
                style={
                    'width': '100px',
                    'padding': '5px',
                    'border': '1px solid #ddd',
                    'borderRadius': '4px',
                    'marginLeft': '10px'
                }
            )
        ])
    ])

def create_activity_chart(df, selected_metric, start_date, end_date, goal_value):
    # Handle unit conversions and data preprocessing
    if selected_metric == 'duration':
        df[selected_metric] = df[selected_metric] / 60  # Convert to minutes
    elif selected_metric == 'distance':
        df[selected_metric] = df[selected_metric] / 1000  # Convert to kilometers

    mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
    filtered_df = df.loc[mask]

    # For metrics that might not exist in all activities
    if selected_metric not in filtered_df.columns:
        filtered_df[selected_metric] = 0

    goal_reached = filtered_df[filtered_df[selected_metric] >= goal_value]
    goal_not_reached = filtered_df[filtered_df[selected_metric] < goal_value]

    # Create activity type markers
    activity_types = filtered_df['activityType'].apply(lambda x: x['typeKey'] if isinstance(x, dict) else 'unknown')

    fig = go.Figure()

    # Add bars for goal reached activities
    fig.add_trace(go.Bar(
        x=goal_reached['startTimeLocal'],
        y=goal_reached[selected_metric],
        marker_color='green',
        name='Goal Reached',
        text=activity_types[goal_reached.index],
        hovertemplate="Date: %{x}<br>" +
                      f"{selected_metric}: %{{y}}<br>" +
                      "Activity: %{text}<br>" +
                      "<extra></extra>"
    ))

    # Add bars for activities not reaching goal
    fig.add_trace(go.Bar(
        x=goal_not_reached['startTimeLocal'],
        y=goal_not_reached[selected_metric],
        marker_color='red',
        name='Goal Not Reached',
        text=activity_types[goal_not_reached.index],
        hovertemplate="Date: %{x}<br>" +
                      f"{selected_metric}: %{{y}}<br>" +
                      "Activity: %{text}<br>" +
                      "<extra></extra>"
    ))

    # Add goal line
    fig.add_trace(go.Scatter(
        x=[start_date, end_date],
        y=[goal_value, goal_value],
        mode='lines',
        name='Goal',
        line=dict(color='blue', dash='dash')
    ))

    # Customize layout
    metric_label = selected_metric.replace('_', ' ').title()
    units = get_metric_units(selected_metric)

    fig.update_layout(
        title=f"{metric_label} Over Time",
        xaxis_title='Date',
        yaxis_title=f"{metric_label} ({units})",
        xaxis=dict(
            tickformat="%b %d",
            ticklabelmode="period",
            dtick="D1"
        ),
        barmode='group',
        hovermode='closest'
    )

    return fig

def get_metric_units(metric):
    """Return the appropriate units for each metric"""
    units = {
        'calories': 'kcal',
        'steps': 'steps',
        'duration': 'minutes',
        'averageHR': 'bpm',
        'maxHR': 'bpm',
        'aerobicTrainingEffect': 'points',
        'anaerobicTrainingEffect': 'points',
        'distance': 'km',
        'averageSpeed': 'km/h',
        'maxSpeed': 'km/h',
        'movingDuration': 'minutes',
        'moderateIntensityMinutes': 'minutes',
        'vigorousIntensityMinutes': 'minutes',
        'elevationGain': 'm',
        'elevationLoss': 'm',
        'maxElevation': 'm',
        'totalSets': 'sets',
        'totalReps': 'reps',
        'activeSets': 'sets',
        'waterEstimated': 'ml',
        'minTemperature': '°C',
        'maxTemperature': '°C'
    }
    return units.get(metric, '')