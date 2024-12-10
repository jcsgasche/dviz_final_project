from dash import Dash, html
import dash_bootstrap_components as dbc
from pathlib import Path

from modules.charts.barchart import create_barchart_layout
from modules.charts.activity_breakdown import create_activity_breakdown_layout
from modules.utils import calculate_date_range, create_data_layout
from modules.callbacks.data_callbacks import register_data_callbacks
from modules.callbacks.ui_callbacks import register_ui_callbacks
from modules.callbacks.barchart_callbacks import register_barchart_callbacks
from modules.callbacks.activity_breakdown_callbacks import register_activity_breakdown_callbacks

# BOOTSTRAP, CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, LUMEN,
# LUX, MATERIA, MINTY, MORPH, PULSE, QUARTZ, SANDSTONE, SIMPLEX, SKETCHY,
# SLATE, SOLAR, SPACELAB, SUPERHERO, UNITED, VAPOR, YETI, ZEPHYR
THEME = dbc.themes.LUX

# Initialize the Dash app with the theme
app = Dash(__name__,
           external_stylesheets=[THEME],
           suppress_callback_exceptions=True)

first_day_last_month, last_day_last_month = calculate_date_range()

# Create the navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More", header=True),
                dbc.DropdownMenuItem("Settings", href="#"),
                dbc.DropdownMenuItem("Help", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="PFIFA! - Personal Functional Interactive Fitness Analysis",
    brand_href="#",
    color="primary",
    dark=True,
)

# Main layout with Bootstrap components
app.layout = html.Div([
    navbar,
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
                    dbc.CardBody(create_activity_breakdown_layout())
                ], className="mb-4 shadow")
            ])
        ])
    ], fluid=True, className="py-4")
], style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})

# Register callbacks
register_data_callbacks(app)
register_ui_callbacks(app)
register_barchart_callbacks(app)
register_activity_breakdown_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
