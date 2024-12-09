# modules/utils.py
from datetime import datetime, timedelta
from dash import dcc, html

def calculate_date_range():
    today = datetime.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)
    return first_day_last_month, last_day_last_month

def create_general_layout():
    return html.Div([
        html.H1("PFIFA! - Personal Functional Interactive Fitness Analysis"),

        html.H1("Load Data"),
        html.Div([
            dcc.RadioItems(
                id='data-source',
                options=[
                    {'label': 'Fetch from Garmin', 'value': 'garmin'},
                    {'label': 'Upload Local Dataset', 'value': 'upload'}
                ],
                value='garmin',
                labelStyle={'display': 'inline-block', 'margin-right': '20px'}
            )
        ], style={'margin-bottom': '20px'}),

        html.Div([
            html.Label("Garmin Email:"),
            dcc.Input(id='garmin-email', type='email', placeholder='Enter your Garmin email', style={'width': '300px'}),
            html.Br(),
            html.Label("Garmin Password:"),
            dcc.Input(id='garmin-password', type='password', placeholder='Enter your Garmin password', style={'width': '300px'}),
            html.Br(),
            html.Button('Fetch Data', id='fetch-button', n_clicks=0, style={'margin-top': '10px'})
        ], id='garmin-login', style={'display': 'block'}),

        html.Div(create_upload_section(), id='file-upload', style={'display': 'none'}),
        html.Div(id='garmin-status', style={'margin-top': '10px', 'color': 'green'}),
        html.Div(create_refresh_section(), id='refresh-section', style={'margin-bottom': '20px'}),
    ])

def create_upload_section():
    return [
        dcc.Upload(
            id='upload-data',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            style={
                'width': '300px',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div(id='upload-status', style={'margin-top': '10px', 'color': 'green'})
    ]

def create_refresh_section():
    return html.Button('Refresh Data', id='refresh-button', n_clicks=0)