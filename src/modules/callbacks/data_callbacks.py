# modules/callbacks/data_callbacks.py
from dash import Input, Output, State
import pandas as pd
import base64
import io
import json
from garminconnect import Garmin
from datetime import datetime

def register_data_callbacks(app):
    @app.callback(
        [Output('stored-data', 'data'),
         Output('strength-data-store', 'data'),
         Output('garmin-status', 'children')],
        [Input('fetch-button', 'n_clicks'),
         Input('upload-data', 'contents')],
        [State('garmin-email', 'value'),
         State('garmin-password', 'value'),
         State('data-source', 'value'),
         State('upload-data', 'filename')]
    )
    def update_data(n_clicks, contents, username, password, data_source, filename):
        if not any([n_clicks, contents]):
            return None, None, ""

        if data_source == 'garmin' and n_clicks:
            if not username or not password:
                return None, None, "Please provide Garmin username and password."

            try:
                api = Garmin(username, password)
                api.login()

                # Fetch all activities first
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

                # Convert all activities to DataFrame for regular charts
                activities_df = pd.DataFrame(all_activities)

                return (
                    activities_df.to_dict('records'),
                    json.dumps(strength_activities),
                    "Data fetched successfully from Garmin."
                )

            except Exception as e:
                return None, None, f"Error: {str(e)}"

        elif data_source == 'upload' and contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            try:
                if 'json' in filename.lower():
                    # Parse the uploaded JSON
                    data = json.loads(decoded)

                    # Process all activities regardless of type
                    all_activities = []
                    strength_activities = []

                    # Handle both single object and list formats
                    activities_list = data if isinstance(data, list) else [data]

                    for activity in activities_list:
                        # Add to strength activities if it has exercise sets
                        if 'summarizedExerciseSets' in activity:
                            strength_activities.append(activity)
                        # Add all activities to the main list
                        all_activities.append(activity)

                    # Convert to DataFrame for regular charts
                    activities_df = pd.DataFrame(all_activities)

                    return (
                        activities_df.to_dict('records'),
                        json.dumps(strength_activities),
                        f"File '{filename}' processed successfully."
                    )
                else:
                    return None, None, "Please upload a JSON file."

            except Exception as e:
                print(f"Error processing file: {str(e)}")  # For debugging
                return None, None, f"Error processing file: {str(e)}"

        return None, None, ""

    @app.callback(
        Output("download-section", "style"),
        [Input("stored-data", "data")]
    )
    def show_download_section(data):
        if data:
            return {'marginTop': '20px', 'display': 'block'}
        return {'marginTop': '20px', 'display': 'none'}

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

        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if download_type == 'all' and all_data:
            return dict(
                content=json.dumps(all_data, indent=2),
                filename=f"garmin_activities_{timestamp}.json"
            )
        elif download_type == 'strength' and strength_data:
            return dict(
                content=strength_data,  # strength_data is already JSON string
                filename=f"garmin_strength_activities_{timestamp}.json"
            )

        return None