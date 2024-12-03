import pandas
from dash import Dash, dcc, html, Input, Output, State
import dash
from dash.exceptions import PreventUpdate
import io
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import base64
from garminconnect import Garmin

# Calculate the last full month’s date range
today = datetime.today()
first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
last_day_last_month = today.replace(day=1) - timedelta(days=1)

# Initialize Dash app
app = Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Interactive Fitness Activity Dashboard"),

    # Radio buttons to select data source
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

    # Garmin login form
    html.Div([
        html.Label("Garmin Email:"),
        dcc.Input(id='garmin-email', type='email', placeholder='Enter your Garmin email', style={'width': '300px'}),
        html.Br(),
        html.Label("Garmin Password:"),
        dcc.Input(id='garmin-password', type='password', placeholder='Enter your Garmin password', style={'width': '300px'}),
        html.Br(),
        html.Button('Fetch Data', id='fetch-button', n_clicks=0, style={'margin-top': '10px'})
    ], id='garmin-login', style={'display': 'block'}),

    # File upload component
    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
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
    ], id='file-upload', style={'display': 'none'}),

    # Garmin status message
    html.Div(id='garmin-status', style={'margin-top': '10px', 'color': 'green'}),

    # Button to manually refresh data (only for Garmin fetch)
    html.Div([
        html.Button('Refresh Data', id='refresh-button', n_clicks=0)
    ], id='refresh-section', style={'margin-bottom': '20px'}),


    # Dropdown for metric selection
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

    # Date range picker with last full month as default
    html.Label("Select Time Frame:"),
    dcc.DatePickerRange(
        id='date-range',
        start_date=first_day_last_month.date(),
        end_date=last_day_last_month.date()
    ),

    # Input for goal setting
    html.Label("Set Goal Value:"),
    dcc.Input(id="goal-input", type="number", value=500, placeholder="Enter goal value"),
    html.Button("Set Goal", id="set-goal-button", n_clicks=0),

    # Graph to display the activity data
    dcc.Graph(id="activity-graph"),

    # Store component to hold the fetched or uploaded data
    dcc.Store(id='stored-data'),
])

# Callback to toggle visibility of Garmin login and file upload based on data source
@app.callback(
    [Output('garmin-login', 'style'),
     Output('file-upload', 'style'),
     Output('refresh-section', 'style')],
    [Input('data-source', 'value')]
)
def toggle_data_source(selected_source):
    if selected_source == 'garmin':
        return {'display': 'block'}, {'display': 'none'}, {'display': 'block', 'margin-bottom': '20px'}
    else:
        return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}

@app.callback(
    [
        Output('stored-data', 'data'),
        Output('garmin-status', 'children'),
        Output('upload-status', 'children')
    ],
    [
        Input('fetch-button', 'n_clicks'),
        Input('upload-data', 'contents')
    ],
    [
        State('garmin-email', 'value'),
        State('garmin-password', 'value'),
        State('data-source', 'value'),
        State('upload-data', 'filename')
    ]
)
def handle_data_sources(fetch_clicks, upload_contents, email, password, data_source, upload_filename):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    stored_data = dash.no_update
    garmin_message = dash.no_update
    upload_message = dash.no_update

    if triggered_id == 'fetch-button' and data_source == 'garmin':
        if not email or not password:
            garmin_message = "Please provide both email and password."
            return stored_data, garmin_message, dash.no_update

        df, message = fetch_garmin_data(email, password)

        if df.empty:
            garmin_message = message
            return stored_data, garmin_message, dash.no_update
        else:
            stored_data = df.to_dict(orient='records')
            garmin_message = message
            return stored_data, garmin_message, dash.no_update

    elif triggered_id == 'upload-data' and data_source == 'upload':
        if upload_contents is None:
            upload_message = "No file uploaded."
            return stored_data, dash.no_update, upload_message

        content_type, content_string = upload_contents.split(',')
        decoded = base64.b64decode(content_string)

        try:
            # For upload:
            if 'json' in upload_filename.lower():
                data = json.load(io.BytesIO(decoded))
                print("Upload data structure:", type(data), data[:1])  # Print first item
                df = pd.DataFrame(data)
            elif 'csv' in upload_filename.lower():
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in upload_filename.lower() or 'xlsx' in upload_filename.lower():
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                upload_message = "Unsupported file format. Please upload a JSON, CSV, or Excel file."
                return stored_data, dash.no_update, upload_message

            required_columns = {"startTimeLocal", 'steps', 'calories', "distance", "averageHR"}
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                upload_message = f"Missing required columns: {', '.join(missing_columns)}"
                return stored_data, dash.no_update, upload_message

            df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'], errors='coerce')

            if df['startTimeLocal'].isnull().any():
                upload_message = "Invalid date format in 'startTimeLocal' column."
                return stored_data, dash.no_update, upload_message

            stored_data = df.to_dict(orient='records')
            upload_message = f"File '{upload_filename}' processed successfully."
            return stored_data, dash.no_update, upload_message

        except Exception as e:
            print(f"Error processing file: {e}")
            upload_message = f"Error processing file: {e}"
            return stored_data, dash.no_update, upload_message

    raise PreventUpdate

# Function to fetch data from Garmin
def fetch_garmin_data(username, password):
    try:
        client = Garmin(username, password)
        client.login()
        activities = client.get_activities(0, 30)

        activity_data = {
            "startTimeLocal": [],
            'steps': [],
            'calories': [],
            "distance": [],
            "averageHR": [],
        }

        for activity in activities:
            activity_data['startTimeLocal'].append(activity["startTimeLocal"])
            activity_data['steps'].append(activity.get('steps', 0))
            activity_data['calories'].append(activity.get('calories', 0))
            activity_data['distance'].append(activity.get("distance", 0) / 1000)
            activity_data['averageHR'].append(activity.get("averageHR", 0))

        df = pd.DataFrame(activity_data)
        return df, "Data fetched successfully from Garmin."
    except Exception as e:
        print(f"Error fetching Garmin data: {e}")
        return pd.DataFrame(), f"Error fetching data: {e}"

# Callback to trigger data refresh (only applicable for Garmin data)
@app.callback(
    Output('fetch-button', 'n_clicks'),
    [Input('refresh-button', 'n_clicks')],
    [State('data-source', 'value')]
)
def refresh_data(n_clicks_refresh, data_source):
    if data_source != 'garmin':
        raise PreventUpdate
    if n_clicks_refresh > 0:
        return n_clicks_refresh + 1  # Increment to trigger the fetch callback
    return dash.no_update


@app.callback(
    Output('activity-graph', 'figure'),
    [Input('metric-selector', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('set-goal-button', 'n_clicks'),
     Input('activity-graph', 'relayoutData'),
     Input('stored-data', 'data')],  # Add stored-data as Input
    [State('goal-input', 'value')]
)
def update_chart(selected_metric, start_date, end_date, n_clicks, relayout_data, stored_data, goal_value):
    if not stored_data:
        print("No stored data!")
        return go.Figure()  # Return empty figure if no data

    df = pd.DataFrame(stored_data)
    df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

    if goal_value is None or n_clicks == 0:
        goal_value = 500

    if relayout_data and 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
        start_date = relayout_data['xaxis.range[0]'][:10]
        end_date = relayout_data['xaxis.range[1]'][:10]

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


# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
