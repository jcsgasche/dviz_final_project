from dash import html, dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Activity type mapping for nicer labels
ACTIVITY_TYPE_LABELS = {
    'strength_training': 'Strength Training',
    'trail_running': 'Trail Running',
    'running': 'Running',
    'cycling': 'Cycling',
    'walking': 'Walking',
    'hiking': 'Hiking',
    'swimming': 'Swimming',
    'yoga': 'Yoga',
    'cardio': 'Cardio',
    'unknown': 'Other'
}

# Metric configurations
METRIC_CONFIGS = {
    'count': {'label': 'Activity Count', 'unit': 'activities', 'format': '.0f'},
    'duration': {'label': 'Duration', 'unit': 'minutes', 'format': '.1f'},
    'calories': {'label': 'Calories', 'unit': 'kcal', 'format': '.0f'},
    'distance': {'label': 'Distance', 'unit': 'km', 'format': '.2f'},
    'activityTrainingLoad': {'label': 'Training Load', 'unit': 'points', 'format': '.1f'},
    'elevationGain': {'label': 'Elevation Gain', 'unit': 'm', 'format': '.1f'}
}

# Dropdown options
BREAKDOWN_METRICS = [
    {'label': config['label'], 'value': metric}
    for metric, config in METRIC_CONFIGS.items()
]

def create_activity_breakdown_layout():
    return html.Div([
        html.H1("Activity Type Breakdown", className="chart-title"),
        html.Div([
            html.Label("Select Metric:", className="dropdown-label"),
            dcc.Dropdown(
                id='breakdown-metric-selector',
                options=BREAKDOWN_METRICS,
                value='count',
                clearable=False,
                style={'width': '200px'}
            )
        ], style={'marginBottom': '20px', 'marginTop': '10px'}),
        dcc.Graph(
            id='activity-breakdown-chart',
            config={'displayModeBar': True,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d']}
        )
    ])

def create_empty_donut_chart(message):
    fig = go.Figure(data=[go.Pie(
        labels=['No Data'],
        values=[1],
        hole=0.5,
        textinfo='none',
        marker=dict(colors=['#E0E0E0']),  # Light gray color
        hoverinfo='none'
    )])

    # Add message text in the center
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14),
        align='center',
    )

    # Update layout for empty state
    fig.update_layout(
        showlegend=False,
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=80, l=20, r=20, b=20),
        font=dict(family="Arial, sans-serif"),
        annotations=[{
            'font': {'size': 18}
        }]
    )

    return fig

def create_activity_breakdown_chart(df, selected_metric):
    if df is None:
        return create_empty_donut_chart("Waiting for you to add<br>your personal fitness data")

    # Create an explicit copy
    df = df.copy()

    # Now these operations will be safe
    df['activity_type'] = df['activityType'].apply(lambda x: x['typeKey'] if isinstance(x, dict) else 'unknown')
    df['activity_type_label'] = df['activity_type'].map(ACTIVITY_TYPE_LABELS)

    metric_config = METRIC_CONFIGS[selected_metric]

    # Check if there's any data in the filtered period
    if len(df) == 0:
        return create_empty_donut_chart("No data available<br>in this period of time")

    if selected_metric == 'count':
        # For count, get frequency of each activity type
        breakdown = df['activity_type_label'].value_counts()
        total = len(df)
        hover_template = "Activity: %{label}<br>Count: %{value}<br>Percentage: %{percent}"
    else:
        # For other metrics, handle conversions and sums
        if selected_metric == 'distance':
            df[selected_metric] = df[selected_metric] / 1000  # Convert to km
        elif selected_metric == 'duration':
            df[selected_metric] = df[selected_metric] / 60  # Convert to minutes

        breakdown = df.groupby('activity_type_label')[selected_metric].sum()
        total = breakdown.sum()
        hover_template = (f"Activity: %{{label}}<br>"
                          f"{metric_config['label']}: %{{value:{metric_config['format']}}} {metric_config['unit']}"
                          f"<br>Percentage: %{{percent}}")

    # Create color scale for consistent colors
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # Create the donut chart
    fig = go.Figure(data=[go.Pie(
        labels=breakdown.index,
        values=breakdown.values,
        hole=0.5,
        name="Activity Distribution",
        hovertemplate=hover_template + "<extra></extra>",
        marker=dict(colors=colors[:len(breakdown)]),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=12)
    )])

    # Format the title with total
    if selected_metric == 'count':
        title_text = f"Activity Distribution (Total: {total:,} activities)"
    else:
        title_text = (f"Activity Distribution by {metric_config['label']} "
                      f"(Total: {total:{metric_config['format']}} {metric_config['unit']})")

    # Update layout
    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.5,
            xanchor='center',
            font=dict(size=16)
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=80, l=20, r=20, b=100),
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
    )

    # Add annotations for small segments
    min_percent_for_label = 3  # Only show labels for segments > 3%
    for i in range(len(breakdown)):
        percent = (breakdown.values[i] / total) * 100
        if percent < min_percent_for_label:
            fig.data[0].textinfo = 'label'

    return fig