# modules/charts/musclemap/musclemap.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json

# Updated musclemap.py

def create_musclemap_layout():
    return html.Div([
        html.H1("Muscle Activity Map"),

        # Add colorblind mode toggle
        html.Div([
            dbc.Checklist(
                options=[
                    {"label": "Colorblind Friendly Mode", "value": True}
                ],
                value=[],
                id="colorblind-toggle",
                switch=True,  # This makes it look like a toggle switch
                style={'marginBottom': '10px'}
            ),
        ]),

        html.Div([
            html.Img(
                id='muscle-map-image',
                style={
                    'width': '100%',
                    'min-width': '900px',
                    'max-width': '1500px',
                    'height': 'auto',
                    'margin': 'auto',
                    'display': 'block'
                }
            ),
        ], id='muscle-map-container', style={
            'display': 'block',
            'width': '100%',
            'min-width': '900px',
            'max-width': '1500px',
            'margin': 'auto'
        }),
        dcc.Store(id='processed-strength-data-store'),
        dcc.Store(id='muscle-view-type', data='map'),
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

    # Constant mapping of muscles
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

    # Initialize with fixed order and all muscles
    muscle_activity = {
        'Front Chest': 0, 'Back Lats': 0, 'Front Deltoids': 0, 'Back Deltoids': 0,
        'Front Abs': 0, 'Back Triceps': 0, 'Front Biceps': 0, 'Front Quads': 0,
        'Back Glutes': 0, 'Back Hamstrings': 0
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

    # Create the spider chart
    fig = go.Figure()

    # Add trace with all muscles (including zeros)
    fig.add_trace(go.Scatterpolar(
        r=list(muscle_activity.values()),
        theta=list(muscle_activity.keys()),
        fill='toself',
        name='Muscle Activity'
    ))

    # Set fixed tick marks and range
    max_value = max(muscle_activity.values()) if any(muscle_activity.values()) else 1
    tick_values = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    tick_text = [f"{int(v * 100)}%" for v in tick_values]

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=True,
                ticktext=tick_text,
                tickvals=[v * max_value for v in tick_values],
                range=[0, max_value * 1.1]
            ),
            angularaxis=dict(
                showticklabels=True,
                tickfont=dict(size=16)
            )
        ),
        showlegend=True,
        height=600
    )

    return fig

def create_empty_spider_chart(message="Waiting for you to add<br>your personal fitness data"):
    """Create an empty spider chart with default muscle groups and message"""
    empty_muscles = {
        'Front Chest': 0, 'Back Lats': 0, 'Front Deltoids': 0, 'Back Deltoids': 0,
        'Front Abs': 0, 'Back Triceps': 0, 'Front Biceps': 0, 'Front Quads': 0,
        'Back Glutes': 0, 'Back Hamstrings': 0
    }

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=list(empty_muscles.values()),
        theta=list(empty_muscles.keys()),
        fill='toself',
        name='Muscle Activity',
        fillcolor='rgba(200, 200, 200, 0.2)',
        line=dict(
            color='rgba(150, 150, 150, 0.5)',
            width=1
        ),
        opacity=1,
        showlegend=False
    ))

    # Set fixed tick marks for empty chart
    tick_values = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    tick_text = [f"{int(v * 100)}%" for v in tick_values]

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(200, 200, 200, 0.2)',
            radialaxis=dict(
                visible=True,
                showticklabels=True,
                ticktext=tick_text,
                tickvals=tick_values,
                range=[0, 1],
                linecolor='rgba(150, 150, 150, 0.5)',
                gridcolor='rgba(150, 150, 150, 0.5)',
                layer='below traces'
            ),
            angularaxis=dict(
                showticklabels=True,
                tickfont=dict(size=16),
                linecolor='rgba(150, 150, 150, 0.5)',
                gridcolor='rgba(150, 150, 150, 0.5)',
                layer='below traces'
            ),
            domain=dict(x=[0, 1], y=[0, 1])
        ),
        showlegend=False,
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white',
        annotations=[{
            'text': message,
            'x': 0.5,
            'y': 0.5,
            'xref': 'paper',
            'yref': 'paper',
            'showarrow': False,
            'font': {'size': 26},
            'xanchor': 'center',
            'yanchor': 'middle',
            'align': 'center',
            'bgcolor': 'rgba(255, 255, 255, 0.9)',
            'bordercolor': 'rgba(0, 0, 0, 0)',
            'borderwidth': 0
        }]
    )

    return fig