from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from pathlib import Path

from modules.charts.barchart import create_barchart_layout
from modules.charts.activity_breakdown import create_activity_breakdown_layout
from modules.charts.musclemap import create_musclemap_layout
from modules.utils import calculate_date_range, create_data_layout
from modules.callbacks.data_callbacks import register_data_callbacks
from modules.callbacks.ui_callbacks import register_ui_callbacks
from modules.callbacks.barchart_callbacks import register_barchart_callbacks
from modules.callbacks.activity_breakdown_callbacks import register_activity_breakdown_callbacks

THEME = dbc.themes.LUX

app = Dash(__name__,
           external_stylesheets=[THEME],
           suppress_callback_exceptions=True)

first_day_last_month, last_day_last_month = calculate_date_range()

floating_date_picker = dbc.Container([
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
            'top': '80px',  # Below navbar
            'right': '20px',
            'zIndex': 1000,
            'width': 'auto',
            'minWidth': '300px',
            'backgroundColor': 'white',
            'borderRadius': '4px'
        })
], fluid=True)

navbar = dbc.NavbarSimple(
    brand="PFIFA! - Personal Functional Interactive Fitness Analysis",
    brand_href="#",
    color="primary",
    dark=True,
)

app.layout = html.Div([
    navbar,
    floating_date_picker,
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
                    dbc.CardBody(create_barchart_layout(first_day_last_month, last_day_last_month))
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
                    dbc.CardBody(create_activity_breakdown_layout())
                ], className="mb-4 shadow")
            ])
        ])
    ], fluid=True, className="py-4")
], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

register_data_callbacks(app)
register_ui_callbacks(app)
register_barchart_callbacks(app)
register_activity_breakdown_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)