from garminconnect import Garmin, GarminConnectAuthenticationError
import getpass
import datetime
import json

def main():
    # Prompt the user for Garmin Connect credentials
    username = input("Enter your Garmin username: ")
    password = getpass.getpass("Enter your Garmin password: ")

    # Initialize the Garmin client
    try:
        api = Garmin(username, password)
    except Exception as e:
        print("Error initializing Garmin client:", e)
        return

    # Login to Garmin Connect
    try:
        api.login()
        print("Successfully logged in to Garmin Connect.")
    except GarminConnectAuthenticationError as auth_err:
        print("Authentication error:", auth_err)
        # Check if MFA is required
        if "two-factor" in str(auth_err).lower() or "multi-factor" in str(auth_err).lower():
            mfa_code = input("Enter the MFA code sent to your device: ")
            try:
                api.login(mfa_code)
                print("Successfully logged in with MFA.")
            except Exception as e:
                print("Error logging in with MFA:", e)
                return
        else:
            print("Login failed due to authentication error.")
            return
    except Exception as e:
        print("Error logging in to Garmin Connect:", e)
        return

    # Prompt for start and end dates
    start_date_str = input("Enter the start date (YYYY-MM-DD): ")
    end_date_str = input("Enter the end date (YYYY-MM-DD): ")

    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError as e:
        print("Invalid date format:", e)
        return

    # Initialize variables for fetching activities
    start = 0
    limit = 100  # Number of activities to fetch per request
    activities = []
    more_activities = True

    # Fetch activities in batches and filter by date range and activity type
    while more_activities:
        print(f"Fetching activities {start + 1} to {start + limit}...")
        try:
            batch = api.get_activities(start, limit)
        except Exception as e:
            print("Error fetching activities:", e)
            return

        if not batch:
            break

        for activity in batch:
            # Parse the activity date
            activity_date_str = activity.get('startTimeLocal', activity.get('startTimeGMT'))
            try:
                activity_date = datetime.datetime.strptime(
                    activity_date_str, '%Y-%m-%d %H:%M:%S'
                ).date()
            except ValueError:
                # Handle activities with milliseconds in the timestamp
                activity_date = datetime.datetime.strptime(
                    activity_date_str, '%Y-%m-%d %H:%M:%S.%f'
                ).date()

            # Check if activity is within the date range
            if activity_date < start_date:
                # Since activities are ordered from newest to oldest, we can stop
                more_activities = False
                break
            elif activity_date > end_date:
                continue  # Skip activities after the end date

            # Filter activities by type 'strength_training'
            if activity['activityType']['typeKey'] == 'strength_training':
                activities.append(activity)

        # Check if we've fetched all activities
        if len(batch) < limit:
            break

        start += limit

    # Save the filtered activities to a JSON file
    if activities:
        with open('strength_activities.json', 'w') as f:
            json.dump(activities, f, indent=4)
        print(
            f"Found {len(activities)} strength activities between {start_date} and {end_date}."
        )
        print("Activities have been saved to 'strength_activities.json'.")
    else:
        print(f"No strength activities found between {start_date} and {end_date}.")

if __name__ == "__main__":
    main()