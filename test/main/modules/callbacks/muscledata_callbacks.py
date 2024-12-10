# modules/callbacks/muscledata_callbacks.py
import json
import datetime
from dash.dependencies import Input, Output, State
from garminconnect import Garmin, GarminConnectAuthenticationError
import os

from modules.musclemap import musclemap_load, musclemap_plot

def register_muscledata_callbacks(app):
    @app.callback(
        [Output('garmin-status', 'children'),
        Output('strength-data-store', 'data')],
        [Input('fetch-button', 'n_clicks')],
        [State('garmin-email', 'value'),
        State('garmin-password', 'value')]
    )
    def fetch_strength_data(n_clicks, username, password):
        if n_clicks is None or n_clicks == 0:
            return "", None

        if not username or not password:
            return "Please provide Garmin username and password.", None

        try:
            # Initialize and login to Garmin
            api = Garmin(username, password)
            api.login()
        except GarminConnectAuthenticationError as auth_err:
            return f"Authentication error: {auth_err}", None
        except Exception as e:
            return f"Error initializing Garmin client: {e}", None

        # Define a date range (last 30 days) - adjust as needed
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=30)
        end_date = today

        # Fetch activities
        start = 0
        limit = 100
        strength_activities = []
        more_activities = True

        while more_activities:
            try:
                batch = api.get_activities(start, limit)
            except Exception as e:
                return f"Error fetching activities: {e}", None

            if not batch:
                break

            for activity in batch:
                activity_date_str = activity.get('startTimeLocal', activity.get('startTimeGMT'))
                if not activity_date_str:
                    continue
                try:
                    # Attempt parsing with and without milliseconds
                    try:
                        activity_date = datetime.datetime.strptime(activity_date_str, '%Y-%m-%d %H:%M:%S').date()
                    except ValueError:
                        activity_date = datetime.datetime.strptime(activity_date_str, '%Y-%m-%d %H:%M:%S.%f').date()
                except ValueError:
                    continue

                # Check date range
                if activity_date < start_date:
                    more_activities = False
                    break
                elif activity_date > end_date:
                    continue

                # Filter for strength_training
                if activity['activityType']['typeKey'] == 'strength_training':
                    strength_activities.append(activity)

            if len(batch) < limit:
                break
            start += limit

        if not strength_activities:
            return f"No strength activities found between {start_date} and {end_date}.", None

        msg = f"Fetched {len(strength_activities)} strength activities from Garmin."
        # Return as JSON string for storage in dcc.Store
        data_json = json.dumps(strength_activities)
        return msg, data_json

    @app.callback(
        [Output('processed-strength-data-store', 'data'),
        Output('muscle-map-image', 'src')],
        [Input('strength-data-store', 'data')]
    )
    def process_and_plot_muscle_map(raw_data):
        if not raw_data:
            return None, None

        strength_activities = json.loads(raw_data)

        # Process the strength activities
        processed_data = musclemap_load.process_strength_activities(strength_activities)

        # Load muscle coordinates
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Coordinates path is relative to modules/musclemap directory
        coordinates_path = os.path.join(script_dir, '..', 'musclemap', 'data', 'muscle_coordinates.json')
        muscle_coordinates = musclemap_plot.load_and_parse_muscle_coordinates(coordinates_path)

        # Generate the muscle map image
        img_data = musclemap_plot.plot_muscle_map(
            processed_data,
            muscle_coordinates,
            title="Muscle Map - Front View",
            zoom_out_factor=1.5
        )

        # Return processed data and image src (base64 data URL)
        img_src = f"data:image/png;base64,{img_data}"
        return json.dumps(processed_data), img_src
