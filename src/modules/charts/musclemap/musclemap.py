# modules/charts/musclemap/musclemap.py
from dash import html, dcc
import plotly.graph_objects as go
import json

# modules/charts/musclemap/musclemap.py
def create_musclemap_layout():
    """Create the layout for the muscle map visualization with spider chart toggle"""
    return html.Div([
        html.H1("Muscle Activity Map"),

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

            # Store components - only keep those not in app.py
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

    # Initialize counters for muscle groups with full names
    muscle_activity = {
        'Front Chest': 0, 'Back Lats': 0, 'Front Deltoids': 0, 'Back Deltoids': 0,
        'Front Abs': 0, 'Back Triceps': 0, 'Front Biceps': 0, 'Front Quads': 0,
        'Back Glutes': 0, 'Back Hamstrings': 0
    }

    # Mapping of internal names to display names
    muscle_name_mapping = {
        'FrontChest': 'Front Chest',
        'BackLats': 'Back Lats',
        'FrontDelts': 'Front Deltoids',
        'BackDelts': 'Back Deltoids',
        'FrontAbs': 'Front Abs',
        'BackTriceps': 'Back Triceps',
        'FrontBiceps': 'Front Biceps',
        'FrontQuads': 'Front Quads',
        'BackGlutes': 'Back Glutes',
        'BackHamstrings': 'Back Hamstrings'
    }

    # Process each activity
    for activity in processed_data:
        for exercise in activity['exercises']:
            reps = exercise.get('repetitions', 0) * exercise.get('sets', 1)

            # Process primary muscles
            for muscle in exercise['primary_muscles']:
                if muscle != 'Undefined':
                    base_muscle = muscle.replace('Right', '').replace('Left', '')
                    display_name = muscle_name_mapping.get(base_muscle)
                    if display_name in muscle_activity:
                        muscle_activity[display_name] += reps * 1.0

            # Process secondary muscles
            for muscle in exercise['secondary_muscles']:
                if muscle != 'Undefined':
                    base_muscle = muscle.replace('Right', '').replace('Left', '')
                    display_name = muscle_name_mapping.get(base_muscle)
                    if display_name in muscle_activity:
                        muscle_activity[display_name] += reps * 0.5

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
                showticklabels=True,  # Show the numeric values
                range=[0, max(active_muscles.values()) * 1.1]
            ),
            angularaxis=dict(
                showticklabels=True,  # Show the muscle labels
                tickfont=dict(size=12)  # Adjust font size as needed
            )
        ),
        showlegend=True,
        height=600
    )

    return fig

def create_empty_spider_chart(message="Waiting for you to add<br>your personal fitness data"):
    """Create an empty spider chart with default muscle groups and message, matching barchart style"""
    empty_muscles = {
        'FrontChest': 0, 'BackLats': 0, 'FrontDelts': 0, 'BackDelts': 0,
        'FrontAbs': 0, 'BackTriceps': 0, 'FrontBiceps': 0, 'FrontQuads': 0,
        'BackGlutes': 0, 'BackHamstrings': 0
    }

    fig = go.Figure()

    # Add the trace with explicit styling for every component
    fig.add_trace(go.Scatterpolar(
        r=list(empty_muscles.values()),
        theta=list(empty_muscles.keys()),
        fill='toself',
        name='Muscle Activity',
        fillcolor='rgba(200, 200, 200, 0.2)',  # Background color matching barchart
        line=dict(
            color='rgba(150, 150, 150, 0.5)',  # Darker grey for lines
            width=1
        ),
        opacity=1,  # Ensure full opacity
        showlegend=False
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(200, 200, 200, 0.2)',  # Set polar background color
            radialaxis=dict(
                showticklabels=False,
                range=[0, 1],
                linecolor='rgba(150, 150, 150, 0.5)',
                gridcolor='rgba(150, 150, 150, 0.5)',
                layer='below traces'  # Ensure grid is below the trace
            ),
            angularaxis=dict(
                showticklabels=False,
                linecolor='rgba(150, 150, 150, 0.5)',
                gridcolor='rgba(150, 150, 150, 0.5)',
                layer='below traces'  # Ensure grid is below the trace
            ),
            domain=dict(x=[0, 1], y=[0, 1])  # Ensure proper sizing
        ),
        showlegend=False,
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        # Add centered annotation matching barchart style
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