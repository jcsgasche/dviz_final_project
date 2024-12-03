# modules/charts/barchart.py
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import dash
from dash.exceptions import PreventUpdate

def create_chart_layout(first_day_last_month, last_day_last_month):
    return html.Div([
        html.H1("Interactive Fitness Activity Dashboard Blabi Blablubb"),

        html.Div([
            dcc.RadioItems(
                id='data-source-chart',
                options=[
                    {'label': 'Fetch from Garmin lolool', 'value': 'garmin'},
                    {'label': 'Upload Local Dataset Jackson', 'value': 'upload'}
                ],
                value='garmin',
                labelStyle={'display': 'inline-block', 'margin-right': '20px'}
            )
        ], style={'margin-bottom': '20px'}),
    ])