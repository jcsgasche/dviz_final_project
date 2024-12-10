from dash import Input, Output, State
import pandas as pd
import base64
import io
import json
from garminconnect import Garmin
import datetime
from modules.musclemap import musclemap_load, musclemap_plot
import os

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

    @app.callback(
        [Output('processed-strength-data-store', 'data'),
         Output('muscle-map-image', 'src')],
        [Input('strength-data-store', 'data'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_muscle_map(raw_data, start_date, end_date):
        if not raw_data or not start_date or not end_date:
            return None, None

        strength_activities = json.loads(raw_data)

        # Filter activities by date range
        filtered_activities = []
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        for activity in strength_activities:
            activity_date_str = activity.get('startTimeLocal', activity.get('startTimeGMT'))
            if not activity_date_str:
                continue

            try:
                activity_date = datetime.datetime.strptime(
                    activity_date_str.split('.')[0], '%Y-%m-%d %H:%M:%S'
                ).date()

                if start <= activity_date <= end:
                    filtered_activities.append(activity)
            except ValueError:
                continue

        # Process the filtered activities
        processed_data = musclemap_load.process_strength_activities(filtered_activities)

        # Load muscle coordinates
        script_dir = os.path.dirname(os.path.abspath(__file__))
        coordinates_path = os.path.join(script_dir, '..', 'musclemap', 'data', 'muscle_coordinates.json')
        muscle_coordinates = musclemap_plot.load_and_parse_muscle_coordinates(coordinates_path)

        # Generate the muscle map image
        img_data = musclemap_plot.plot_muscle_map(
            processed_data,
            muscle_coordinates,
            title=f"Muscle Activity ({start_date} to {end_date})",
            zoom_out_factor=1.5
        )

        img_src = f"data:image/png;base64,{img_data}"
        return json.dumps(processed_data), img_src