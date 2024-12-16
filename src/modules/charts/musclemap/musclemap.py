# modules/charts/musclemap/musclemap.py
from dash import html, dcc
import plotly.graph_objects as go

def create_empty_spider_chart(message="Waiting for you to add<br>your personal fitness data"):
    """Create an empty spider chart with default muscle groups and message"""
    empty_muscles = {
        'FrontChest': 0, 'BackLats': 0, 'FrontDelts': 0, 'BackDelts': 0,
        'FrontAbs': 0, 'BackTriceps': 0, 'FrontBiceps': 0, 'FrontQuads': 0,
        'BackGlutes': 0, 'BackHamstrings': 0
    }

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(empty_muscles.values()),
        theta=list(empty_muscles.keys()),
        fill='toself',
        name='Muscle Activity'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # Add centered annotation matching barchart style
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            size=18
        ),
        xanchor='center',
        yanchor='middle',
        align='center',
        bgcolor='rgba(255, 255, 255, 0.9)'  # Semi-transparent white background
    )

    return fig

def create_musclemap_layout():
    """Create the layout for the muscle map visualization with spider chart toggle"""
    return html.Div([
        html.H1("Muscle Activity Map"),  # Match barchart font

        # Toggle button container
        html.Div([
            html.Button(
                "Toggle View",
                id='toggle-muscle-view',
                n_clicks=0,
                style={
                    'marginBottom': '10px',
                }
            ),
        ]),

        # Container for both visualizations
        html.Div([
            # Original muscle map
            html.Div([
                html.Img(
                    id='muscle-map-image',
                    style={
                        'width': '100%',
                        'maxWidth': '800px',
                        'margin': 'auto',
                        'display': 'block'
                    }
                ),
            ], id='muscle-map-container', style={'display': 'block'}),

            # Spider chart
            html.Div([
                dcc.Graph(
                    id='muscle-spider-chart',
                    style={'height': '600px'},
                    figure=create_empty_spider_chart()
                ),
            ], id='spider-chart-container', style={'display': 'none'}),

            # Store components
            dcc.Store(id='strength-data-store'),
            dcc.Store(id='processed-strength-data-store'),
            dcc.Store(id='muscle-view-type', data='map'),
        ])
    ])

def create_spider_chart(processed_data, start_date, end_date):
    """Create a spider chart from the muscle activity data"""
    if not processed_data:
        return create_empty_spider_chart()

    # Parse the JSON string if it's not already a list
    if isinstance(processed_data, str):
        try:
            processed_data = json.loads(processed_data)
        except json.JSONDecodeError:
            return create_empty_spider_chart("No data available<br>in this period of time")

    # Initialize counters for muscle groups
    muscle_activity = {
        'FrontChest': 0, 'BackLats': 0, 'FrontDelts': 0, 'BackDelts': 0,
        'FrontAbs': 0, 'BackTriceps': 0, 'FrontBiceps': 0, 'FrontQuads': 0,
        'BackGlutes': 0, 'BackHamstrings': 0
    }

    # Process each activity
    for activity in processed_data:
        for exercise in activity['exercises']:
            reps = exercise.get('repetitions', 0) * exercise.get('sets', 1)

            # Process primary muscles
            for muscle in exercise['primary_muscles']:
                if muscle != 'Undefined':
                    base_muscle = muscle.replace('Right', '').replace('Left', '')
                    if base_muscle in muscle_activity:
                        muscle_activity[base_muscle] += reps * 1.0

            # Process secondary muscles
            for muscle in exercise['secondary_muscles']:
                if muscle != 'Undefined':
                    base_muscle = muscle.replace('Right', '').replace('Left', '')
                    if base_muscle in muscle_activity:
                        muscle_activity[base_muscle] += reps * 0.5

    # Remove muscle groups with no activity
    active_muscles = {k: v for k, v in muscle_activity.items() if v > 0}

    if not active_muscles:
        return create_empty_spider_chart("No data available<br>in this period of time")

    # Create the spider chart
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=list(active_muscles.values()),
        theta=list(active_muscles.keys()),
        fill='toself',
        name='Muscle Activity'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(active_muscles.values()) * 1.1]
            )
        ),
        showlegend=False,
        height=600
    )

    return fig