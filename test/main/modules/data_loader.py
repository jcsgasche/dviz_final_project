import json
import pandas as pd
from garminconnect import Garmin

def load_data(json_path):
    """Load data from a local JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])
    return df.to_dict(orient='records')

def fetch_garmin_data(email, password):
    """Fetch data from Garmin."""
    try:
        client = Garmin(email, password)
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
        df['Date'] = pd.to_datetime(df['Date'])
        return df.to_dict(orient='records')

    except Exception as e:
        print(f"Error fetching Garmin data: {e}")
        return None
