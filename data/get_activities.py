import pandas as pd
import json
from garminconnect import Garmin
from typing import Tuple
import getpass

def export_garmin_data(username: str, password: str) -> Tuple[str, str]:
    """
    Export Garmin Connect data to JSON files.

    Args:
        username (str): Garmin Connect username
        password (str): Garmin Connect password

    Returns:
        Tuple[str, str]: Paths to the general activities and strength training JSON files
    """
    try:
        # Initialize and login to Garmin Connect
        api = Garmin(username, password)
        api.login()

        # Fetch and save general activities
        activities = api.get_activities(0, 30)
        activities_df = pd.DataFrame(activities)
        activities_file = 'garmin_activities.json'
        activities_df.to_json(activities_file, orient='records', indent=4)

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

        # Save strength training activities
        strength_file = 'garmin_strength_activities.json'
        with open(strength_file, 'w') as f:
            json.dump(strength_activities, f, indent=4)

        print(f"Successfully exported {len(activities)} general activities to {activities_file}")
        print(f"Successfully exported {len(strength_activities)} strength activities to {strength_file}")

        return activities_file, strength_file

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None, None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Export Garmin Connect data to JSON files')
    parser.add_argument('--username', help='Garmin Connect username')
    parser.add_argument('--password', help='Garmin Connect password')

    args = parser.parse_args()

    # If credentials aren't provided as arguments, prompt for them
    username = args.username
    password = args.password

    if not username:
        username = input("Enter your Garmin Connect username: ")
    if not password:
        password = getpass.getpass("Enter your Garmin Connect password: ")

    export_garmin_data(username, password)