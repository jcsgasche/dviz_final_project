from dash import Dash, html, dcc
import json
from pathlib import Path

from modules.charts.barchart import create_barchart_layout
from modules.charts.activity_breakdown import create_activity_breakdown_layout
from modules.utils import calculate_date_range, create_general_layout
from modules.callbacks.ui_callbacks import register_ui_callbacks
from modules.callbacks.barchart_callbacks import register_barchart_callbacks
from modules.callbacks.activity_breakdown_callbacks import register_activity_breakdown_callbacks
from modules.callbacks.muscledata_callbacks import register_muscledata_callbacks

app = Dash(__name__)
first_day_last_month, last_day_last_month = calculate_date_range()

app.layout = html.Div([
    # General layout and existing charts
    create_general_layout(),
    create_barchart_layout(first_day_last_month, last_day_last_month),
    create_activity_breakdown_layout(),

    # Add Garmin login and data fetch UI
    html.H2("Garmin Data Fetch & Muscle Map"),
    html.Div([
        html.Label("Garmin Email:"),
        dcc.Input(
            id='garmin-email', type='email',
            placeholder='Enter your Garmin email',
            style={'width': '300px'}
        ),
        html.Br(),
        html.Label("Garmin Password:"),
        dcc.Input(
            id='garmin-password', type='password',
            placeholder='Enter your Garmin password',
            style={'width': '300px'}
        ),
        html.Br(),
        html.Button('Fetch Data', id='fetch-button', n_clicks=0, style={'margin-top': '10px'}),
        html.Div(id='garmin-status', style={'margin-top': '10px', 'color': 'green'}),
    ], style={'margin-bottom': '20px'}),

    # Hidden stores for fetched and processed data
    dcc.Store(id='strength-data-store'),
    dcc.Store(id='processed-strength-data-store'),

    # Display muscle map
    html.Div([
        html.H2("Muscle Map"),
        html.Img(id='muscle-map-image', style={'max-width': '100%', 'height': 'auto'})
    ], style={'margin-top': '20px'})
])

# Removed register_data_callbacks(app) to avoid duplicate outputs
# If data_callbacks are necessary, ensure they do not produce the same output or rename their outputs.
# register_data_callbacks(app) 

register_ui_callbacks(app)
register_barchart_callbacks(app)
register_activity_breakdown_callbacks(app)
register_muscledata_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
