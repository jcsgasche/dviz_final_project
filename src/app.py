import base64
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from pathlib import Path

from modules.charts.barchart import create_barchart_layout
from modules.charts.activity_breakdown import create_activity_breakdown_layout
from modules.charts.musclemap.musclemap import create_musclemap_layout
from modules.utils import calculate_date_range, create_data_layout
from modules.callbacks.data_callbacks import register_data_callbacks
from modules.callbacks.barchart_callbacks import register_barchart_callbacks
from modules.callbacks.activity_breakdown_callbacks import register_activity_breakdown_callbacks
from modules.callbacks.musclemap_callbacks import register_musclemap_callbacks

THEME = dbc.themes.LUX

app = Dash(__name__,
           external_stylesheets=[THEME],
           suppress_callback_exceptions=True)

first_day_last_month, last_day_last_month = calculate_date_range()

logo_path = Path(__file__).parent / 'modules' / 'charts' / 'musclemap' / 'data' / 'LOGO.png'
with open(logo_path, 'rb') as f:
    encoded_logo = base64.b64encode(f.read()).decode()

logo_image = html.Img(
    src=f'data:image/png;base64,{encoded_logo}',
    style={'height': '90px', 'marginLeft': '40px'}
)

data_stores = html.Div([
    dcc.Store(id='stored-data', storage_type='local'),
    dcc.Store(id='strength-data-store', storage_type='local'),
    dcc.Store(id='last-update-time', storage_type='local'),
])

floating_controls = dbc.Container([
    dbc.Card([
        dbc.CardBody([
            html.H6("Display Settings", className="mb-3"),
            dbc.Checklist(
                options=[
                    {"label": "Colorblind Friendly Mode", "value": True}
                ],
                value=[],
                id="global-colorblind-toggle",
                switch=True,
                className="mb-2"
            ),
        ])
    ], className="shadow-sm mb-3",
        style={
            'position': 'fixed',
            'top': '100px',
            'right': '20px',
            'zIndex': 1000,
            'width': 'auto',
            'minWidth': '300px',
            'backgroundColor': 'white',
            'borderRadius': '4px'
        }),

    # Date Range Card (moved down)
    dbc.Card([
        dbc.CardBody([
            html.H6("Date Range", className="mb-3"),
            dcc.DatePickerRange(
                id='date-range',
                start_date=first_day_last_month.date(),
                end_date=last_day_last_month.date(),
                className="mb-2"
            ),
        ])
    ], className="shadow-sm",
        style={
            'position': 'fixed',
            'top': '200px',
            'right': '20px',
            'zIndex': 1000,
            'width': 'auto',
            'minWidth': '300px',
            'backgroundColor': 'white',
            'borderRadius': '4px'
        })
], fluid=True)

navbar = dbc.Navbar(
    dbc.Container(
        [
            logo_image,
            html.H4(
                "PFIFA! - Personal Functional Interactive Fitness Analysis",
                className="mx-auto",
                style={"color": "white", "margin": "0", "fontSize": "30px"}
            )
        ],
        fluid=True
    ),
    color="primary",
    dark=True
)

# Update the main layout
app.layout = html.Div([
    navbar,
    data_stores,
    html.Div(id='data-status-container'),
    floating_controls,
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(create_data_layout())
                ], className="mb-4 shadow")
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(create_musclemap_layout())
                ], className="mb-4 shadow")
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(create_barchart_layout(first_day_last_month, last_day_last_month))
                ], className="mb-4 shadow")
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(create_activity_breakdown_layout())
                ], className="mb-4 shadow")
            ])
        ])
    ], fluid=True, className="py-4")
], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

register_data_callbacks(app)
register_barchart_callbacks(app)
register_activity_breakdown_callbacks(app)
register_musclemap_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)