# modules/charts/barchart.py
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import dash
from dash.exceptions import PreventUpdate

def create_barchart_layout(first_day_last_month, last_day_last_month):
    return html.Div([
        html.H1("Interactive Fitness Activity Dashboard"),

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
        create_metric_controls(first_day_last_month, last_day_last_month),
        dcc.Graph(id="activity-graph"),
        dcc.Store(id='stored-data')
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

def create_metric_controls(first_day_last_month, last_day_last_month):
    return html.Div([
        html.Label("Select Metric:"),
        dcc.Dropdown(
            id='metric-selector',
            options=[
                {'label': 'Calories', 'value': 'calories'},
                {'label': 'Steps', 'value': 'steps'},
                {'label': 'Duration', 'value': 'duration'}
            ],
            value='calories'
        ),
        html.Label("Select Time Frame:"),
        dcc.DatePickerRange(
            id='date-range',
            start_date=first_day_last_month.date(),
            end_date=last_day_last_month.date()
        ),
        html.Label("Set Goal Value:"),
        dcc.Input(id="goal-input", type="number", value=500, placeholder="Enter goal value"),
        html.Button("Set Goal", id="set-goal-button", n_clicks=0)
    ])

def create_activity_chart(df, selected_metric, start_date, end_date, goal_value):
    mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
    filtered_df = df.loc[mask]

    goal_reached = filtered_df[filtered_df[selected_metric] >= goal_value]
    goal_not_reached = filtered_df[filtered_df[selected_metric] < goal_value]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=goal_reached['startTimeLocal'],
        y=goal_reached[selected_metric],
        marker_color='green',
        name='Goal Reached'
    ))

    fig.add_trace(go.Bar(
        x=goal_not_reached['startTimeLocal'],
        y=goal_not_reached[selected_metric],
        marker_color='red',
        name='Goal Not Reached'
    ))

    fig.add_trace(go.Scatter(
        x=[start_date, end_date],
        y=[goal_value, goal_value],
        mode='lines',
        name='Goal',
        line=dict(color='blue', dash='dash')
    ))

    fig.update_layout(
        title=f"{selected_metric.capitalize()} Over Time",
        xaxis_title='startTimeLocal',
        yaxis_title=selected_metric.capitalize(),
        xaxis=dict(
            tickformat="%b %d",
            ticklabelmode="period",
            dtick="D1"
        ),
        barmode='group'
    )

    return fig