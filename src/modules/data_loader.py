
# modules/data_loader.py
import pandas as pd
import json
import io
import base64
from garminconnect import Garmin

def process_activity_data(data, source="file"):
    """Common processing function for both API and file data"""
    try:
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data

        # Convert to datetime but don't enforce it as strictly for strength data
        if 'startTimeLocal' in df.columns:
            df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'], errors='coerce')

        # For strength activities, we need different processing
        if 'summarizedExerciseSets' in df.columns:
            # Don't enforce the same column requirements
            return df, f"Strength data processed successfully from {source}."

        # For regular activities, check required columns
        required_columns = {"startTimeLocal", 'steps', 'calories', "distance", "averageHR"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"

        return df, f"Data processed successfully from {source}."

    except Exception as e:
        return None, f"Error processing data: {e}"

def fetch_garmin_data(username, password):
    try:
        client = Garmin(username, password)
        client.login()
        activities = client.get_activities(0, 30)
        return process_activity_data(activities, "Garmin API")
    except Exception as e:
        print(f"Error fetching Garmin data: {e}")
        return pd.DataFrame(), f"Error fetching data: {e}"

def process_uploaded_file(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'json' in filename.lower():
            data = json.load(io.BytesIO(decoded))
            return process_activity_data(data, filename)
        else:
            return None, "Unsupported file format. Please upload a JSON file."

    except Exception as e:
        return None, f"Error processing file: {e}"