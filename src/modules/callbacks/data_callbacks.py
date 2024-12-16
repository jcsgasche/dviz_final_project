# modules/callbacks/data_callbacks.py
import dash
from dash import Input, Output, State
import pandas as pd
import json
import base64
import io
from datetime import datetime
from garminconnect import Garmin

def register_data_callbacks(app):
    # Separate callback for file upload
    @app.callback(
        [Output('stored-data', 'data', allow_duplicate=True),
         Output('strength-data-store', 'data', allow_duplicate=True),
         Output('garmin-status', 'children', allow_duplicate=True),
         Output('last-update-time', 'data', allow_duplicate=True)],
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def process_upload(contents, filename):
        if contents is None:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            if 'json' in filename.lower():
                data = json.loads(decoded)
                all_activities = []
                strength_activities = []

                activities_list = data if isinstance(data, list) else [data]

                for activity in activities_list:
                    if 'summarizedExerciseSets' in activity:
                        strength_activities.append(activity)
                    all_activities.append(activity)

                activities_df = pd.DataFrame(all_activities)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                return (
                    activities_df.to_dict('records'),
                    json.dumps(strength_activities),
                    f"File '{filename}' processed successfully.",
                    current_time
                )
            else:
                return None, None, "Please upload a JSON file.", None

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return None, None, f"Error processing file: {str(e)}", None

    # Main callback for Garmin fetch and clear
    @app.callback(
        [Output('stored-data', 'data'),
         Output('strength-data-store', 'data'),
         Output('garmin-status', 'children'),
         Output('last-update-time', 'data'),
         Output('upload-data', 'contents')],  # Add output to reset upload component
        [Input('fetch-button', 'n_clicks'),
         Input('upload-data', 'contents'),
         Input('clear-data-button', 'n_clicks')],
        [State('garmin-email', 'value'),
         State('garmin-password', 'value'),
         State('data-source', 'value'),
         State('upload-data', 'filename')]
    )
    def update_data(n_clicks, contents, clear_clicks, username, password, data_source, filename):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Handle clear data button
        if trigger_id == 'clear-data-button':
            return None, None, "Data cleared. You can now upload new data or fetch from Garmin.", None, None

        # Handle file upload
        if trigger_id == 'upload-data' and contents:
            try:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)

                if 'json' in filename.lower():
                    data = json.loads(decoded)
                    all_activities = []
                    strength_activities = []

                    activities_list = data if isinstance(data, list) else [data]

                    for activity in activities_list:
                        if 'summarizedExerciseSets' in activity:
                            strength_activities.append(activity)
                        all_activities.append(activity)

                    activities_df = pd.DataFrame(all_activities)
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    return (
                        activities_df.to_dict('records'),
                        json.dumps(strength_activities),
                        f"File '{filename}' processed successfully.",
                        current_time,
                        None  # Reset upload contents after successful processing
                    )
                else:
                    return None, None, "Please upload a JSON file.", None, None

            except Exception as e:
                print(f"Error processing file: {str(e)}")
                return None, None, f"Error processing file: {str(e)}", None, None

        # Handle Garmin fetch
        if trigger_id == 'fetch-button' and n_clicks:
            if not username or not password:
                return None, None, "Please provide Garmin username and password.", None, dash.no_update

            try:
                api = Garmin(username, password)
                api.login()

                start = 0
                limit = 100
                all_activities = []
                strength_activities = []
                more_activities = True

                while more_activities:
                    batch = api.get_activities(start, limit)
                    if not batch:
                        break

                    for activity in batch:
                        if activity['activityType']['typeKey'] == 'strength_training':
                            strength_activities.append(activity)
                        all_activities.append(activity)

                    if len(batch) < limit:
                        break
                    start += limit

                activities_df = pd.DataFrame(all_activities)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                return (
                    activities_df.to_dict('records'),
                    json.dumps(strength_activities),
                    "Data fetched successfully from Garmin.",
                    current_time,
                    dash.no_update
                )

            except Exception as e:
                return None, None, f"Error: {str(e)}", None, dash.no_update

        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        [Output('garmin-login', 'style', allow_duplicate=True),
         Output('file-upload', 'style', allow_duplicate=True)],
        [Input('data-source', 'value')],
        prevent_initial_call=True
    )
    def toggle_input_visibility(data_source):
        if data_source == 'garmin':
            return {'display': 'block'}, {'display': 'none'}
        return {'display': 'none'}, {'display': 'block'}

    @app.callback(
        [Output('download-section', 'style'),
         Output('clear-data-section', 'style'),
         Output('last-update-display', 'children')],
        [Input('stored-data', 'data'),
         Input('last-update-time', 'data')]
    )
    def update_ui_elements(data, last_update):
        if data:
            display_style = {'marginTop': '20px', 'display': 'block'}
            last_update_text = f"Last updated: {last_update}" if last_update else ""
            return display_style, display_style, last_update_text
        return {'display': 'none'}, {'display': 'none'}, ""

    @app.callback(
        Output("download-data", "data"),
        Input("btn-download", "n_clicks"),
        [State("download-type", "value"),
         State("stored-data", "data"),
         State("strength-data-store", "data")],
        prevent_initial_call=True
    )
    def download_data(n_clicks, download_type, all_data, strength_data):
        if not n_clicks:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if download_type == 'all' and all_data:
            return dict(
                content=json.dumps(all_data, indent=2),
                filename=f"garmin_activities_{timestamp}.json"
            )
        elif download_type == 'strength' and strength_data:
            return dict(
                content=strength_data,
                filename=f"garmin_strength_activities_{timestamp}.json"
            )

        return None