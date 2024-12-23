# modules/charts/barchart.py
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import dash
import json
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc

COLOR_SCHEMES = {
    'default': {
        'reached': 'green',
        'almost': 'orange',
        'not_reached': 'red',
        'goal_line': '#3b9c4e',
        'almost_line': '#f5c43d'
    },
    'colorblind': {
        'reached': '#225ea8',  # Light yellow
        'almost': '#41b6c4',   # Medium blue
        'not_reached': '#ffffd9',  # Dark blue
        'goal_line': '#225ea8',
        'almost_line': '#41b6c4'
    }
}

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

def create_summary_chart(df, start_date, end_date, stored_goals, selected_metrics=None, colorblind_mode=False):
    """Create a summary chart showing metrics' performance as percentage of their goals"""
    summary_data = {}

    # Determine which metrics to display
    metrics_to_show = selected_metrics if selected_metrics else [opt['value'] for opt in METRIC_OPTIONS]

    # Calculate mean for each metric in the period and convert to percentage of goal
    for metric in metrics_to_show:
        if metric in df.columns:
            # Apply any necessary conversions
            values = df[metric]
            if metric == 'duration':
                values = values / 60  # Convert to minutes
            elif metric == 'distance':
                values = values / 1000  # Convert to kilometers

            mean_value = values.mean()
            goal_value = stored_goals.get(metric, get_default_goals()[metric])

            # Calculate percentage of goal reached
            percentage = (mean_value / goal_value * 100) if goal_value != 0 else 0

            summary_data[metric] = {
                'percentage': percentage,
                'mean': mean_value,
                'goal': goal_value,
                'reached': percentage >= 100,
                'almost_reached': 75 <= percentage < 100
            }

    # Create the summary bar chart
    fig = go.Figure()

    # Prepare data for plotting
    metrics = []
    percentages_reached = []
    percentages_almost_reached = []
    percentages_not_reached = []
    hover_texts = []

    # Sort metrics by their labels
    sorted_metrics = sorted(summary_data.keys(), key=lambda x: METRIC_LABEL_MAP.get(x, x))
    valid_values = [p for p in (percentages_reached + percentages_almost_reached + percentages_not_reached) if p is not None]

    for metric in sorted_metrics:
        data = summary_data[metric]
        metric_label = METRIC_LABEL_MAP.get(metric, metric.replace('_', ' ').title())
        metrics.append(metric_label)

        percentage = data['percentage']
        if data['reached']:
            percentages_reached.append(percentage)
            percentages_almost_reached.append(None)
            percentages_not_reached.append(None)
        elif data['almost_reached']:
            percentages_reached.append(None)
            percentages_almost_reached.append(percentage)
            percentages_not_reached.append(None)
        else:
            percentages_reached.append(None)
            percentages_almost_reached.append(None)
            percentages_not_reached.append(percentage)

        # Create detailed hover text
        units = get_metric_units(metric)
        hover_texts.append(
            f"Metric: {metric_label}<br>" +
            f"Goal: {data['goal']:.1f} {units}<br>" +
            f"Average: {data['mean']:.1f} {units}<br>" +
            f"Percentage: {data['percentage']:.1f}%"
        )

    colors = COLOR_SCHEMES['colorblind'] if colorblind_mode else COLOR_SCHEMES['default']

    # Add bars for goals reached
    fig.add_trace(go.Bar(
        x=metrics,
        y=percentages_reached,
        marker_color=colors['reached'],
        name='Goal Reached',
        text=[f"{p:.1f}%" if p is not None else "" for p in percentages_reached],
        textposition='auto',
        hovertext=hover_texts,
        hoverinfo='text'
    ))

    # Add bars for goals almost reached
    fig.add_trace(go.Bar(
        x=metrics,
        y=percentages_almost_reached,
        marker_color=colors['almost'],
        name='Goal Almost Reached',
        text=[f"{p:.1f}%" if p is not None else "" for p in percentages_almost_reached],
        textposition='auto',
        hovertext=hover_texts,
        hoverinfo='text'
    ))

    # Add bars for goals not reached
    fig.add_trace(go.Bar(
        x=metrics,
        y=percentages_not_reached,
        marker_color=colors['not_reached'],
        name='Goal Not Reached',
        text=[f"{p:.1f}%" if p is not None else "" for p in percentages_not_reached],
        textposition='auto',
        hovertext=hover_texts,
        hoverinfo='text'
    ))

    # Update goal lines with appropriate colors
    fig.add_shape(
        type="line",
        x0=0,
        x1=1,
        y0=100,
        y1=100,
        line=dict(
            color=colors['goal_line'],
            width=2,
            dash="dash",
        ),
        xref="paper",
        yref="y"
    )

    fig.add_shape(
        type="line",
        x0=0,
        x1=1,
        y0=75,
        y1=75,
        line=dict(
            color=colors['almost_line'],
            width=2,
            dash="dot",
        ),
        xref="paper",
        yref="y"
    )

    # Update legend lines
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='lines',
        name='Goal (100%)',
        line=dict(
            color=colors['goal_line'],
            dash='dash'
        ),
        showlegend=True
    ))

    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='lines',
        name='Goal Almost Reached (75%)',
        line=dict(
            color=colors['almost_line'],
            dash='dot'
        ),
        showlegend=True
    ))

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
        marker_line=dict(color='rgba(150, 150, 150, 0.5)', width=1),  # Add this line
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

# Add this function after create_metric_controls:
def create_summary_controls():
    return html.Div([
        # Toggle between full/custom summary
        html.Div([
            dbc.RadioItems(
                id='summary-type',
                options=[
                    {'label': 'All Metrics', 'value': 'all'},
                    {'label': 'Custom Selection', 'value': 'custom'}
                ],
                value='all',
                inline=True,
                className="mb-3"
            ),
        ]),

        # Dropdown for selecting metrics (initially hidden)
        html.Div([
            dcc.Dropdown(
                id='summary-metrics-selector',
                options=METRIC_OPTIONS,
                value=[METRIC_OPTIONS[0]['value']],  # Default to first metric
                multi=True,
                placeholder="Select metrics to display...",
            )
        ], id='summary-metrics-dropdown', style={'display': 'none'})
    ])

# Update the create_data_loaded_div function to include the new controls:
def create_data_loaded_div(first_day_last_month, last_day_last_month):
    return html.Div([
        html.H1("Goal/Reached Dashboard"),

        # Container for controls
        html.Div([
            # Remove colorblind toggle since it's now global

            # Toggle button
            html.Button(
                "Toggle View",
                id='toggle-summary-view',
                n_clicks=0,
                style={'marginBottom': '10px'}
            ),

            # Summary view controls (initially hidden)
            html.Div(
                create_summary_controls(),
                id='summary-controls',
                style={'display': 'none'}
            ),

            # Rest of the existing controls...
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
            html.Div([
                html.H3("Metric Goals", style={'marginTop': '20px', 'display': 'inline-block'}),
                html.Button(
                    "⯆",
                    id='collapse-goals-button',
                    n_clicks=0,
                    style={
                        'marginLeft': '10px',
                        'background': 'none',
                        'border': 'none',
                        'fontSize': '20px',
                        'cursor': 'pointer',
                        'padding': '5px 10px',
                        'verticalAlign': 'middle',
                        'lineHeight': '1',
                        'color': '#666'
                    }
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            dbc.Collapse(
                [
                    html.Div(id='current-goals-display'),
                    html.Br(),
                    html.Button("Reset Goals to Default", id='reset-goals-button', n_clicks=0)
                ],
                id='goals-collapse',
                is_open=True
            )
        ]),
    ], id='data-loaded-div', style={'display': 'none'})

def create_barchart_layout(first_day_last_month, last_day_last_month):
    return html.Div([
        # The initial loading div
        create_initial_loading_div(),

        # The data loaded div (hidden initially)
        create_data_loaded_div(first_day_last_month, last_day_last_month),

        # Only keep the stores that aren't in app.py
        dcc.Store(id='stored-goals', data=get_default_goals()),
        dcc.Store(id='view-type', data='detail')
    ])

def create_activity_chart(df, selected_metric, start_date, end_date, goal_value, colorblind_mode=False):
    if df is None:
        return create_empty_chart("Waiting for you to add<br>your personal fitness data")

    # Handle unit conversions and data preprocessing
    if selected_metric == 'duration':
        df[selected_metric] = df[selected_metric] / 60  # Convert to minutes
    elif selected_metric == 'distance':
        df[selected_metric] = df[selected_metric] / 1000  # Convert to kilometers

    mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
    filtered_df = df.loc[mask]

    if len(filtered_df) == 0:
        return create_empty_chart("No data available<br>in this period of time")

    if selected_metric not in filtered_df.columns:
        filtered_df[selected_metric] = 0

    goal_reached = filtered_df[filtered_df[selected_metric] >= goal_value]
    goal_almost_reached = filtered_df[(filtered_df[selected_metric] >= 0.75 * goal_value) &
                                      (filtered_df[selected_metric] < goal_value)]
    goal_not_reached = filtered_df[filtered_df[selected_metric] < 0.75 * goal_value]

    activity_types = filtered_df['activityType'].apply(lambda x: x['typeKey'] if isinstance(x, dict) else 'unknown')

    colors = COLOR_SCHEMES['colorblind'] if colorblind_mode else COLOR_SCHEMES['default']

    fig = go.Figure()

    # Add bars for "Goal Reached"
    fig.add_trace(go.Bar(
        x=goal_reached['startTimeLocal'],
        y=goal_reached[selected_metric],
        marker_color=colors['reached'],
        name='Goal Reached',
        text=activity_types[goal_reached.index],
        hovertemplate="Date: %{x}<br>" +
                      f"{selected_metric}: %{{y}}<br>" +
                      "Activity: %{text}<br>" +
                      "<extra></extra>"
    ))

    # Add bars for "Goal Almost Reached"
    fig.add_trace(go.Bar(
        x=goal_almost_reached['startTimeLocal'],
        y=goal_almost_reached[selected_metric],
        marker_color=colors['almost'],
        name='Goal Almost Reached',
        text=activity_types[goal_almost_reached.index],
        hovertemplate="Date: %{x}<br>" +
                      f"{selected_metric}: %{{y}}<br>" +
                      "Activity: %{text}<br>" +
                      "<extra></extra>"
    ))

    # Add bars for "Goal Not Reached"
    fig.add_trace(go.Bar(
        x=goal_not_reached['startTimeLocal'],
        y=goal_not_reached[selected_metric],
        marker_color=colors['not_reached'],
        name='Goal Not Reached',
        text=activity_types[goal_not_reached.index],
        hovertemplate="Date: %{x}<br>" +
                      f"{selected_metric}: %{{y}}<br>" +
                      "Activity: %{text}<br>" +
                      "<extra></extra>"
    ))

    # Update goal lines with appropriate colors
    fig.add_trace(go.Scatter(
        x=[start_date, end_date],
        y=[goal_value, goal_value],
        mode='lines',
        name='Goal (100%)',
        line=dict(color=colors['goal_line'], dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=[start_date, end_date],
        y=[0.75 * goal_value, 0.75 * goal_value],
        mode='lines',
        name='Goal Almost Reached (75%)',
        line=dict(color=colors['almost_line'], dash='dot')
    ))

    # Customize layout
    metric_label = METRIC_LABEL_MAP.get(selected_metric, selected_metric.replace('_', ' ').title())
    units = get_metric_units(selected_metric)

    fig.update_layout(
        title=f"{metric_label} Over Time",
        yaxis_title=f"{metric_label} ({units})",
        xaxis=dict(
            tickformat="%b %d",
            ticklabelmode="period",
            dtick="D1"
        ),
        barmode='group',
        hovermode='closest',
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
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