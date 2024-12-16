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
        'movingDuration': 900,  # minutes
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

def create_summary_chart(df, start_date, end_date, stored_goals):
    """Create a summary chart showing all metrics' performance as percentage of their goals"""
    summary_data = {}

    # Calculate mean for each metric in the period and convert to percentage of goal
    for metric in METRIC_OPTIONS:
        metric_key = metric['value']
        if metric_key in df.columns:
            # Apply any necessary conversions
            values = df[metric_key]
            if metric_key == 'duration':
                values = values / 60  # Convert to minutes
            elif metric_key == 'distance':
                values = values / 1000  # Convert to kilometers

            mean_value = values.mean()
            goal_value = stored_goals.get(metric_key, get_default_goals()[metric_key])

            # Calculate percentage of goal reached
            percentage = (mean_value / goal_value * 100) if goal_value != 0 else 0

            summary_data[metric_key] = {
                'percentage': percentage,
                'mean': mean_value,  # Keep raw value for hover info
                'goal': goal_value,  # Keep goal for hover info
                'reached': percentage >= 100
            }

    # Create the summary bar chart
    fig = go.Figure()

    # Prepare data for plotting
    metrics = []
    percentages_reached = []
    percentages_not_reached = []
    hover_texts = []

    # Sort metrics by their labels
    sorted_metrics = sorted(summary_data.keys(), key=lambda x: METRIC_LABEL_MAP.get(x, x))

    for metric in sorted_metrics:
        data = summary_data[metric]
        metric_label = METRIC_LABEL_MAP.get(metric, metric.replace('_', ' ').title())
        metrics.append(metric_label)

        percentage = data['percentage']
        if data['reached']:
            percentages_reached.append(percentage)
            percentages_not_reached.append(None)
        else:
            percentages_reached.append(None)
            percentages_not_reached.append(percentage)

        # Create detailed hover text
        units = get_metric_units(metric)
        hover_texts.append(
            f"Metric: {metric_label}<br>" +
            f"Goal: {data['goal']:.1f} {units}<br>" +
            f"Average: {data['mean']:.1f} {units}<br>" +
            f"Percentage: {data['percentage']:.1f}%"
        )

    # Add bars for goals reached
    fig.add_trace(go.Bar(
        x=metrics,
        y=percentages_reached,
        marker_color='green',
        name='Goal Reached',
        text=[f"{p:.1f}%" if p is not None else "" for p in percentages_reached],
        textposition='auto',
        hovertext=hover_texts,
        hoverinfo='text'
    ))

    # Add bars for goals not reached
    fig.add_trace(go.Bar(
        x=metrics,
        y=percentages_not_reached,
        marker_color='red',
        name='Goal Not Reached',
        text=[f"{p:.1f}%" if p is not None else "" for p in percentages_not_reached],
        textposition='auto',
        hovertext=hover_texts,
        hoverinfo='text'
    ))

    # Add 100% goal line
    fig.add_trace(go.Scatter(
        x=metrics,
        y=[100] * len(metrics),
        mode='lines',
        name='Goal (100%)',
        line=dict(
            color='blue',
            dash='dash'
        )
    ))

    # Customize layout
    fig.update_layout(
        title='Summary of All Metrics (Percentage of Goals Reached)',
        xaxis_title='Metrics',
        yaxis_title='Percentage of Goal (%)',
        xaxis=dict(
            tickangle=45,
            tickmode='array',
            ticktext=metrics,
            tickvals=list(range(len(metrics)))
        ),
        yaxis=dict(
            range=[0, max(max([p for p in percentages_reached if p is not None] +
                              [p for p in percentages_not_reached if p is not None]) * 1.1, 120)],  # Make sure 100% line is visible
        ),
        showlegend=True,
        height=600,
        margin=dict(b=150),  # Add bottom margin for rotated labels
        hovermode='closest',
        barmode='overlay'  # This ensures bars don't stack
    )

    return fig

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

def create_empty_chart(message):
    """Create an empty chart with a centered message and greyed out background bars"""
    fig = go.Figure()

    # Create background bar chart data
    background_x = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    background_y = [30, 45, 25, 60, 40, 35, 50]

    # Add grey background bars
    fig.add_trace(go.Bar(
        x=background_x,
        y=background_y,
        marker_color='rgba(200, 200, 200, 0.2)',  # Very light grey
        showlegend=False,
        hoverinfo='skip'
    ))

    # Add centered message
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=14),
        xanchor='center',
        yanchor='middle',
        align='center',
        bgcolor='rgba(255, 255, 255, 0.9)'  # Semi-transparent white background
    )

    # Update layout
    fig.update_layout(
        showlegend=False,
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=80, l=20, r=20, b=20),
        font=dict(family="Arial, sans-serif"),
        xaxis=dict(
            showticklabels=False,  # Hide x-axis labels
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            showticklabels=False,  # Hide y-axis labels
            showgrid=False,
            zeroline=False
        ),
        # Ensure the bars are behind the message
        annotations=[{
            'text': message,
            'x': 0.5,
            'y': 0.5,
            'xref': 'paper',
            'yref': 'paper',
            'showarrow': False,
            'font': {'size': 18},
            'xanchor': 'center',
            'yanchor': 'middle',
            'align': 'center',
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': 'rgba(0, 0, 0, 0)',
            'borderwidth': 0
        }]
    )

    return fig

def create_initial_loading_div():
    """Create the initial empty state div"""
    initial_empty_figure = create_empty_chart("Waiting for you to add<br>your personal fitness data")
    return html.Div([
        html.H1("Goal/Reached Dashboard"),
        dcc.Graph(
            figure=initial_empty_figure,
            config={
                'displayModeBar': False,
                'staticPlot': True,
            }
        )
    ], id='initial-loading-div')

def create_data_loaded_div(first_day_last_month, last_day_last_month):
    """Create the complete div for when data is loaded"""
    return html.Div([
        html.H1("Goal/Reached Dashboard"),

        # Container for controls
        html.Div([
            # Toggle button
            html.Button(
                "Toggle View",
                id='toggle-summary-view',
                n_clicks=0,
                style={'marginBottom': '10px'}
            ),

            # Metric selector container
            html.Div([
                html.Label("Select Metric:"),
                dcc.Dropdown(
                    id='metric-selector',
                    options=METRIC_OPTIONS,
                    value='calories'
                )
            ], id='metric-selector-container', style={'width': '50%', 'marginBottom': '20px'}),

            # Quick goal setting
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
            ], id='quick-goal-container'),
        ]),

        # Container for both graphs
        html.Div([
            dcc.Graph(id="activity-graph", style={'display': 'block'}),
            dcc.Graph(id="summary-graph", style={'display': 'none'}),
        ]),

        # Goals management section
        html.Div([
            html.H3("Metric Goals", style={'marginTop': '20px'}),
            html.Div(id='current-goals-display'),
            html.Br(),
            html.Button("Reset Goals to Default", id='reset-goals-button', n_clicks=0)
        ])
    ], id='data-loaded-div', style={'display': 'none'})

def create_barchart_layout(first_day_last_month, last_day_last_month):
    return html.Div([
        # The initial loading div
        create_initial_loading_div(),

        # The data loaded div (hidden initially)
        create_data_loaded_div(first_day_last_month, last_day_last_month),

        # Store components for data persistence
        dcc.Store(id='stored-data'),
        dcc.Store(id='stored-goals', data=get_default_goals()),
        dcc.Store(id='view-type', data='detail')
    ])

def create_activity_chart(df, selected_metric, start_date, end_date, goal_value):
    # If df is None (initial state, no data loaded)
    if df is None:
        return create_empty_chart("Waiting for you to add<br>your personal fitness data")

    # Handle unit conversions and data preprocessing
    if selected_metric == 'duration':
        df[selected_metric] = df[selected_metric] / 60  # Convert to minutes
    elif selected_metric == 'distance':
        df[selected_metric] = df[selected_metric] / 1000  # Convert to kilometers

    mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
    filtered_df = df.loc[mask]

    # Check if there's any data in the filtered period
    if len(filtered_df) == 0:
        return create_empty_chart("No data available<br>in this period of time")

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
    metric_label = METRIC_LABEL_MAP.get(selected_metric, selected_metric.replace('_', ' ').title())
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