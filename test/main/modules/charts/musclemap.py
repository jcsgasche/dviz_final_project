from dash import html, dcc

def create_musclemap_layout():
    """Create the layout for the muscle map visualization"""
    return html.Div([
        html.H1("Muscle Activity Map"),

        html.Div([
            # Image will be updated by callbacks
            html.Img(
                id='muscle-map-image',
                style={
                    'width': '100%',
                    'maxWidth': '800px',
                    'margin': 'auto',
                    'display': 'block'
                }
            ),

            # Store components for muscle map data
            dcc.Store(id='strength-data-store'),
            dcc.Store(id='processed-strength-data-store'),

            # Status message area
            html.Div(id='muscle-map-status',
                     style={'textAlign': 'center', 'marginTop': '10px'})
        ])
    ])