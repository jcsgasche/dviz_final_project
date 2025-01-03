from datetime import datetime, timedelta
from dash import dcc, html

def calculate_date_range():
    today = datetime.today()
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)
    return first_day_last_month, last_day_last_month

def create_data_layout():
    return html.Div([
        html.H1("Load Data"),
        html.Div([
            dcc.RadioItems(
                id='data-source',
                options=[
                    {'label': 'Fetch from Garmin', 'value': 'garmin'},
                    {'label': 'Upload Local Dataset', 'value': 'upload'}
                ],
                value='garmin',
                labelStyle={'display': 'inline-block', 'margin-right': '30px'},
                inputStyle={"margin-right": "5px"}
            )
        ], style={'margin-bottom': '20px'}),

        html.Div([
            html.Div([
                html.Label("Garmin Email:", style={'marginRight': '10px', 'marginBottom': '10px'}),
                dcc.Input(id='garmin-email', type='email', placeholder='Enter your Garmin email', style={'width': '300px'}),
                html.Br(),
                html.Label("Garmin Password:", style={'marginRight': '10px'}),
                dcc.Input(id='garmin-password', type='password', placeholder='Enter your Garmin password', style={'width': '300px'}),
                html.Br(),
                html.Button('Fetch Data', id='fetch-button', n_clicks=0, style={'margin-top': '10px'})
            ], id='garmin-login', style={'display': 'block'}),

            html.Div(create_upload_section(), id='file-upload', style={'display': 'none'}),

            html.Div(style={
                'marginTop': '20px',
                'padding': '10px 0',
                'borderTop': '1px solid #eee',
                'borderBottom': '1px solid #eee',
                'minHeight': '50px',
                'display': 'flex',
                'alignItems': 'center'
            }, children=[
                html.Div(id='data-status-container')
            ]),

        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Hr(style={'margin': '20px 0'}),
            html.P(id='last-update-display', style={'color': '#666', 'fontStyle': 'italic'}),
        ]),

        html.Div([
            html.Hr(style={'margin': '20px 0'}),
            html.H6("Download Data"),
            dcc.Dropdown(
                id='download-type',
                options=[
                    {'label': 'All Activities', 'value': 'all'},
                    {'label': 'Strength Activities Only', 'value': 'strength'}
                ],
                value='all',
                style={'width': '300px', 'marginBottom': '10px'}
            ),
            html.Button("Download Data", id="btn-download", n_clicks=0,
                        style={'marginRight': '10px'}),
            dcc.Download(id="download-data")
        ], id='download-section', style={'marginTop': '20px', 'display': 'none'}),

        html.Div([
            html.Hr(style={'margin': '20px 0'}),
            html.Button(
                "Clear Stored Data",
                id="clear-data-button",
                n_clicks=0,
                style={
                    'backgroundColor': '#dc3545',
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'borderRadius': '4px'
                }
            ),
        ], id='clear-data-section', style={'marginTop': '20px', 'display': 'none'})
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
            contents=None,
            multiple=False
        ),
        html.Div(id='upload-status', style={'margin-top': '10px', 'color': 'green'})
    ]