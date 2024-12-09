
# modules/data_loader.py
import pandas as pd
import json
import io
import base64
from garminconnect import Garmin

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

def process_uploaded_file(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'json' in filename.lower():
            data = json.load(io.BytesIO(decoded))
            df = pd.DataFrame(data)
        else:
            return None, "Unsupported file format. Please upload a JSON file."

        required_columns = {"startTimeLocal", 'steps', 'calories', "distance", "averageHR"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"

        df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'], errors='coerce')
        if df['startTimeLocal'].isnull().any():
            return None, "Invalid date format in 'startTimeLocal' column."

        return df, f"File '{filename}' processed successfully."

    except Exception as e:
        return None, f"Error processing file: {e}"