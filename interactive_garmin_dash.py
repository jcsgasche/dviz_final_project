import base64
import io
from garminconnect import Garmin
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server  # For deployment purposes

# Define layout
app.layout = html.Div([
    html.H1("Activity Dashboard"),

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

    # Garmin status message
    html.Div(id='garmin-status', style={'margin-top': '10px', 'color': 'green'}),

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

    # Dropdown to select the metric
    html.Div([
        dcc.Dropdown(
            id="metric-dropdown",
            options=[
                {"label": "Steps", "value": "Steps"},
                {"label": "Calories", "value": "Calories"},
                {"label": "Distance (km)", "value": "Distance_km"},
                {"label": "Average Heart Rate", "value": "Avg_HeartRate"}
            ],
            value="Steps",
            clearable=False,
            style={'width': '300px'}
        )
    ], style={'margin-top': '20px', 'margin-bottom': '20px'}),

    # Button to manually refresh data (only for Garmin fetch)
    html.Div([
        html.Button('Refresh Data', id='refresh-button', n_clicks=0)
    ], id='refresh-section', style={'margin-bottom': '20px'}),

    # Graph to display the activity data
    dcc.Graph(id="activity-graph"),

    # Store component to hold the fetched or uploaded data
    dcc.Store(id='stored-data')
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

# Function to fetch data from Garmin
def fetch_garmin_data(username, password):
    try:
        client = Garmin(username, password)
        client.login()
        activities = client.get_activities(0, 30)

        activity_data = {
            "Date": [],
            "Steps": [],
            "Calories": [],
            "Distance_km": [],
            "Avg_HeartRate": [],
        }

        for activity in activities:
            activity_data["Date"].append(activity["startTimeLocal"])
            activity_data["Steps"].append(activity.get("steps", 0))
            activity_data["Calories"].append(activity.get("calories", 0))
            activity_data["Distance_km"].append(activity.get("distance", 0) / 1000)
            activity_data["Avg_HeartRate"].append(activity.get("averageHR", 0))

        df = pd.DataFrame(activity_data)
        return df, "Data fetched successfully from Garmin."
    except Exception as e:
        print(f"Error fetching Garmin data: {e}")
        return pd.DataFrame(), f"Error fetching data: {e}"

# Callback to handle Garmin data fetching and file uploads
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
            garmin_message = message  # Error message
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
            if 'csv' in upload_filename.lower():
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in upload_filename.lower() or 'xlsx' in upload_filename.lower():
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                upload_message = "Unsupported file format. Please upload a CSV or Excel file."
                return stored_data, dash.no_update, upload_message

            # Validate required columns
            required_columns = {"Date", "Steps", "Calories", "Distance_km", "Avg_HeartRate"}
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                upload_message = f"Uploaded file is missing required columns: {', '.join(missing_columns)}"
                return stored_data, dash.no_update, upload_message

            # Convert 'Date' column to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # Check for conversion errors
            if df['Date'].isnull().any():
                upload_message = "Some dates could not be parsed. Please check your 'Date' column."
                return stored_data, dash.no_update, upload_message

            stored_data = df.to_dict(orient='records')
            upload_message = f"File '{upload_filename}' uploaded and processed successfully."
            return stored_data, dash.no_update, upload_message

        except Exception as e:
            print(f"Error processing uploaded file: {e}")
            upload_message = f"Error processing file: {e}"
            return stored_data, dash.no_update, upload_message

    else:
        raise PreventUpdate

# Callback to update the graph based on selected metric and data source
@app.callback(
    Output("activity-graph", "figure"),
    [
        Input("metric-dropdown", "value"),
        Input('stored-data', 'data')
    ]
)
def update_graph(selected_metric, data):
    if data is None:
        return {
            "data": [],
            "layout": {
                "title": "No data available. Please fetch from Garmin or upload a dataset."
            }
        }

    df = pd.DataFrame(data)

    if df.empty:
        return {
            "data": [],
            "layout": {
                "title": "Data is empty."
            }
        }

    # Ensure 'Date' is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Drop rows with invalid dates
    df = df.dropna(subset=['Date'])

    # Sort by Date
    df = df.sort_values('Date')

    fig = px.line(df, x="Date", y=selected_metric, markers=True, title=f"{selected_metric} per Day")
    fig.update_layout(xaxis_title="Date", yaxis_title=selected_metric)
    fig.update_xaxes(tickangle=45)
    return fig

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

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
