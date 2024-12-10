# modules/callbacks/data_callbacks.py
from dash import Input, Output, State
import pandas as pd
import base64
import io
import json
from garminconnect import Garmin

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

                # Fetch general activities
                activities = api.get_activities(0, 30)
                activities_df = pd.DataFrame(activities)

                # Fetch strength training activities
                start = 0
                limit = 100
                strength_activities = []
                more_activities = True

                while more_activities:
                    batch = api.get_activities(start, limit)
                    if not batch:
                        break

                    for activity in batch:
                        if activity['activityType']['typeKey'] == 'strength_training':
                            strength_activities.append(activity)

                    if len(batch) < limit:
                        break
                    start += limit

                return activities_df.to_dict('records'), json.dumps(strength_activities), "Data fetched successfully from Garmin."

            except Exception as e:
                return None, None, f"Error: {str(e)}"

        elif data_source == 'upload' and contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            try:
                if 'json' in filename.lower():
                    data = json.loads(decoded)
                    df = pd.DataFrame(data)
                    return df.to_dict('records'), json.dumps([]), f"File '{filename}' processed successfully."
                else:
                    return None, None, "Please upload a JSON file."
            except Exception as e:
                return None, None, f"Error processing file: {str(e)}"

        return None, None, ""