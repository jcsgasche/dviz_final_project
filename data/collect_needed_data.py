import pandas as pd
from garminconnect import Garmin

# Function to fetch data from Garmin
def fetch_garmin_data(username, password):
    try:
        # Log in to Garmin
        client = Garmin(username, password)
        client.login()
        # Fetch last 30 activities
        activities = client.get_activities(0, 30)

        # Extract required data
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

        # Convert to DataFrame
        df = pd.DataFrame(activity_data)
        return df
    except Exception as e:
        print(f"Error fetching Garmin data: {e}")
        return pd.DataFrame()

# Save data to CSV
def save_data_to_csv(df, filename="garmin_data.csv"):
    if not df.empty:
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save.")

# Replace with your Garmin credentials
garmin_email = "janicksteffen@hotmail.com"
garmin_password = "07@Janick@98"

# Fetch and save data
df = fetch_garmin_data(garmin_email, garmin_password)
save_data_to_csv(df)
